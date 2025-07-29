# type: ignore
import unittest
from unittest.mock import Mock

from nqs_pycore import TokenMetadata, Wallet
from sortedcontainers import SortedDict

from nqs_sdk_extension.observer.metric_info import CompoundMarketMetrics, ComptrollerAgentMetrics
from nqs_sdk_extension.observer.protocol.compoundv2 import ComptrollerObserver
from nqs_sdk_extension.protocol import Comptroller
from nqs_sdk_extension.state.compoundv2 import (
    BorrowSnapshot,
    StateCompoundMarket,
    StateComptroller,
    StateInterestRateModel,
)
from nqs_sdk_extension.transaction.compoundv2 import TransactionHelperCompoundv2

tran_helper = TransactionHelperCompoundv2()


def dummy_metadata(id: int, decimal: int):
    return TokenMetadata(f"token{id}", f"USD{id}", decimal)


class TestProtocolMetrics(unittest.TestCase):
    def setUp(self):
        # create a state with fake values
        self.market_1_state = StateCompoundMarket(
            id=0,
            name="Compound market 1",
            block_number=2,
            block_timestamp=0,
            symbol="cUSDC",
            address="0x1",
            underlying="USDC",
            underlying_address="0x01",
            underlying_decimals=6,
            interest_rate_model=StateInterestRateModel(
                multiplier_per_block=20_000_000_000,
                base_rate_per_block=0,
                jump_multiplier_per_block=500_000_000_000,
                kink=800_000_000_000_000_000,
            ),
            decimals=8,
            initial_exchange_rate_mantissa=200_000_000_000_000,
            accrual_block_number=2,
            reserve_factor_mantissa=450_000_000_000_000_000,
            borrow_index=1_000_000_000_000_000_000,
            total_borrows=0,
            total_supply=0,
            total_reserves=0,
            collateral_factor=500_000_000_000_000_000,
            borrow_cap=0,
            account_borrows={},
            total_cash=0,
        )

        self.market_2_state = StateCompoundMarket(
            id=2,
            name="Compound market 2",
            block_number=2,
            block_timestamp=0,
            symbol="cWETH",
            address="0x2",
            underlying="WETH",
            underlying_address="0x02",
            underlying_decimals=18,
            interest_rate_model=StateInterestRateModel(
                multiplier_per_block=85_000_000_000,
                base_rate_per_block=7_000_000_000,
                jump_multiplier_per_block=18_000_000_000_000,
                kink=800_000_000_000_000_000,
            ),
            decimals=8,
            initial_exchange_rate_mantissa=200_000_000_000_000,
            accrual_block_number=2,
            reserve_factor_mantissa=200_000_000_000_000_000,
            borrow_index=1_000_000_000_000_000_000,
            total_borrows=0,
            total_supply=0,
            total_reserves=0,
            collateral_factor=800_000_000_000_000_000,
            borrow_cap=100_000_000_000_000_000_000_000,
            account_borrows={
                "underwater": BorrowSnapshot(principal=1 * 10**18, interest_index=1_000_000_000_000_000_000)
            },
            total_cash=0,
        )

        comptroller_state = StateComptroller(
            id=3,
            name="comptroller",
            block_number=2,
            block_timestamp=0,
            close_factor_mantissa=500_000_000_000_000_000,
            liquidation_incentive_mantissa=1_080_000_000_000_000_000,
            max_assets=20,
            market_states={"cUSDC": self.market_1_state, "cWETH": self.market_2_state},
        )

        self.wallet = Wallet(
            holdings={"WETH": 0, "USDC": 10_000},
            tokens_metadata={  # type: ignore
                "WETH": dummy_metadata(1, 18),
                "USDC": dummy_metadata(2, 6),
            },
            erc721_tokens=[],
            agent_name="agent",
        )

        self.arbitrageur_wallet = Wallet(
            holdings={"WETH": 0, "USDC": 0},
            tokens_metadata={  # type: ignore
                "WETH": dummy_metadata(1, 18),
                "USDC": dummy_metadata(2, 6),
            },
            erc721_tokens=[],
            agent_name="arbitrageur",
        )

        self.underwater_wallet = Wallet(
            holdings={"WETH": 1, "cUSDC": 1800 / 0.02},
            erc721_tokens=[],
            tokens_metadata={  # type: ignore
                "WETH": dummy_metadata(1, 18),
                "cUSDC": dummy_metadata(2, 8),
            },
            agent_name="underwater",
        )

        # create mint transactions
        mint1 = tran_helper.create_mint_transaction(
            mint_amount=10_000 * 10**6, ctoken="cUSDC", block_number=2, sender_wallet=self.wallet
        )
        mint2 = tran_helper.create_mint_transaction(mint_amount=100_000 * 10**6, ctoken="cUSDC", block_number=2)
        mint3 = tran_helper.create_mint_transaction(mint_amount=1_000 * 10**18, ctoken="cWETH", block_number=2)
        # create Comptroller and process mint transactions
        comptroller = Comptroller(comptroller_state)
        comptroller.process_transactions([mint1, mint2, mint3])
        self.comptroller = comptroller
        # create borrow transactions
        borrow_1 = tran_helper.create_borrow_transaction(borrow_amount=10_000 * 10**6, ctoken="cUSDC", block_number=2)
        borrow_2 = tran_helper.create_borrow_transaction(
            borrow_amount=1 * 10**18, ctoken="cWETH", block_number=2, sender_wallet=self.wallet
        )
        self.borrows = [borrow_1, borrow_2]
        # prepare the spot oracle
        spot_oracle = Mock()
        spot_oracle.numeraire = "USDC"
        spot_oracle.get_selected_spots.return_value = {("WETH", "USDC"): 2000.0, ("USDC", "USDC"): 1.0}
        self.spot_oracle = spot_oracle
        # prepare the observer by setting it manually
        observer = ComptrollerObserver(comptroller=self.comptroller)
        observer._observer_id = "compound_v2"
        observer.spot_oracle = spot_oracle
        observer.metric_info = ComptrollerAgentMetrics("compound_v2")
        observer.numeraire_decimals = 18
        observer._markets_observables["cUSDC"].metric_info = CompoundMarketMetrics("compound_v2", token="USDC")
        observer._markets_observables["cWETH"].metric_info = CompoundMarketMetrics("compound_v2", token="WETH")
        self.observer = observer

    def test_global_metrics(self):
        # collect total amounts minted from the events
        events_usdc = self.comptroller.markets["cUSDC"].events_ready_to_collect
        minted_amount_usdc = 0
        for event in events_usdc:
            minted_amount_usdc += event.amount
        # get the global markets position
        global_position = self.observer._markets_observables["cUSDC"].get_global_position()
        # check the results
        self.assertAlmostEqual(
            global_position['compound_v2.total_cash:{token="USDC"}'].value,
            (self.market_1_state.total_cash + minted_amount_usdc),
        )
        self.assertAlmostEqual(
            global_position['compound_v2.total_supply:{token="USDC"}'].value,
            int(
                minted_amount_usdc
                / 10**self.market_1_state.underlying_decimals
                / 0.02
                * 10**self.market_1_state.decimals
            ),
        )
        self.assertAlmostEqual(global_position['compound_v2.total_borrow:{token="USDC"}'].value, 0)
        self.assertAlmostEqual(global_position['compound_v2.total_reserves:{token="USDC"}'].value, 0)

    def test_rate_metrics(self):
        # get the market rates
        rates_observables = self.observer._markets_observables["cUSDC"].get_rates()
        # check the results
        self.assertEqual(rates_observables['compound_v2.utilisation_ratio:{token="USDC"}'].value, 0)
        self.assertEqual(rates_observables['compound_v2.borrow_rate_apr:{token="USDC"}'].value, 0)
        self.assertEqual(rates_observables['compound_v2.supply_rate_apr:{token="USDC"}'].value, 0)

        # process borrow transactions and recompute observables
        self.comptroller.inject_spot_values(3, self.spot_oracle.get_selected_spots())
        self.comptroller.process_transactions(self.borrows)
        rates_observables_after = self.observer._markets_observables["cUSDC"].get_rates()

        # compute rates
        util_rate = (
            self.comptroller.markets["cUSDC"].total_borrows
            * 10**18
            // (self.comptroller.markets["cUSDC"].total_borrows + self.comptroller.markets["cUSDC"].total_cash)
        )
        borrow_rate = util_rate * self.market_1_state.interest_rate_model.multiplier_per_block // 10**18
        blocks_per_year = 5 * 60 * 24 * 365  # 12 seconds per block
        borrow_rate_apr = borrow_rate * blocks_per_year

        one_minus_reserve_factor = 10**18 - self.market_1_state.reserve_factor_mantissa
        rate_to_pool = borrow_rate * one_minus_reserve_factor // 10**18
        supply_rate = util_rate * rate_to_pool // 10**18
        supply_rate_apr = supply_rate * blocks_per_year

        self.assertAlmostEqual(rates_observables_after['compound_v2.utilisation_ratio:{token="USDC"}'].value, util_rate)
        self.assertAlmostEqual(
            rates_observables_after['compound_v2.borrow_rate_apr:{token="USDC"}'].value, borrow_rate_apr
        )
        self.assertAlmostEqual(
            rates_observables_after['compound_v2.supply_rate_apr:{token="USDC"}'].value, supply_rate_apr
        )

    def test_agent_collateralisation(self):
        self.comptroller.inject_spot_values(3, self.spot_oracle.get_selected_spots())
        self.comptroller.process_transactions(self.borrows)

        spots = self.spot_oracle.get_selected_spots()
        agent_metrics = self.observer.get_agent_collateralisation_level(wallet=self.wallet, spots=spots)

        self.assertAlmostEqual(agent_metrics["compound_v2.total_debt"].value, int(spots[("WETH", "USDC")] * 10**18))
        self.assertAlmostEqual(agent_metrics["compound_v2.total_collateral"].value, int(10000 * 10**18))
        self.assertAlmostEqual(
            agent_metrics["compound_v2.debt_collateral_ratio"].value, int(spots[("WETH", "USDC")] / 10000 * 10**18)
        )
        self.assertAlmostEqual(
            agent_metrics["compound_v2.liquidation_threshold"].value, self.market_1_state.collateral_factor
        )
        self.assertAlmostEqual(
            agent_metrics["compound_v2.net_position"].value, int((10000 - spots[("WETH", "USDC")]) * 10**18)
        )

    def test_generated_interests(self):
        spots = self.spot_oracle.get_selected_spots()
        self.comptroller.inject_spot_values(3, spots)
        self.comptroller.process_transactions(self.borrows)

        self.observer._agent_wallets.setdefault(self.wallet.agent_name, self.wallet)
        self.observer._agent_cumulated_debt_interests.setdefault(self.wallet.agent_name, 0)
        self.observer._agent_cumulated_collateral_interests.setdefault(self.wallet.agent_name, 0)
        agent_metrics = self.observer.get_agent_generated_interests(wallet=self.wallet, current_spot=spots)

        self.assertAlmostEqual(agent_metrics['compound_v2.current_debt:{token="USDC"}'].value, 0)
        self.assertAlmostEqual(
            agent_metrics['compound_v2.current_collateral:{token="USDC"}'].value,
            10000 * 10**self.market_1_state.underlying_decimals,
        )
        self.assertAlmostEqual(agent_metrics['compound_v2.cumulated_collateral_interests:{token="USDC"}'].value, 0)
        self.assertAlmostEqual(agent_metrics['compound_v2.cumulated_debt_interests:{token="USDC"}'].value, 0)
        self.assertAlmostEqual(
            agent_metrics['compound_v2.current_debt:{token="WETH"}'].value,
            1 * 10**self.market_2_state.underlying_decimals,
        )
        self.assertAlmostEqual(agent_metrics['compound_v2.current_collateral:{token="WETH"}'].value, 0)
        self.assertAlmostEqual(agent_metrics['compound_v2.cumulated_collateral_interests:{token="WETH"}'].value, 0)
        self.assertAlmostEqual(agent_metrics['compound_v2.cumulated_debt_interests:{token="WETH"}'].value, 0)
        self.assertAlmostEqual(agent_metrics["compound_v2.total_cumulated_debt_interests"].value, 0)
        self.assertAlmostEqual(agent_metrics["compound_v2.total_cumulated_debt_interests"].value, 0)

        # process another transaction in both markets to accrue interests
        borrow_1 = tran_helper.create_borrow_transaction(borrow_amount=1 * 10**6, ctoken="cUSDC", block_number=20000)
        borrow_2 = tran_helper.create_borrow_transaction(borrow_amount=1 * 10**18, ctoken="cWETH", block_number=20000)
        self.comptroller.process_transactions([borrow_1, borrow_2])
        agent_metrics_new = self.observer.get_agent_generated_interests(wallet=self.wallet, current_spot=spots)
        self.assertAlmostEqual(agent_metrics_new['compound_v2.current_debt:{token="USDC"}'].value, 0)
        self.assertAlmostEqual(agent_metrics_new['compound_v2.cumulated_debt_interests:{token="USDC"}'].value, 0)
        self.assertAlmostEqual(agent_metrics_new['compound_v2.current_collateral:{token="WETH"}'].value, 0)
        self.assertAlmostEqual(agent_metrics_new['compound_v2.cumulated_collateral_interests:{token="WETH"}'].value, 0)
        self.assertAlmostEqual(
            agent_metrics_new['compound_v2.current_collateral:{token="USDC"}'].value
            - agent_metrics['compound_v2.current_collateral:{token="USDC"}'].value,
            agent_metrics_new['compound_v2.cumulated_collateral_interests:{token="USDC"}'].value,
        )
        self.assertAlmostEqual(
            agent_metrics_new['compound_v2.current_collateral:{token="USDC"}'].value
            - agent_metrics['compound_v2.current_collateral:{token="USDC"}'].value,
            agent_metrics_new["compound_v2.total_cumulated_collateral_interests"].value
            * 10
            ** (
                agent_metrics_new['compound_v2.current_collateral:{token="USDC"}'].decimals
                - agent_metrics_new["compound_v2.total_cumulated_collateral_interests"].decimals
            ),
        )
        self.assertAlmostEqual(
            agent_metrics_new['compound_v2.current_debt:{token="WETH"}'].value
            - agent_metrics['compound_v2.current_debt:{token="WETH"}'].value,
            agent_metrics_new['compound_v2.cumulated_debt_interests:{token="WETH"}'].value,
        )

        # process another transaction in both markets to accrue interests
        borrow_3 = tran_helper.create_borrow_transaction(borrow_amount=1 * 10**6, ctoken="cUSDC", block_number=40000)
        borrow_4 = tran_helper.create_borrow_transaction(borrow_amount=1 * 10**18, ctoken="cWETH", block_number=40000)
        self.comptroller.process_transactions([borrow_3, borrow_4])
        self.observer._agent_cumulated_debt_interests[self.wallet.agent_name] = 0
        self.observer._agent_cumulated_collateral_interests[self.wallet.agent_name] = 0
        agent_metrics_new2 = self.observer.get_agent_generated_interests(wallet=self.wallet, current_spot=spots)
        self.assertAlmostEqual(
            agent_metrics_new2['compound_v2.current_collateral:{token="USDC"}'].value
            - agent_metrics_new['compound_v2.current_collateral:{token="USDC"}'].value,
            agent_metrics_new2['compound_v2.cumulated_collateral_interests:{token="USDC"}'].value
            - agent_metrics_new['compound_v2.cumulated_collateral_interests:{token="USDC"}'].value,
        )
        self.assertAlmostEqual(
            agent_metrics_new2['compound_v2.current_collateral:{token="USDC"}'].value
            - agent_metrics_new['compound_v2.current_collateral:{token="USDC"}'].value,
            (
                agent_metrics_new2["compound_v2.total_cumulated_collateral_interests"].value
                - agent_metrics_new["compound_v2.total_cumulated_collateral_interests"].value
            )
            * 10
            ** (
                agent_metrics_new2['compound_v2.current_collateral:{token="USDC"}'].decimals
                - agent_metrics_new["compound_v2.total_cumulated_collateral_interests"].decimals
            ),
        )
        self.assertAlmostEqual(
            agent_metrics_new2['compound_v2.current_debt:{token="WETH"}'].value
            - agent_metrics_new['compound_v2.current_debt:{token="WETH"}'].value,
            agent_metrics_new2['compound_v2.cumulated_debt_interests:{token="WETH"}'].value
            - agent_metrics_new['compound_v2.cumulated_debt_interests:{token="WETH"}'].value,
        )
        self.assertAlmostEqual(
            (
                agent_metrics_new2['compound_v2.current_debt:{token="WETH"}'].value
                - agent_metrics_new['compound_v2.current_debt:{token="WETH"}'].value
            )
            * 2000,
            (
                agent_metrics_new2["compound_v2.total_cumulated_debt_interests"].value
                - agent_metrics_new["compound_v2.total_cumulated_debt_interests"].value
            ),
        )
        self.assertAlmostEqual(
            agent_metrics_new2['compound_v2.cumulated_debt_interests:{token="WETH"}'].value * 2000,
            agent_metrics_new2["compound_v2.total_cumulated_debt_interests"].value,
        )

    def test_liquidate_max_debt(self):
        initial_debt_numeraire = 2000 * 10**18
        initial_collateral_numeraire = 1800 * 10**18

        self.comptroller.inject_spot_values(3, self.spot_oracle.get_selected_spots())
        self.observer._agent_total_debt["agent"] = initial_debt_numeraire
        self.observer._agent_total_collateral["agent"] = initial_collateral_numeraire
        self.observer._agent_total_collateral_discounted["agent"] = (
            initial_collateral_numeraire * self.market_1_state.collateral_factor // 10**18
        )
        debts = SortedDict({initial_debt_numeraire: "cWETH", 0: "cUSDC"})
        collaterals = SortedDict({0: "cWETH", initial_collateral_numeraire: "cUSDC"})

        trx = self.observer.liquidate_max_debt(
            liquidated_wallet=self.wallet,
            block_number=3,
            debts=debts,
            collaterals=collaterals,
            arbitrageur_wallet=self.arbitrageur_wallet,
        )
        self.assertEqual(trx.ctoken, "cWETH")
        self.assertEqual(trx.ctoken_collateral, "cUSDC")
        self.assertEqual(
            trx.repay_amount,
            initial_debt_numeraire
            * self.comptroller.close_factor_mantissa
            // 10**18
            / self.comptroller.stored_spot[("WETH", "USDC")],
        )

        self.assertEqual(collaterals[self.observer._agent_total_collateral["agent"]], "cUSDC")
        self.assertEqual(debts[self.observer._agent_total_debt["agent"]], "cWETH")

        self.assertAlmostEqual(
            self.observer._agent_total_debt["agent"],
            initial_debt_numeraire * self.comptroller.close_factor_mantissa // 10**18,
        )
        self.assertAlmostEqual(
            self.observer._agent_total_collateral["agent"],
            initial_collateral_numeraire
            - initial_debt_numeraire
            * self.comptroller.close_factor_mantissa
            * self.comptroller.liquidation_incentive_mantissa
            / 10**36,
        )

        self.assertAlmostEqual(
            self.observer._agent_total_collateral_discounted["agent"],
            (
                initial_collateral_numeraire
                - initial_debt_numeraire
                * self.comptroller.close_factor_mantissa
                * self.comptroller.liquidation_incentive_mantissa
                / 10**36
            )
            * self.market_1_state.collateral_factor
            / 10**18,
        )

    def test_liquidate_max_collateral(self):
        initial_debt_numeraire = 500 * 10**18
        initial_collateral_numeraire = 180 * 10**18

        self.comptroller.inject_spot_values(3, self.spot_oracle.get_selected_spots())
        self.observer._agent_total_debt["agent"] = initial_debt_numeraire
        self.observer._agent_total_collateral["agent"] = initial_collateral_numeraire
        self.observer._agent_total_collateral_discounted["agent"] = (
            initial_collateral_numeraire * self.market_1_state.collateral_factor // 10**18
        )
        debts = SortedDict({initial_debt_numeraire: "cWETH", 0: "cUSDC"})
        collaterals = SortedDict({0: "cWETH", initial_collateral_numeraire: "cUSDC"})

        trx = self.observer.liquidate_max_collateral(
            liquidated_wallet=self.wallet,
            block_number=3,
            debts=debts,
            collaterals=collaterals,
            arbitrageur_wallet=self.arbitrageur_wallet,
        )
        self.assertEqual(trx.ctoken, "cWETH")
        self.assertEqual(trx.ctoken_collateral, "cUSDC")
        self.assertEqual(
            trx.repay_amount,
            initial_collateral_numeraire
            * 10**18
            // self.comptroller.liquidation_incentive_mantissa
            // int(self.comptroller.stored_spot[("WETH", "USDC")]),
        )

        self.assertEqual(list(collaterals.keys()), [0])
        self.assertEqual(debts[self.observer._agent_total_debt["agent"]], "cWETH")

        self.assertAlmostEqual(
            self.observer._agent_total_debt["agent"],
            initial_debt_numeraire
            - initial_collateral_numeraire * 10**18 // self.comptroller.liquidation_incentive_mantissa,
        )
        self.assertAlmostEqual(self.observer._agent_total_collateral["agent"], 0)

        self.assertAlmostEqual(self.observer._agent_total_collateral_discounted["agent"], 0)

    def test_create_arbitrage_transactions(self):
        initial_debt_numeraire = 2000 * 10**18
        initial_collateral_numeraire = 1800 * 10**18

        self.comptroller.inject_spot_values(3, self.spot_oracle.get_selected_spots())
        self.observer._agent_total_debt["underwater"] = initial_debt_numeraire
        self.observer._agent_total_collateral["underwater"] = initial_collateral_numeraire
        self.observer._agent_total_collateral_discounted["underwater"] = (
            initial_collateral_numeraire * self.market_1_state.collateral_factor // 10**18
        )

        trx_list = self.observer.create_single_wallet_arbitrage_transactions(
            wallet=self.underwater_wallet,
            block_number=3,
            block_timestamp=0,
            arbitrageur_wallet=self.arbitrageur_wallet,
        )

        self.assertEqual(len(trx_list), 3)
        self.assertEqual({trx.ctoken for trx in trx_list}, {"cWETH"})
        self.assertEqual({trx.ctoken_collateral for trx in trx_list}, {"cUSDC"})

        repay_0 = (
            initial_debt_numeraire
            * self.comptroller.close_factor_mantissa
            // 10**18
            // int(self.comptroller.stored_spot[("WETH", "USDC")])
        )
        collateral_0 = (
            initial_collateral_numeraire
            - initial_debt_numeraire
            * self.comptroller.close_factor_mantissa
            * self.comptroller.liquidation_incentive_mantissa
            // 10**36
        )
        repay_1 = repay_0 * self.comptroller.close_factor_mantissa // 10**18
        collateral_1 = (
            collateral_0
            - initial_debt_numeraire
            * self.comptroller.close_factor_mantissa
            // 10**18
            * self.comptroller.close_factor_mantissa
            // 10**18
            * self.comptroller.liquidation_incentive_mantissa
            // 10**18
        )
        repay_2 = (
            collateral_1
            * 10**18
            // self.comptroller.liquidation_incentive_mantissa
            // int(self.comptroller.stored_spot[("WETH", "USDC")])
        )

        self.assertAlmostEqual(trx_list[0].repay_amount, repay_0)
        self.assertAlmostEqual(trx_list[1].repay_amount, repay_1)
        self.assertAlmostEqual(trx_list[2].repay_amount, repay_2)

        self.assertAlmostEqual(self.observer._agent_total_collateral["underwater"], 0)
        self.assertAlmostEqual(self.observer._agent_total_collateral_discounted["underwater"], 0)
        self.assertAlmostEqual(
            self.observer._agent_total_debt["underwater"],
            initial_debt_numeraire
            * self.comptroller.close_factor_mantissa
            // 10**18
            * self.comptroller.close_factor_mantissa
            // 10**18
            - collateral_1 * 10**18 // self.comptroller.liquidation_incentive_mantissa,
        )
