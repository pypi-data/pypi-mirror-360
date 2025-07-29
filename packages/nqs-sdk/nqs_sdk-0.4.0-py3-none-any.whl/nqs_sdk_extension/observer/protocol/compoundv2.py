from decimal import Decimal
from typing import Dict, Optional, Sequence

from nqs_pycore import Wallet
from sortedcontainers import SortedDict

from nqs_sdk_extension.agent.agent_action import CustomVariable
from nqs_sdk_extension.observer import DEFAULT_DECIMALS, ABCObserver, SingleObservable
from nqs_sdk_extension.observer.metric_info import CompoundMarketMetrics, ComptrollerAgentMetrics
from nqs_sdk_extension.observer.protocol.protocol_observer import ProtocolObserver
from nqs_sdk_extension.protocol.lending_protocol.compoundv2.compoundv2 import (
    LENDING_PROTOCOL_MANDATORY_TOKEN,
    Borrow,
    CompoundMarket,
    Comptroller,
    Liquidation,
    Mint,
    Redeem,
    Repay,
)
from nqs_sdk_extension.protocol.lending_protocol.compoundv2.full_math import EXPSCALE
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.compoundv2 import LiquidateTransactionCompv2
from nqs_sdk_extension.wallet.arbitrageur_wallet import Arbitrageur_NAME

TOL = 10**-6


class ComptrollerObserver(ProtocolObserver):
    def __init__(self, comptroller: Comptroller) -> None:
        super().__init__()
        self._comptroller = comptroller
        self.ctoken_list = list(self._comptroller.markets.keys())
        self._markets_observables = {
            ctoken: Compoundv2MarketObserver(self._comptroller.markets[ctoken]) for ctoken in self.ctoken_list
        }
        # auxiliary variables for agent metrics
        self._agent_wallets: dict[str, Wallet] = {}
        self._liquidatable_wallets: dict[str, Wallet] = {}
        self._agent_total_debt: dict[str, int] = {}
        self._agent_total_collateral: dict[str, int] = {}
        self._agent_total_collateral_discounted: dict[str, int] = {}
        self._agent_cumulated_debt_interests: dict[str, int] = {}
        self._agent_cumulated_collateral_interests: dict[str, int] = {}

    def set_environment(self, observable_id: str, env_observers: Optional[Dict[str, ABCObserver]]) -> None:
        self._observer_id = observable_id
        self.metric_info = ComptrollerAgentMetrics(self._observer_id)

    def get_all_observables(self, block_number: int, block_timestamp: int) -> dict[str, SingleObservable]:
        new_observables: dict[str, SingleObservable] = {}
        for market_observable in self._markets_observables.values():
            new_observables.update(market_observable.collect_market_observables())
        return new_observables

    @property
    def markets_observables(self) -> dict:
        return self._markets_observables

    ##################################################################################################################
    ######################################## agent observables #######################################################
    ##################################################################################################################
    def get_agent_observables(
        self, block_number: int, block_timestamp: int, wallet: Wallet
    ) -> dict[str, SingleObservable]:
        virtual_position: dict[str, SingleObservable] = {}

        cerc20_tokens = wallet.get_cerc20_tokens()
        if len(cerc20_tokens) == 0:
            return virtual_position

        self._agent_cumulated_debt_interests[wallet.agent_name] = 0
        self._agent_cumulated_collateral_interests[wallet.agent_name] = 0

        spots = self.spot_oracle.get_selected_spots(
            [(LENDING_PROTOCOL_MANDATORY_TOKEN, self.spot_oracle.numeraire)] + self._comptroller.required_spots,
            block_timestamp,
        )

        virtual_position.update(self.get_agent_collateralisation_level(wallet, spots))
        if wallet.agent_name != Arbitrageur_NAME:
            self._agent_wallets.setdefault(wallet.agent_name, wallet)
            virtual_position.update(self.get_agent_generated_interests(wallet, spots))
        return virtual_position

    def get_agent_collateralisation_level(
        self, wallet: Wallet, spots: dict[tuple[str, str], float]
    ) -> dict[str, SingleObservable]:
        collateralisation_level: dict[str, SingleObservable] = {}

        # collateral and debt are returned by Compound with 18 decimals
        collateral_discounted, debt, collateral_undiscounted = self._comptroller.get_hypothetical_account_net_position(
            wallet, "", 0, 0, spots
        )

        collateralisation_level[self.metric_info.total_debt.name] = SingleObservable(
            value=int(
                Decimal(debt).scaleb(-DEFAULT_DECIMALS)
                * Decimal(spots[(LENDING_PROTOCOL_MANDATORY_TOKEN, self.spot_oracle.numeraire)]).scaleb(
                    self.numeraire_decimals
                )
            ),
            decimals=self.numeraire_decimals,
        )
        collateralisation_level[self.metric_info.total_collateral.name] = SingleObservable(
            value=int(
                Decimal(collateral_undiscounted).scaleb(-DEFAULT_DECIMALS)
                * Decimal(spots[(LENDING_PROTOCOL_MANDATORY_TOKEN, self.spot_oracle.numeraire)]).scaleb(
                    self.numeraire_decimals
                )
            ),
            decimals=self.numeraire_decimals,
        )
        # these are in USDC units, with 18 decimals, following the convention of the protocol.
        # These quantities are used only during the liquidation process
        self._agent_total_debt[wallet.agent_name] = debt
        self._agent_total_collateral[wallet.agent_name] = collateral_undiscounted

        value = debt * 10**DEFAULT_DECIMALS // collateral_undiscounted if collateral_undiscounted != 0 else 0
        collateralisation_level[self.metric_info.debt_collateral_ratio.name] = SingleObservable(
            value=value, decimals=DEFAULT_DECIMALS
        )

        value = (
            collateral_discounted * 10**DEFAULT_DECIMALS // collateral_undiscounted
            if collateral_undiscounted != 0
            else 0
        )
        collateralisation_level[self.metric_info.liquidation_threshold.name] = SingleObservable(
            value=value, decimals=DEFAULT_DECIMALS
        )
        self._agent_total_collateral_discounted[wallet.agent_name] = collateral_discounted

        collateralisation_level[self.metric_info.net_position.name] = SingleObservable(
            value=collateralisation_level[self.metric_info.total_collateral.name].value
            - collateralisation_level[self.metric_info.total_debt.name].value,
            decimals=self.numeraire_decimals,
        )
        return collateralisation_level

    def get_agent_generated_interests(
        self, wallet: Wallet, current_spot: dict[tuple[str, str], float]
    ) -> dict[str, SingleObservable]:
        cumulated_interests: dict[str, SingleObservable] = {}
        for market_observable in self._markets_observables.values():
            virtual_position_market = market_observable.collect_virtual_positions(wallet)
            cumulated_interests.update(virtual_position_market)
            self._agent_cumulated_collateral_interests[wallet.agent_name] += int(
                Decimal(
                    virtual_position_market[market_observable.metric_info.cumulated_collateral_interests.name].value
                ).scaleb(-market_observable.underlying_decimals)
                * Decimal(current_spot[(market_observable.underlying, LENDING_PROTOCOL_MANDATORY_TOKEN)])
                * Decimal(current_spot[(LENDING_PROTOCOL_MANDATORY_TOKEN, self.spot_oracle.numeraire)]).scaleb(
                    self.numeraire_decimals
                )
            )
            self._agent_cumulated_debt_interests[wallet.agent_name] += int(
                Decimal(
                    virtual_position_market[market_observable.metric_info.cumulated_debt_interests.name].value
                ).scaleb(-market_observable.underlying_decimals)
                * Decimal(current_spot[(market_observable.underlying, LENDING_PROTOCOL_MANDATORY_TOKEN)])
                * Decimal(current_spot[(LENDING_PROTOCOL_MANDATORY_TOKEN, self.spot_oracle.numeraire)]).scaleb(
                    self.numeraire_decimals
                )
            )

        cumulated_interests[self.metric_info.total_cumulated_collateral_interests.name] = SingleObservable(
            value=self._agent_cumulated_collateral_interests[wallet.agent_name], decimals=self.numeraire_decimals
        )
        cumulated_interests[self.metric_info.total_cumulated_debt_interests.name] = SingleObservable(
            value=self._agent_cumulated_debt_interests[wallet.agent_name], decimals=self.numeraire_decimals
        )
        cumulated_interests[self.metric_info.total_fees.name] = SingleObservable(
            value=self._agent_cumulated_collateral_interests[wallet.agent_name]
            - self._agent_cumulated_debt_interests[wallet.agent_name],
            decimals=self.numeraire_decimals,
        )

        return cumulated_interests

    def agents_id_to_update(self) -> list[str]:
        return list(self._liquidatable_wallets.keys())

    def exists_arbitrage_opportunity(self, block_number: int, block_timestamp: int) -> bool:
        spots = self.spot_oracle.get_selected_spots(
            [(LENDING_PROTOCOL_MANDATORY_TOKEN, self.spot_oracle.numeraire)] + self._comptroller.required_spots,
            block_timestamp,
        )
        self._comptroller.inject_spot_values(block_timestamp, spots)
        for agent_id, wallet in self._agent_wallets.items():
            wallet_collateralisation = self.get_agent_collateralisation_level(wallet, spots)
            if (
                wallet_collateralisation[self.metric_info.debt_collateral_ratio.name].value
                >= wallet_collateralisation[self.metric_info.liquidation_threshold.name].value
                and wallet_collateralisation[self.metric_info.total_collateral.name].value > TOL
            ):
                self._liquidatable_wallets[agent_id] = wallet
        return bool(self._liquidatable_wallets)

    def create_arbitrage_transactions(
        self, block_number: int, block_timestamp: int, arbitrageur_wallet: Wallet
    ) -> Sequence[ABCTransaction]:
        liquidation_trxs: list[LiquidateTransactionCompv2] = []
        for agent_id, wallet in self._liquidatable_wallets.items():
            liquidation_trxs += self.create_single_wallet_arbitrage_transactions(
                wallet, block_number, block_timestamp, arbitrageur_wallet
            )
        self._liquidatable_wallets = {}
        return liquidation_trxs

    def create_single_wallet_arbitrage_transactions(
        self, wallet: Wallet, block_number: int, block_timestamp: int, arbitrageur_wallet: Wallet
    ) -> list[LiquidateTransactionCompv2]:
        liquidation_trxs: list[LiquidateTransactionCompv2] = []
        debts: SortedDict[int, str] = SortedDict()
        collaterals: SortedDict[int, str] = SortedDict()

        # this is for the corner case in which arbitrages exist straight from the beginning of the simulation
        if not self._comptroller.stored_spot:
            updated_spots = self.spot_oracle.get_selected_spots(self._comptroller.required_spots, block_timestamp)
            self._comptroller.inject_spot_values(block_timestamp, updated_spots)

        for market_obs in self._markets_observables.values():
            virtual_position = market_obs.collect_virtual_positions(wallet)
            numeraire_debt = (
                virtual_position[market_obs.metric_info.current_debt.name].value
                * int(
                    Decimal(self._comptroller.stored_spot[(market_obs.underlying, LENDING_PROTOCOL_MANDATORY_TOKEN)])
                    * 10 ** (36 - market_obs.underlying_decimals)
                )
                // EXPSCALE
            )
            numeraire_collateral = (
                virtual_position[market_obs.metric_info.current_collateral.name].value
                * int(
                    Decimal(self._comptroller.stored_spot[(market_obs.underlying, LENDING_PROTOCOL_MANDATORY_TOKEN)])
                    * 10 ** (36 - market_obs.underlying_decimals)
                )
                // EXPSCALE
            )
            debts[numeraire_debt] = market_obs._compound_market.symbol
            collaterals[numeraire_collateral] = market_obs._compound_market.symbol

        while (
            self._agent_total_debt[wallet.agent_name]
            > self._agent_total_collateral_discounted[wallet.agent_name]
            > 10 ** (DEFAULT_DECIMALS - 1)
        ):
            max_debt, _ = debts.peekitem(-1)
            max_collateral, _ = collaterals.peekitem(-1)
            if (
                max_debt
                * (self._comptroller.close_factor_mantissa)
                // EXPSCALE
                * (self._comptroller.liquidation_incentive_mantissa)
                // EXPSCALE
                < max_collateral
            ):
                liquidation_trxs.append(
                    self.liquidate_max_debt(wallet, block_number, debts, collaterals, arbitrageur_wallet)
                )
            else:
                liquidation_trxs.append(
                    self.liquidate_max_collateral(wallet, block_number, debts, collaterals, arbitrageur_wallet)
                )
        return liquidation_trxs

    def liquidate_max_debt(
        self,
        liquidated_wallet: Wallet,
        block_number: int,
        debts: SortedDict,
        collaterals: SortedDict,
        arbitrageur_wallet: Wallet,
    ) -> LiquidateTransactionCompv2:
        debt, ctoken_borrowed = debts.popitem()
        collateral, ctoken_collateral = collaterals.popitem()

        # this is ok as current debt is converted in USDC using the formulae from the SC
        repay_amount = int(
            debt
            * self._comptroller.close_factor_mantissa
            // int(
                Decimal(
                    self._comptroller.stored_spot[
                        (self._markets_observables[ctoken_borrowed].underlying, LENDING_PROTOCOL_MANDATORY_TOKEN)
                    ]
                )
                * 10 ** (36 - self._comptroller.markets[ctoken_borrowed].underlying_decimals)
            )
        )

        new_collateral_value = (
            collateral
            - debt
            * self._comptroller.close_factor_mantissa
            // EXPSCALE
            * self._comptroller.liquidation_incentive_mantissa
            // EXPSCALE
        )

        debts[debt * self._comptroller.close_factor_mantissa // EXPSCALE] = ctoken_borrowed
        self._agent_total_debt[liquidated_wallet.agent_name] -= (
            debt * self._comptroller.close_factor_mantissa // EXPSCALE
        )
        self._agent_total_collateral_discounted[liquidated_wallet.agent_name] -= (
            (collateral - new_collateral_value)
            * self._comptroller.markets[ctoken_collateral].collateral_factor_mantissa
            // EXPSCALE
        )
        self._agent_total_collateral[liquidated_wallet.agent_name] -= collateral - new_collateral_value
        collaterals[new_collateral_value] = ctoken_collateral

        return LiquidateTransactionCompv2(
            **{
                "block_number": block_number,
                "protocol_id": self._observer_id,
                "sender_wallet": arbitrageur_wallet,
                "borrower": liquidated_wallet,
                "repay_amount": repay_amount,
                "ctoken_collateral": ctoken_collateral,
                "ctoken": ctoken_borrowed,
            }
        )

    def liquidate_max_collateral(
        self,
        liquidated_wallet: Wallet,
        block_number: int,
        debts: SortedDict,
        collaterals: SortedDict,
        arbitrageur_wallet: Wallet,
    ) -> LiquidateTransactionCompv2:
        debt, ctoken_borrowed = debts.popitem()
        collateral, ctoken_collateral = collaterals.popitem()

        repay_amount = int(
            collateral
            * EXPSCALE
            // self._comptroller.liquidation_incentive_mantissa
            * EXPSCALE
            // int(
                Decimal(
                    self._comptroller.stored_spot[
                        (self._markets_observables[ctoken_borrowed].underlying, LENDING_PROTOCOL_MANDATORY_TOKEN)
                    ]
                )
                * 10 ** (36 - self._comptroller.markets[ctoken_borrowed].underlying_decimals)
            )
        )
        repay_amount_numeraire = collateral * EXPSCALE // self._comptroller.liquidation_incentive_mantissa

        debts[debt - repay_amount_numeraire] = ctoken_borrowed
        self._agent_total_debt[liquidated_wallet.agent_name] -= repay_amount_numeraire
        self._agent_total_collateral_discounted[liquidated_wallet.agent_name] -= (
            collateral * self._comptroller.markets[ctoken_collateral].collateral_factor_mantissa // EXPSCALE
        )
        self._agent_total_collateral[liquidated_wallet.agent_name] -= collateral
        collaterals[0] = ctoken_collateral

        return LiquidateTransactionCompv2(
            **{
                "block_number": block_number,
                "protocol_id": self._observer_id,
                "sender_wallet": arbitrageur_wallet,
                "borrower": liquidated_wallet,
                "repay_amount": repay_amount,
                "ctoken_collateral": ctoken_collateral,
                "ctoken": ctoken_borrowed,
            }
        )


##################################################################################################################
######################################## Compound Markets ########################################################
##################################################################################################################


class Compoundv2MarketObserver(ABCObserver):
    def __init__(self, compound_market: CompoundMarket) -> None:
        super().__init__()
        self._compound_market = compound_market
        self.underlying = compound_market.underlying
        self.underlying_decimals = compound_market.underlying_decimals

        # auxiliary variables for agent metrics
        self._agent_exchange_rate_stored: dict[str, int] = {}
        self._agent_collateral_stored: dict[str, int] = {}
        self._agent_debt_index_stored: dict[str, int] = {}
        self._agent_principal_debt_stored: dict[str, int] = {}
        self._agent_cumulated_debt_interests: dict[str, int] = {}
        self._agent_cumulated_collateral_interests: dict[str, int] = {}

    def set_environment(self, observable_id: str, env_observers: Optional[Dict[str, ABCObserver]]) -> None:
        self._observer_id = observable_id
        self.metric_info = CompoundMarketMetrics("compound_v2", token=self._compound_market.underlying)

    def get_rates(self) -> dict[str, SingleObservable]:
        """
        Returns utilisation, borrow and supply rate of the compound market
        """
        denominator = (
            self._compound_market.total_cash
            + self._compound_market.total_borrows
            - self._compound_market.total_reserves
        )
        utilisation = (self._compound_market.total_borrows * EXPSCALE // denominator) if denominator != 0 else 0
        borrow_rate = self._compound_market.interest_rate_model.get_borrow_rate(
            self._compound_market.total_cash,
            self._compound_market.total_borrows,
            self._compound_market.total_reserves,
        )
        supply_rate = self._compound_market.interest_rate_model.get_supply_rate(
            self._compound_market.total_cash,
            self._compound_market.total_borrows,
            self._compound_market.total_reserves,
            self._compound_market.reserve_factor_mantissa,
        )
        # same as here Calculating the APR Using Rate Per Block - https://docs.compound.finance/v2/
        blocks_per_year = 5 * 60 * 24 * 365  # 12 seconds per block
        supply_rate_apr = supply_rate * blocks_per_year
        borrow_rate_apr = borrow_rate * blocks_per_year

        return {
            self.metric_info.utilisation_ratio.name: SingleObservable(value=utilisation, decimals=DEFAULT_DECIMALS),
            self.metric_info.borrow_rate_apr.name: SingleObservable(value=borrow_rate_apr, decimals=DEFAULT_DECIMALS),
            self.metric_info.supply_rate_apr.name: SingleObservable(value=supply_rate_apr, decimals=DEFAULT_DECIMALS),
        }

    def collect_protocol_events(self) -> dict[str, SingleObservable]:
        collected_metrics: dict[str, SingleObservable] = {}
        if not self._compound_market.events_ready_to_collect:
            return collected_metrics
        for event in self._compound_market.events_ready_to_collect:
            if isinstance(event, (Mint, Redeem, Borrow, Repay, Liquidation)):
                metric = getattr(self.metric_info, event.amount_type)
                collected_metrics[metric.name] = SingleObservable(
                    value=collected_metrics.get(metric.name, SingleObservable(0, 0)).value + event.amount,
                    decimals=self._compound_market.underlying_decimals,
                )
            else:
                raise NotImplementedError(f"Event {event} not supported...")
        self._compound_market.events_ready_to_collect.clear()
        return collected_metrics

    def get_global_position(self) -> dict[str, SingleObservable]:
        global_position = {
            self.metric_info.total_cash.name: SingleObservable(
                value=self._compound_market.total_cash, decimals=self._compound_market.underlying_decimals
            ),
            self.metric_info.total_borrow.name: SingleObservable(
                value=self._compound_market.total_borrows, decimals=self._compound_market.underlying_decimals
            ),
            self.metric_info.total_supply.name: SingleObservable(
                value=self._compound_market.total_supply, decimals=self._compound_market.decimals
            ),
            self.metric_info.total_reserves.name: SingleObservable(
                value=self._compound_market.total_reserves, decimals=self._compound_market.underlying_decimals
            ),
        }
        return global_position

    def collect_market_observables(self) -> dict[str, SingleObservable]:
        new_observables: dict[str, SingleObservable] = {}
        new_observables.update(self.get_global_position())
        new_observables.update(self.collect_protocol_events())
        new_observables.update(self.get_rates())
        return new_observables

    def get_all_observables(self, block_number: int, block_timestamp: int) -> dict[str, SingleObservable]:
        # the market observables are already collected by the comptroller - no need to get them separately
        return {}

    ##################################################################################################################
    ######################################## agent observables #######################################################
    ##################################################################################################################
    def collect_collateral_interests(self, wallet: Wallet, exchange_rate: int) -> int:
        collateral_holding = self._agent_collateral_stored.get(wallet.agent_name, 0)
        exchange_rate_stored = self._agent_exchange_rate_stored.get(wallet.agent_name, -1)
        self._agent_cumulated_collateral_interests.setdefault(wallet.agent_name, 0)

        if exchange_rate_stored != -1:
            self._agent_cumulated_collateral_interests[wallet.agent_name] += (
                collateral_holding * exchange_rate - collateral_holding * exchange_rate_stored
            ) // EXPSCALE
        self._agent_collateral_stored[wallet.agent_name] = int(wallet.get_balance_of(self._compound_market.symbol))
        self._agent_exchange_rate_stored[wallet.agent_name] = exchange_rate
        return self._agent_cumulated_collateral_interests[wallet.agent_name]

    def collect_debt_interests(self, wallet: Wallet) -> int:
        index_stored = self._agent_debt_index_stored.get(wallet.agent_name, 0)
        principal_stored = self._agent_principal_debt_stored.setdefault(wallet.agent_name, 0)
        self._agent_cumulated_debt_interests.setdefault(wallet.agent_name, 0)
        new_principal, original_index = self._compound_market.get_borrow_snapshot(wallet)

        if principal_stored != 0:
            self._agent_cumulated_debt_interests[wallet.agent_name] += (
                principal_stored * self._compound_market.borrow_index - principal_stored * index_stored
            ) // original_index

        self._agent_debt_index_stored[wallet.agent_name] = self._compound_market.borrow_index
        self._agent_principal_debt_stored[wallet.agent_name] = new_principal
        return self._agent_cumulated_debt_interests[wallet.agent_name]

    def collect_virtual_positions(self, wallet: Wallet, collect_interests: bool = True) -> dict[str, SingleObservable]:
        virtual_positions: dict[str, SingleObservable] = {}
        debt, collateral, exchange_rate = self._compound_market.get_wallet_virtual_position(wallet)

        # current debt and collateral
        virtual_positions[self.metric_info.current_debt.name] = SingleObservable(
            value=debt, decimals=self._compound_market.underlying_decimals
        )
        virtual_positions[self.metric_info.current_collateral.name] = SingleObservable(
            value=collateral, decimals=self._compound_market.underlying_decimals
        )

        if collect_interests:
            # generated interests
            virtual_positions[self.metric_info.cumulated_collateral_interests.name] = SingleObservable(
                value=self.collect_collateral_interests(wallet, exchange_rate),
                decimals=self._compound_market.underlying_decimals,
            )
            virtual_positions[self.metric_info.cumulated_debt_interests.name] = SingleObservable(
                value=self.collect_debt_interests(wallet), decimals=self._compound_market.underlying_decimals
            )

        return virtual_positions

    def get_agent_observables(
        self, block_number: int, block_timestamp: int, wallet: Wallet
    ) -> dict[str, SingleObservable]:
        return {}

    def get_custom_variable(self, variable_name: str) -> CustomVariable:
        raise NotImplementedError
