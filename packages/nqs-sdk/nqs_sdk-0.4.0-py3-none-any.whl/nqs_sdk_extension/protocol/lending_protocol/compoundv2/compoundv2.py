from __future__ import annotations

import copy
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Tuple

from nqs_pycore import Wallet

from nqs_sdk_extension.constants import OVERFLOW
from nqs_sdk_extension.protocol import ABCProtocol
from nqs_sdk_extension.protocol.lending_protocol.compoundv2.ctoken_interest_rate import CTokenInterestRateModel
from nqs_sdk_extension.protocol.lending_protocol.compoundv2.full_math import (
    EXPSCALE,
    Exp,
    div_exp,
    div_int_exp,
    mul_exp,
    mul_exp_int,
    mul_int_exp,
    mul_scalar_truncate,
    mul_scalar_truncate_add_int,
)
from nqs_sdk_extension.protocol.utils import rollback_on_failure
from nqs_sdk_extension.state import ABCProtocolState
from nqs_sdk_extension.state.compoundv2 import BorrowSnapshot, StateCompoundMarket, StateComptroller
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.compoundv2 import (
    BorrowTransactionCompv2,
    LiquidateTransactionCompv2,
    MintTransactionCompv2,
    RedeemTransactionCompv2,
    RepayBorrowTransactionCompv2,
    TransactionCompoundv2,
    TransferTransactionCompv2,
)
from nqs_sdk_extension.wallet.arbitrageur_wallet import ArbitrageurWallet

LENDING_PROTOCOL_MANDATORY_TOKEN = "USDC"


class Comptroller(ABCProtocol):
    def __init__(self, state: StateComptroller, gas_fee: int = 0, gas_fee_ccy: Optional[str] = None):
        super().__init__(state, gas_fee, gas_fee_ccy)
        self.close_factor_mantissa = state.close_factor_mantissa
        self.liquidation_incentive_mantissa = state.liquidation_incentive_mantissa
        self.max_assets = state.max_assets
        self.borrow_caps: dict[str, int] = {}
        self.collateral_factor_mantissa: dict[str, int] = {}
        self.markets: dict[str, CompoundMarket] = {}
        self.spot_update_timestamp = -1

        for market in state.market_states:
            self.initialise_market(state.market_states[market])

        self.underlying_tokens = [market.underlying for _, market in self.markets.items()]
        # Compound uses USD prices - with the simplifying assumption that 1USDC=1USD always
        self.required_spots = [(x, LENDING_PROTOCOL_MANDATORY_TOKEN) for x in self.underlying_tokens]
        self._stored_spot: dict[Tuple[str, str], float] = {}

    def initialise_market(self, state_market: StateCompoundMarket) -> None:
        for supported_market in self.markets.keys():
            assert (
                supported_market != state_market.symbol
            ), f"Trying to add the market {supported_market}, which is already supported by the Comptroller"
        self.markets[state_market.symbol] = CompoundMarket(state_market, self)
        self.collateral_factor_mantissa[state_market.symbol] = state_market.collateral_factor
        self.borrow_caps[state_market.symbol] = state_market.borrow_cap

    def get_hypothetical_account_net_position_internal(
        self,
        wallet: Wallet,
        ctoken_modify: str,
        redeem_tokens: int,
        borrow_amount: int,
        underlying_price: dict[Tuple[str, str], float],
    ) -> Tuple[int, int, int]:
        if isinstance(wallet, ArbitrageurWallet):
            return OVERFLOW // 2, 0, OVERFLOW // 2

        return self.get_hypothetical_account_net_position(
            wallet, ctoken_modify, redeem_tokens, borrow_amount, underlying_price
        )

    def get_hypothetical_account_net_position(
        self,
        wallet: Wallet,
        ctoken_modify: str,
        redeem_tokens: int,
        borrow_amount: int,
        underlying_price: dict[Tuple[str, str], float],
    ) -> Tuple[int, int, int]:
        holdings = wallet.holdings.keys()
        interacting_markets = [
            market.symbol
            for market in self.markets.values()
            if market.symbol in holdings or market.underlying in holdings
        ]
        sum_collateral = 0
        sum_collateral_undiscounted = 0
        sum_borrow_plus_effects = 0
        for ctoken in interacting_markets:
            ctoken_balance, borrow_balance, exchange_rate_mantissa = self.markets[ctoken].get_account_snapshot(wallet)
            exchange_rate = Exp(exchange_rate_mantissa)
            collateral_factor = Exp(self.collateral_factor_mantissa[ctoken])
            token_price = Exp(
                int(
                    Decimal(underlying_price[(self.markets[ctoken].underlying, LENDING_PROTOCOL_MANDATORY_TOKEN)])
                    * 10 ** (36 - self.markets[ctoken].underlying_decimals)
                )
            )

            tokens_to_denom = mul_exp(mul_exp(collateral_factor, exchange_rate), token_price)
            sum_collateral = mul_scalar_truncate_add_int(tokens_to_denom, ctoken_balance, sum_collateral)
            sum_collateral_undiscounted = mul_scalar_truncate_add_int(
                mul_exp(exchange_rate, token_price), ctoken_balance, sum_collateral_undiscounted
            )
            sum_borrow_plus_effects = mul_scalar_truncate_add_int(token_price, borrow_balance, sum_borrow_plus_effects)

            if ctoken == ctoken_modify:
                sum_borrow_plus_effects = mul_scalar_truncate_add_int(
                    tokens_to_denom, redeem_tokens, sum_borrow_plus_effects
                )
                sum_borrow_plus_effects = mul_scalar_truncate_add_int(
                    token_price, borrow_amount, sum_borrow_plus_effects
                )
        return sum_collateral, sum_borrow_plus_effects, sum_collateral_undiscounted

    def get_hypothetical_account_liquidity(
        self,
        wallet: Wallet,
        ctoken_modify: str,
        redeem_tokens: int,
        borrow_amount: int,
        underlying_price: dict[Tuple[str, str], float],
    ) -> Tuple[int, int]:
        sum_collateral, sum_borrow_plus_effects, _ = self.get_hypothetical_account_net_position_internal(
            wallet, ctoken_modify, redeem_tokens, borrow_amount, underlying_price
        )
        if sum_collateral > sum_borrow_plus_effects:
            return sum_collateral - sum_borrow_plus_effects, 0
        else:
            return 0, sum_borrow_plus_effects - sum_collateral

    def redeem_allowed(self, ctoken: str, redeemer: Wallet, redeem_tokens: int) -> Tuple[bool, str]:
        if ctoken not in redeemer.holdings.keys():
            return True, ""

        _, shortfall = self.get_hypothetical_account_liquidity(redeemer, ctoken, redeem_tokens, 0, self._stored_spot)
        if shortfall > 0:
            return (
                False,
                f"Insufficient collateral - Cannot redeem {redeem_tokens / 10**8} {self.markets[ctoken].symbol}. "
                f"That would generate a shortfall of {-shortfall / EXPSCALE} {LENDING_PROTOCOL_MANDATORY_TOKEN}.",
            )
        return True, ""

    def transfer_allowed(self, ctoken: str, src: Wallet, transfer_tokens: int) -> Tuple[bool, str]:
        # this function is necessary when we integrate the COMP distribution logic
        return self.redeem_allowed(ctoken, src, transfer_tokens)

    def borrow_allowed(self, ctoken: str, borrower: Wallet, borrow_amount: int) -> Tuple[bool, str]:
        _, shortfall = self.get_hypothetical_account_liquidity(borrower, ctoken, 0, borrow_amount, self._stored_spot)
        if shortfall > 0:
            return (
                False,
                f"Insufficient collateral - Cannot borrow "
                f"{borrow_amount / 10**self.markets[ctoken].underlying_decimals} {self.markets[ctoken].symbol} "
                f"underlying. That would generate a shortfall of "
                f"{-shortfall / EXPSCALE} {LENDING_PROTOCOL_MANDATORY_TOKEN}.",
            )
        return True, ""

    def borrow_cap_check(self, ctoken: str, borrow_amount: int) -> Tuple[bool, str]:
        if self.borrow_caps[ctoken] != 0:
            total_borrows = self.markets[ctoken].total_borrows
            next_total_borrows = total_borrows + borrow_amount
            if next_total_borrows > self.borrow_caps[ctoken]:
                return (
                    False,
                    f"Impossible to borrow {borrow_amount / 10**self.markets[ctoken].underlying_decimals}"
                    f"{self.markets[ctoken].underlying}. The borrow cap "
                    f"({self.borrow_caps[ctoken] / 10**self.markets[ctoken].underlying_decimals}"
                    f"{self.markets[ctoken].underlying}) would "
                    f"be breached.",
                )
        return True, ""

    def liquidate_borrow_allowed(self, ctoken_borrowed: str, borrower: Wallet, repay_amount: int) -> Tuple[bool, str]:
        borrow_balance = self.markets[ctoken_borrowed].borrow_balance_stored_internal(borrower)
        available_liquidity, shortfall = self.get_hypothetical_account_liquidity(borrower, "", 0, 0, self._stored_spot)
        if shortfall == 0:
            return (
                False,
                f"Liquidation failed because of insufficient shortfall. The account has a positive balance of "
                f"{available_liquidity / EXPSCALE} {LENDING_PROTOCOL_MANDATORY_TOKEN}",
            )
        max_close = mul_scalar_truncate(Exp(self.close_factor_mantissa), borrow_balance)
        if repay_amount > max_close:
            return (
                False,
                f"It is not possible to liquidate more than what is specified by the close factor. Trying to repay "
                f"{repay_amount / 10** self.markets[ctoken_borrowed].underlying_decimals}"
                f"{self.markets[ctoken_borrowed].underlying}, while the maximum amount is "
                f"{max_close / 10** self.markets[ctoken_borrowed].underlying_decimals}",
            )
        return True, ""

    def liquidate_calculate_seize_token(
        self,
        ctoken_borrowed: str,
        ctoken_collateral: str,
        actual_repay_amount: int,
        underlying_price: dict[Tuple[str, str], float],
    ) -> int:
        price_borrowed_mantissa = int(
            Decimal(underlying_price[(self.markets[ctoken_borrowed].underlying, LENDING_PROTOCOL_MANDATORY_TOKEN)])
            * 10 ** (36 - self.markets[ctoken_borrowed].underlying_decimals)
        )
        price_collateral_mantissa = int(
            Decimal(underlying_price[(self.markets[ctoken_collateral].underlying, LENDING_PROTOCOL_MANDATORY_TOKEN)])
            * 10 ** (36 - self.markets[ctoken_collateral].underlying_decimals)
        )
        exchange_rate_mantissa = self.markets[ctoken_collateral].exchange_rate_stored_internal()

        numerator = mul_exp(Exp(self.liquidation_incentive_mantissa), Exp(price_borrowed_mantissa))
        denominator = mul_exp(Exp(price_collateral_mantissa), Exp(exchange_rate_mantissa))
        ratio = div_exp(numerator, denominator)

        seize_tokens = mul_scalar_truncate(ratio, actual_repay_amount)
        return seize_tokens

    def process_single_transaction(self, transaction: ABCTransaction) -> None:
        if not isinstance(transaction, TransactionCompoundv2):
            message = "Can only process instances of TransactionCompoundv2"
            message = (
                f"Action {transaction.action_name} - " + message if transaction.action_name is not None else message
            )
            raise ValueError(message)

        self.markets[transaction.ctoken]._handle_transaction(transaction)

    def inject_spot_values(self, timestamp: int, spot_values: dict[tuple[str, str], float]) -> None:
        self._stored_spot = spot_values
        self.spot_update_timestamp = timestamp

    def spots_to_inject(self, transaction: ABCTransaction) -> list[tuple[str, str]]:
        if (
            isinstance(transaction, LiquidateTransactionCompv2)
            or (
                isinstance(transaction, (BorrowTransactionCompv2, RedeemTransactionCompv2))
                and transaction.sender_wallet is not None
            )
            and transaction.block_timestamp > self.spot_update_timestamp
        ):
            return self.required_spots
        else:
            return []

    def process_transactions(self, transactions: list[ABCTransaction]) -> None:
        for transaction in transactions:
            self.process_single_transaction(transaction)

    def get_state(self, block_timestamp: int) -> StateComptroller:
        state = StateComptroller(
            id=self.id,
            block_number=0,
            block_timestamp=block_timestamp,
            name=self.name,
            close_factor_mantissa=self.close_factor_mantissa,
            liquidation_incentive_mantissa=self.liquidation_incentive_mantissa,
            max_assets=self.max_assets,
            market_states={
                market_symbol: market.get_state(block_timestamp) for market_symbol, market in self.markets.items()
            },
        )
        state = copy.deepcopy(state)
        return state

    def restore_from_state(self, state: ABCProtocolState) -> None:
        if isinstance(state, StateComptroller):
            super().__init__(state)
            self.close_factor_mantissa = state.close_factor_mantissa
            self.liquidation_incentive_mantissa = state.liquidation_incentive_mantissa
            self.max_assets = state.max_assets
            self.borrow_caps = {}
            self.collateral_factor_mantissa = {}
            self.markets = {}

            for market in state.market_states:
                self.initialise_market(state.market_states[market])
        else:
            raise ValueError(f"States of the class {state.__class__} cannot restore a Comptroller...")

    @property
    def stored_spot(self) -> dict[Tuple[str, str], float]:
        return self._stored_spot


class CompoundMarket(ABCProtocol):
    def __init__(self, state_market: StateCompoundMarket, comptroller: Comptroller):
        super().__init__(state_market)
        self.interest_rate_model = CTokenInterestRateModel(state_market.interest_rate_model)
        self.name = state_market.name
        self.symbol = state_market.symbol
        self.address = state_market.address
        self.underlying = state_market.underlying
        self.underlying_address = state_market.underlying_address
        self.decimals = state_market.decimals
        self.underlying_decimals = state_market.underlying_decimals
        self.initial_exchange_rate_mantissa = state_market.initial_exchange_rate_mantissa
        self.accrual_block_number = state_market.accrual_block_number
        self.borrow_index = state_market.borrow_index
        self.total_borrows = state_market.total_borrows
        self.total_supply = state_market.total_supply
        self.total_reserves = state_market.total_reserves
        self.total_cash = state_market.total_cash
        self.protocol_seize_share_mantissa = state_market.protocol_seize_share_mantissa
        self.borrow_rate_max_mantissa = state_market.borrow_rate_max_mantissa
        self.reserve_factor_mantissa = state_market.reserve_factor_mantissa
        self.reserve_factor_max_mantissa = state_market.reserve_factor_max_mantissa
        self.account_borrows = copy.deepcopy(state_market.account_borrows)
        self.collateral_factor_mantissa = state_market.collateral_factor
        self.borrow_cap = state_market.borrow_cap
        self.events_ready_to_collect: list = []
        self.comptroller = comptroller

    def get_state(self, block_timestamp: int) -> StateCompoundMarket:
        state = StateCompoundMarket(
            id=self.id,
            block_number=self.accrual_block_number,
            block_timestamp=block_timestamp,
            interest_rate_model=self.interest_rate_model.get_state(),
            name=self.name,
            symbol=self.symbol,
            address=self.address,
            underlying=self.underlying,
            underlying_address=self.underlying_address,
            decimals=self.decimals,
            underlying_decimals=self.underlying_decimals,
            initial_exchange_rate_mantissa=self.initial_exchange_rate_mantissa,
            accrual_block_number=self.accrual_block_number,
            reserve_factor_max_mantissa=self.reserve_factor_max_mantissa,
            borrow_index=self.borrow_index,
            total_borrows=self.total_borrows,
            total_supply=self.total_supply,
            total_reserves=self.total_reserves,
            collateral_factor=self.collateral_factor_mantissa,
            borrow_cap=self.borrow_cap,
            account_borrows=self.account_borrows,
            total_cash=self.total_cash,
            protocol_seize_share_mantissa=self.protocol_seize_share_mantissa,
            borrow_rate_max_mantissa=self.borrow_rate_max_mantissa,
            reserve_factor_mantissa=self.reserve_factor_mantissa,
        )
        state = copy.deepcopy(state)
        return state

    def restore_from_state(self, state: ABCProtocolState) -> None:
        if isinstance(state, StateCompoundMarket):
            super().__init__(state)
            self.interest_rate_model = CTokenInterestRateModel(state.interest_rate_model)
            self.name = state.name
            self.symbol = state.symbol
            self.address = state.address
            self.underlying = state.underlying
            self.underlying_address = state.underlying_address
            self.decimals = state.decimals
            self.underlying_decimals = state.underlying_decimals
            self.initial_exchange_rate_mantissa = state.initial_exchange_rate_mantissa
            self.accrual_block_number = state.accrual_block_number
            self.borrow_index = state.borrow_index
            self.total_borrows = state.total_borrows
            self.total_supply = state.total_supply
            self.total_reserves = state.total_reserves
            self.total_cash = state.total_cash
            self.protocol_seize_share_mantissa = state.protocol_seize_share_mantissa
            self.borrow_rate_max_mantissa = state.borrow_rate_max_mantissa
            self.reserve_factor_mantissa = state.reserve_factor_mantissa
            self.reserve_factor_max_mantissa = state.reserve_factor_max_mantissa
            self.account_borrows = state.account_borrows
            self.collateral_factor_mantissa = state.collateral_factor
            self.borrow_cap = state.borrow_cap
        else:
            raise ValueError(f"States of the class {state.__class__} cannot restore a CompoundMarket...")

    def accrue_interest(self, current_block_number: int) -> bool:
        if current_block_number == self.accrual_block_number:
            return True

        borrow_rate_mantissa = self.interest_rate_model.get_borrow_rate(
            self.total_cash, self.total_borrows, self.total_reserves
        )
        if borrow_rate_mantissa > self.borrow_rate_max_mantissa:
            self.logger.warning(
                f"In the Compound V2 market {self.symbol} the borrow rate {borrow_rate_mantissa} exceeds "
                f"the max borrow rate {self.borrow_rate_max_mantissa}"
            )
            return False
        block_delta = current_block_number - self.accrual_block_number
        simple_interest_factor = mul_exp_int(Exp(borrow_rate_mantissa), block_delta)
        interest_accumulated = mul_scalar_truncate(simple_interest_factor, self.total_borrows)
        total_borrow_new = interest_accumulated + self.total_borrows
        total_reserves_new = mul_scalar_truncate_add_int(
            Exp(self.reserve_factor_mantissa), interest_accumulated, self.total_reserves
        )
        borrow_index_new = mul_scalar_truncate_add_int(simple_interest_factor, self.borrow_index, self.borrow_index)

        self.accrual_block_number = current_block_number
        self.borrow_index = borrow_index_new
        self.total_borrows = total_borrow_new
        self.total_reserves = total_reserves_new
        return True

    def exchange_rate_stored_internal(self) -> int:
        if self.total_supply == 0:
            return self.initial_exchange_rate_mantissa
        else:
            cash_plus_borrows_minus_reserves = self.total_cash + self.total_borrows - self.total_reserves
            return cash_plus_borrows_minus_reserves * EXPSCALE // self.total_supply

    def borrow_balance_stored_internal(self, wallet: Wallet) -> int:
        borrow_snapshot = self.account_borrows.setdefault(wallet.agent_name, BorrowSnapshot(0, 0))
        if borrow_snapshot.principal == 0:
            return 0

        principal_times_index = borrow_snapshot.principal * self.borrow_index
        return principal_times_index // borrow_snapshot.interest_index

    def get_borrow_snapshot(self, wallet: Wallet) -> Tuple[int, int]:
        borrow_snapshot = self.account_borrows.setdefault(wallet.agent_name, BorrowSnapshot(0, 0))
        return borrow_snapshot.principal, borrow_snapshot.interest_index

    def get_account_snapshot(self, wallet: Wallet) -> Tuple[int, int, int]:
        return (
            int(wallet.get_balance_of(self.symbol)),
            self.borrow_balance_stored_internal(wallet),
            self.exchange_rate_stored_internal(),
        )

    def _mint_internal(
        self,
        msg_sender: Wallet | None,
        block_timestamp: int,
        block_number: int,
        mint_amount: int,
        action_name: Optional[str],
    ) -> None:
        succeed = self.accrue_interest(block_number)
        if succeed:
            self._mint_fresh(
                msg_sender=msg_sender,
                block_timestamp=block_timestamp,
                block_number=block_number,
                mint_amount=mint_amount,
                action_name=action_name,
            )

    @rollback_on_failure
    def _mint_fresh(
        self,
        msg_sender: Wallet | None,
        block_timestamp: int,
        block_number: int,
        mint_amount: int,
        action_name: Optional[str],
    ) -> None:
        if self.accrual_block_number != block_number:
            message = (
                f"Cannot accept the mint transaction in {self.symbol} as the transaction block "
                f"number {block_number} does not match the accrual block number {self.accrual_block_number}"
            )
            message = f"Action {action_name} - " + message if action_name is not None else message
            self.logger.warning(message)
            return
        exchange_rate = Exp(self.exchange_rate_stored_internal())

        if msg_sender is not None:
            msg_sender.transfer_from(self.underlying, mint_amount, action_name)
        self.total_cash += mint_amount
        mint_tokens = div_int_exp(mint_amount, exchange_rate)

        self.total_supply += mint_tokens
        if msg_sender is not None:
            msg_sender.transfer_to(self.symbol, mint_tokens, action_name)
        mint_event = Mint(amount=mint_amount)
        msg = f"Transaction: Mint - Status: Succeeded - Comment: {mint_event}"
        if isinstance(msg_sender, Wallet) and not isinstance(msg_sender, ArbitrageurWallet):
            self.logger.info(
                f"Key: {self.logger_key_tx} - Timestamp: {block_timestamp} - Block number: {block_number} - "
                f"Agent: {msg_sender.agent_name} - " + msg
            )
        else:
            self.logger.debug(msg)
        self.events_ready_to_collect.append(mint_event)

    def _redeem_internal(
        self,
        msg_sender: Wallet | None,
        block_timestamp: int,
        block_number: int,
        redeem_amount_in: int,
        redeem_tokens_in: int,
        action_name: Optional[str],
    ) -> None:
        succeed = self.accrue_interest(block_number)
        if succeed:
            self._redeem_fresh(
                msg_sender=msg_sender,
                block_timestamp=block_timestamp,
                block_number=block_number,
                redeem_amount_in=redeem_amount_in,
                redeem_tokens_in=redeem_tokens_in,
                action_name=action_name,
            )

    @rollback_on_failure
    def _redeem_fresh(
        self,
        msg_sender: Wallet | None,
        block_timestamp: int,
        block_number: int,
        redeem_amount_in: int,
        redeem_tokens_in: int,
        action_name: Optional[str],
    ) -> None:
        warning_prefix = f"User {msg_sender.agent_name}: " if msg_sender is not None else ""
        warning_prefix = f"Action {action_name} - " + warning_prefix if action_name is not None else warning_prefix
        if redeem_tokens_in > 0 and redeem_amount_in > 0:
            self.logger.warning(
                warning_prefix
                + "Impossible to execute the redeem transaction: one of redeem_tokens_in or redeem_amount_in "
                "needs to be 0"
            )
            return

        exchange_rate = Exp(self.exchange_rate_stored_internal())
        if redeem_tokens_in > 0:
            redeem_tokens = redeem_tokens_in
            redeem_amount = mul_scalar_truncate(exchange_rate, redeem_tokens_in)
        else:
            redeem_tokens = div_int_exp(redeem_amount_in, exchange_rate)
            redeem_amount = redeem_amount_in

        if msg_sender is not None:
            is_allowed, message = self.comptroller.redeem_allowed(self.symbol, msg_sender, redeem_tokens)
            if not is_allowed:
                self.logger.warning(warning_prefix + message)
                return
        if self.accrual_block_number != block_number:
            self.logger.warning(
                warning_prefix
                + f"Cannot accept the redeem transaction in {self.symbol} as the transaction block number "
                f"{block_number} does not match the accrual block number {self.accrual_block_number}"
            )
            return
        if self.total_cash < redeem_amount:
            self.logger.warning(
                warning_prefix
                + f"The redeem amount {redeem_amount} exceeds the total cash {self.total_cash} available in "
                f"{self.symbol}"
            )
            return

        self.total_supply -= redeem_tokens
        self.total_cash -= redeem_amount
        if msg_sender is not None:
            msg_sender.transfer_from(self.symbol, redeem_tokens, action_name)
            msg_sender.transfer_to(self.underlying, redeem_amount, action_name)
        redeem_event = Redeem(amount=redeem_amount)
        msg = f"Transaction: Redeem - Status: Succeeded - Comment: {redeem_event}"
        if isinstance(msg_sender, Wallet) and not isinstance(msg_sender, ArbitrageurWallet):
            self.logger.info(
                f"Key: {self.logger_key_tx} - Timestamp: {block_timestamp} - Block number: {block_number} - "
                f"Agent: {msg_sender.agent_name} - " + msg
            )
        else:
            self.logger.debug(msg)
        self.events_ready_to_collect.append(redeem_event)

    def _borrow_internal(
        self,
        msg_sender: Wallet | None,
        block_timestamp: int,
        block_number: int,
        borrow_amount: int,
        action_name: Optional[str],
    ) -> None:
        succeed = self.accrue_interest(block_number)
        if succeed:
            self._borrow_fresh(msg_sender, block_timestamp, block_number, borrow_amount, action_name)

    def _borrow_fresh(
        self,
        msg_sender: Wallet | None,
        block_timestamp: int,
        block_number: int,
        borrow_amount: int,
        action_name: Optional[str],
    ) -> None:
        warning_prefix = f"User {msg_sender.agent_name}: " if msg_sender is not None else ""
        warning_prefix = f"Action {action_name} - " + warning_prefix if action_name is not None else warning_prefix
        if msg_sender is not None:
            is_allowed, message = self.comptroller.borrow_allowed(self.symbol, msg_sender, borrow_amount)
            if not is_allowed:
                self.logger.warning(warning_prefix + message)
                return
        is_allowed, message = self.comptroller.borrow_cap_check(self.symbol, borrow_amount)
        if not is_allowed:
            self.logger.warning(warning_prefix + message)
            return
        if self.accrual_block_number != block_number:
            self.logger.warning(
                warning_prefix
                + f"Cannot accept the borrow transaction in {self.symbol} as the transaction block number "
                f"{block_number} does not match the accrual block number {self.accrual_block_number}"
            )
            return
        if self.total_cash < borrow_amount:
            self.logger.warning(
                warning_prefix
                + f"The borrow amount {borrow_amount} exceeds the total cash {self.total_cash} available in "
                f"{self.symbol}"
            )
            return

        account_borrow_prev = self.borrow_balance_stored_internal(msg_sender) if msg_sender is not None else 0
        account_borrow_new = account_borrow_prev + borrow_amount
        total_borrow_new = self.total_borrows + borrow_amount

        if account_borrow_new >= OVERFLOW or total_borrow_new >= OVERFLOW:
            self.logger.warning(
                warning_prefix
                + f"Cannot execute the borrow transaction in {self.symbol} market. The new borrow amount "
                f"{account_borrow_new} or market total borrow amount {total_borrow_new} generate an overflow error"
            )
            return

        if msg_sender is not None:
            self.account_borrows[msg_sender.agent_name].principal = account_borrow_new
            self.account_borrows[msg_sender.agent_name].interest_index = self.borrow_index
            msg_sender.transfer_to(self.underlying, borrow_amount, action_name)

        self.total_borrows = total_borrow_new
        self.total_cash -= borrow_amount

        borrow_event = Borrow(amount=borrow_amount)
        msg = f"Transaction: Borrow - Status: Succeeded - Comment: {borrow_event}"
        if isinstance(msg_sender, Wallet) and not isinstance(msg_sender, ArbitrageurWallet):
            self.logger.info(
                f"Key: {self.logger_key_tx} - Timestamp: {block_timestamp} - Block number: {block_number} - "
                f"Agent: {msg_sender.agent_name} - " + msg
            )
        else:
            self.logger.debug(msg)
        self.events_ready_to_collect.append(borrow_event)

    def _repay_borrow_internal(
        self,
        msg_sender: Wallet | None,
        block_timestamp: int,
        block_number: int,
        borrow_wallet: Wallet | None,
        repay_amount: int,
        action_name: Optional[str],
    ) -> None:
        succeed = self.accrue_interest(block_number)
        if succeed:
            self._repay_borrow_fresh(
                msg_sender, block_timestamp, block_number, borrow_wallet, repay_amount, action_name
            )

    def _repay_borrow_fresh(
        self,
        msg_sender: Wallet | None,
        block_timestamp: int,
        block_number: int,
        borrow_wallet: Wallet | None,
        repay_amount: int,
        action_name: Optional[str],
    ) -> int:
        warning_prefix = f"User {msg_sender.agent_name}: " if msg_sender is not None else ""
        warning_prefix = f"Action {action_name} - " + warning_prefix if action_name is not None else warning_prefix
        if self.accrual_block_number != block_number:
            self.logger.warning(
                warning_prefix
                + f"Cannot accept the repay transaction in {self.symbol} as the transaction block number "
                f"{block_number} does not match the accrual block number {self.accrual_block_number}"
            )
            return 0

        if (repay_amount == -1 or repay_amount == OVERFLOW) and borrow_wallet is None:
            raise NotImplementedError(
                "it is not possible to know the exact amount to repay if the borrow wallet is not specified"
            )
        account_borrow_prev = (
            self.borrow_balance_stored_internal(borrow_wallet) if borrow_wallet is not None else OVERFLOW
        )
        repay_amount_final = account_borrow_prev if (repay_amount == -1 or repay_amount == OVERFLOW) else repay_amount

        if msg_sender is not None:
            if not msg_sender.has_enough_balance(repay_amount_final, self.underlying):
                self.logger.warning(
                    warning_prefix + f"Impossible to execute the repay transaction. The sender wallet has a balance of"
                    f"{msg_sender.holdings[self.underlying] / 10**self.underlying_decimals}"
                    f"{self.underlying} while trying to repay "
                    f"{repay_amount_final / 10**self.underlying_decimals}"
                )
                return 0

        account_borrow_new = account_borrow_prev - repay_amount_final
        total_borrow_new = self.total_borrows - repay_amount_final

        if account_borrow_new < 0:
            self.logger.warning(
                warning_prefix + f"Impossible to execute the repay borrow transation in the {self.symbol} market."
                f"The repay amount {repay_amount_final / 10**self.underlying_decimals} is bigger"
                f"than the current borrow balance ({account_borrow_prev / 10**self.underlying_decimals})."
            )
            return 0
        if total_borrow_new < 0:
            self.logger.warning(
                warning_prefix + f"Impossible to execute the repay borrow transation in the {self.symbol} market."
                f"The repay amount {repay_amount_final / 10**self.underlying_decimals} would generate"
                f"a negative total borrow balance in the market."
            )
            return 0

        if msg_sender is not None:
            msg_sender.transfer_from(self.underlying, repay_amount_final, action_name)

        if borrow_wallet is not None:
            self.account_borrows[borrow_wallet.agent_name].principal = account_borrow_new
            self.account_borrows[borrow_wallet.agent_name].interest_index = self.borrow_index
        self.total_borrows = total_borrow_new
        self.total_cash += repay_amount_final
        repay_event = Repay(amount=repay_amount_final)
        msg = f"Transaction: Repay - Status: Succeeded - Comment: {repay_event}"
        if isinstance(msg_sender, Wallet) and not isinstance(msg_sender, ArbitrageurWallet):
            self.logger.info(
                f"Key: {self.logger_key_tx} - Timestamp: {block_timestamp} - Block number: {block_number} - "
                f"Agent: {msg_sender.agent_name} - " + msg
            )
        else:
            self.logger.debug(msg)
        self.events_ready_to_collect.append(repay_event)
        return repay_amount_final

    def _liquidate_borrow_internal(
        self,
        msg_sender: Wallet | None,
        block_timestamp: int,
        block_number: int,
        borrower: Wallet | None,
        repay_amount: int,
        ctoken_collateral: str,
        action_name: Optional[str],
    ) -> None:
        succeed_borrow = self.accrue_interest(block_number)
        succeed_collateral = self.comptroller.markets[ctoken_collateral].accrue_interest(block_number)
        if (
            succeed_collateral
            and succeed_borrow
            and self._liquidate_borrow_internal_checks(
                msg_sender, block_number, borrower, repay_amount, ctoken_collateral, action_name
            )
        ):
            self._liquidate_borrow_fresh(
                msg_sender=msg_sender,
                borrower=borrower,
                repay_amount=repay_amount,
                ctoken_collateral=ctoken_collateral,
                block_timestamp=block_timestamp,
                block_number=block_number,
                action_name=action_name,
            )

    def _liquidate_borrow_internal_checks(
        self,
        msg_sender: Wallet | None,
        block_number: int,
        borrower: Wallet | None,
        repay_amount: int,
        ctoken_collateral: str,
        action_name: Optional[str],
    ) -> bool:
        warning_prefix = f"User {msg_sender.agent_name}: " if msg_sender is not None else ""
        warning_prefix = f"Action {action_name}: " + warning_prefix if action_name is not None else warning_prefix
        if borrower is not None:
            is_allowed, message = self.comptroller.liquidate_borrow_allowed(self.symbol, borrower, repay_amount)
            if not is_allowed:
                self.logger.warning(warning_prefix + message)
                return False
        if self.accrual_block_number != block_number:
            self.logger.warning(
                warning_prefix
                + f"Cannot accept the liquidate transaction in {self.symbol} as the transaction block number "
                f"{block_number} does not match the accrual block number {self.accrual_block_number}"
            )
            return False

        if self.comptroller.markets[ctoken_collateral].accrual_block_number != block_number:
            self.logger.warning(
                warning_prefix + f"Cannot accept the liquidate transaction in "
                f"{self.comptroller.markets[ctoken_collateral].symbol} as the transaction block number "
                f"{block_number} does not match the accrual block number "
                f"{self.comptroller.markets[ctoken_collateral].accrual_block_number}"
            )
            return False

        if borrower is not None and msg_sender is not None:
            if borrower.agent_name == msg_sender.agent_name:
                self.logger.warning(
                    warning_prefix + f"Borrower and Liquidator cannot be the same wallet ({msg_sender.agent_name})"
                )
                return False
        if repay_amount == 0:
            self.logger.warning(warning_prefix + "The liquidation amount needs to be greater than 0")
            return False
        if repay_amount == -1 or repay_amount == OVERFLOW:
            self.logger.warning(warning_prefix + "The liquidation amount needs to be a finite amount (and not -1).")
            return False
        return True

    @rollback_on_failure
    def _liquidate_borrow_fresh(
        self,
        msg_sender: Wallet | None,
        block_timestamp: int,
        block_number: int,
        borrower: Wallet | None,
        repay_amount: int,
        ctoken_collateral: str,
        action_name: Optional[str],
    ) -> None:
        warning_prefix = f"User {msg_sender.agent_name} -" if msg_sender is not None else ""
        warning_prefix = f"Action {action_name} -" if action_name is not None else warning_prefix
        actual_repay_amount = self._repay_borrow_fresh(
            msg_sender, block_timestamp, block_number, borrower, repay_amount, action_name
        )

        seize_tokens = self.comptroller.liquidate_calculate_seize_token(
            self.symbol, ctoken_collateral, actual_repay_amount, self.comptroller.stored_spot
        )

        if borrower is not None:
            if not borrower.has_enough_balance(seize_tokens, ctoken_collateral):
                self.logger.warning(
                    warning_prefix + f"It is impossible to execute the liquidation transaction: the borrower does not "
                    f"have enough cTokens. Trying to seize {seize_tokens / 10 ** self.decimals} while "
                    f"holding {borrower.get_balance_of_float(ctoken_collateral)}"
                )
                return

        self.comptroller.markets[ctoken_collateral]._seize_internal(msg_sender, borrower, seize_tokens, action_name)

    def _seize_internal(
        self, msg_sender: Wallet | None, borrower: Wallet | None, seize_tokens: int, action_name: Optional[str]
    ) -> None:
        protocol_seize_tokens = mul_int_exp(seize_tokens, Exp(self.protocol_seize_share_mantissa))
        liquidator_seize_tokens = seize_tokens - protocol_seize_tokens
        exchange_rate = Exp(self.exchange_rate_stored_internal())

        protocol_seize_amount = mul_scalar_truncate(exchange_rate, protocol_seize_tokens)

        total_reserves_new = self.total_reserves + protocol_seize_amount

        self.total_reserves = total_reserves_new
        self.total_supply -= protocol_seize_tokens
        if borrower is not None:
            borrower.transfer_from(self.symbol, seize_tokens, action_name)
        if msg_sender is not None:
            msg_sender.transfer_to(self.symbol, liquidator_seize_tokens, action_name)
        self.events_ready_to_collect.append(Liquidation(amount=mul_scalar_truncate(exchange_rate, seize_tokens)))

    def get_wallet_virtual_position(self, wallet: Wallet) -> Tuple[int, int, int]:
        holdings, borrow_balance, exchange_rate = self.get_account_snapshot(wallet)
        collateral = holdings * exchange_rate // EXPSCALE
        return borrow_balance, collateral, exchange_rate

    @rollback_on_failure
    def _transfer_tokens(
        self, msg_sender: Wallet | None, dst_wallet: Wallet | None, amount: int, action_name: Optional[str]
    ) -> None:
        warning_prefix = f"User {msg_sender.agent_name}: " if msg_sender is not None else ""
        warning_prefix = f"Action {action_name} - " + warning_prefix if action_name is not None else warning_prefix
        # in this function we assume that src == spender ( == event.sender_wallet)
        if msg_sender is not None:
            is_allowed, message = self.comptroller.transfer_allowed(self.symbol, msg_sender, amount)
            if not is_allowed:
                self.logger.warning(warning_prefix + message)
                return

        if msg_sender is not None and dst_wallet is not None and msg_sender.agent_name == dst_wallet.agent_name:
            self.logger.warning(
                warning_prefix + f"It is not possible to transfer cTokens from a wallet, to the same wallet"
                f" ({msg_sender.agent_name})"
            )
            return

        if msg_sender is not None:
            msg_sender.transfer_from(self.symbol, amount, action_name)
        if dst_wallet is not None:
            dst_wallet.transfer_to(self.symbol, amount, action_name)

    def process_single_transaction(self, transaction: ABCTransaction) -> None:
        self._handle_transaction(transaction)

    def process_transactions(self, transactions: list[ABCTransaction]) -> None:
        for transaction in transactions:
            self._handle_transaction(transaction)

    def _handle_transaction(self, transaction: ABCTransaction) -> None:
        if isinstance(transaction, MintTransactionCompv2):
            self._mint_internal(
                transaction.sender_wallet,
                transaction.block_timestamp,
                transaction.block_number,
                transaction.mint_amount,
                transaction.action_name,
            )
        elif isinstance(transaction, RedeemTransactionCompv2):
            self._redeem_internal(
                transaction.sender_wallet,
                transaction.block_timestamp,
                transaction.block_number,
                transaction.redeem_amount_in,
                transaction.redeem_tokens_in,
                transaction.action_name,
            )
        elif isinstance(transaction, BorrowTransactionCompv2):
            self._borrow_internal(
                transaction.sender_wallet,
                transaction.block_timestamp,
                transaction.block_number,
                transaction.borrow_amount,
                transaction.action_name,
            )
        elif isinstance(transaction, RepayBorrowTransactionCompv2):
            self._repay_borrow_internal(
                transaction.sender_wallet,
                transaction.block_timestamp,
                transaction.block_number,
                transaction.borrow_wallet,
                transaction.repay_amount,
                transaction.action_name,
            )
        elif isinstance(transaction, LiquidateTransactionCompv2):
            self._liquidate_borrow_internal(
                transaction.sender_wallet,
                transaction.block_timestamp,
                transaction.block_number,
                transaction.borrower,
                transaction.repay_amount,
                transaction.ctoken_collateral,
                transaction.action_name,
            )
        elif isinstance(transaction, TransferTransactionCompv2):
            self._transfer_tokens(
                msg_sender=transaction.sender_wallet,
                dst_wallet=transaction.dst_wallet,
                amount=transaction.amount,
                action_name=transaction.action_name,
            )
        else:
            raise NotImplementedError(f"Events of class {transaction.__class__} are not supported by Compound V2...")


# Events
@dataclass
class Liquidation:
    amount: int
    amount_type: str = "seized"


@dataclass
class Borrow:
    amount: int
    amount_type: str = "borrowed"


@dataclass
class Repay:
    amount: int
    amount_type: str = "repaid"


@dataclass
class Mint:
    amount: int
    amount_type: str = "deposited"


@dataclass
class Redeem:
    amount: int
    amount_type: str = "redeemed"
