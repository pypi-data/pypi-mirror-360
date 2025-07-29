import logging
from decimal import Decimal
from typing import Dict, Optional

from nqs_pycore import Wallet

from nqs_sdk_extension.agent.abc_agent import ABCAgent
from nqs_sdk_extension.agent.agent_action import CustomVariable
from nqs_sdk_extension.observer import DEFAULT_DECIMALS, ABCObserver, SingleObservable
from nqs_sdk_extension.observer.metric_names import AgentMetrics
from nqs_sdk_extension.observer.utils import make_metric_name, prefix_agent_to_metric_name


class AgentObserver(ABCObserver):
    def __init__(self, agent: ABCAgent):
        super().__init__()
        self._agent = agent
        self._initial_holding: int | None = None

    def set_environment(self, observable_id: str, env_observers: Optional[Dict[str, ABCObserver]]) -> None:
        if env_observers is None:
            raise ValueError("Agent observability needs to be provided with environment observers")
        self._observer_id = observable_id
        self._env_observers = env_observers
        self.metric_names = AgentMetrics(agent=self._observer_id)

    def aggregate_portfolio_metrics(self, block_number: int, block_timestamp: int) -> dict[str, SingleObservable]:
        new_observables: dict[str, SingleObservable] = {}
        current_position_value = 0
        total_fees = 0
        for obs_id, observer in self._env_observers.items():
            agent_obs = observer.get_agent_observables(block_number, block_timestamp, self._agent.wallet)
            agent_obs = self._prefix_agent_to_all_observables(agent_obs)

            protocol = obs_id if obs_id != self._observer_id else "all"
            current_position_value += agent_obs.get(
                make_metric_name(agent=self._observer_id, protocol=protocol, metric="net_position"),
                SingleObservable(value=0, decimals=self.numeraire_decimals),
            ).value
            total_fees += agent_obs.get(
                make_metric_name(agent=self._observer_id, protocol=protocol, metric="total_fees"),
                SingleObservable(value=0, decimals=self.numeraire_decimals),
            ).value
            new_observables.update(agent_obs)
        new_observables[self.metric_names.total_holding] = SingleObservable(
            decimals=self.numeraire_decimals, value=current_position_value
        )
        new_observables[self.metric_names.total_fees] = SingleObservable(
            decimals=self.numeraire_decimals, value=total_fees
        )
        return new_observables

    def get_all_observables(self, block_number: int, block_timestamp: int) -> dict[str, SingleObservable]:
        new_observables = self.aggregate_portfolio_metrics(block_number, block_timestamp)
        current_position_value = new_observables[self.metric_names.total_holding].value

        if self._initial_holding is None:
            self._initial_holding = current_position_value

        new_observables[self.metric_names.pnl] = SingleObservable(
            value=current_position_value - self._initial_holding, decimals=self.numeraire_decimals
        )
        return new_observables

    def get_custom_variable(self, variable_name: str) -> CustomVariable:
        return self._agent.custom_variables[variable_name]

    # ------------------- Protected methods -------------------

    def _prefix_agent_to_all_observables(self, observables: dict[str, SingleObservable]) -> dict[str, SingleObservable]:
        return {prefix_agent_to_metric_name(k, self._observer_id): v for k, v in observables.items()}

    def get_agent_observables(
        self, block_number: int, block_timestamp: int, wallet: Wallet
    ) -> dict[str, SingleObservable]:
        """
        Return the holdings of the user's wallet, in integer representation
        """
        all_holdings: dict[str, SingleObservable] = {}
        if self._agent.wallet.agent_name != wallet.agent_name:
            return all_holdings

        total_wallet_holdings = 0
        spot_prices = self.spot_oracle.get_selected_spots(
            [
                (x, self.spot_oracle.numeraire)
                for x in set(self._agent.wallet.get_list_tokens()).intersection(self.spot_oracle.tokens)
            ],
            block_timestamp,
        )
        for token in self._agent.wallet.get_list_tokens():
            try:
                token_balance = self._agent.wallet.get_balance_of(token)
            except Exception as e:
                if "Cannot convert NaN value to u128" not in str(e):
                    raise e
                else:
                    logging.warning(
                        f"Unexpected NaN while getting the balance of {token}: {e} {block_number} {block_timestamp}"
                    )
                    token_balance = 0

            if token not in self.metric_names.holdings.keys():
                names_dict = {"protocol": "all", "metric": "wallet_holdings", "token": token}
                self.metric_names.holdings[token] = make_metric_name(**names_dict)
            if token not in self._agent.wallet.tokens_metadata:
                raise ValueError(
                    f"Token {token} not found in the wallet's metadata. Please check that the token has "
                    f"been added to the backtest configuration"
                )
            all_holdings.update(
                {
                    self.metric_names.holdings[token]: SingleObservable(
                        value=token_balance, decimals=self._agent.wallet.tokens_metadata[token].decimals
                    )
                }
            )

            if token in self.spot_oracle.tokens:
                total_wallet_holdings += (
                    token_balance
                    * int(
                        Decimal(spot_prices[(token, self.spot_oracle.numeraire)])
                        * 10 ** (2 * DEFAULT_DECIMALS - self._agent.wallet.tokens_metadata[token].decimals)
                    )
                    // 10 ** (2 * DEFAULT_DECIMALS - self.numeraire_decimals)
                )

        all_holdings.update(
            {
                self.metric_names.net_position: SingleObservable(
                    value=total_wallet_holdings, decimals=self.numeraire_decimals
                )
            }
        )
        return all_holdings
