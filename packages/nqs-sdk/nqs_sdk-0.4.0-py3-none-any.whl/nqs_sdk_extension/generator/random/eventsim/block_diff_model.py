from typing import Optional, Tuple

import numpy as np

from nqs_sdk_extension.generator.random.eventsim.base_model import BaseModel
from nqs_sdk_extension.generator.random.eventsim.generalized_linear_model import NegativeBinomial, Poisson


class BlockDiffModel(BaseModel):
    def __init__(
        self,
        supports_seasonality: bool = False,
        weekly: bool = False,
        daily: bool = False,
        order: int = 3,
    ) -> None:
        super().__init__(supports_seasonality, weekly, daily, order)


class BlockDiffPoisson(BlockDiffModel):
    def __init__(
        self,
        weekly: bool = False,
        daily: bool = False,
        order: int = 3,
        lam: float = 1.0,
        b: Optional[np.ndarray] = None,
        timestamp: Optional[int] = None,
    ) -> None:
        super().__init__(True, weekly, daily, order)
        self.timestamp = timestamp
        if not self.daily and not self.weekly:
            self.lam = lam
        else:
            self.statsmodel = Poisson(b)

    def get_poisson_lambda(self) -> float:
        if not self.daily and not self.weekly:
            mean = self.lam
        else:
            exog = self.get_seasonal_regressor(self.timestamp)  # type: ignore
            mean = float(self.statsmodel.predict(np.array(list(exog.values()), ndmin=2)))

        return mean


class BlockDiffNegativeBinomial(BlockDiffModel):
    def __init__(
        self,
        weekly: bool = False,
        daily: bool = False,
        order: int = 3,
        n: float = 1.0,
        p: float = 0.5,
        b: Optional[np.ndarray] = None,
        size: Optional[int] = None,
        timestamp: Optional[int] = None,
    ) -> None:
        super().__init__(True, weekly, daily, order)
        self.timestamp = timestamp

        if not self.daily and not self.weekly:
            self.n = n
            self.p = p
        else:
            self.statsmodel = NegativeBinomial(np.array(b), size)  # type: ignore

    def get_parameters(self) -> Tuple[float, float]:
        if not self.daily and not self.weekly:
            n = self.n
            p = self.p
        else:
            exog = self.get_seasonal_regressor(self.timestamp)  # type: ignore
            mean = float(self.statsmodel.predict(np.array(list(exog.values()), ndmin=2))[0])
            n = self.statsmodel.size
            p = n / (n + mean)

        return n, p


class BlockDiffECDF(BlockDiffModel):
    def __init__(self, x: np.ndarray, proba: np.ndarray, q: np.ndarray) -> None:
        super().__init__()
        self.x = x
        self.proba = proba
        self.q = q
