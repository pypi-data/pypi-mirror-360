from abc import ABC
from dataclasses import dataclass, fields

from nqs_sdk_extension.observer.utils import MetricInfo, make_metric_info, remove_agent_from_metric_name


############### AGENT ###############
@dataclass
class AgentProtocolMetrics(ABC):
    net_position: MetricInfo
    total_fees: MetricInfo

    def __init__(self, observer_id: str, agent: str | None = None):
        self.net_position = make_metric_info(observer_id, "net_position")
        self.total_fees = make_metric_info(observer_id, "total_fees", agent=agent)

    def initialise_metric_names_dict(self) -> None:
        """
        create a dictionary representation of the dataclass, to be used when instantiating a RL agent
        :return:
        """
        self.metric_names: dict[str, MetricInfo] = {}
        for _ in fields(self):
            metric_info = getattr(self, _.name)
            if isinstance(metric_info, dict):
                self.metric_names.update({_.name: _ for _ in metric_info.values()})
            else:
                self.metric_names.update({metric_info.name: metric_info})

    def get_metric_info(self, metric_name: str) -> MetricInfo | None:
        metric_wo_agent = remove_agent_from_metric_name(metric_name)
        metric_info_wo_agent = self.metric_names.get(metric_wo_agent)
        if metric_info_wo_agent is not None:
            return metric_info_wo_agent
        metric_info = self.metric_names.get(metric_name)
        return metric_info


############### COMPOUND ###############
@dataclass
class ComptrollerAgentMetrics(AgentProtocolMetrics):
    debt_collateral_ratio: MetricInfo
    liquidation_threshold: MetricInfo
    total_debt: MetricInfo
    total_collateral: MetricInfo
    total_cumulated_debt_interests: MetricInfo
    total_cumulated_collateral_interests: MetricInfo

    def __init__(self, observer_id: str):
        super().__init__(observer_id)
        self.debt_collateral_ratio = make_metric_info(observer_id, "debt_collateral_ratio")
        self.liquidation_threshold = make_metric_info(observer_id, "liquidation_threshold", upper_bound=1.0)
        self.total_debt = make_metric_info(observer_id, "total_debt")
        self.total_collateral = make_metric_info(observer_id, "total_collateral")
        self.total_cumulated_debt_interests = make_metric_info(observer_id, "total_cumulated_debt_interests")
        self.total_cumulated_collateral_interests = make_metric_info(
            observer_id, "total_cumulated_collateral_interests"
        )


@dataclass
class CompoundMarketAgentMetrics(AgentProtocolMetrics):
    current_debt: MetricInfo
    current_collateral: MetricInfo
    total_cumulated_debt_interests: MetricInfo
    total_cumulated_collateral_interests: MetricInfo
    cumulated_debt_interests: MetricInfo
    cumulated_collateral_interests: MetricInfo

    def __init__(self, observer_id: str, token: str):
        super().__init__(observer_id)
        self.current_debt = make_metric_info(observer_id, "current_debt", token=token)
        self.current_collateral = make_metric_info(observer_id, "current_collateral", token=token)
        self.total_cumulated_debt_interests = make_metric_info(
            observer_id, "total_cumulated_debt_interests", token=token
        )
        self.total_cumulated_collateral_interests = make_metric_info(
            observer_id, "total_cumulated_collateral_interests", token=token
        )
        self.cumulated_debt_interests = make_metric_info(observer_id, "cumulated_debt_interests", token=token)
        self.cumulated_collateral_interests = make_metric_info(
            observer_id, "cumulated_collateral_interests", token=token
        )


@dataclass
class CompoundMarketMetrics(CompoundMarketAgentMetrics):
    utilisation_ratio: MetricInfo
    borrow_rate_apr: MetricInfo
    supply_rate_apr: MetricInfo
    total_cash: MetricInfo
    total_supply: MetricInfo
    total_reserves: MetricInfo
    total_borrow: MetricInfo
    deposited: MetricInfo
    redeemed: MetricInfo
    borrowed: MetricInfo
    repaid: MetricInfo
    seized: MetricInfo

    def __init__(self, observer_id: str, token: str):
        super().__init__(observer_id, token)
        self.utilisation_ratio = make_metric_info(observer_id, "utilisation_ratio", token=token, upper_bound=1.0)
        self.borrow_rate_apr = make_metric_info(observer_id, "borrow_rate_apr", token=token)
        self.supply_rate_apr = make_metric_info(observer_id, "supply_rate_apr", token=token)
        self.total_cash = make_metric_info(observer_id, "total_cash", token=token)
        self.total_supply = make_metric_info(observer_id, "total_supply", token=token)
        self.total_reserves = make_metric_info(observer_id, "total_reserves", token=token)
        self.total_borrow = make_metric_info(observer_id, "total_borrow", token=token)
        self.deposited = make_metric_info(observer_id, "deposited", token=token)
        self.redeemed = make_metric_info(observer_id, "redeemed", token=token)
        self.borrowed = make_metric_info(observer_id, "borrowed", token=token)
        self.repaid = make_metric_info(observer_id, "repaid", token=token)
        self.seized = make_metric_info(observer_id, "seized", token=token)
