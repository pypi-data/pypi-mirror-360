import copy
import logging
from typing import Any, Dict, Optional

from nqs_pycore import LPTokenUniv3, Wallet
from sortedcontainers import SortedDict, SortedSet

from nqs_sdk_extension.protocol import ABCProtocol
from nqs_sdk_extension.protocol.amm.uniswapv3.events import Burn, Collect, Create, Mint, Swap, Update
from nqs_sdk_extension.protocol.amm.uniswapv3.utils import StepComputations, SwapState, calculate_amounts
from nqs_sdk_extension.protocol.utils import rollback_on_failure
from nqs_sdk_extension.state import ABCProtocolState, StateUniv3, TickDataUniv3
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.uniswap import (
    BurnTransactionUniv3,
    CollectTransactionUniv3,
    MintTransactionUniv3,
    SwapTransactionUniv3,
    TransactionUniv3,
)
from nqs_sdk_extension.wallet.arbitrageur_wallet import ArbitrageurWallet
from nqs_sdk_extension.wallet.utils import (
    AgentLiquidityError,
    AmountNoneError,
    TickInitializationError,
    TickRangeError,
    TokenAlreadyExistsError,
    WrongTickRangeError,
)

from .fixed_point_128 import FixedPoint128
from .full_math import FullMath
from .swap_math import SwapMath
from .tick_math import TickMath

PROTOCOL_FEE = 0  # XXX not supported yet / not an issue for now
TOLERANCE_LIQUIDITY = 10  # arbitrary threshold


class UniswapV3(ABCProtocol):
    """
    Important notes:
    - The liquidity across ticks is càdlàg by convention. For example at tick t: [0, t) and [t, +inf).
    - The base asset is token0 (WETH) and the quote asset is token1 (USDT) so that the price is balance1/balance0.
    - A pool should always be initialized with a price/tick
    """

    # TODO: add consistency checks on the state
    def __init__(self, state: StateUniv3, gas_fee: int = 0, gas_fee_ccy: Optional[str] = None):
        super().__init__(state, gas_fee, gas_fee_ccy)
        self.__reset_from_state(state)
        # constants
        self.liquidity_decimals = 0.5 * (self.decimals0 + self.decimals1)
        self.factor_liquidity = 10 ** (-0.5 * (self.decimals0 + self.decimals1))
        self.factor_decimals0 = 10**-self.decimals0
        self.factor_decimals1 = 10**-self.decimals1
        self.token_ids: set[str] = set()

    def __reset_from_state(self, state: StateUniv3) -> None:
        state = copy.deepcopy(state)
        self.block_number = state.block_number
        self.block_timestamp = state.block_timestamp
        self.token0 = state.token0  # not used
        self.token1 = state.token1  # not used
        self.symbol0 = state.symbol0  # used by wallet
        self.symbol1 = state.symbol1  # used by wallet
        self.decimals0 = state.decimals0
        self.decimals1 = state.decimals1
        self.liquidity = state.liquidity
        self.tick = state.tick
        self.sqrt_price_x96 = state.sqrt_price_x96
        self.fee_growth_global_0_x128 = state.fee_growth_global_0_x128  # tracker for global fee growth
        self.fee_growth_global_1_x128 = state.fee_growth_global_1_x128  # tracker for global fee growth
        self.fee_tier = state.fee_tier  # fee in pips
        # Use a SortedDict to keep track of the ticks for efficient iteration
        self.ticks: Dict[int, TickDataUniv3] = SortedDict()
        for tick in state.ticks:
            self.ticks[tick.tick_idx] = tick
        self.tickSet = SortedSet(self.ticks.keys())  # helper
        self.events_ready_to_collect: list = []
        self.n_tick_crossed: int = 0

    def process_transactions(self, transactions: list[ABCTransaction]) -> None:
        for transaction in transactions:
            self.process_single_transaction(transaction)

    def process_single_transaction(self, transaction: ABCTransaction) -> None:
        if not isinstance(transaction, TransactionUniv3):
            message = "Can only process instances of TransactionUniswapV3"
            message = (
                f"Action {transaction.action_name} - " + message if transaction.action_name is not None else message
            )
            raise ValueError(message)
        self._handle_transaction(transaction=transaction, msg_sender=transaction.sender_wallet)

    def get_state(self, block_timestamp: int) -> StateUniv3:
        # XXX: not compatible with rollbackonfailure
        # if block_timestamp < self.block_timestamp:
        #     raise ValueError("Cannot get state at a previous block timestamp")
        # elif block_timestamp != self.block_timestamp:
        #    self.logger.warning("Requested state at a different block timestamp")
        state = StateUniv3(
            id=self.id,
            name=self.name,
            block_number=self.block_number,
            block_timestamp=self.block_timestamp,
            token0=self.token0,
            token1=self.token1,
            symbol0=self.symbol0,
            symbol1=self.symbol1,
            decimals0=self.decimals0,
            decimals1=self.decimals1,
            fee_tier=self.fee_tier,
            liquidity=self.liquidity,
            sqrt_price_x96=self.sqrt_price_x96,
            fee_growth_global_0_x128=self.fee_growth_global_0_x128,
            fee_growth_global_1_x128=self.fee_growth_global_1_x128,
            tick=self.tick,
            ticks=list(self.ticks.values()),
        )
        state = copy.deepcopy(state)
        return state

    def restore_from_state(self, state: ABCProtocolState) -> None:
        if not isinstance(state, StateUniv3):
            raise ValueError("Can only restore from instances of StateUniswapV3")
        self.__reset_from_state(state)

    def get_spot(self) -> float:
        return TickMath.sqrt_price_x96_to_price(self.sqrt_price_x96, self.decimals0, self.decimals1)

    def get_total_tokens_owed(
        self,
        token: LPTokenUniv3,
        fee_growth_inside_0_last_x128_last: int | None = None,
        fee_growth_inside_1_last_x128_last: int | None = None,
    ) -> tuple[int, int]:
        if token.liquidity > 0:
            if fee_growth_inside_0_last_x128_last is None or fee_growth_inside_1_last_x128_last is None:
                fee_growth_inside_0_last_x128_last = self._get_fee_growth_inside(
                    token.tick_lower, token.tick_upper, True
                )
                fee_growth_inside_1_last_x128_last = self._get_fee_growth_inside(
                    token.tick_lower, token.tick_upper, False
                )
            # compute the amount of tokens owed to the LP since last position update
            liquidity = token.liquidity
            tokens_owed0 = FullMath.mul_div_rounding_up(
                liquidity, int(fee_growth_inside_0_last_x128_last - int(token.fee_growth_inside_0_last_x128)), 2**128
            )
            tokens_owed1 = FullMath.mul_div_rounding_up(
                liquidity, int(fee_growth_inside_1_last_x128_last - int(token.fee_growth_inside_1_last_x128)), 2**128
            )
        else:
            # position has been burned
            tokens_owed0 = tokens_owed1 = 0
        # add the previously owed fees to the LP
        tokens_owed0 += token.tokens_owed_0
        tokens_owed1 += token.tokens_owed_1
        return tokens_owed0, tokens_owed1

    # ------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------

    @rollback_on_failure
    def _handle_transaction(self, transaction: ABCTransaction, msg_sender: Wallet) -> None:
        self.block_number = transaction.block_number
        self.block_timestamp = transaction.block_timestamp
        if isinstance(transaction, SwapTransactionUniv3):
            # do not process agent swaps with 0 amount (that could come from expression evaluations)
            if transaction.sender_wallet is None or (
                not (
                    transaction.amount0_in == 0
                    or transaction.amount1_in == 0
                    or transaction.amount0_out == 0
                    or transaction.amount0_out == 0
                )
            ):
                self._update_from_swap(
                    amount0_in=transaction.amount0_in,
                    amount1_in=transaction.amount1_in,
                    amount0_out=transaction.amount0_out,
                    amount1_out=transaction.amount1_out,
                    msg_sender=transaction.sender_wallet,
                    sqrt_price_limit_x96=transaction.sqrt_price_limit_x96,
                    action_name=transaction.action_name,
                )
            else:
                message = (
                    f"Swap transaction at block {transaction.block_number} from "
                    f"{transaction.sender_wallet.agent_name} is not executed as the swap amount is 0"
                )
                message = (
                    f"Action {transaction.action_name} - " + message if transaction.action_name is not None else message
                )
                self.logger.warning(message)
        elif isinstance(transaction, MintTransactionUniv3):
            # only the parameter `amount` is needed for a mint
            if (transaction.amount is None) or (transaction.sender_wallet is not None):
                transaction = self._compute_lp_amounts(transaction)
            # do not process mints with 0 amount (that could come from expression evaluations)
            if transaction.amount > 0:  # type: ignore
                self._update_from_mint(
                    amount=transaction.amount,
                    amount0=transaction.amount0,
                    amount1=transaction.amount1,
                    tick_lower=transaction.tick_lower,
                    tick_upper=transaction.tick_upper,
                    msg_sender=transaction.sender_wallet,
                    token_id=transaction.token_id,
                    action_name=transaction.action_name,
                )
            else:
                if transaction.sender_wallet is not None:
                    message = (
                        f"Mint transaction at block {transaction.block_number} from "
                        f"{transaction.sender_wallet.agent_name} is not executed as the mint amount is 0"
                    )
                    message = (
                        f"Action {transaction.action_name} - " + message
                        if transaction.action_name is not None
                        else message
                    )
                    self.logger.warning(message)
        elif isinstance(transaction, BurnTransactionUniv3):
            # only the parameter `amount` is needed for a burn
            if (transaction.amount is None) or (transaction.sender_wallet is not None):
                transaction = self._compute_lp_amounts(transaction)
            # do not process burns with 0 amount (that could come from expression evaluations)
            if transaction.amount > 0:  # type: ignore
                self._update_from_burn(
                    amount=transaction.amount,
                    amount0=transaction.amount0,
                    amount1=transaction.amount1,
                    tick_lower=transaction.tick_lower,
                    tick_upper=transaction.tick_upper,
                    msg_sender=transaction.sender_wallet,
                    token_id=transaction.token_id,
                    action_name=transaction.action_name,
                )
                if transaction.sender_wallet is not None:
                    self._update_from_collect(
                        amount0=None,
                        amount1=None,
                        tick_lower=transaction.tick_lower,
                        tick_upper=transaction.tick_upper,
                        msg_sender=transaction.sender_wallet,
                        token_id=transaction.token_id,
                        action_name=transaction.action_name,
                    )
            else:
                if transaction.sender_wallet is not None:
                    message = (
                        f"Burn transaction at block {transaction.block_number} from "
                        f"{transaction.sender_wallet.agent_name} is not executed as the burn amount is 0"
                    )
                    message = (
                        f"Action {transaction.action_name} - " + message
                        if transaction.action_name is not None
                        else message
                    )
                    self.logger.warning(message)
        elif isinstance(transaction, CollectTransactionUniv3):
            # check that the msg_sender is not None
            if transaction.sender_wallet is None:
                message = "msg_sender should not be None"
                message = (
                    f"Action {transaction.action_name} - " + message if transaction.action_name is not None else message
                )
                raise ValueError(message)
            # collect all the accumulated fees
            self._update_from_collect(
                amount0=transaction.amount0,
                amount1=transaction.amount1,
                tick_lower=transaction.tick_lower,
                tick_upper=transaction.tick_upper,
                msg_sender=transaction.sender_wallet,
                token_id=transaction.token_id,
                action_name=transaction.action_name,
            )
        else:
            raise ValueError("Actions of type {} are not supported".format(transaction.action_type))
        self.logger.debug(transaction)

        # check the current liquidity against the net liquidity in ticks
        if self.logger.getEffectiveLevel() == logging.DEBUG:
            current_liquidity = 0
            for i in range(len(self.tickSet) - 1):
                t_lower = self.tickSet[i]
                tick = self.ticks[t_lower]
                if t_lower <= self.tick:
                    current_liquidity += tick.liquidity_net
            if self.liquidity != current_liquidity:
                print(f"Liquidity disalignment at block {self.block_number}")

    def _update_from_mint(
        self,
        amount: int | None,
        amount0: int | None,
        amount1: int | None,
        tick_lower: int,
        tick_upper: int,
        msg_sender: Wallet | None,
        token_id: str | None = None,
        action_name: str | None = None,
    ) -> None:
        if tick_lower > tick_upper:
            raise ValueError(
                f"Lower tick :{tick_lower} is greater than upper tick : {tick_upper} at block {self.block_number}"
            )
        if amount is None:
            raise ValueError("amount should not be None")
        # get ticks
        tick_data_lower = self._get_or_init_tick(tick_lower)
        tick_data_upper = self._get_or_init_tick(tick_upper)
        # update tick data
        tick_data_lower.liquidity_net += amount
        tick_data_upper.liquidity_net -= amount
        tick_data_lower.liquidity_gross += amount
        tick_data_upper.liquidity_gross += amount
        if (self.tick >= tick_lower) and (self.tick < tick_upper):
            self.liquidity += amount
        # update wallet if available
        if msg_sender is not None:
            if amount0 is None or amount1 is None:
                raise ValueError("amounts should not be None")
            msg_sender.transfer_from(self.symbol0, amount0, action_name)
            msg_sender.transfer_from(self.symbol1, amount1, action_name)
            self._update_position(tick_lower, tick_upper, amount, msg_sender, token_id, action_name)
        # create and log event
        mint_event = Mint(
            block_number=self.block_number,
            block_timestamp=self.block_timestamp,
            tick_lower=tick_lower,
            tick_upper=tick_upper,
            amount=amount,
            amount0=0 if amount0 is None else amount0,
            amount1=0 if amount1 is None else amount1,
            sqrt_price_x96=self.sqrt_price_x96,
        )
        msg = f"Transaction: Mint - Status: Succeeded - Comment: {mint_event}"
        if isinstance(msg_sender, Wallet) and not isinstance(msg_sender, ArbitrageurWallet):
            self.logger.info(
                f"Key: {self.logger_key_tx} - Timestamp: {self.block_timestamp} - Block number: {self.block_number} - "
                f"Agent: {msg_sender.agent_name} - " + msg
            )
        else:
            self.logger.debug(msg)
        self.events_ready_to_collect.append(mint_event)

    def _update_from_burn(
        self,
        amount: int | None,
        amount0: int | None,
        amount1: int | None,
        tick_lower: int,
        tick_upper: int,
        msg_sender: Wallet | None,
        token_id: str | None = None,
        action_name: str | None = None,
    ) -> None:
        if amount is None:
            raise ValueError("amounts should not be None")
        # ticks should be already initialized
        tick_data_lower = self.ticks.get(tick_lower, None)
        tick_data_upper = self.ticks.get(tick_upper, None)
        if (tick_data_lower is None) or (tick_data_upper is None):
            message = "ticks should be already initialized"
            message = f"Action {action_name} - " + message if action_name is not None else message
            raise TickInitializationError(message)
        # update tick data
        tick_data_lower.liquidity_net -= amount
        tick_data_upper.liquidity_net += amount
        tick_data_lower.liquidity_gross -= amount
        tick_data_upper.liquidity_gross -= amount
        if (self.tick >= tick_lower) and (self.tick < tick_upper):
            # check that liquidity is non-negative !
            if self.liquidity - amount < -TOLERANCE_LIQUIDITY:  # arbitrary threshold
                message = "cannot burn more liquidity than available"
                if msg_sender is None:
                    raise ValueError(message + " - on block : " + f"{self.block_number}")
                else:
                    message = f"Action {action_name} - " + message if action_name is not None else message
                    raise AgentLiquidityError(message)
            self.liquidity -= amount
            # XXX patch precision issue if no error raised
            if self.liquidity < 0:
                tick_data_lower.liquidity_net -= self.liquidity
                tick_data_upper.liquidity_net += self.liquidity
                tick_data_lower.liquidity_gross -= self.liquidity
                tick_data_upper.liquidity_gross -= self.liquidity
                self.liquidity = 0
        # update wallet if available
        if msg_sender is not None:
            self._update_position(tick_lower, tick_upper, -amount, msg_sender, token_id, action_name)
            if amount0 is None or amount1 is None:
                raise ValueError("amounts should not be None")
            msg_sender.transfer_to(self.symbol0, amount0, action_name)
            msg_sender.transfer_to(self.symbol1, amount1, action_name)
        # delete tick if not needed anymore (should be done after the wallet update to avoid inconsistency)
        if tick_data_lower.liquidity_gross == 0:
            self.tickSet.remove(tick_lower)
            self.ticks.pop(tick_lower)
        if tick_data_upper.liquidity_gross == 0:
            self.tickSet.remove(tick_upper)
            self.ticks.pop(tick_upper)
        # create and log event
        burn_event = Burn(
            block_number=self.block_number,
            block_timestamp=self.block_timestamp,
            tick_lower=tick_lower,
            tick_upper=tick_upper,
            amount=amount,
            amount0=0 if amount0 is None else amount0,
            amount1=0 if amount1 is None else amount1,
        )
        msg = f"Transaction: Burn - Status: Succeeded - Comment: {burn_event}"
        if isinstance(msg_sender, Wallet) and not isinstance(msg_sender, ArbitrageurWallet):
            self.logger.info(
                f"Key: {self.logger_key_tx} - Timestamp: {self.block_timestamp} - Block number: {self.block_number} - "
                f"Agent: {msg_sender.agent_name} - " + msg
            )
        else:
            self.logger.debug(msg)
        self.events_ready_to_collect.append(burn_event)

    # This implements the same logic as in the smart-contracts
    # https://github.com/Uniswap/v3-core/blob/d8b1c635c275d2a9450bd6a78f3fa2484fef73eb/contracts/UniswapV3Pool.sol#L596
    # ruff: noqa: C901
    def _update_from_swap(
        self,
        amount0_in: int | None,
        amount0_out: int | None,
        amount1_in: int | None,
        amount1_out: int | None,
        sqrt_price_limit_x96: int | None = None,
        msg_sender: Wallet | None = None,
        action_name: str | None = None,
    ) -> None:
        zero_for_one = self.is_zero_for_one(amount0_in, amount0_out, amount1_in, amount1_out)
        exact_input = self.is_exact_input(amount0_in, amount0_out, amount1_in, amount1_out)
        amount_specified = [x for x in [amount0_in, amount0_out, amount1_in, amount1_out] if x is not None][
            0
        ]  # there is only one non-None value
        # amount_specified = int(amount_specified)
        if sqrt_price_limit_x96 is None:
            if zero_for_one:
                sqrt_price_limit_x96 = TickMath.MIN_SQRT_RATIO
            else:
                sqrt_price_limit_x96 = TickMath.MAX_SQRT_RATIO

        else:
            if zero_for_one and sqrt_price_limit_x96 >= self.sqrt_price_x96:
                sqrt_price_limit_x96 = TickMath.MIN_SQRT_RATIO
            elif not zero_for_one and sqrt_price_limit_x96 <= self.sqrt_price_x96:
                sqrt_price_limit_x96 = TickMath.MAX_SQRT_RATIO
        # no need for cache struct
        liquidity_start = self.liquidity
        # temporary variables
        state = SwapState(
            amount_specified_remaining=amount_specified if exact_input else -amount_specified,
            amount_calculated=0,
            sqrt_price_x96=self.sqrt_price_x96,
            tick=self.tick,
            fee_growth_global_x128=self.fee_growth_global_0_x128 if zero_for_one else self.fee_growth_global_1_x128,
            protocol_fee=0,
            liquidity=liquidity_start,
        )
        fee_amount = 0  # used to track the total fees collected in the event
        tick_modifications = []

        # continue swapping as long as we haven't used the entire input/output and haven't reached the price limit
        while (state.amount_specified_remaining != 0) and (state.sqrt_price_x96 != sqrt_price_limit_x96):
            step = StepComputations()
            step.sqrt_price_start_x96 = state.sqrt_price_x96
            step.tick_next = self.get_next_tick(state.tick, state.sqrt_price_x96, zero_for_one)

            # ensure that we do not overshoot the min/max tick, as the tick bitmap is not aware of these bounds
            if step.tick_next < TickMath.MIN_TICK:
                step.tick_next = TickMath.MIN_TICK
            elif step.tick_next > TickMath.MAX_TICK:
                step.tick_next = TickMath.MAX_TICK

            # get the price for the next tick
            step.sqrt_price_next_x96 = TickMath.get_sqrt_ratio_at_tick(step.tick_next)

            # compute values to swap to the target tick, price limit, or point where input/output amount is exhausted
            state.sqrt_price_x96, step.amount_in, step.amount_out, step.fee_amount = SwapMath.compute_swap_step(
                state.sqrt_price_x96,
                sqrt_price_limit_x96
                if (zero_for_one and step.sqrt_price_next_x96 < sqrt_price_limit_x96)
                or (not zero_for_one and step.sqrt_price_next_x96 > sqrt_price_limit_x96)
                else step.sqrt_price_next_x96,
                state.liquidity,
                state.amount_specified_remaining,
                self.fee_tier,
            )

            if exact_input:
                state.amount_specified_remaining -= step.amount_in + step.fee_amount
                state.amount_calculated -= step.amount_out
            else:
                state.amount_specified_remaining += step.amount_out
                state.amount_calculated += step.amount_in + step.fee_amount

            fee_amount += step.fee_amount

            # if the protocol fee is on, calculate how much is owed, decrement fee_amount, and increment protocol_fee
            # if cache.feeProtocol > 0:
            #    delta = step.fee_amount // cache.feeProtocol
            #    step.fee_amount -= delta
            #    state.protocol_fee += delta

            # update global fee tracker
            if state.liquidity > 0:
                state.fee_growth_global_x128 += FullMath.mul_div(step.fee_amount, FixedPoint128.Q128, state.liquidity)

            # shift tick if we reached the next price
            if state.sqrt_price_x96 == step.sqrt_price_next_x96:
                tick_modification = self.simulate_tick_cross(
                    self.ticks,
                    step.tick_next,
                    state.fee_growth_global_x128 if zero_for_one else self.fee_growth_global_0_x128,
                    self.fee_growth_global_1_x128 if zero_for_one else state.fee_growth_global_x128,
                )
                tick_modifications.append(tick_modification)
                liquidity_net = tick_modification["liquidity_net"]
                # if we're moving leftward, we interpret liquidity_net as the opposite sign
                # safe because liquidity_net cannot be type(int128).min
                if zero_for_one:
                    liquidity_net = -liquidity_net
                state.liquidity = state.liquidity + liquidity_net
                if state.liquidity <= 0:
                    message = "liquidity cannot be negative"
                    if msg_sender is None:
                        self.logger.warning(
                            message
                            + ", transaction is reverted because of a negative liquidity on pool"
                            + f"{self.name}"
                        )
                        return None
                    elif isinstance(msg_sender, ArbitrageurWallet):
                        raise ValueError(
                            message + ", arbitrageur's swap size is too big at block : " + f"{self.block_number}"
                        )
                    else:
                        message = f"Action {action_name} - " + message if action_name is not None else message
                        raise AgentLiquidityError(message)

                self.n_tick_crossed += 1  # inner metric update
                state.tick = step.tick_next - 1 if zero_for_one else step.tick_next  # XXX: not clear why -1
            elif state.sqrt_price_x96 != step.sqrt_price_start_x96:
                # recompute unless we're on a lower tick boundary (i.e. already transitioned ticks), and haven't moved
                state.tick = TickMath.get_tick_at_sqrt_ratio(state.sqrt_price_x96)
            # end while loop

        for modification in tick_modifications:
            tick_data = self.ticks[modification["tick"]]
            tick_data.fee_growth_outside_0_x128 = modification["new_fee_growth_outside_0_x128"]
            tick_data.fee_growth_outside_1_x128 = modification["new_fee_growth_outside_1_x128"]

        # update tick and write an oracle entry if the tick change
        if state.tick != self.tick:
            self.sqrt_price_x96 = state.sqrt_price_x96
            self.tick = state.tick
        else:
            # otherwise just update the price
            self.sqrt_price_x96 = state.sqrt_price_x96

        # update liquidity if it changed
        if liquidity_start != state.liquidity:
            self.liquidity = state.liquidity

        # update fee growth global
        if zero_for_one:
            self.fee_growth_global_0_x128 = state.fee_growth_global_x128
            # if state.protocol_fee > 0:
            #    protocol_fees.token0 += state.protocol_fee
        else:
            self.fee_growth_global_1_x128 = state.fee_growth_global_x128
            # if state.protocol_fee > 0:
            #    protocol_fees.token1 += state.protocol_fee

        # final amounts to be transferred
        if zero_for_one == exact_input:
            amount0 = amount_specified - state.amount_specified_remaining
            amount1 = state.amount_calculated
        else:
            amount0 = state.amount_calculated
            amount1 = amount_specified - state.amount_specified_remaining

        # cast to int, math library is not integer only
        amount0 = int(amount0)
        amount1 = int(amount1)

        # do the transfers and collect payment
        if msg_sender is not None:
            if zero_for_one:
                msg_sender.transfer_from(self.symbol0, abs(amount0), action_name)
                msg_sender.transfer_to(self.symbol1, abs(amount1), action_name)
            else:
                msg_sender.transfer_to(self.symbol0, abs(amount0), action_name)
                msg_sender.transfer_from(self.symbol1, abs(amount1), action_name)
        # create and log event
        swap_event = Swap(
            block_number=self.block_number,
            block_timestamp=self.block_timestamp,
            amount0=amount0,
            amount1=amount1,
            zero_for_one=zero_for_one,
            fee_amount=fee_amount,
            sqrt_price_x96=self.sqrt_price_x96,
            liquidity=self.liquidity,
            tick=self.tick,
        )
        msg = f"Transaction: Swap - Status: Succeeded - Comment: {swap_event}"
        if isinstance(msg_sender, Wallet) and not isinstance(msg_sender, ArbitrageurWallet):
            self.logger.info(
                f"Key: {self.logger_key_tx} - Timestamp: {self.block_timestamp} - Block number: {self.block_number} - "
                f"Agent: {msg_sender.agent_name} - " + msg
            )
        else:
            self.logger.debug(msg)
        self.events_ready_to_collect.append(swap_event)

    def tick_cross(self, tick: int, fee_growth_global_0_x128: int, fee_growth_global_1_x128: int) -> int:
        tick_data = self.ticks.get(tick, None)
        if tick_data is None:
            raise TickInitializationError("tick should be already initialized")
        tick_data.fee_growth_outside_0_x128 = fee_growth_global_0_x128 - tick_data.fee_growth_outside_0_x128
        tick_data.fee_growth_outside_1_x128 = fee_growth_global_1_x128 - tick_data.fee_growth_outside_1_x128
        return tick_data.liquidity_net

    @staticmethod
    def simulate_tick_cross(
        ticks: Dict[int, TickDataUniv3], tick: int, fee_growth_global_0_x128: int, fee_growth_global_1_x128: int
    ) -> Dict[str, Any]:
        tick_data = ticks.get(tick, None)
        if tick_data is None:
            raise TickInitializationError("tick should be already initialized")
        new_fee_growth_outside_0_x128 = fee_growth_global_0_x128 - tick_data.fee_growth_outside_0_x128
        new_fee_growth_outside_1_x128 = fee_growth_global_1_x128 - tick_data.fee_growth_outside_1_x128
        return {
            "tick": tick,
            "new_fee_growth_outside_0_x128": new_fee_growth_outside_0_x128,
            "new_fee_growth_outside_1_x128": new_fee_growth_outside_1_x128,
            "liquidity_net": tick_data.liquidity_net,
        }

    def get_next_tick(self, tick: int, sqrt_price_ratio_x96: int, zero_for_one: bool) -> int:
        if tick in self.tickSet:
            tick_idx = self.tickSet.index(tick)
            if zero_for_one:
                if TickMath.get_sqrt_ratio_at_tick(tick) == sqrt_price_ratio_x96:
                    tick_idx_next = tick_idx - 1
                else:
                    tick_idx_next = tick_idx
            else:
                tick_idx_next = tick_idx + 1
        else:
            tick_idx = self.tickSet.bisect_left(tick)
            if zero_for_one:
                tick_idx_next = tick_idx - 1
            else:
                tick_idx_next = tick_idx
        assert tick_idx_next >= 0
        assert tick_idx_next < len(self.tickSet)
        tick_next = self.tickSet[tick_idx_next]
        return tick_next  # type: ignore

    def _update_from_collect(
        self,
        amount0: int | None,
        amount1: int | None,
        tick_lower: int,
        tick_upper: int,
        msg_sender: Wallet,
        token_id: str | None = None,
        action_name: str | None = None,
    ) -> None:
        # get LP position
        token_id = (
            token_id
            if token_id is not None
            else UniswapV3.get_token_id(msg_sender.agent_name, self.name, tick_lower, tick_upper)
        )
        nft_lp = self._get_lp_token(msg_sender, token_id, action_name)
        # refresh tokens owed to the LP if needed
        if nft_lp.liquidity > 0:
            self._refresh_tokens_owed(nft_lp)
            # msg_sender.replace_erc721_token(nft_lp)
        tokens_owed0, tokens_owed1 = nft_lp.tokens_owed_0, nft_lp.tokens_owed_1
        # tokens to transfer
        if amount0 is None or amount0 > tokens_owed0:
            tokens_to_transfer0, tokens_owed0 = tokens_owed0, 0
        else:
            tokens_to_transfer0, tokens_owed0 = amount0, tokens_owed0 - amount0
        if amount1 is None or amount1 > tokens_owed1:
            tokens_to_transfer1, tokens_owed1 = tokens_owed1, 0
        else:
            tokens_to_transfer1, tokens_owed1 = amount1, tokens_owed1 - amount1
        # transfer to wallet
        msg_sender.transfer_to(self.symbol0, tokens_to_transfer0, action_name)
        msg_sender.transfer_to(self.symbol1, tokens_to_transfer1, action_name)
        # update tokens owed
        nft_lp.tokens_owed_0, nft_lp.tokens_owed_1 = tokens_owed0, tokens_owed1
        msg_sender.replace_erc721_token(nft_lp)
        # log and create event
        collect_event = Collect(
            token_id=nft_lp.token_id,
            block_number=self.block_number,
            block_timestamp=self.block_timestamp,
            tick_lower=tick_lower,
            tick_upper=tick_upper,
            amount0=tokens_to_transfer0,
            amount1=tokens_to_transfer1,
        )
        msg = f"Transaction: Collect - Status: Succeeded - Comment: {collect_event}"
        if isinstance(msg_sender, Wallet) and not isinstance(msg_sender, ArbitrageurWallet):
            self.logger.info(
                f"Key: {self.logger_key_tx} - Timestamp: {self.block_timestamp} - Block number: {self.block_number} - "
                f"Agent: {msg_sender.agent_name} - " + msg
            )
        else:
            self.logger.debug(msg)
        self.events_ready_to_collect.append(collect_event)

    def _refresh_tokens_owed(self, nft_lp: LPTokenUniv3) -> None:
        fee_growth_inside_0_last_x128_last, fee_growth_inside_1_last_x128_last = self._get_fee_growth_inside_0_and_1(
            nft_lp.tick_lower, nft_lp.tick_upper
        )
        nft_lp.tokens_owed_0, nft_lp.tokens_owed_1 = self.get_total_tokens_owed(
            nft_lp, fee_growth_inside_0_last_x128_last, fee_growth_inside_1_last_x128_last
        )
        nft_lp.fee_growth_inside_0_last_x128 = fee_growth_inside_0_last_x128_last
        nft_lp.fee_growth_inside_1_last_x128 = fee_growth_inside_1_last_x128_last

    def _compute_lp_amounts(
        self, transaction: MintTransactionUniv3 | BurnTransactionUniv3
    ) -> MintTransactionUniv3 | BurnTransactionUniv3:
        """
        Compute and amend the amount of token0 and token1,
        and the virtual liquidity for a given LP transaction.

        This function follows the white-paper logic and not the smart-contract implementation.
        """

        transaction.tick_lower, transaction.tick_upper = int(transaction.tick_lower), int(transaction.tick_upper)
        if transaction.tick_lower > transaction.tick_upper:
            message = "Tick_lower should be lower than tick_upper"
            message = (
                f"Action {transaction.action_name} - " + message if transaction.action_name is not None else message
            )
            raise TickRangeError(message)
        sqrt_price = TickMath.sqrt_price_x96_to_sqrt_price(self.sqrt_price_x96, self.decimals0, self.decimals1)
        sqrt_price_lower = TickMath.tick_to_price(transaction.tick_lower, self.decimals0, self.decimals1) ** 0.5
        sqrt_price_upper = TickMath.tick_to_price(transaction.tick_upper, self.decimals0, self.decimals1) ** 0.5

        amount, amount0, amount1 = calculate_amounts(
            sqrt_price_lower=sqrt_price_lower,
            sqrt_price_upper=sqrt_price_upper,
            sqrt_price=sqrt_price,
            user_input_amount=transaction.amount,
            user_input_amount0=transaction.amount0,
            user_input_amount1=transaction.amount1,
            decimals0=self.decimals0,
            decimals1=self.decimals1,
        )

        if amount is None or amount0 is None or amount1 is None:
            raise TickRangeError(
                """The user is trying to provide liquidity in the wrong tick range
                (amount0 with spot above the upper tick or amount1 with spot below the lower tick)"""
            )

        if transaction.amount0 is None:
            transaction.amount0 = amount0
        if transaction.amount1 is None:
            transaction.amount1 = amount1
        if transaction.amount is None:
            transaction.amount = amount
        return transaction

    def _get_or_init_tick(self, tick_idx: int) -> TickDataUniv3:
        if self.ticks.get(tick_idx, None) is None:
            liquidity_gross = 0
            liquidity_net = 0
            fee_growth_outside_0_x128 = self.fee_growth_global_0_x128 if tick_idx <= self.tick else 0
            fee_growth_outside_1_x128 = self.fee_growth_global_1_x128 if tick_idx <= self.tick else 0
            self.ticks[tick_idx] = TickDataUniv3(
                liquidity_gross=liquidity_gross,
                liquidity_net=liquidity_net,
                fee_growth_outside_0_x128=fee_growth_outside_0_x128,
                fee_growth_outside_1_x128=fee_growth_outside_1_x128,
                tick_idx=tick_idx,
            )
            self.tickSet.add(tick_idx)
        return self.ticks[tick_idx]

    def _get_fee_growth_below(self, tick_idx: int, is_token0: bool) -> int:
        tick_below = self.ticks.get(tick_idx, None)
        if tick_below is None:
            raise TickInitializationError("tick should be already initialized")
        if self.tick >= tick_idx:
            if is_token0:
                fee_growth = tick_below.fee_growth_outside_0_x128
            else:
                fee_growth = tick_below.fee_growth_outside_1_x128
        else:
            if is_token0:
                fee_growth = self.fee_growth_global_0_x128 - tick_below.fee_growth_outside_0_x128
            else:
                fee_growth = self.fee_growth_global_1_x128 - tick_below.fee_growth_outside_1_x128
        return fee_growth

    def _get_fee_growth_above(self, tick_idx: int, is_token0: bool) -> int:
        tick_above = self.ticks.get(tick_idx, None)
        if tick_above is None:
            raise TickInitializationError("tick should be already initialized")
        if self.tick >= tick_idx:
            if is_token0:
                fee_growth = self.fee_growth_global_0_x128 - tick_above.fee_growth_outside_0_x128
            else:
                fee_growth = self.fee_growth_global_1_x128 - tick_above.fee_growth_outside_1_x128
        else:
            if is_token0:
                fee_growth = tick_above.fee_growth_outside_0_x128
            else:
                fee_growth = tick_above.fee_growth_outside_1_x128
        return fee_growth

    def _get_fee_growth_inside(self, tick_idx_below: int, tick_idx_above: int, is_token0: bool) -> int:
        fee_growth_global = self.fee_growth_global_0_x128 if is_token0 else self.fee_growth_global_1_x128
        fee_growth_below = self._get_fee_growth_below(tick_idx_below, is_token0)
        fee_growth_above = self._get_fee_growth_above(tick_idx_above, is_token0)
        fee_range = fee_growth_global - fee_growth_below - fee_growth_above
        return fee_range

    def _get_fee_growth_inside_0_and_1(self, tick_idx_below: int, tick_idx_above: int) -> tuple[int, int]:
        fee_growth_inside_0_last_x128_last = self._get_fee_growth_inside(tick_idx_below, tick_idx_above, True)
        fee_growth_inside_1_last_x128_last = self._get_fee_growth_inside(tick_idx_below, tick_idx_above, False)
        return fee_growth_inside_0_last_x128_last, fee_growth_inside_1_last_x128_last

    def _update_position(
        self,
        tick_lower: int,
        tick_upper: int,
        amount: int,
        wallet: Wallet,
        token_id: str | None = None,
        action_name: str | None = None,
    ) -> None:
        try:
            # if a custom token_id was not provided, look for the default version
            token_id = (
                token_id
                if token_id is not None
                else UniswapV3.get_token_id(wallet.agent_name, self.name, tick_lower, tick_upper)
            )
            nft_lp = self._get_lp_token(wallet, token_id, action_name)
            if nft_lp.tick_lower != tick_lower or nft_lp.tick_upper != tick_upper:
                message = (
                    f"Attempting to modify the existing position {token_id} on a wrong tick range. "
                    f"NFT tick range: {nft_lp.tick_lower}, {nft_lp.tick_upper}, requested tick "
                    f"range: {tick_lower}, {tick_upper}."
                )
                message = f"Action {action_name} - " + message if action_name is not None else message
                raise WrongTickRangeError(message)
            wallet.has_enough_liquidity(nft_lp, -amount, action_name)
            # amounts owed to the LP
            self._refresh_tokens_owed(nft_lp)
            # update total liquidity
            nft_lp.liquidity += amount
            wallet.replace_erc721_token(nft_lp)
            update_event = Update(
                token_id=nft_lp.token_id,
                block_number=self.block_number,
                block_timestamp=self.block_timestamp,
                delta_amount=amount,
                sqrt_price_x96=self.sqrt_price_x96,
            )
            self.events_ready_to_collect.append(update_event)
        # if the LP position is not found, create a new one
        except Exception as e:
            if "Missing ERC721" not in str(e):
                logging.error(f"Exception {e}")
                raise e
            # re-raise the exception if it is for a burn transaction
            if amount < 0:
                raise e
            nft_lp = self._create_position(tick_lower, tick_upper, amount, wallet.agent_name, token_id, action_name)
            wallet.mint_erc721(nft_lp)
            create_event = Create(
                token_id=nft_lp.token_id,
                tick_lower=tick_lower,
                tick_upper=tick_upper,
                block_number=self.block_number,
                block_timestamp=self.block_timestamp,
                amount=amount,
                sqrt_price_x96=self.sqrt_price_x96,
            )
            self.events_ready_to_collect.append(create_event)

    def _create_position(
        self,
        tick_lower: int,
        tick_upper: int,
        amount: int,
        agent_name: str,
        token_id: str | None = None,
        action_name: str | None = None,
    ) -> LPTokenUniv3:
        fee_growth_inside_0_last_x128 = self._get_fee_growth_inside(tick_lower, tick_upper, True)
        fee_growth_inside_1_last_x128 = self._get_fee_growth_inside(tick_lower, tick_upper, False)
        token_id = (
            token_id if token_id is not None else UniswapV3.get_token_id(agent_name, self.name, tick_lower, tick_upper)
        )
        if token_id in self.token_ids:
            message = f"token_id {token_id} already exists"
            message = f"Action {action_name} - " + message if action_name is not None else message
            raise TokenAlreadyExistsError(message)
        self.token_ids.add(token_id)
        nft_lp = LPTokenUniv3(
            pool_name=self.name,
            token_id=token_id,
            tick_lower=tick_lower,
            tick_upper=tick_upper,
            liquidity=amount,
            fee_growth_inside_0_last_x128=fee_growth_inside_0_last_x128,
            fee_growth_inside_1_last_x128=fee_growth_inside_1_last_x128,
            tokens_owed_0=0,
            tokens_owed_1=0,
        )
        return nft_lp

    # ------------------------------------------------------------
    # Swap static methods
    # ------------------------------------------------------------

    @staticmethod
    def is_zero_for_one(
        amount0_in: int | None, amount0_out: int | None, amount1_in: int | None, amount1_out: int | None
    ) -> bool:
        """
        Check if the swap is from token0 to token1.
        """
        if amount0_in is not None and amount1_in is None and amount0_out is None and amount1_out is None:
            return True
        elif amount0_in is None and amount1_in is not None and amount0_out is None and amount1_out is None:
            return False
        elif amount0_in is None and amount1_in is None and amount0_out is None and amount1_out is not None:
            return True
        elif amount0_in is None and amount1_in is None and amount0_out is not None and amount1_out is None:
            return False
        else:
            raise AmountNoneError("only one amount should be not None for a swap")

    @staticmethod
    def is_exact_input(
        amount0_in: int | None, amount0_out: int | None, amount1_in: int | None, amount1_out: int | None
    ) -> bool:
        """
        Check if the swap set the amount of tokens to input, or to output.
        """
        if amount0_in is not None and amount1_in is None and amount0_out is None and amount1_out is None:
            return True
        elif amount0_in is None and amount1_in is not None and amount0_out is None and amount1_out is None:
            return True
        elif amount0_in is None and amount1_in is None and amount0_out is None and amount1_out is not None:
            return False
        elif amount0_in is None and amount1_in is None and amount0_out is not None and amount1_out is None:
            return False
        else:
            raise AmountNoneError("only one amount should be not None for a swap")

    # ------------------------------------------------------------
    # LP static methods
    # These functions work with decimal numbers, not large integers
    # ------------------------------------------------------------

    # Not used anymore
    @staticmethod
    def _get_position(pool_name: str, tick_lower: int, tick_upper: int, wallet: Wallet) -> LPTokenUniv3:
        for token in wallet.get_erc721_tokens():
            if isinstance(token, LPTokenUniv3) and (token.pool_name == pool_name):
                if token.tick_lower == tick_lower and token.tick_upper == tick_upper:
                    return token
        else:
            raise ValueError("LP position not found")

    @staticmethod
    def get_token_id(agent_name: str, pool_name: str, tick_lower: int, tick_upper: int) -> str:
        assert tick_lower < tick_upper, "tick_lower should be stritcly lower than tick_upper"
        return f"{agent_name}_{pool_name}_{tick_lower}_{tick_upper}"

    @staticmethod
    def _get_lp_token(wallet: Wallet, token_id: str, action_name: str | None) -> LPTokenUniv3:
        nft_lp = wallet.get_erc721_token(token_id, action_name)
        if not isinstance(nft_lp, LPTokenUniv3):
            raise ValueError(
                "token_id does not correspond to a UniswapV3 LP position, is the token_id not globally unique?"
            )
        return nft_lp

    # ------------------------------------------------------------
    # LEGACY UNUSED METHODS
    # ------------------------------------------------------------

    @staticmethod
    def get_swap_amount_out(zero_for_one: bool, amount0_v: float, amount1_v: float, amount_in: float) -> float:
        """
        Compute the amount out of a swap, given the amount in and the direction of the swap.
        """
        if zero_for_one:
            amount_out = UniswapV3.constant_product_swap(amount1_v, amount0_v, amount_in)
        else:
            amount_out = UniswapV3.constant_product_swap(amount0_v, amount1_v, amount_in)
        return amount_out

    @staticmethod
    def get_post_swap_price(zero_for_one: bool, amount0_v: float, amount1_v: float, amount_in: float) -> float:
        """
        Compute the price after a swap, given the direction of the swap, the amount in,
        and the initial virtual reserves.
        """
        l_square = amount0_v * amount1_v
        if zero_for_one:
            price = l_square / (amount0_v + amount_in) ** 2
        else:
            price = (amount1_v + amount_in) ** 2 / l_square
        return price

    @staticmethod
    def get_virtual_reserves(liquidity: int, sqrt_price: float) -> tuple[float, float]:
        amount0_v = liquidity / sqrt_price
        amount1_v = liquidity * sqrt_price
        return amount0_v, amount1_v

    @staticmethod
    def constant_product_swap(x: float, y: float, dy: float) -> float:
        """
        compute the amount outputed by a swap using constant product rule
        ----------
        x : virtual amount x
        y : virtual amount y
        dy : amount inputed to the swap
        ----------
        dx : amount outputed by the swap
        """
        new_x = (x * y) / (y + dy)
        dx = x - new_x
        return dx
