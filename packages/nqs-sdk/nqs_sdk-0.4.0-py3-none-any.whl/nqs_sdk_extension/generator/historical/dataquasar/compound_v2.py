import json
import logging
from enum import Enum
from typing import Any, Tuple, no_type_check

from nqs_sdk import BlockNumberOrTimestamp
from nqs_sdk.state.compoundv2 import StateCERC20
from nqs_sdk_extension.constants import OVERFLOW
from nqs_sdk_extension.generator.historical.dataquasar.abc_dtq import DTQSoloGenerator
from nqs_sdk_extension.spot import DataLoader
from nqs_sdk_extension.state import ABCProtocolState
from nqs_sdk_extension.state.compoundv2 import StateCompoundMarket, StateComptroller, StateInterestRateModel
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.compoundv2 import (
    BorrowTransactionCompv2,
    LiquidateTransactionCompv2,
    MintTransactionCompv2,
    RedeemTransactionCompv2,
    RepayBorrowTransactionCompv2,
    TransactionCompoundv2,
)

CTOKEN_ACCRUE_EVENTS = ["cErc20_evt_AccrueInterest", "cErc20Delegator_evt_AccrueInterest", "cEther_evt_AccrueInterest"]

CTOKENS_EVENTS = {
    "cerc20": {
        "accrue_interest": "cErc20_evt_AccrueInterest",
        "mint": "cErc20_evt_Mint",
        "borrow": "cErc20_evt_Borrow",
        "liquidation": " cErc20_evt_LiquidateBorrow",
        "redeem": "cErc20_evt_Redeem",
        "repay": "cErc20_evt_RepayBorrow",
    },
    "cerc20_delegator": {
        "accrue_interest": "cErc20Delegator_evt_AccrueInterest",
        "mint": "cErc20Delegator_evt_Mint",
        "borrow": "cErc20Delegator_evt_Borrow",
        "liquidation": " cErc20Delegator_evt_LiquidateBorrow",
        "redeem": "cErc20Delegator_evt_Redeem",
        "repay": "cErc20Delegator_evt_RepayBorrow",
    },
    "ceth": {
        "accrue_interest": "cEther_evt_AccrueInterest",
        "mint": "cEther_evt_Mint",
        "borrow": "cEther_evt_Borrow",
        "liquidation": " cEther_evt_LiquidateBorrow",
        "redeem": "cEther_evt_Redeem",
        "repay": "cEther_evt_RepayBorrow",
    },
}

EXCLUDED_MARKETS = ["cSAI", "cREP"]


class CompoundV2CallNames(Enum):
    MINT_CERC20 = "MintCerc20"
    REDEEM_CERC20 = "RedeemCerc20"
    REDEEM_UNDERLYING_CERC20 = "RedeemUnderlyingCerc20"
    BORROW_CERC20 = "BorrowCerc20"
    REPAY_BORROW_CERC20 = "RepayBorrowCerc20"
    REPAY_BORROW_BEHALF_CERC20 = "RepayBorrowBehalfCerc20"
    LIQUIDATE_BORROW_CERC20 = "LiquidateBorrowCerc20"
    MINT_CETH = "MintCeth"
    LIQUIDATE_BORROW_CETH = "LiquidateBorrowCeth"
    REPAY_BORROW_BEHALF_CETH = "RepayBorrowBehalfCeth"


class DTQCompoundv2Generator(DTQSoloGenerator):
    def __init__(self, id: int, name: str, protocol_info: dict):
        super().__init__(id, name)
        self.market_addresses: dict[str, dict] = self.get_markets_list()
        if protocol_info.get("markets", None) is not None:
            self.market_addresses = {
                key: self.market_addresses[key] for key in protocol_info["markets"] if key in self.market_addresses
            }
        self.total_borrows: dict[str, dict] = {}
        self.underlying_prices: dict[str, dict] = {}

        self.c_address_symbol_mapping: dict[str, dict] = {}
        for key, inner_dict in self.market_addresses.items():
            address = inner_dict.get("address")
            protocol_id = inner_dict.get("id")
            self.total_borrows[key] = {}
            self.underlying_prices[key] = {}
            self.c_address_symbol_mapping[str(address)] = {"symbol": key, "id": protocol_id}
        # logger
        self.logger = logging.getLogger("DTQCompoundV2GeneratorLogger")

    def generate_ctoken_metadata(self) -> list[StateCERC20]:
        ctoken_state: list[StateCERC20] = []

        for ctoken in self.market_addresses:
            ctoken_state += [
                StateCERC20(
                    name=ctoken,
                    symbol=ctoken,
                    decimals=8,
                    # address=self.market_addresses[ctoken]["address"],
                    underlying_symbol=self.market_addresses[ctoken]["underlying"],
                    underlying_address=self.market_addresses[ctoken]["underlying_address"],
                    comptroller_id="comptroller",
                    total_supply=None,
                )
            ]
        return ctoken_state

    def get_markets_list(self) -> dict[str, dict] | Any:
        markets: dict[str, dict] = {}
        offset = 0
        market_list = DataLoader.quantlib_source().compound_v2_market_list()

        market_list = {
            ctoken: {
                "address": market_list["market_address"][i],
                "underlying_address": market_list["underlying_address"][i],
                "id": i + offset,
                "underlying": market_list["underlying_symbol"][i],
            }
            for i, ctoken in enumerate(market_list["symbol"])
        }
        # remove the legacy WBTC market (this could not be done in pyquantlib, so it is done here)
        if (
            "cWBTC" in market_list.keys()
            and market_list["cWBTC"]["address"] == "0xc11b1268c1a384e55c48c2391d8d480264a3a7f4"
        ):
            del market_list["cWBTC"]
        markets.update(market_list)

        return markets

    def generate_state_at_block(self, block_number: int, id: int = -1) -> StateComptroller:
        market_states = {}
        liquidation_incentive_mantissa, close_factor_mantissa = self._get_globals(block_number)
        for ctoken in self.market_addresses.keys():
            if ctoken in EXCLUDED_MARKETS:
                continue
            market_states[ctoken] = self._make_compound_market_state(ctoken, block_number)

        comptroller_state = StateComptroller(
            id=id,
            name="comptroller",
            block_number=block_number,
            block_timestamp=0,
            close_factor_mantissa=close_factor_mantissa,
            liquidation_incentive_mantissa=liquidation_incentive_mantissa,
            max_assets=len(market_states),  # todo - DTQ should fetch this
            market_states=market_states,
        )

        return comptroller_state

    def generate_transactions_at_block(self, block_number: int) -> list[ABCTransaction]:
        return self.generate_transactions_between_blocks(block_number, block_number)

    def generate_transactions_between_blocks(
        self, block_number_from: int, block_number_to: int
    ) -> list[ABCTransaction]:
        addresses_to_backtest = [ctoken["address"] for ctoken in self.market_addresses.values()]
        data_calls = self._load_historical_calls(block_number_from, block_number_to, addresses_to_backtest)
        transactions: list[TransactionCompoundv2] = self._make_transactions_from_calls(
            data_calls, addresses_to_backtest
        )
        sorted_transactions: list[ABCTransaction] = self.sort_transactions(transactions)
        return sorted_transactions

    @no_type_check
    def make_transaction(
        self,
        event_type: str,
        timestamp: int,
        block_number: int,
        amount: int,
        ctoken: str,
        ctoken_collateral: str | None,
        total_borrow: int | None,
        block_index: int | None = None,
    ) -> TransactionCompoundv2:
        match event_type:
            case "mint":
                transaction = MintTransactionCompv2(
                    block_number=block_number,
                    block_index=block_index,
                    block_timestamp=timestamp,
                    protocol_id=self.name,
                    sender_wallet=None,
                    mint_amount=amount,
                    ctoken=ctoken,
                )
            case "redeem":
                transaction = RedeemTransactionCompv2(
                    block_number=block_number,
                    block_index=block_index,
                    block_timestamp=timestamp,
                    protocol_id=self.name,
                    sender_wallet=None,
                    redeem_amount_in=amount,
                    redeem_tokens_in=0,
                    ctoken=ctoken,
                )
            case "borrow":
                self.total_borrows[ctoken][block_number] = total_borrow
                transaction = BorrowTransactionCompv2(
                    block_number=block_number,
                    block_index=block_index,
                    block_timestamp=timestamp,
                    protocol_id=self.name,
                    sender_wallet=None,
                    borrow_amount=amount,
                    ctoken=ctoken,
                )
            case "repay":
                self.total_borrows[ctoken][block_number] = total_borrow
                transaction = RepayBorrowTransactionCompv2(
                    block_number=block_number,
                    block_index=block_index,
                    block_timestamp=timestamp,
                    protocol_id=self.name,
                    sender_wallet=None,
                    borrow_wallet=None,
                    repay_amount=amount,
                    ctoken=ctoken,
                )
            case "liquidate":
                if ctoken_collateral is None:
                    raise ValueError(
                        "Collateral address is required for liquidation transactions, got an error for "
                        f"transaction at block {block_number} for market {ctoken}"
                    )
                transaction = LiquidateTransactionCompv2(
                    block_number=block_number,
                    block_index=block_index,
                    block_timestamp=timestamp,
                    protocol_id=self.name,
                    sender_wallet=None,
                    borrower=None,
                    repay_amount=amount,
                    ctoken_collateral=ctoken_collateral,
                    ctoken=ctoken,
                )
            case _:
                raise Exception(
                    f"Unknown event type {event_type} expected one of 'mint', 'redeem', 'borrow', 'repay', 'liquidate'"
                )
        return transaction

    def compare_two_states(self, state_left: ABCProtocolState, state_right: ABCProtocolState) -> None:
        if not isinstance(state_left, StateComptroller) or not isinstance(state_right, StateComptroller):
            raise ValueError("States are not of type StateComptroller")

        for market in state_left.market_states.keys():
            self.logger.info(f"Comparing the info of the {market} market")
            self.compare_market_states(state_left.market_states[market], state_right.market_states[market])

    def compare_market_states(self, state_left: StateCompoundMarket, state_right: StateCompoundMarket) -> None:
        self.logger.info(
            f"Comparing the total_borrow: "
            f"{(float(state_left.total_borrows) / 10 ** state_left.underlying_decimals) :.4f} "
            f"vs {(float(state_right.total_borrows) / 10 ** state_left.underlying_decimals):.4f}"
        )
        self.logger.info(
            f"Comparing the total_reserves: "
            f"{(float(state_left.total_reserves) / 10 ** state_left.underlying_decimals) :.4f} "
            f"vs {(float(state_right.total_reserves) / 10 ** state_left.underlying_decimals):.4f}"
        )
        self.logger.info(
            f"Comparing the total_cash: {(float(state_left.total_cash) / 10 ** state_left.underlying_decimals) :.4f} "
            f"vs {(float(state_right.total_cash) / 10 ** state_left.underlying_decimals):.4f}"
        )
        self.logger.info(
            f"Comparing the total_supply: {(float(state_left.total_supply) / 10 ** state_left.decimals) :.4f} "
            f"vs {(float(state_right.total_supply) / 10 ** state_left.decimals):.4f}"
        )

    # ------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------

    def _get_globals(self, block_number: int) -> Tuple[int, int]:
        globals = DataLoader.quantlib_source().compound_v2_globals(end_block=block_number)

        if globals is None:
            raise ValueError("Cannot fetch close factor and liquidation incentive")

        return round(globals["liquidation_incentive"][-1] * 10**18), round(globals["close_factor"][-1] * 10**18)

    def _get_market_snapshot(self, block_number: int, ctoken_symbol: str, is_initial_state: bool = False) -> Any:
        snapshot = DataLoader.quantlib_source().compound_v2_market_snapshot(
            market=self.market_addresses[ctoken_symbol]["address"],
            exclusive_upper_bound=is_initial_state,
            at_block=block_number,
        )

        if snapshot is None:
            raise ValueError(f"failed to fetch the market snapshot for {ctoken_symbol}")

        return snapshot

    def _get_borrow_index(self, block_number: int, ctoken_symbol: str) -> Tuple[int, int]:
        query_result = DataLoader.quantlib_source().compound_v2_market_borrow_index(
            self.market_addresses[ctoken_symbol]["address"],
            event_type="cErc20_evt_AccrueInterest",
            at_block=block_number,
        )

        if query_result is None:
            raise ValueError(f"failed to fetch the latest borrow index for {ctoken_symbol}")

        return int(query_result["borrow_index"]), int(query_result["block_number"])

    def _make_compound_market_state(self, ctoken_symbol: str, block_number: int) -> StateCompoundMarket:
        market_snapshot = self._get_market_snapshot(block_number, ctoken_symbol, is_initial_state=True)
        interest_rate_state = StateInterestRateModel(
            multiplier_per_block=int(market_snapshot["multiplier_per_block"]),
            base_rate_per_block=int(market_snapshot["base_rate_per_block"]),
            jump_multiplier_per_block=int(market_snapshot["jump_multiplier_per_block"]),
            kink=int(market_snapshot["kink"]),
            blocks_per_year=int(market_snapshot["blocks_per_year"]),
        )

        borrow_index, accrual_block_number = self._get_borrow_index(block_number, ctoken_symbol)
        state = StateCompoundMarket(
            id=self.id + self.market_addresses[ctoken_symbol]["id"],
            block_number=block_number,
            block_timestamp=int(market_snapshot["timestamp"]),
            interest_rate_model=interest_rate_state,
            name=self.name + f"_{ctoken_symbol}",
            symbol=ctoken_symbol,
            address=self.market_addresses[ctoken_symbol]["address"],
            underlying=ctoken_symbol.replace("c", "").replace("2", ""),
            underlying_address=self.market_addresses[ctoken_symbol]["underlying_address"],
            decimals=8,
            underlying_decimals=market_snapshot["underlying_decimals"],
            initial_exchange_rate_mantissa=int(
                market_snapshot["exchange_rate"] * 10 ** (18 - 8 + market_snapshot["underlying_decimals"])
            ),
            accrual_block_number=accrual_block_number,
            borrow_index=borrow_index,
            total_borrows=int(market_snapshot["total_borrow"] * 10 ** market_snapshot["underlying_decimals"]),
            total_supply=int(market_snapshot["total_supply"] * 10**8),
            total_reserves=int(market_snapshot["reserves"] * 10 ** market_snapshot["underlying_decimals"]),
            collateral_factor=int(market_snapshot["collateral_factor"] * 10**18),
            borrow_cap=0,  # todo this needs to be added to the fields fetched
            account_borrows={},
            total_cash=int(market_snapshot["cash"] * 10 ** market_snapshot["underlying_decimals"]),
            reserve_factor_mantissa=int(market_snapshot["reserve_factor"] * 10**18),
        )

        return state

    def _load_historical_calls(self, begin: int, end: int, addresses_to_backtest: list[str]) -> dict:
        begin_formatted = BlockNumberOrTimestamp.block_number(begin)
        end_formatted = BlockNumberOrTimestamp.block_number(end)

        data_calls = DataLoader.quantlib_source().compound_v2_market_calls(
            markets=addresses_to_backtest,
            begin=begin_formatted,
            end=end_formatted,
        )

        return data_calls

    def _make_transactions_from_calls(
        self, data_calls: dict, addresses_to_backtest: list[str]
    ) -> list[TransactionCompoundv2]:
        timestamp_vec = data_calls["timestamp"]
        block_number_vec = data_calls["block_number"]
        trace_index_vec = data_calls["trace_index"]
        market_address_vec = data_calls["market_address"]
        value_vec = data_calls["value"]
        call_name_vec = data_calls["call_name"]
        data_vec = data_calls["data"]
        transactions: list[TransactionCompoundv2] = []

        for i in range(len(timestamp_vec)):
            transaction_data = json.loads(data_vec[i])
            timestamp = int(timestamp_vec[i])

            match call_name_vec[i]:
                case CompoundV2CallNames.MINT_CETH.value:
                    transaction = self.make_transaction(
                        event_type="mint",
                        timestamp=timestamp,
                        block_number=int(block_number_vec[i]),
                        amount=int(value_vec[i]),
                        ctoken=self.c_address_symbol_mapping[market_address_vec[i]]["symbol"],
                        ctoken_collateral=None,
                        total_borrow=None,
                        block_index=int(trace_index_vec[i]),
                    )
                case CompoundV2CallNames.MINT_CERC20.value:
                    transaction = self.make_transaction(
                        event_type="mint",
                        timestamp=timestamp,
                        block_number=int(block_number_vec[i]),
                        amount=int(transaction_data["mintAmount"], 16),
                        ctoken=self.c_address_symbol_mapping[market_address_vec[i]]["symbol"],
                        ctoken_collateral=None,
                        total_borrow=None,
                        block_index=int(trace_index_vec[i]),
                    )
                case CompoundV2CallNames.BORROW_CERC20.value:
                    transaction = self.make_transaction(
                        event_type="borrow",
                        timestamp=timestamp,
                        block_number=int(block_number_vec[i]),
                        amount=int(transaction_data["borrowAmount"], 16),
                        ctoken=self.c_address_symbol_mapping[market_address_vec[i]]["symbol"],
                        ctoken_collateral=None,
                        total_borrow=None,
                        block_index=int(trace_index_vec[i]),
                    )
                case CompoundV2CallNames.REDEEM_CERC20.value:
                    transaction = self.make_transaction(
                        event_type="redeem",
                        timestamp=timestamp,
                        block_number=int(block_number_vec[i]),
                        amount=int(transaction_data["redeemTokens"], 16),
                        ctoken=self.c_address_symbol_mapping[market_address_vec[i]]["symbol"],
                        ctoken_collateral=None,
                        total_borrow=None,
                        block_index=int(trace_index_vec[i]),
                    )
                case CompoundV2CallNames.REDEEM_UNDERLYING_CERC20.value:
                    transaction = self.make_transaction(
                        event_type="redeem",
                        timestamp=timestamp,
                        block_number=int(block_number_vec[i]),
                        amount=int(transaction_data["redeemAmount"], 16),
                        ctoken=self.c_address_symbol_mapping[market_address_vec[i]]["symbol"],
                        ctoken_collateral=None,
                        total_borrow=None,
                        block_index=int(trace_index_vec[i]),
                    )
                case CompoundV2CallNames.REPAY_BORROW_CERC20.value:
                    transaction = self.make_transaction(
                        event_type="repay",
                        timestamp=timestamp,
                        block_number=int(block_number_vec[i]),
                        amount=int(transaction_data["repayAmount"], 16),
                        ctoken=self.c_address_symbol_mapping[market_address_vec[i]]["symbol"],
                        ctoken_collateral=None,
                        total_borrow=None,
                        block_index=int(trace_index_vec[i]),
                    )
                case CompoundV2CallNames.REPAY_BORROW_BEHALF_CERC20.value:
                    transaction = self.make_transaction(
                        event_type="repay",
                        timestamp=timestamp,
                        block_number=int(block_number_vec[i]),
                        amount=int(transaction_data["repayAmount"], 16),
                        ctoken=self.c_address_symbol_mapping[market_address_vec[i]]["symbol"],
                        ctoken_collateral=None,
                        total_borrow=None,
                        block_index=int(trace_index_vec[i]),
                    )
                case CompoundV2CallNames.REPAY_BORROW_BEHALF_CETH.value:
                    transaction = self.make_transaction(
                        event_type="repay",
                        timestamp=timestamp,
                        block_number=int(block_number_vec[i]),
                        amount=int(value_vec[i]),
                        ctoken=self.c_address_symbol_mapping[market_address_vec[i]]["symbol"],
                        ctoken_collateral=None,
                        total_borrow=None,
                        block_index=int(trace_index_vec[i]),
                    )
                case CompoundV2CallNames.LIQUIDATE_BORROW_CERC20.value:
                    transaction = self.make_transaction(
                        event_type="liquidate",
                        timestamp=timestamp,
                        block_number=int(block_number_vec[i]),
                        amount=int(transaction_data["repayAmount"], 16),
                        ctoken=self.c_address_symbol_mapping[market_address_vec[i]]["symbol"],
                        ctoken_collateral=transaction_data["cTokenCollateral"],
                        total_borrow=None,
                        block_index=int(trace_index_vec[i]),
                    )
                case CompoundV2CallNames.LIQUIDATE_BORROW_CETH.value:
                    transaction = self.make_transaction(
                        event_type="liquidate",
                        timestamp=timestamp,
                        block_number=int(block_number_vec[i]),
                        amount=int(value_vec[i]),
                        ctoken=self.c_address_symbol_mapping[market_address_vec[i]]["symbol"],
                        ctoken_collateral=transaction_data["cTokenCollateral"],
                        total_borrow=None,
                        block_index=int(trace_index_vec[i]),
                    )
                case _:
                    raise ValueError(
                        f"Unknown call name {call_name_vec[i]} received for CompoundV2"
                        f" at block {block_number_vec[i]} for market {market_address_vec[i]}"
                    )

            transactions.append(transaction)

        return transactions

    def sort_transactions(self, transactions: list[TransactionCompoundv2]) -> list[ABCTransaction]:
        # Only get transactions from markets we want to backtest
        sorted_transactions: list[ABCTransaction] = [
            transaction
            for transaction in transactions
            if transaction.ctoken in self.market_addresses.keys() and transaction.ctoken not in EXCLUDED_MARKETS
        ]

        # Remove liquidation transactions with collaterals not in the list of backtested markets
        sorted_transactions = [
            transaction
            for transaction in sorted_transactions
            if not isinstance(transaction, LiquidateTransactionCompv2)
            or transaction.ctoken_collateral in self.market_addresses.keys()
        ]

        # Remove repay transactions for which the amounts are equal to OVERFLOW or -1 as this input means
        # that the user wants to fully repay its debt. However as we don't know the exact amount to repay it means
        # that we can't backtest it
        sorted_transactions = [
            transaction
            for transaction in sorted_transactions
            if not isinstance(transaction, RepayBorrowTransactionCompv2)
            or transaction.repay_amount not in [OVERFLOW, -1]
        ]

        # Sort transactions by block number and block index
        sorted_transactions.sort(key=lambda x: (x.block_number, x.block_index))
        return sorted_transactions
