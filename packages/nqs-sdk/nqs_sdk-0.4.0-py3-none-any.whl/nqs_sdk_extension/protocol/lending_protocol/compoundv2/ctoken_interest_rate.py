import copy

from nqs_sdk_extension.state.compoundv2 import StateInterestRateModel

BASE: int = 10**18


class CTokenInterestRateModel:
    """
    Interest Rate Model for cTokens (Not only parameters can be updated, but interest rate models themselves can be
    updated)
    """

    def __init__(
        self,
        state: StateInterestRateModel,
    ):
        self.multiplier_per_block = state.multiplier_per_block
        self.base_rate_per_block = state.base_rate_per_block
        self.jump_multiplier_per_block = state.jump_multiplier_per_block
        self.kink = state.kink
        self.base = state.base
        self.blocks_per_year = state.blocks_per_year

    @staticmethod
    def utilization_rate(cash: int, borrows: int, reserves: int) -> int:
        if borrows == 0:
            return 0

        return borrows * BASE // (cash + borrows - reserves)

    def get_borrow_rate(self, cash: int, borrows: int, reserves: int) -> int:
        util = self.utilization_rate(cash, borrows, reserves)

        if util <= self.kink:
            return (util * self.multiplier_per_block // BASE) + self.base_rate_per_block
        else:
            normal_rate = (self.kink * self.multiplier_per_block // BASE) + self.base_rate_per_block
            excess_util = util - self.kink
            return (excess_util * self.jump_multiplier_per_block // BASE) + normal_rate

    def get_supply_rate(self, cash: int, borrows: int, reserves: int, reserve_factor_mantissa: int) -> int:
        one_minus_reserve_factor = BASE - reserve_factor_mantissa
        borrow_rate = self.get_borrow_rate(cash, borrows, reserves)
        rate_to_pool = borrow_rate * one_minus_reserve_factor // BASE
        return self.utilization_rate(cash, borrows, reserves) * rate_to_pool // BASE

    def get_state(self) -> StateInterestRateModel:
        state = StateInterestRateModel(
            multiplier_per_block=self.multiplier_per_block,
            base_rate_per_block=self.base_rate_per_block,
            jump_multiplier_per_block=self.jump_multiplier_per_block,
            kink=self.kink,
            base=self.base,
            blocks_per_year=self.blocks_per_year,
        )
        state = copy.deepcopy(state)
        return state
