import logging
import math
from decimal import Decimal
from typing import Dict, Optional, Sequence, Tuple

import numpy as np
from nqs_pycore import LPTokenUniv3, Wallet

from nqs_sdk_extension.constants import CAP_FEES_TO_LVR, PROFIT_MULTIPLICATOR
from nqs_sdk_extension.observer import DEFAULT_DECIMALS, ABCObserver, SingleObservable
from nqs_sdk_extension.observer.metric_names import Uniswapv3Metrics
from nqs_sdk_extension.observer.protocol.amm_utils import uniswap_v3_il  # type: ignore
from nqs_sdk_extension.observer.protocol.buffer import TimeSeriesBuffer
from nqs_sdk_extension.observer.protocol.protocol_observer import ProtocolObserver
from nqs_sdk_extension.observer.protocol.token_metrics import TokenMetricsUniv3
from nqs_sdk_extension.observer.utils import add_position_to_metric_name
from nqs_sdk_extension.protocol import UniswapV3
from nqs_sdk_extension.protocol.amm.uniswapv3.events import Burn, Collect, Create, Mint, Swap, Update
from nqs_sdk_extension.protocol.amm.uniswapv3.sqrt_price_math import SqrtPriceMath
from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.protocol.amm.uniswapv3.utils import lp_from_liquidity_to_amount0_amount1
from nqs_sdk_extension.state.erc721 import StateERC721
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.uniswap import SwapTransactionUniv3


class UniswapV3Observer(ProtocolObserver):
    def __init__(self, protocol: UniswapV3) -> None:
        super().__init__()
        self.amm: UniswapV3 = protocol
        # variables updated from events in batch mode
        # volumes in ONLY and AFTER fees
        self.total_volume0 = 0
        self.total_volume1 = 0
        self.total_volume_num = 0
        self.total_fee0 = 0
        self.total_fee1 = 0
        self.total_fee_num = 0
        # variables used to compute history dependent metrics
        self.buffer = TimeSeriesBuffer()
        self.tokens_metrics: dict[str, TokenMetricsUniv3] = {}
        # arbitrage stuffs
        self.arbitrage_prices: tuple[float, float] = (0, 0)
        # logger
        self.logger = logging.getLogger("UniswapV3ObserverLogger")

    def set_environment(self, observable_id: str, env_observers: Optional[Dict[str, ABCObserver]]) -> None:
        if env_observers is None:
            raise ValueError("Uniswap observability needs to be provided with environment observers")
        self._observer_id = observable_id
        self.metric_names = Uniswapv3Metrics(self._observer_id, self.amm.symbol0, self.amm.symbol1)

    def get_all_observables(self, block_number: int, block_timestamp: int) -> dict[str, SingleObservable]:
        new_observables: dict[str, SingleObservable] = {}
        # compute market spot
        market_spot = self.spot_oracle.get_token_numeraire_spot([self.amm.symbol0, self.amm.symbol1], block_timestamp)
        # update internal state
        self.update_from_protocol_events(market_spot)
        # add observables
        new_observables.update(self._get_pool_dex_spot())
        new_observables.update(self._get_pool_liquidity())
        new_observables.update(self._get_pool_holdings(market_spot))
        new_observables.update(self._get_pool_volumes())
        new_observables.update(self._get_pool_fees())
        new_observables.update(self._get_current_tick())
        return new_observables

    def get_agent_observables(
        self, block_number: int, block_timestamp: int, wallet: Wallet
    ) -> dict[str, SingleObservable]:
        tokens = wallet.get_erc721_tokens_for_pool_name(self.amm.name)
        market_spot = self.spot_oracle.get_token_numeraire_spot([self.amm.symbol0, self.amm.symbol1], block_timestamp)
        erc721_observables: dict[str, SingleObservable] = {}
        # observables per position
        for token in tokens:
            token_observables = self._get_individual_erc721_observables(token, market_spot)
            erc721_observables.update(**token_observables)
        # observables aggregated
        if tokens:
            aggregated_observables = self._get_aggregated_erc721_observables(tokens, erc721_observables)
            erc721_observables.update(**aggregated_observables)
        return erc721_observables

    def update_from_protocol_events(self, market_spot: dict[Tuple[str, str], float]) -> None:
        events = self.amm.events_ready_to_collect
        if len(events) == 0:
            return None
        # update internal state
        self._update_volumes_and_fees(events, market_spot)
        # update internal timeseries buffer
        self._update_timeseries_buffer(events)
        # update token metrics
        self._update_token_metrics(events)
        # clear events
        self.amm.events_ready_to_collect.clear()
        # clear buffer (if needed)
        self.buffer.flush()  # TODO: align with observation grid

    def flush_buffer(self) -> None:
        self.buffer.flush_to_last_observation()

    def agents_id_to_update(self) -> list[str]:
        return []

    def get_token_metrics(self, token_id: str) -> TokenMetricsUniv3:
        try:
            return self.tokens_metrics[token_id]
        except KeyError:
            raise ValueError("Token does not exist")

    # ----------------------------------------
    # private methods
    # ----------------------------------------
    def _update_token_metrics(self, events: list[Swap | Mint | Burn | Collect | Create | Update]) -> None:
        # update token events from protocol events
        for event in events:
            if isinstance(event, Collect):
                self.logger.debug(f"Collect event: {event}")
                try:
                    self.tokens_metrics[event.token_id].update_from_collect_event(event.amount0, event.amount1)
                except KeyError:
                    raise ValueError("Token does not exist")
            elif isinstance(event, Create):
                self.logger.debug(f"Create event: {event}")
                if event.token_id in self.tokens_metrics.keys():
                    raise ValueError("Token already exists")
                market_spot_all = self.spot_oracle.get_token_numeraire_spot([self.amm.symbol1], event.block_timestamp)
                market_spot = market_spot_all[(self.amm.symbol1, self.spot_oracle.numeraire)]
                price_lower = TickMath.tick_to_price(event.tick_lower, self.amm.decimals0, self.amm.decimals1)
                price_upper = TickMath.tick_to_price(event.tick_upper, self.amm.decimals0, self.amm.decimals1)
                price = TickMath.sqrt_price_x96_to_price(event.sqrt_price_x96, self.amm.decimals0, self.amm.decimals1)
                amount0, amount1 = lp_from_liquidity_to_amount0_amount1(
                    np.sqrt(price), np.sqrt(price_lower), np.sqrt(price_upper), event.amount * self.amm.factor_liquidity
                )
                if amount0 is None or amount1 is None:
                    raise ValueError("Amounts are None")  # To handle mypy
                token_metrics = TokenMetricsUniv3(
                    token_id=event.token_id,
                    tick_lower=event.tick_lower,
                    tick_upper=event.tick_upper,
                    price_lower=price_lower,
                    price_upper=price_upper,
                    block_number=event.block_number,
                    liquidity=event.amount,
                    initial_amount0=amount0,
                    initial_amount1=amount1,
                    factor_liquidity=self.amm.factor_liquidity,
                    price=TickMath.sqrt_price_x96_to_price(
                        event.sqrt_price_x96, self.amm.decimals0, self.amm.decimals1
                    ),
                    market_spot=market_spot,
                )
                self.tokens_metrics[event.token_id] = token_metrics
            elif isinstance(event, Update):
                self.logger.debug(f"Update event: {event}")
                market_spot_all = self.spot_oracle.get_token_numeraire_spot([self.amm.symbol1], event.block_timestamp)
                market_spot = market_spot_all[(self.amm.symbol1, self.spot_oracle.numeraire)]
                try:
                    self.tokens_metrics[event.token_id].update_from_update_event(
                        block_number=event.block_number,
                        delta_amount=event.delta_amount,
                        price=TickMath.sqrt_price_x96_to_price(
                            event.sqrt_price_x96, self.amm.decimals0, self.amm.decimals1
                        ),
                        market_spot=market_spot,
                    )
                except KeyError:
                    raise ValueError("Token does not exist")
        return None

    def _get_individual_erc721_observables(
        self, token: StateERC721, market_spot: dict[Tuple[str, str], float]
    ) -> dict[str, SingleObservable]:
        if not isinstance(token, LPTokenUniv3):
            raise ValueError("UniswapV3Observer can only observe LPTokenUniv3")
        token_observables: dict[str, SingleObservable] = {}
        # add observables
        token_observables.update(self._get_single_token_static_ptf_value(token, market_spot))
        token_observables.update(self._get_single_token_liquidity(token))
        token_observables.update(self._get_single_token_pl(token))
        token_observables.update(self._get_single_token_il(token, market_spot))
        token_observables.update(self._get_single_token_fees(token, market_spot))
        token_observables.update(self._get_single_token_lvr(token, market_spot))
        token_observables.update(self._get_single_token_bounds_price(token))
        token_observables.update(self._get_single_token_amounts_and_greeks(token))
        return token_observables

    def _get_aggregated_erc721_observables(
        self, tokens: list[StateERC721], erc721_observables: dict[str, SingleObservable]
    ) -> dict[str, SingleObservable]:
        agg_observables: dict[str, SingleObservable] = {}
        agg_observables.update(self._aggregate_tokens_static_ptf_value(erc721_observables, tokens))
        agg_observables.update(self._aggregate_tokens_il(erc721_observables, tokens))
        agg_observables.update(self._aggregate_tokens_pl(erc721_observables, tokens))
        agg_observables.update(self._aggregate_tokens_current_value(erc721_observables, tokens))
        agg_observables.update(self._aggregate_tokens_lvr(erc721_observables, tokens))
        agg_observables.update(self._aggregate_tokens_total_fees(erc721_observables, tokens))
        agg_observables.update(self._aggregate_tokens_fees_collected(erc721_observables, tokens))
        agg_observables.update(self._aggregate_tokens_fees_not_collected(erc721_observables, tokens))
        agg_observables.update(self._aggregate_tokens_liquidity(erc721_observables, tokens))
        agg_observables.update(self._aggregate_tokens_active_liquidity(erc721_observables, tokens))
        agg_observables.update(self._aggregate_tokens_amounts(erc721_observables, tokens))
        agg_observables.update(self._aggregate_tokens_greeks(erc721_observables, tokens))

        # add the uncollected fees to the total value of the position
        agg_observables[self.metric_names.net_position].value += agg_observables[
            self.metric_names.fees_not_collected_num
        ].value
        return agg_observables

    def _update_volumes_and_fees(
        self, events: list[Swap | Mint | Burn | Collect | Create | Update], market_spot: dict[Tuple[str, str], float]
    ) -> None:
        for event in events:
            if isinstance(event, Swap):
                if event.zero_for_one:
                    # compute volume and fees in token0 units
                    fee0 = event.fee_amount
                    volume0 = event.amount0 - fee0  # volume AFTER fees
                    # update total volume and fees
                    spot0num = market_spot[(self.amm.symbol0, self.spot_oracle.numeraire)]
                    self.total_volume0 += volume0
                    self.total_fee0 += fee0
                    self.total_volume_num += int(
                        Decimal(volume0).scaleb(-self.amm.decimals0) * Decimal(spot0num).scaleb(self.numeraire_decimals)
                    )
                    self.total_fee_num += int(
                        Decimal(fee0).scaleb(-self.amm.decimals0) * Decimal(spot0num).scaleb(self.numeraire_decimals)
                    )
                    self.logger.debug(f"Swap event zero for one: volume={volume0} and fee={fee0}")
                else:
                    # compute volume and fees in token1 units
                    fee1 = event.fee_amount
                    volume1 = event.amount1 - fee1  # volume AFTER fees
                    # update total volume and fees
                    spot1num = market_spot[(self.amm.symbol1, self.spot_oracle.numeraire)]
                    self.total_volume1 += volume1
                    self.total_fee1 += fee1
                    self.total_volume_num += int(
                        Decimal(volume1).scaleb(-self.amm.decimals1) * Decimal(spot1num).scaleb(self.numeraire_decimals)
                    )
                    self.total_fee_num += int(
                        Decimal(fee1).scaleb(-self.amm.decimals1) * Decimal(spot1num).scaleb(self.numeraire_decimals)
                    )
                    self.logger.debug(f"Swap event one for zero: volume={volume1} and fee={fee1}")
        return None

    def _update_timeseries_buffer(self, events: list[Swap | Mint | Burn | Collect | Create | Update]) -> None:
        # get only one (the last) transaction per block - only Swaps or Mints
        ordered_events = {event.block_number: event for event in events if isinstance(event, (Swap, Mint))}
        for event in ordered_events.values():
            # check here if buffer is updatable to avoid computing the price for nothing
            if self.buffer.updatable(event.block_number):
                price = TickMath.sqrt_price_x96_to_price(event.sqrt_price_x96, self.amm.decimals0, self.amm.decimals1)
                self.buffer.update_from_swap_event(
                    price=price, block_number=event.block_number, block_timestamp=event.block_timestamp
                )

    # ----------------------------------------
    # Pool metrics calculation
    # ----------------------------------------

    def _get_pool_liquidity(self) -> dict[str, SingleObservable]:
        return {
            # TODO fix this
            self.metric_names.pool_liquidity: SingleObservable(self.amm.liquidity, int(self.amm.liquidity_decimals))
        }

    def _get_current_tick(self) -> dict[str, SingleObservable]:
        return {self.metric_names.current_tick: SingleObservable(self.amm.tick, 0)}

    def _get_pool_dex_spot(self) -> dict[str, SingleObservable]:
        spot_price = TickMath.sqrt_price_x96_to_price(self.amm.sqrt_price_x96, self.amm.decimals0, self.amm.decimals1)
        # arbitrary: we report the spot with 18 decimals, as we do for the spot_oracle
        return {
            self.metric_names.spot: SingleObservable(
                int(Decimal(spot_price).scaleb(DEFAULT_DECIMALS)), DEFAULT_DECIMALS
            )
        }

    def _get_pool_holdings(self, market_spot: dict[Tuple[str, str], float]) -> dict[str, SingleObservable]:
        # compute pool holdings from the liquidity distribution -> SLOW
        liquidity: int = 0
        holdings0: int = 0
        holdings1: int = 0
        sqrt_price = TickMath.sqrt_price_x96_to_sqrt_price(
            self.amm.sqrt_price_x96, self.amm.decimals0, self.amm.decimals1
        )
        for i in range(len(self.amm.tickSet) - 1):
            t_lower = self.amm.tickSet[i]
            t_upper = self.amm.tickSet[i + 1]
            sqrt_price_lower = TickMath.tick_to_price(t_lower, self.amm.decimals0, self.amm.decimals1) ** 0.5
            sqrt_price_upper = TickMath.tick_to_price(t_upper, self.amm.decimals0, self.amm.decimals1) ** 0.5
            tick = self.amm.ticks[t_lower]
            liquidity += tick.liquidity_net
            amount = liquidity * self.amm.factor_liquidity
            amount0, amount1 = lp_from_liquidity_to_amount0_amount1(
                sqrt_price, sqrt_price_lower, sqrt_price_upper, amount
            )
            # converting to int the values that have been processed as floats -
            # TODO consider changing UniswapV3.lp_from_liquidity_to_amount0_amount1
            if amount0 is None or amount1 is None:
                raise ValueError("Amounts are None")  # To handle mypy
            holdings0 += int(Decimal(amount0).scaleb(self.amm.decimals0))
            holdings1 += int(Decimal(amount1).scaleb(self.amm.decimals1))
        # final liquidity should be zero
        if liquidity + self.amm.ticks[t_upper].liquidity_net != 0:
            raise ValueError("Net liquidity does not sum to zero")
        # compute TVL
        tvl_num = int(
            Decimal(holdings0).scaleb(-self.amm.decimals0)
            * Decimal(market_spot[(self.amm.symbol0, self.spot_oracle.numeraire)]).scaleb(self.numeraire_decimals)
        ) + int(
            Decimal(holdings1).scaleb(-self.amm.decimals1)
            * Decimal(market_spot[(self.amm.symbol1, self.spot_oracle.numeraire)]).scaleb(self.numeraire_decimals)
        )
        return {
            self.metric_names.holding0: SingleObservable(holdings0, self.amm.decimals0),
            self.metric_names.holding1: SingleObservable(holdings1, self.amm.decimals1),
            self.metric_names.tvl_num: SingleObservable(tvl_num, self.numeraire_decimals),
        }

    def _get_pool_volumes(self) -> dict[str, SingleObservable]:
        volumes_observables: dict[str, SingleObservable] = {}
        volumes_observables.update(
            {self.metric_names.volume0: SingleObservable(self.total_volume0, self.amm.decimals0)}
        )
        volumes_observables.update(
            {self.metric_names.volume1: SingleObservable(self.total_volume1, self.amm.decimals1)}
        )
        volumes_observables.update(
            {self.metric_names.volume_num: SingleObservable(self.total_volume_num, self.numeraire_decimals)}
        )
        return volumes_observables

    def _get_pool_fees(self) -> dict[str, SingleObservable]:
        fees_observables: dict[str, SingleObservable] = {}
        fees_observables.update({self.metric_names.fees0: SingleObservable(self.total_fee0, self.amm.decimals0)})
        fees_observables.update({self.metric_names.fees1: SingleObservable(self.total_fee1, self.amm.decimals1)})
        fees_observables.update(
            {self.metric_names.total_fees_pool: SingleObservable(self.total_fee_num, self.numeraire_decimals)}
        )
        return fees_observables

    # ----------------------------------------
    # Token metrics calculation
    # ----------------------------------------
    def _get_single_token_static_ptf_value(
        self, token: LPTokenUniv3, market_spot: dict[Tuple[str, str], float]
    ) -> dict[str, SingleObservable]:
        try:
            token_metrics = self.tokens_metrics[token.token_id]
        except KeyError:
            raise ValueError("Token does not exist")

        initial_amount0 = token_metrics.initial_amount0
        initial_amount1 = token_metrics.initial_amount1
        current_price = TickMath.sqrt_price_x96_to_price(
            self.amm.sqrt_price_x96, self.amm.decimals0, self.amm.decimals1
        )

        static_value_metric_name = add_position_to_metric_name(self.metric_names.static_ptf_value, token.token_id)
        single_token_static_ptf_value = initial_amount0 * current_price + initial_amount1
        # adjust for the numéraire point-in-time
        single_token_static_ptf_value *= market_spot[(self.amm.symbol1, self.spot_oracle.numeraire)]
        return {
            static_value_metric_name: SingleObservable(
                int(single_token_static_ptf_value * 10**self.numeraire_decimals), self.numeraire_decimals
            )
        }

    def _get_single_token_pl(self, token: LPTokenUniv3) -> dict[str, SingleObservable]:
        try:
            token_metrics = self.tokens_metrics[token.token_id]
        except KeyError:
            raise ValueError("Token does not exist")
        abs_pl_metric_name = add_position_to_metric_name(self.metric_names.abs_permanent_loss, token.token_id)
        return {abs_pl_metric_name: SingleObservable(token_metrics.abs_pl_num, self.numeraire_decimals)}

    def _get_single_token_il(
        self, token: LPTokenUniv3, market_spot: dict[Tuple[str, str], float]
    ) -> dict[str, SingleObservable]:
        try:
            token_metrics = self.tokens_metrics[token.token_id]
        except KeyError:
            raise ValueError("Token does not exist")
        min_price = token_metrics.price_lower
        max_price = token_metrics.price_upper
        # last liquidity value in token_metrics should match the one in the ERC721 token
        assert math.isclose(token_metrics.liquidity, token.liquidity), "Liquidity values are not close enough"
        current_price = TickMath.sqrt_price_x96_to_price(
            self.amm.sqrt_price_x96, self.amm.decimals0, self.amm.decimals1
        )
        abs_il_vec = [0]
        position_value_vec = [0]
        rel_il_vec = [0]
        for _, price, liquidity in iter(token_metrics.il_open_positions):
            # we can use the float values and convert them at the end in integer representation.
            # this is risk-free as these values are not stored in the protocol
            rel_il, abs_il, position_value = uniswap_v3_il(
                min_price, max_price, price, current_price, liquidity * self.amm.factor_liquidity
            )
            # adjust for the numéraire point-in-time
            abs_il *= market_spot[(self.amm.symbol1, self.spot_oracle.numeraire)]
            position_value *= market_spot[(self.amm.symbol1, self.spot_oracle.numeraire)]
            abs_il_vec.append(abs_il)
            rel_il_vec.append(rel_il)
            position_value_vec.append(position_value)
        # aggregate values
        abs_il = np.sum(abs_il_vec)
        position_value = np.sum(position_value_vec)
        portfolio_value = np.sum(np.array(position_value_vec) / (1.0 + np.array(rel_il_vec)))
        perc_il = 100 * (position_value / portfolio_value - 1.0) if token_metrics.il_open_positions else 0
        # adjust for the numéraire ex-post ALREADY DONE BEFORE !!!
        # position_value *= market_spot[(self.amm.symbol1, self.spot_oracle.numeraire)]
        # abs_il *= market_spot[(self.amm.symbol1, self.spot_oracle.numeraire)]
        # prepare metrics names
        perc_metric_name = add_position_to_metric_name(self.metric_names.perc_impermanent_loss, token.token_id)
        abs_metric_name = add_position_to_metric_name(self.metric_names.abs_impermanent_loss, token.token_id)
        current_value_metric_name = add_position_to_metric_name(self.metric_names.net_position, token.token_id)
        return {
            perc_metric_name: SingleObservable(int(perc_il * 10**DEFAULT_DECIMALS), DEFAULT_DECIMALS),
            abs_metric_name: SingleObservable(int(abs_il * 10**self.numeraire_decimals), self.numeraire_decimals),
            current_value_metric_name: SingleObservable(
                int(position_value * 10**self.numeraire_decimals), self.numeraire_decimals
            ),
        }

    def _get_single_token_lvr(
        self, token: LPTokenUniv3, market_spot: dict[Tuple[str, str], float]
    ) -> dict[str, SingleObservable]:
        try:
            token_metrics: TokenMetricsUniv3 = self.tokens_metrics[token.token_id]
            token_metrics.update_lvr_from_buffer(self.buffer)
            lvr = token_metrics.lvr
        except KeyError:
            raise ValueError("Token does not exist")
        lvr = lvr * market_spot[(self.amm.symbol1, self.spot_oracle.numeraire)]
        lvr_name = add_position_to_metric_name(self.metric_names.loss_versus_rebalancing, token.token_id)
        _, _, _, _, total_fees_not_collected, total_fees_collected = self._compute_fees(token, market_spot)
        total_fees = (total_fees_not_collected + total_fees_collected) / 10**self.numeraire_decimals
        if lvr == 0.0:
            total_fees_relative_to_lvr = 0.0
        else:
            total_fees_relative_to_lvr = 100.0 * total_fees / lvr
        total_fees_relative_to_lvr = min(total_fees_relative_to_lvr, CAP_FEES_TO_LVR)
        total_fees_relative_to_lvr_name = add_position_to_metric_name(
            self.metric_names.total_fees_relative_to_lvr, token.token_id
        )
        # we can use the float values and convert them at the end in integer representation.
        # this is risk-free as these values are not stored in the protocol
        return {
            lvr_name: SingleObservable(int(lvr * 10**self.numeraire_decimals), self.numeraire_decimals),
            total_fees_relative_to_lvr_name: SingleObservable(
                int(total_fees_relative_to_lvr * 10**DEFAULT_DECIMALS), DEFAULT_DECIMALS
            ),
        }

    def _get_single_token_fees(
        self, token: LPTokenUniv3, market_spot: dict[Tuple[str, str], float]
    ) -> dict[str, SingleObservable]:
        (
            fee_collected0,
            fee_collected1,
            fees_not_collected0,
            fees_not_collected1,
            total_fees_not_collected,
            total_fees_collected,
        ) = self._compute_fees(token, market_spot)
        fee_observables: dict[str, SingleObservable] = {}

        metric_name = add_position_to_metric_name(self.metric_names.fees_collected0, token.token_id)
        fee_observables.update({metric_name: SingleObservable(fee_collected0, self.amm.decimals0)})
        metric_name = add_position_to_metric_name(self.metric_names.fees_collected1, token.token_id)
        fee_observables.update({metric_name: SingleObservable(fee_collected1, self.amm.decimals1)})

        metric_name = add_position_to_metric_name(self.metric_names.fees_collected_num, token.token_id)
        fee_observables.update({metric_name: SingleObservable(total_fees_collected, self.numeraire_decimals)})

        metric_name = add_position_to_metric_name(self.metric_names.fees_not_collected0, token.token_id)
        fee_observables.update({metric_name: SingleObservable(fees_not_collected0, self.amm.decimals0)})
        metric_name = add_position_to_metric_name(self.metric_names.fees_not_collected1, token.token_id)
        fee_observables.update({metric_name: SingleObservable(fees_not_collected1, self.amm.decimals1)})

        metric_name = add_position_to_metric_name(self.metric_names.fees_not_collected_num, token.token_id)
        fee_observables.update({metric_name: SingleObservable(total_fees_not_collected, self.numeraire_decimals)})

        metric_name = add_position_to_metric_name(self.metric_names.total_fees, token.token_id)
        fee_observables.update(
            {metric_name: SingleObservable(total_fees_not_collected + total_fees_collected, self.numeraire_decimals)}
        )
        return fee_observables

    def _compute_fees(self, token: LPTokenUniv3, market_spot: dict[Tuple[str, str], float]) -> tuple:
        spot0num = market_spot[(self.amm.symbol0, self.spot_oracle.numeraire)]
        spot1num = market_spot[(self.amm.symbol1, self.spot_oracle.numeraire)]

        # fees collected in token0 and token1 units
        fee_collected0 = self.tokens_metrics[token.token_id].fee_collected0  # already in token units
        fee_collected1 = self.tokens_metrics[token.token_id].fee_collected1  # already in token units

        # fees not collected in token0 and token1 units
        amount_owed0, amount_owed1 = self.amm.get_total_tokens_owed(token)
        fees_not_collected0 = amount_owed0
        fees_not_collected1 = amount_owed1

        # total fees not collected in numéraire units
        total_fees_not_collected = int(
            Decimal(fees_not_collected0).scaleb(-self.amm.decimals0) * Decimal(spot0num).scaleb(self.numeraire_decimals)
            + Decimal(fees_not_collected1).scaleb(-self.amm.decimals1)
            * Decimal(spot1num).scaleb(self.numeraire_decimals)
        )

        # total fees in numéraire units
        total_fees_collected = int(
            Decimal(fee_collected0).scaleb(-self.amm.decimals0) * Decimal(spot0num).scaleb(self.numeraire_decimals)
            + Decimal(fee_collected1).scaleb(-self.amm.decimals1) * Decimal(spot1num).scaleb(self.numeraire_decimals)
        )

        return (
            fee_collected0,
            fee_collected1,
            fees_not_collected0,
            fees_not_collected1,
            total_fees_not_collected,
            total_fees_collected,
        )

    def _get_single_token_liquidity(self, token: LPTokenUniv3) -> dict[str, SingleObservable]:
        liquidity_observables: dict[str, SingleObservable] = {}
        # position liquidity
        metric_name = add_position_to_metric_name(self.metric_names.liquidity, token.token_id)
        liquidity = token.liquidity
        liquidity_observables.update({metric_name: SingleObservable(liquidity, int(self.amm.liquidity_decimals))})
        # active liquidity
        metric_name = add_position_to_metric_name(self.metric_names.active_liquidity, token.token_id)
        is_active = (token.tick_lower <= self.amm.tick) and (self.amm.tick < token.tick_upper)
        active_liquidity = liquidity if is_active else 0
        liquidity_observables.update(
            {metric_name: SingleObservable(active_liquidity, int(self.amm.liquidity_decimals))}
        )
        return liquidity_observables

    def _get_single_token_bounds_price(self, token: LPTokenUniv3) -> dict[str, SingleObservable]:
        bounds_observables: dict[str, SingleObservable] = {}
        try:
            price_lower = self.tokens_metrics[token.token_id].price_lower
            price_upper = self.tokens_metrics[token.token_id].price_upper
        except KeyError:
            price_lower = TickMath.tick_to_price(token.tick_lower, self.amm.decimals0, self.amm.decimals1)
            price_upper = TickMath.tick_to_price(token.tick_upper, self.amm.decimals0, self.amm.decimals1)
        lower_bound = price_lower
        upper_bound = price_upper
        # relative bounds
        metric_name = add_position_to_metric_name(self.metric_names.lower_bound_price, token.token_id)
        bounds_observables.update(
            {metric_name: SingleObservable(int(lower_bound * 10**DEFAULT_DECIMALS), DEFAULT_DECIMALS)}
        )
        metric_name = add_position_to_metric_name(self.metric_names.upper_bound_price, token.token_id)
        bounds_observables.update(
            {metric_name: SingleObservable(int(upper_bound * 10**DEFAULT_DECIMALS), DEFAULT_DECIMALS)}
        )
        return bounds_observables

    def _get_single_token_amounts_and_greeks(self, token: LPTokenUniv3) -> dict[str, SingleObservable]:
        amounts_observables: dict[str, SingleObservable] = {}
        sqrt_price = TickMath.sqrt_price_x96_to_sqrt_price(
            self.amm.sqrt_price_x96, self.amm.decimals0, self.amm.decimals1
        )
        sqrt_price_lower = TickMath.tick_to_price(token.tick_lower, self.amm.decimals0, self.amm.decimals1) ** 0.5
        sqrt_price_upper = TickMath.tick_to_price(token.tick_upper, self.amm.decimals0, self.amm.decimals1) ** 0.5
        # check that the liquidity is non-zero
        if token.liquidity == 0:
            amount0 = amount1 = 0.0
        else:
            # mint / burn event should be submitted with only one of the three flags set to True
            amount_float = token.liquidity * self.amm.factor_liquidity
            # compute the amount of token0 and token1 owned by a LP
            amount0_tmp, amount1_tmp = lp_from_liquidity_to_amount0_amount1(
                sqrt_price, sqrt_price_lower, sqrt_price_upper, amount_float
            )
            if amount0_tmp is None or amount1_tmp is None:
                raise ValueError("Amounts are None")
            amount0, amount1 = amount0_tmp, amount1_tmp
        metric_name0 = add_position_to_metric_name(self.metric_names.token_amount0, token.token_id)
        metric_name1 = add_position_to_metric_name(self.metric_names.token_amount1, token.token_id)
        # this is the same conversion used in the protocol logic, for consistency
        amounts_observables.update(
            {
                metric_name0: SingleObservable(int(amount0 / self.amm.factor_decimals0), self.amm.decimals0),
                metric_name1: SingleObservable(int(amount1 / self.amm.factor_decimals1), self.amm.decimals1),
            }
        )

        # Calculate Greeks
        current_price = TickMath.sqrt_price_x96_to_price(
            self.amm.sqrt_price_x96, self.amm.decimals0, self.amm.decimals1
        )
        price_lower = TickMath.tick_to_price(token.tick_lower, self.amm.decimals0, self.amm.decimals1)
        price_upper = TickMath.tick_to_price(token.tick_upper, self.amm.decimals0, self.amm.decimals1)

        # Only calculate Greeks if the position is active (in range)
        if price_lower <= current_price <= price_upper and token.liquidity > 0:
            # Delta: sensitivity to price changes
            # For a concentrated liquidity position, delta ≈ -amount0 / price + amount1
            delta = -amount0 / current_price + amount1

            # Gamma: second derivative of portfolio value with respect to price
            # For concentrated liquidity: gamma ≈ amount0 / price^2
            gamma = amount0 / (current_price**2) if current_price > 0 else 0

            # Theta: time decay (for LP positions, related to fee earning)
            # Simplified theta calculation based on fee rate and time
            fee_rate = self.amm.fee_tier / 1_000_000  # Convert from pips to decimal
            # Estimate theta as potential fee earnings per unit time
            theta = (amount0 * current_price + amount1) * fee_rate
        else:
            # Position is out of range
            delta = gamma = theta = 0.0

        # Add Greeks to observables
        delta_metric_name = add_position_to_metric_name(self.metric_names.delta, token.token_id)
        gamma_metric_name = add_position_to_metric_name(self.metric_names.gamma, token.token_id)
        theta_metric_name = add_position_to_metric_name(self.metric_names.theta, token.token_id)

        amounts_observables.update(
            {
                delta_metric_name: SingleObservable(int(delta * 10**DEFAULT_DECIMALS), DEFAULT_DECIMALS),
                gamma_metric_name: SingleObservable(int(gamma * 10**DEFAULT_DECIMALS), DEFAULT_DECIMALS),
                theta_metric_name: SingleObservable(int(theta * 10**DEFAULT_DECIMALS), DEFAULT_DECIMALS),
            }
        )

        return amounts_observables

    # ----------------------------------------
    # Aggregated metrics across all positions
    # ----------------------------------------

    @staticmethod
    def _aggregate_metric(
        metric_name: str, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> SingleObservable:
        metric_values = [
            erc721_observables[add_position_to_metric_name(metric_name, token.token_id)].value for token in tokens
        ]
        # every observable has the same decimals here. Get any of such observables
        decimals = erc721_observables[add_position_to_metric_name(metric_name, tokens[0].token_id)].decimals
        return SingleObservable(sum(metric_values), decimals)

    def _aggregate_tokens_lvr(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        total_fees = self._aggregate_metric(self.metric_names.total_fees, erc721_observables, tokens)
        total_lvr = self._aggregate_metric(self.metric_names.loss_versus_rebalancing, erc721_observables, tokens)
        if total_lvr.value == 0.0:
            total_fees_relative_to_lvr = 0.0
        else:
            total_fees_relative_to_lvr = 100 * total_fees.value / total_lvr.value
        total_fees_relative_to_lvr = min(total_fees_relative_to_lvr, CAP_FEES_TO_LVR)
        return {
            self.metric_names.loss_versus_rebalancing: total_lvr,
            self.metric_names.total_fees_relative_to_lvr: SingleObservable(
                int(total_fees_relative_to_lvr * 10**DEFAULT_DECIMALS), DEFAULT_DECIMALS
            ),
        }

    def _aggregate_tokens_static_ptf_value(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        total_static_ptf_value = self._aggregate_metric(self.metric_names.static_ptf_value, erc721_observables, tokens)
        return {self.metric_names.static_ptf_value: total_static_ptf_value}

    def _aggregate_tokens_il(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        total_il = self._aggregate_metric(self.metric_names.abs_impermanent_loss, erc721_observables, tokens)
        total_static_ptf_value = self._aggregate_metric(self.metric_names.static_ptf_value, erc721_observables, tokens)
        if total_static_ptf_value.value == 0.0:
            total_perc_il = 0.0
        else:
            total_perc_il = 100.0 * total_il.value / total_static_ptf_value.value
        return {
            self.metric_names.abs_impermanent_loss: total_il,
            self.metric_names.perc_impermanent_loss: SingleObservable(
                int(Decimal(total_perc_il).scaleb(DEFAULT_DECIMALS)),
                DEFAULT_DECIMALS,
            ),
        }

    def _aggregate_tokens_pl(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        total_pl = self._aggregate_metric(self.metric_names.abs_permanent_loss, erc721_observables, tokens)
        return {self.metric_names.abs_permanent_loss: total_pl}

    def _aggregate_tokens_current_value(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        current_holding = self._aggregate_metric(self.metric_names.net_position, erc721_observables, tokens)
        return {self.metric_names.net_position: current_holding}

    def _aggregate_tokens_total_fees(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        total_fees = self._aggregate_metric(self.metric_names.total_fees, erc721_observables, tokens)
        return {self.metric_names.total_fees: total_fees}

    def _aggregate_tokens_fees_collected(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        total_fees_collected = self._aggregate_metric(self.metric_names.fees_collected_num, erc721_observables, tokens)
        return {self.metric_names.fees_collected_num: total_fees_collected}

    def _aggregate_tokens_fees_not_collected(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        total_fees_not_collected = self._aggregate_metric(
            self.metric_names.fees_not_collected_num, erc721_observables, tokens
        )
        return {self.metric_names.fees_not_collected_num: total_fees_not_collected}

    def _aggregate_tokens_liquidity(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        total_liquidity = self._aggregate_metric(self.metric_names.liquidity, erc721_observables, tokens)
        return {self.metric_names.liquidity: total_liquidity}

    def _aggregate_tokens_active_liquidity(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        total_active_liquidity = self._aggregate_metric(self.metric_names.active_liquidity, erc721_observables, tokens)
        return {self.metric_names.active_liquidity: total_active_liquidity}

    def _aggregate_tokens_amounts(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        total_amount0 = self._aggregate_metric(self.metric_names.token_amount0, erc721_observables, tokens)
        total_amount1 = self._aggregate_metric(self.metric_names.token_amount1, erc721_observables, tokens)
        return {
            self.metric_names.token_amount0: total_amount0,
            self.metric_names.token_amount1: total_amount1,
        }

    def _aggregate_tokens_greeks(
        self, erc721_observables: dict[str, SingleObservable], tokens: list[StateERC721]
    ) -> dict[str, SingleObservable]:
        total_delta = self._aggregate_metric(self.metric_names.delta, erc721_observables, tokens)
        total_gamma = self._aggregate_metric(self.metric_names.gamma, erc721_observables, tokens)
        total_theta = self._aggregate_metric(self.metric_names.theta, erc721_observables, tokens)

        return {
            self.metric_names.delta: total_delta,
            self.metric_names.gamma: total_gamma,
            self.metric_names.theta: total_theta,
        }

    ######### arbitrage specific ##############################################################################
    def exists_arbitrage_opportunity(self, block_number: int, block_timestamp: int) -> bool:
        dex_spot_data = self._get_pool_dex_spot()[self.metric_names.spot]
        dex_spot = dex_spot_data.value / 10**dex_spot_data.decimals
        if dex_spot == 0:
            logging.warning(f"The dex spot is {0} for the pool {self.amm.name} at block {block_number}")
            return False

        spot_symbol = [(self.amm.symbol0, self.amm.symbol1)]
        market_spot = self.spot_oracle.get_selected_spots(spot_symbol, block_timestamp)[spot_symbol[0]]
        fee_tier = self.amm.fee_tier / 1_000_000
        if abs(dex_spot / market_spot - 1) > PROFIT_MULTIPLICATOR * fee_tier and self.amm.liquidity > 0:
            self.arbitrage_prices = (dex_spot, market_spot)
            return True
        else:
            self.arbitrage_prices = (-1, -1)
            return False

    def create_arbitrage_transactions(
        self, block_number: int, block_timestamp: int, arbitrageur_wallet: Wallet
    ) -> Sequence[ABCTransaction]:
        amount0_in, amount1_in = self._get_arbitrage_value()
        if amount0_in == 0 and amount1_in is None or amount0_in is None and amount1_in == 0:
            return []
        else:
            return [
                SwapTransactionUniv3(
                    block_number=block_number,
                    protocol_id=self._observer_id,
                    sender_wallet=arbitrageur_wallet,
                    amount0_in=amount0_in,
                    amount1_in=amount1_in,
                )
            ]

    def _get_arbitrage_value(self) -> tuple[int | None, int | None]:  # noqa
        if self.arbitrage_prices == (-1, -1):
            raise ValueError("There is no arbitrage opportunity, this function should not be called")
        liquidity_tolerance = 1
        arbitrage_size_alpha, arbitrage_size_beta = 0, 0
        arbitrage_size_alpha_tmp, arbitrage_size_beta_tmp = 0, 0
        fee_tier = self.amm.fee_tier / 1_000_000
        temporary_spot = self.arbitrage_prices[0]
        market_spot = self.arbitrage_prices[1]
        temporary_liquidity = self.amm.liquidity

        if (market_spot / temporary_spot - 1) < -fee_tier and temporary_liquidity > liquidity_tolerance:
            target_spot = market_spot * (1 + fee_tier)

            tick_down = self.amm.get_next_tick(
                tick=self.amm.tick,
                sqrt_price_ratio_x96=self.amm.sqrt_price_x96,
                zero_for_one=True,
            )

            current_ratio = TickMath.price_to_sqrt_price_x96(temporary_spot, self.amm.decimals0, self.amm.decimals1)

            while True:
                tick_ratio_down = TickMath.get_sqrt_ratio_at_tick(tick_down)
                target_ratio = TickMath.price_to_sqrt_price_x96(target_spot, self.amm.decimals0, self.amm.decimals1)
                if target_ratio >= tick_ratio_down:
                    arbitrage_size_alpha_tmp += SqrtPriceMath.get_amount0_delta_unsigned(
                        sqrt_ratio_a_x96=target_ratio,
                        sqrt_ratio_b_x96=current_ratio,
                        liquidity=temporary_liquidity,
                        round_up=True,
                    )
                    arbitrage_size_alpha = arbitrage_size_alpha_tmp
                    logging.debug("The pool " + f"{self.amm.name}" + " had enough liquidity to complete the arbitrage.")
                    return round(arbitrage_size_alpha / (1 - fee_tier)), None

                else:
                    if temporary_liquidity - self.amm.ticks[tick_down].liquidity_net < liquidity_tolerance:
                        logging.info(
                            "The pool "
                            + f"{self.amm.name}"
                            + " did not have enough liquidity to fully complete the arbitrage."
                        )
                        return round(arbitrage_size_alpha_tmp / (1 - fee_tier)), None

                    arbitrage_size_alpha_tmp += SqrtPriceMath.get_amount0_delta_unsigned(
                        sqrt_ratio_a_x96=tick_ratio_down,
                        sqrt_ratio_b_x96=current_ratio,
                        liquidity=temporary_liquidity,
                        round_up=True,
                    )
                    current_ratio = tick_ratio_down
                    temporary_liquidity = temporary_liquidity - self.amm.ticks[tick_down].liquidity_net
                    if self.amm.tickSet.bisect_left(tick_down) == 0:
                        assert temporary_liquidity <= liquidity_tolerance
                        logging.debug(
                            "The pool "
                            + f"{self.amm.name}"
                            + " did not have enough liquidity to fully complete the arbitrage."
                        )
                        return round(arbitrage_size_alpha_tmp / (1 - fee_tier)), None
                    else:
                        tick_down = self.amm.tickSet[self.amm.tickSet.bisect_left(tick_down) - 1]

        elif (market_spot / temporary_spot - 1) > fee_tier and temporary_liquidity > liquidity_tolerance:
            target_spot = market_spot * (1 - fee_tier)
            tick_up = self.amm.get_next_tick(
                tick=self.amm.tick,
                sqrt_price_ratio_x96=self.amm.sqrt_price_x96,
                zero_for_one=False,
            )
            current_ratio = TickMath.price_to_sqrt_price_x96(temporary_spot, self.amm.decimals0, self.amm.decimals1)
            while True:
                tick_ratio_up = TickMath.get_sqrt_ratio_at_tick(tick_up)
                target_ratio = TickMath.price_to_sqrt_price_x96(target_spot, self.amm.decimals0, self.amm.decimals1)
                if target_ratio <= tick_ratio_up:
                    arbitrage_size_beta_tmp += SqrtPriceMath.get_amount1_delta_unsigned(
                        sqrt_ratio_a_x96=current_ratio,
                        sqrt_ratio_b_x96=target_ratio,
                        liquidity=temporary_liquidity,
                        round_up=True,
                    )
                    arbitrage_size_beta = arbitrage_size_beta_tmp
                    logging.debug("The pool " + f"{self.amm.name}" + " had enough liquidity to complete the arbitrage.")
                    return None, round(arbitrage_size_beta / (1 - fee_tier))

                else:
                    if temporary_liquidity + self.amm.ticks[tick_up].liquidity_net < liquidity_tolerance:
                        logging.info(
                            "The pool "
                            + f"{self.amm.name}"
                            + " did not have enough liquidity to fully complete the arbitrage."
                        )
                        return None, round(arbitrage_size_beta_tmp / (1 - fee_tier))

                    arbitrage_size_beta_tmp += SqrtPriceMath.get_amount1_delta_unsigned(
                        sqrt_ratio_a_x96=current_ratio,
                        sqrt_ratio_b_x96=tick_ratio_up,
                        liquidity=temporary_liquidity,
                        round_up=True,
                    )
                    current_ratio = tick_ratio_up
                    temporary_liquidity = temporary_liquidity + self.amm.ticks[tick_up].liquidity_net
                    if self.amm.tickSet.bisect_right(tick_up) == len(self.amm.tickSet):
                        assert temporary_liquidity <= liquidity_tolerance
                        logging.debug(
                            "The pool "
                            + f"{self.amm.name}"
                            + " did not have enough liquidity to fully complete the arbitrage."
                        )
                        return None, round(arbitrage_size_beta_tmp / (1 - fee_tier))
                    else:
                        tick_up = self.amm.tickSet[self.amm.tickSet.bisect_right(tick_up)]

        return 0, None
