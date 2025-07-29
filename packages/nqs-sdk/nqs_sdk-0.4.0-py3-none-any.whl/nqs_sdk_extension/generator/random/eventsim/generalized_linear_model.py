from abc import ABC, abstractmethod
from typing import Optional

import numpy as np

# Taken from Event Simulator Project - only the predict methods are preserved


class Link(ABC):
    @abstractmethod
    def link(self, eta: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def inv_link(self, mu: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def inv_link_derivative(self, mu: np.ndarray) -> np.ndarray:
        pass


class LogLink(Link):
    def link(self, eta: np.ndarray) -> np.ndarray:
        return np.array(np.exp(eta))

    def inv_link(self, mu: np.ndarray) -> np.ndarray:
        return np.array(np.log(mu))

    def inv_link_derivative(self, mu: np.ndarray) -> np.ndarray:
        return 1 / mu


class GeneralizedLinearModel(ABC):
    def __init__(self, link: Link, family: str, b: Optional[np.ndarray]):
        self.link = link
        self.family = family
        self.b = b

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.b is None:
            raise ValueError("The parameter b is not fitted")
        if x.shape[1] != self.b.shape[0]:
            raise ValueError("Dimensions of x and b do not match")

        return self.link.link(x @ self.b)


class Poisson(GeneralizedLinearModel):
    def __init__(self, b: Optional[np.ndarray]) -> None:
        super().__init__(LogLink(), "poisson", b)


class NegativeBinomial(GeneralizedLinearModel):
    def __init__(self, b: Optional[np.ndarray], size: float) -> None:
        super().__init__(LogLink(), "negative_binomial", b)
        self.size = size
