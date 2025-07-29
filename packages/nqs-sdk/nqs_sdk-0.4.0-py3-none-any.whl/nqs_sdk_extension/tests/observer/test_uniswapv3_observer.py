# type: ignore
import unittest
from unittest.mock import Mock

import numpy as np
from nqs_pycore import LPTokenUniv3

from nqs_sdk_extension.observer.metric_names import Uniswapv3Metrics
from nqs_sdk_extension.observer.protocol.token_metrics import TokenMetricsUniv3
from nqs_sdk_extension.observer.protocol.uniswapv3 import UniswapV3Observer
from nqs_sdk_extension.protocol import UniswapV3
from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.protocol.amm.uniswapv3.uniswap_v3 import Collect, Create, Swap, Update
from nqs_sdk_extension.state import StateUniv3
from nqs_sdk_extension.transaction.uniswap import TransactionHelperUniv3

tran_helper = TransactionHelperUniv3()


class TestProtocolMetrics(unittest.TestCase):
    def setUp(self):
        # create a state with fake values
        state = StateUniv3(
            id=0,
            name="fakeV3",
            block_number=0,
            block_timestamp=0,
            token0="0x0",
            token1="0x1",
            symbol0="USDC",
            symbol1="USDT",
            decimals0=18,
            decimals1=18,
            fee_tier=10_000,  # 1%
            liquidity=0,
            sqrt_price_x96=int(1 * 2**96),
            fee_growth_global_0_x128=0,
            fee_growth_global_1_x128=0,
            tick=0,
            ticks=[],  # empty list of ticks
        )
        # create mint transactions
        mint1 = tran_helper.create_mint_transaction(
            amount0=10_000 * 10**18,
            tick_lower=-100,
            tick_upper=100,
            block_number=0,
        )
        mint2 = tran_helper.create_mint_transaction(
            amount0=123_000 * 10**18,
            tick_lower=10,
            tick_upper=100,
            block_number=0,
        )
        mint3 = tran_helper.create_mint_transaction(
            amount1=777_000 * 10**18,
            tick_lower=-100,
            tick_upper=-10,
            block_number=0,
        )
        # create AMM and process mint transactions
        amm = UniswapV3(state=state)
        amm.process_transactions([mint1, mint2, mint3])
        self.amm = amm
        # create swap transactions
        swap0in_1 = tran_helper.create_swap_transaction(amount0_in=123 * 10**18, block_number=0)
        swap0in_2 = tran_helper.create_swap_transaction(amount0_in=45 * 10**18, block_number=0)
        swap1in_1 = tran_helper.create_swap_transaction(amount1_in=678 * 10**18, block_number=0)
        swap1in_2 = tran_helper.create_swap_transaction(amount1_in=90 * 10**18, block_number=0)
        self.swaps = [swap0in_1, swap0in_2, swap1in_1, swap1in_2]
        # prepare the spot oracle
        spot_oracle = Mock()
        spot_oracle.numeraire = "USD"
        spot_oracle.get_token_numeraire_spot.return_value = {("USDC", "USD"): 1.0, ("USDT", "USD"): 1.0}
        self.spot_oracle = spot_oracle
        # prepare the observer by setting it manually
        observer = UniswapV3Observer(protocol=self.amm)
        observer._observer_id = "fakeV3"
        observer.spot_oracle = spot_oracle
        observer.numeraire_decimals = 18
        observer.metric_names = Uniswapv3Metrics(observer._observer_id, "USDC", "USDT")
        self.observer = observer

    def test_get_pool_holdings(self):
        # collect total amounts minted from the events
        events = self.amm.events_ready_to_collect
        minted_amount0 = 0
        minted_amount1 = 0
        for event in events:
            minted_amount0 += event.amount0
            minted_amount1 += event.amount1
        # mock the spot
        market_spot = self.observer.spot_oracle.get_token_numeraire_spot([self.amm.symbol1], 0, 0)
        # get the pool holdings
        holdings = self.observer._get_pool_holdings(market_spot=market_spot)
        # check the results
        self.assertAlmostEqual(
            holdings['fakeV3.total_holdings:{token="USDC"}'].value
            / 10 ** holdings['fakeV3.total_holdings:{token="USDC"}'].decimals,
            minted_amount0 * 10**-18,
        )
        self.assertAlmostEqual(
            holdings['fakeV3.total_holdings:{token="USDT"}'].value
            / 10 ** holdings['fakeV3.total_holdings:{token="USDT"}'].decimals,
            minted_amount1 * 10**-18,
        )
        self.assertAlmostEqual(
            holdings["fakeV3.total_value_locked"].value / 10 ** holdings["fakeV3.total_value_locked"].decimals,
            (minted_amount0 + minted_amount1) * 10**-18,
        )

    def test_get_pool_volumes(self):
        self.amm.process_transactions(self.swaps)
        # estimate the volumes from the swaps
        volume0 = 0
        volume1 = 0
        fee = self.amm.fee_tier / 10**6
        for swap in self.swaps:
            if swap.amount0_in is not None:
                volume0 += swap.amount0_in * (1 - fee)
            elif swap.amount1_in is not None:
                volume1 += swap.amount1_in * (1 - fee)
            else:
                raise ValueError("Invalid swap transaction")
        volume_num = volume0 + volume1
        # update from events
        market_spot = self.observer.spot_oracle.get_token_numeraire_spot([self.amm.symbol0, self.amm.symbol1], 0, 0)
        self.observer.update_from_protocol_events(market_spot)
        # get the pool volumes
        volumes = self.observer._get_pool_volumes()
        # check the results
        self.assertAlmostEqual(volumes['fakeV3.total_volume:{token="USDC"}'].value, volume0)
        self.assertAlmostEqual(volumes['fakeV3.total_volume:{token="USDT"}'].value, volume1)
        self.assertAlmostEqual(volumes["fakeV3.total_volume_numeraire"].value, volume_num)

    def test_get_pool_fees(self):
        self.amm.process_transactions(self.swaps)
        # estimate the volumes from the swaps
        fee0 = 0
        fee1 = 0
        fee = self.amm.fee_tier / 10**6
        for swap in self.swaps:
            if swap.amount0_in is not None:
                fee0 += swap.amount0_in * fee
            elif swap.amount1_in is not None:
                fee1 += swap.amount1_in * fee
            else:
                raise ValueError("Invalid swap transaction")
        fee_num = fee0 + fee1
        # update from events
        market_spot = self.observer.spot_oracle.get_token_numeraire_spot([self.amm.symbol0, self.amm.symbol1], 0, 0)
        self.observer.update_from_protocol_events(market_spot)
        # get the pool volumes
        volumes = self.observer._get_pool_fees()
        # check the results
        self.assertAlmostEqual(volumes['fakeV3.total_fees:{token="USDC"}'].value, fee0)
        self.assertAlmostEqual(volumes['fakeV3.total_fees:{token="USDT"}'].value, fee1)
        self.assertAlmostEqual(volumes["fakeV3.total_fees"].value, fee_num)

    def test_get_pool_dex_spot(self):
        # nothing to test
        pass

    def test_get_pool_liquidity(self):
        # nothing to test
        pass


class TestLPTokenMetrics(unittest.TestCase):
    def setUp(self):
        amm = Mock()
        amm.sqrt_price_x96 = 1 * 2**96
        amm.decimals0 = 18
        amm.decimals1 = 18
        amm.liquidity_decimals = 18
        amm.factor_liquidity = 10**-18
        amm.tick = TickMath.price_to_tick(1.0, amm.decimals0, amm.decimals1)
        self.amm = amm
        # create LP tokens
        self.lp_token1 = LPTokenUniv3(
            pool_name="fakeV3",
            token_id="token1",
            tick_lower=TickMath.price_to_tick(0.90, amm.decimals0, amm.decimals1),
            tick_upper=TickMath.price_to_tick(1.10, amm.decimals0, amm.decimals1),
            liquidity=int(100 / amm.factor_liquidity),
            fee_growth_inside_0_last_x128=0,
            fee_growth_inside_1_last_x128=0,
            tokens_owed_0=0,
            tokens_owed_1=0,
        )
        self.lp_token2 = LPTokenUniv3(
            pool_name="fakeV3",
            token_id="token2",
            tick_lower=TickMath.price_to_tick(1.01, amm.decimals0, amm.decimals1),
            tick_upper=TickMath.price_to_tick(1.10, amm.decimals0, amm.decimals1),
            liquidity=int(200 / amm.factor_liquidity),
            fee_growth_inside_0_last_x128=0,
            fee_growth_inside_1_last_x128=0,
            tokens_owed_0=0,
            tokens_owed_1=0,
        )
        # prepare the spot oracle
        spot_oracle = Mock()
        spot_oracle.numeraire = "USD"
        spot_oracle.get_token_numeraire_spot.return_value = {("USDC", "USD"): 1.0, ("USDT", "USD"): 1.0}
        self.spot_oracle = spot_oracle
        # prepare the observer by setting it manually
        observer = UniswapV3Observer(protocol=self.amm)
        observer._observer_id = "fakeV3"
        observer.spot_oracle = spot_oracle
        observer.numeraire_decimals = 18
        observer.metric_names = Uniswapv3Metrics(observer._observer_id, "USDC", "USDT")
        self.observer = observer

    def test_get_single_token_liquidity(self):
        # get the token observables
        token_observables1 = self.observer._get_single_token_liquidity(self.lp_token1)
        token_observables2 = self.observer._get_single_token_liquidity(self.lp_token2)
        # check the results
        self.assertAlmostEqual(
            token_observables1['fakeV3.liquidity:{position="token1"}'].value,
            100 * 10 ** token_observables1['fakeV3.liquidity:{position="token1"}'].decimals,
        )
        self.assertAlmostEqual(
            token_observables1['fakeV3.active_liquidity:{position="token1"}'].value,
            100 * 10 ** token_observables1['fakeV3.active_liquidity:{position="token1"}'].decimals,
        )
        self.assertAlmostEqual(
            token_observables2['fakeV3.liquidity:{position="token2"}'].value,
            200 * 10 ** token_observables2['fakeV3.liquidity:{position="token2"}'].decimals,
        )
        self.assertEqual(token_observables2['fakeV3.active_liquidity:{position="token2"}'].value, 0)

    def test_get_single_token_bounds(self):
        # get the token observables
        token_observables1 = self.observer._get_single_token_bounds_price(self.lp_token1)
        token_observables2 = self.observer._get_single_token_bounds_price(self.lp_token2)
        # check the results
        self.assertAlmostEqual(
            token_observables1['fakeV3.lower_bound_price:{position="token1"}'].value
            / 10 ** token_observables1['fakeV3.lower_bound_price:{position="token1"}'].decimals,
            0.90,
            delta=0.01,
        )
        self.assertAlmostEqual(
            token_observables1['fakeV3.upper_bound_price:{position="token1"}'].value
            / 10 ** token_observables1['fakeV3.upper_bound_price:{position="token1"}'].decimals,
            1.10,
            delta=0.01,
        )
        self.assertAlmostEqual(
            token_observables2['fakeV3.lower_bound_price:{position="token2"}'].value
            / 10 ** token_observables2['fakeV3.lower_bound_price:{position="token2"}'].decimals,
            1.01,
            delta=0.01,
        )
        self.assertAlmostEqual(
            token_observables2['fakeV3.upper_bound_price:{position="token2"}'].value
            / 10 ** token_observables2['fakeV3.upper_bound_price:{position="token2"}'].decimals,
            1.10,
            delta=0.01,
        )


class TestBuffer(unittest.TestCase):
    def setUp(self):
        # mock AMM
        amm = Mock()
        amm.decimals0 = 18
        amm.decimals1 = 18
        self.amm = amm
        # mock events
        price1 = 1.0
        price2 = 3.0
        price3 = 2.0
        swap1 = Mock(spec=Swap)
        swap1.sqrt_price_x96, swap1.block_number = (price1) ** 0.5 * 2**96, 0
        swap2 = Mock(spec=Swap)
        swap2.sqrt_price_x96, swap2.block_number = (price2) ** 0.5 * 2**96, 24  # default block_step is 25
        swap3 = Mock(spec=Swap)
        swap3.sqrt_price_x96, swap3.block_number = (price3) ** 0.5 * 2**96, 25
        # suppose 1 block == 12 seconds
        swap1.block_timestamp, swap2.block_timestamp, swap3.block_timestamp = 0, 24 * 12, 25 * 12
        self.events = [swap1, swap2, swap3]
        # prepare the observer by setting it manually
        observer = UniswapV3Observer(protocol=self.amm)
        observer._observer_id = "fakeV3"
        self.observer = observer

    def test_update_timeseries_buffer(self):
        events = self.events
        self.observer._update_timeseries_buffer(events)
        # check the buffer
        buffer = self.observer.buffer
        self.assertEqual(buffer.last_block_number, 25)
        self.assertEqual(buffer.block_vec, [0, 25])
        np.testing.assert_almost_equal(np.array(buffer.price_vec), np.array([1.0, 2.0]))
        # buffer.dt_vec  # not tested
        # buffer.rets_vec  # not tested
        # buffer.rvol_vec  # not tested


class TestPerfTokenMetrics(unittest.TestCase):
    def setUp(self):
        amm = Mock()
        amm.symbol0 = "USDC"
        amm.symbol1 = "USDT"
        amm.decimals0 = 0
        amm.decimals1 = 0
        amm.factor_liquidity = 1
        amm.liquidity_decimals = 0
        amm.factor_decimals0 = 1
        amm.factor_decimals1 = 1
        amm.get_total_tokens_owed.return_value = 0, 0
        self.amm = amm
        # prepare buffer
        buffer = Mock()
        # prepare token metrics
        token_metrics_1 = TokenMetricsUniv3(
            token_id="X",
            tick_lower=-100,
            tick_upper=100,
            price_lower=0.9,
            price_upper=1.1,
            block_number=0,
            initial_amount0=100.0,
            initial_amount1=100.0,
            liquidity=100,
            factor_liquidity=1,
            price=1.0,
            market_spot=1.0,
        )
        self.tokens_metrics = {"X": token_metrics_1}
        # prepare the spot oracle
        spot_oracle = Mock()
        spot_oracle.numeraire = "USD"
        spot_oracle.get_token_numeraire_spot.return_value = {("USDC", "USD"): 1.0, ("USDT", "USD"): 1.0}
        self.spot_oracle = spot_oracle
        # prepare the observer by setting it manually
        observer = UniswapV3Observer(protocol=self.amm)
        observer._observer_id = "fakeV3"
        observer.spot_oracle = spot_oracle
        observer.metric_names = Uniswapv3Metrics(observer._observer_id, "USDC", "USDT")
        observer.buffer = buffer
        observer.numeraire_decimals = 18
        observer.tokens_metrics = self.tokens_metrics
        self.observer = observer

    def test_update_token_metrics(self):
        create_y = Create("Y", -100, 100, 0, 0, 100, 1)
        update_y = Update("Y", 1, 1, -100, 1)
        update_x = Update("X", 1, 1, -50, 1)
        collect_x = Collect("X", 1, 1, -100, 100, 2, 3)
        # try to update a token that does not exist
        with self.assertRaises(ValueError) as excinfo:
            self.observer._update_token_metrics([update_y])
            assert str(excinfo.value) == "Token does not exist"
        # create and update the token Y
        self.observer._update_token_metrics([create_y])
        self.assertEqual(self.observer.get_token_metrics("Y").liquidity, 100)
        self.observer._update_token_metrics([update_y])
        self.assertEqual(self.observer.get_token_metrics("Y").liquidity, 0)
        # update the token X
        self.observer._update_token_metrics([update_x])
        self.assertEqual(self.observer.get_token_metrics("X").liquidity, 50)
        # collect the token X
        self.observer._update_token_metrics([collect_x])
        self.assertEqual(self.observer.get_token_metrics("X").fee_collected0, 2)
        self.assertEqual(self.observer.get_token_metrics("X").fee_collected1, 3)

    def test_get_single_token_pl(self):
        # mock the token
        token = Mock()
        token.token_id = "X"
        # partially close a position
        update1 = Update("X", 1, 1, -50, 2.0**0.5 * 2**96)
        self.observer._update_token_metrics([update1])
        pl1 = self.observer._get_single_token_pl(token)
        # close the position
        update2 = Update("X", 1, 1, -50, 2.0**0.5 * 2**96)
        self.observer._update_token_metrics([update2])
        pl2 = self.observer._get_single_token_pl(token)
        # check the PLs
        self.assertEqual(
            pl1['fakeV3.permanent_loss:{position="X"}'].value,
            0.5 * pl2['fakeV3.permanent_loss:{position="X"}'].value,
        )  # does not check the exact value here

    def test_get_single_token_il(self):
        # mock the token
        token = Mock()
        token.token_id = "X"
        token.liquidity = 100
        # set the AMM and spot prices
        self.amm.sqrt_price_x96 = (2) ** 0.5 * 2**96
        market_spot = self.observer.spot_oracle.get_token_numeraire_spot([self.amm.symbol0, self.amm.symbol1], 0, 0)
        # get the initial IL
        il0 = self.observer._get_single_token_il(token, market_spot=market_spot)
        # partially close a position
        update1 = Update("X", 1, 1, -50, 0)
        self.observer._update_token_metrics([update1])
        token.liquidity = 50  # update mock token
        il1 = self.observer._get_single_token_il(token, market_spot=market_spot)
        # check values
        self.assertEqual(
            il0['fakeV3.abs_impermanent_loss:{position="X"}'].value,
            2 * il1['fakeV3.abs_impermanent_loss:{position="X"}'].value,
        )  # does not check the exact value here
        self.assertEqual(
            il0['fakeV3.net_position:{position="X"}'].value,
            2 * il1['fakeV3.net_position:{position="X"}'].value,
        )  # does not check the exact value here

    def test_get_single_token_lvr(self):
        # mock the token
        token = Mock()
        token.token_id = "X"
        # mock the buffer
        buffer = Mock()
        buffer.block_vec = [0, 10, 20, 30, 40, 50]
        buffer.price_vec = [1, 1.02, 1.03, 1.04, 1.05, 1.06]
        buffer.dt_vec = [0, 1, 1, 1, 1, 1]
        buffer.rvol_vec = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
        self.observer.buffer = buffer
        # compute LVR manually
        token_metrics = self.observer.get_token_metrics("X")
        price_lower = token_metrics.price_lower
        price_upper = token_metrics.price_upper
        fake_lvr = 0.0
        for i in range(1, len(buffer.block_vec)):
            price_prev = buffer.price_vec[i - 1]
            liquidity_prev = 100
            dt = buffer.dt_vec[i]
            rvol_prev = buffer.rvol_vec[i - 1]
            if (price_prev > price_lower) and (price_prev < price_upper):
                fake_lvr += 0.25 * liquidity_prev * rvol_prev**2 * price_prev**0.5 * dt
        # update and get the LVR
        market_spot = self.observer.spot_oracle.get_token_numeraire_spot([self.amm.symbol0, self.amm.symbol1], 0, 0)
        lvr_metric = self.observer._get_single_token_lvr(token, market_spot)
        lvr = token_metrics.lvr
        # check the LVR
        self.assertAlmostEqual(
            lvr_metric['fakeV3.loss_versus_rebalancing:{position="X"}'].value
            / 10 ** lvr_metric['fakeV3.loss_versus_rebalancing:{position="X"}'].decimals,
            fake_lvr,
        )
        self.assertAlmostEqual(lvr, fake_lvr)

    def test_get_single_token_fees(self):
        # check metric name
        token = Mock()
        token.token_id = "X"
        token.liquidity = 100
        # set the AMM and spot prices
        self.amm.sqrt_price_x96 = (2) ** 0.5 * 2**96
        market_spot = self.observer.spot_oracle.get_token_numeraire_spot([self.amm.symbol0, self.amm.symbol1], 0, 0)
        # get fees
        fees = self.observer._get_single_token_fees(token, market_spot=market_spot)
        self.assertEqual(fees['fakeV3.fees_not_collected:{position="X"}'].value, 0)

    def test_complex_history_il_lp(self):
        pass  # nice to have but not necessary


class TestAggregatedMetrics(unittest.TestCase):
    """
    Test the aggregated metrics: Does not need to be tested as it is a simple aggregation of the other metrics
    """

    def setUp(self):
        pass


# run the tests
if __name__ == "__main__":
    unittest.main()
    # suite = unittest.TestSuite()
    # suite.addTest(TestPerfTokenMetrics("test_get_single_token_lvr"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
