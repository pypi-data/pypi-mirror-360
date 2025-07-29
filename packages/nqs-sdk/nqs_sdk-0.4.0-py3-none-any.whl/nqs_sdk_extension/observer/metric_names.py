from abc import ABC
from dataclasses import dataclass

from nqs_sdk_extension.observer.utils import make_metric_name


############### AGENT ###############
@dataclass
class AgentProtocolMetrics(ABC):
    net_position: str
    total_fees: str

    def __init__(self, observer_id: str):
        self.net_position = make_metric_name(observer_id, "net_position")
        self.total_fees = make_metric_name(observer_id, "total_fees")


@dataclass
class AgentMetrics(ABC):
    total_holding: str
    pnl: str
    net_position: str
    total_fees: str
    holdings: dict[str, str]

    def __init__(self, agent: str, protocol: str = "all"):
        self.total_holding = make_metric_name(agent=agent, protocol=protocol, metric="total_holding")
        self.pnl = make_metric_name(agent=agent, protocol=protocol, metric="pnl")
        self.net_position = make_metric_name(protocol=protocol, metric="net_position")
        self.total_fees = make_metric_name(agent=agent, protocol=protocol, metric="total_fees")
        self.holdings = {}


############### COMPOUND ###############
@dataclass
class ComptrollerAgentMetrics(AgentProtocolMetrics):
    debt_collateral_ratio: str
    liquidation_threshold: str
    total_debt: str
    total_collateral: str
    total_cumulated_debt_interests: str
    total_cumulated_collateral_interests: str

    def __init__(self, observer_id: str):
        super().__init__(observer_id)
        self.debt_collateral_ratio = make_metric_name(observer_id, "debt_collateral_ratio")
        self.liquidation_threshold = make_metric_name(observer_id, "liquidation_threshold")
        self.total_debt = make_metric_name(observer_id, "total_debt")
        self.total_collateral = make_metric_name(observer_id, "total_collateral")
        self.total_cumulated_debt_interests = make_metric_name(observer_id, "total_cumulated_debt_interests")
        self.total_cumulated_collateral_interests = make_metric_name(
            observer_id, "total_cumulated_collateral_interests"
        )


@dataclass
class CompoundMarketAgentMetrics(AgentProtocolMetrics):
    current_debt: str
    current_collateral: str
    cumulated_debt_interests: str
    cumulated_collateral_interests: str

    def __init__(self, observer_id: str, token: str):
        super().__init__(observer_id)
        self.current_debt = make_metric_name(observer_id, "current_debt", token=token)
        self.current_collateral = make_metric_name(observer_id, "current_collateral", token=token)
        self.cumulated_debt_interests = make_metric_name(observer_id, "cumulated_debt_interests", token=token)
        self.cumulated_collateral_interests = make_metric_name(
            observer_id, "cumulated_collateral_interests", token=token
        )


@dataclass
class CompoundMarketMetrics(CompoundMarketAgentMetrics):
    utilisation_ratio: str
    borrow_rate_apr: str
    supply_rate_apr: str
    total_cash: str
    total_supply: str
    total_reserves: str
    total_borrow: str
    deposited: str
    redeemed: str
    borrowed: str
    repaid: str
    seized: str

    def __init__(self, observer_id: str, token: str):
        super().__init__(observer_id, token)
        self.utilisation_ratio = make_metric_name(observer_id, "utilisation_ratio", token=token)
        self.borrow_rate_apr = make_metric_name(observer_id, "borrow_rate_apr", token=token)
        self.supply_rate_apr = make_metric_name(observer_id, "supply_rate_apr", token=token)
        self.total_cash = make_metric_name(observer_id, "total_cash", token=token)
        self.total_supply = make_metric_name(observer_id, "total_supply", token=token)
        self.total_reserves = make_metric_name(observer_id, "total_reserves", token=token)
        self.total_borrow = make_metric_name(observer_id, "total_borrow", token=token)
        self.deposited = make_metric_name(observer_id, "deposited", token=token)
        self.redeemed = make_metric_name(observer_id, "redeemed", token=token)
        self.borrowed = make_metric_name(observer_id, "borrowed", token=token)
        self.repaid = make_metric_name(observer_id, "repaid", token=token)
        self.seized = make_metric_name(observer_id, "seized", token=token)


############### Uniswap V3 ###############
@dataclass
class Uniswapv3AgentMetrics(AgentProtocolMetrics):
    liquidity: str
    active_liquidity: str
    token_amount0: str
    token_amount1: str
    # Impermanent loss metrics
    abs_impermanent_loss: str
    perc_impermanent_loss: str
    # Permanent loss metrics
    abs_permanent_loss: str
    # Loss versus rebalancing metrics
    loss_versus_rebalancing: str
    total_fees_relative_to_lvr: str
    # Fees metrics
    fees_collected0: str
    fees_collected1: str
    fees_collected_num: str
    fees_not_collected0: str
    fees_not_collected1: str
    fees_not_collected_num: str
    # Bounds metrics
    upper_bound_price: str
    lower_bound_price: str
    # Greeks metrics
    delta: str
    gamma: str
    theta: str

    def __init__(self, observer_id: str, token0: str, token1: str):
        super().__init__(observer_id)
        self.liquidity = make_metric_name(observer_id, "liquidity")
        self.active_liquidity = make_metric_name(observer_id, "active_liquidity")
        self.token_amount0 = make_metric_name(observer_id, "token_amount", token=token0)
        self.token_amount1 = make_metric_name(observer_id, "token_amount", token=token1)
        self.fees_collected0 = make_metric_name(observer_id, "fees_collected", token=token0)
        self.fees_collected1 = make_metric_name(observer_id, "fees_collected", token=token1)
        self.fees_collected_num = make_metric_name(observer_id, "fees_collected")
        self.fees_not_collected0 = make_metric_name(observer_id, "fees_not_collected", token=token0)
        self.fees_not_collected1 = make_metric_name(observer_id, "fees_not_collected", token=token1)
        self.fees_not_collected_num = make_metric_name(observer_id, "fees_not_collected")
        # Relative bounds metrics
        self.upper_bound_price = make_metric_name(observer_id, "upper_bound_price")
        self.lower_bound_price = make_metric_name(observer_id, "lower_bound_price")
        # Impermanent loss metrics
        self.abs_impermanent_loss = make_metric_name(observer_id, "abs_impermanent_loss")
        self.perc_impermanent_loss = make_metric_name(observer_id, "perc_impermanent_loss")
        self.static_ptf_value = make_metric_name(observer_id, "static_ptf_value")
        # Permanent loss metrics
        self.abs_permanent_loss = make_metric_name(observer_id, "permanent_loss")
        # Loss versus rebalancing metrics
        self.loss_versus_rebalancing = make_metric_name(observer_id, "loss_versus_rebalancing")
        self.total_fees_relative_to_lvr = make_metric_name(observer_id, "total_fees_relative_to_lvr")
        # Greeks metrics
        self.delta = make_metric_name(observer_id, "delta")
        self.gamma = make_metric_name(observer_id, "gamma")
        self.theta = make_metric_name(observer_id, "theta")


@dataclass
class Uniswapv3Metrics(Uniswapv3AgentMetrics):
    pool_liquidity: str
    # Spot metrics
    spot: str
    # Holdings metrics
    holding0: str
    holding1: str
    tvl_num: str
    # Volumes metrics
    volume0: str
    volume1: str
    volume_num: str
    # Fees metrics
    fees0: str
    fees1: str
    total_fees_pool: str
    current_tick: str

    def __init__(self, observer_id: str, token0: str, token1: str):
        super().__init__(observer_id, token0, token1)

        self.pool_liquidity = make_metric_name(observer_id, "liquidity")
        # Spot metrics
        self.spot = make_metric_name(observer_id, "dex_spot")
        # Holdings metrics
        self.holding0 = make_metric_name(observer_id, "total_holdings", token=token0)
        self.holding1 = make_metric_name(observer_id, "total_holdings", token=token1)
        self.tvl_num = make_metric_name(observer_id, "total_value_locked")
        # Volumes metrics
        self.volume0 = make_metric_name(observer_id, "total_volume", token=token0)
        self.volume1 = make_metric_name(observer_id, "total_volume", token=token1)
        self.volume_num = make_metric_name(observer_id, "total_volume_numeraire")
        # Fees metrics
        self.fees0 = make_metric_name(observer_id, "total_fees", token=token0)
        self.fees1 = make_metric_name(observer_id, "total_fees", token=token1)
        self.total_fees_pool = make_metric_name(observer_id, "total_fees")
        self.current_tick = make_metric_name(observer_id, "current_tick")
