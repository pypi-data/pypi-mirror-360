import itertools
from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Type

import numpy as np

from nqs_sdk.utils.pickable_generator import PickableGenerator, StatefulGenerator
from nqs_sdk_extension.constants import AVERAGE_NB_OF_BLOCKS_PER_YEAR
from nqs_sdk_extension.generator.random.eventsim.block_diff_model import (
    BlockDiffECDF,
    BlockDiffNegativeBinomial,
    BlockDiffPoisson,
)


def get_vine_copula() -> Type[Any]:
    from nqs_sdk_extension.generator.random.vine_copula import VineCopula

    return VineCopula


class Process(ABC):
    """
    Base class for random process.
    """

    def __init__(self, *kwargs: Any) -> None:
        """
        Initialization of the process, the arguments (optional) should be the parameters of the process.
        """
        self._my_rng: Any = np.random.default_rng()
        self._use_antithetic_variates: bool = False

    @abstractmethod
    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        """
        The method to generate random paths following the process.
        """
        pass

    @abstractmethod
    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        The method to generate a single random value following the process.
        """
        pass

    @abstractmethod
    def use_antithetic_variates(self) -> bool:
        """
        Returns True if the process uses antithetic variates, False otherwise.
        """
        pass

    def set_seed(self, seed: int, use_antithetic_variates: bool) -> None:
        """
        Set the seed of the process.
        """
        self.seed = seed
        if seed % 2 == 0 or not use_antithetic_variates:
            self._my_rng = np.random.default_rng(seed)
        else:
            # we use the seed - 1 to generate the antithetic variates
            self._use_antithetic_variates = True
            self._my_rng = np.random.default_rng(seed - 1)


class ValueProcess(Process):
    """
    A class representing a value process, i.e. a process that
    will be used to generate values for transactions such as
    amounts of tokens to swap.
    """

    def use_antithetic_variates(self) -> bool:
        """
        Returns True if the process uses antithetic variates, False otherwise.
        """
        return self._use_antithetic_variates


class ChoiceProcess(Process):
    """
    A class representing a choice process, i.e. a process that
    will be used to draw a random value from a list of values.
    """

    def use_antithetic_variates(self) -> bool:
        """
        Always returns False as choice processes do not use antithetic variates.
        """
        return False


class FrequencyProcess(Process):
    """
    A class representing a frequency process, i.e. a process that
    will be used to generate block numbers for transactions such as
    mint and burn transactions.
    """

    def use_antithetic_variates(self) -> bool:
        """
        Always returns False as frequency processes do not use antithetic variates.
        """
        return False

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        The method to generate a single random value following the process.
        """
        raise NotImplementedError("Frequency processes do not have a draw_single method.")


class PoissonProcess(FrequencyProcess):
    """
    A class representing a Poisson process.
    Params :
        intensity (float): The intensity of the Poisson process,
        here it is the number of users to simulate.
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns the next random event time following a Poisson process.
        """
        if ("nb_of_users_to_simulate" in kwargs) == ("nb_of_users_to_simulate_per_year" in kwargs):
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
            Expected either nb_of_users_to_simulate or nb_of_users_to_simulate_per_year but got {kwargs.keys()}."""
            )

        if "nb_of_users_to_simulate" in kwargs:
            if "simulation_length_in_blocks" not in kwargs:
                raise ValueError(
                    f"""Parameters of the process have not been set correctly.
                Expected simulation_length_in_blocks but got {kwargs.keys()}."""
                )
            nb_of_users_to_simulate = kwargs["nb_of_users_to_simulate"]
            simulation_length_in_blocks = kwargs["simulation_length_in_blocks"]
            intensity = nb_of_users_to_simulate / simulation_length_in_blocks

        if "nb_of_users_to_simulate_per_year" in kwargs:
            nb_of_users_to_simulate_per_year = kwargs["nb_of_users_to_simulate_per_year"]
            intensity = nb_of_users_to_simulate_per_year / AVERAGE_NB_OF_BLOCKS_PER_YEAR

        def update(intensity: float) -> Tuple[float, float]:
            return intensity, self._my_rng.exponential(1 / intensity)

        return StatefulGenerator(intensity, update)

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        """
        Returns an array of random event times, the number of events is drawn from a Poisson distribution.
        """
        if "nb_of_users_to_simulate" not in kwargs or "simulation_length_in_blocks" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected nb_of_users_to_simulate and simulation_length_in_blocks but got {kwargs.keys()}."""
            )
        nb_of_users_to_simulate, simulation_length_in_blocks = (
            kwargs["nb_of_users_to_simulate"],
            kwargs["simulation_length_in_blocks"],
        )
        cumulative_nb_of_events = self._my_rng.poisson(nb_of_users_to_simulate)
        event_times = np.array(
            np.floor(np.sort(self._my_rng.uniform(0, simulation_length_in_blocks, cumulative_nb_of_events)))
        )
        return event_times


class FittedPoissonProcess(FrequencyProcess):
    """
    A class representing a calibrated Poisson process, possibly taking seasonality into account.
    Params :
        lam (float): lambda
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns the next random event time following a calibrated Poisson process
        """
        model = BlockDiffPoisson(
            kwargs.get("weekly", False),
            kwargs.get("daily", False),
            kwargs.get("order", 3),
            kwargs.get("lam", 1.0),
            kwargs.get("b", None),
            kwargs.get("timestamp", None),
        )

        def update(block_diff_model: BlockDiffPoisson) -> Tuple[BlockDiffPoisson, int]:
            lam = block_diff_model.get_poisson_lambda()
            return block_diff_model, self._my_rng.poisson(lam)

        return StatefulGenerator(model, update)

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        raise NotImplementedError


class ECDFProcess(Process):
    """
    A class representing a ECDF
    """

    def __init__(self) -> None:
        super().__init__()

    def use_antithetic_variates(self) -> bool:
        """
        Always returns False as choice processes do not use antithetic variates.
        """
        return False

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns the next random event time following the empirical CDF
        """
        if "x" not in kwargs or ("proba" not in kwargs and "q" not in kwargs):
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected x and proba or x and q but got {kwargs.keys()}."""
            )

        model = BlockDiffECDF(
            np.array(kwargs.get("x"), dtype=np.float64),
            np.array(kwargs.get("proba"), np.float64),
            np.array(kwargs.get("q", None), np.float64),
        )

        def update(block_diff_model: BlockDiffECDF) -> Tuple[BlockDiffECDF, int | float]:
            if np.isnan(block_diff_model.q).any():
                return block_diff_model, int(self._my_rng.choice(block_diff_model.x, p=block_diff_model.proba))
            else:
                return block_diff_model, float(
                    np.interp(self._my_rng.uniform(), block_diff_model.x, block_diff_model.q)
                )

        return StatefulGenerator(model, update)

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        raise NotImplementedError


class NegativeBinomial(FrequencyProcess):
    """
    A class representing a Fitted Negative Binomial
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns the next random event time following a Negative Binomial Process
        """
        model = BlockDiffNegativeBinomial(
            weekly=kwargs.get("weekly", False),
            daily=kwargs.get("daily", False),
            order=kwargs.get("order", 3),
            n=kwargs.get("n", 1.0),
            p=kwargs.get("p", 0.5),
            b=kwargs.get("b", None),
            size=kwargs.get("size", None),
            timestamp=kwargs.get("timestamp", None),
        )

        def update(block_diff_model: BlockDiffNegativeBinomial) -> Tuple[BlockDiffNegativeBinomial, int]:
            n, p = block_diff_model.get_parameters()
            return block_diff_model, self._my_rng.negative_binomial(n, p)

        return StatefulGenerator(model, update)

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        raise NotImplementedError


class LinearProcess(FrequencyProcess):
    """
    A class representing a Linear process.
    Params :
        intensity (float): The intensity of the Linear process,
        here it is the number of users to simulate.
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        """
        Returns an array of random event times, the number of events is drawn from a Linear distribution.
        """
        if "nb_of_users_to_simulate" not in kwargs or "simulation_length_in_blocks" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected nb_of_users_to_simulate and simulation_length_in_blocks but got {kwargs.keys()}."""
            )
        nb_of_users_to_simulate, simulation_length_in_blocks = (
            kwargs["nb_of_users_to_simulate"],
            kwargs["simulation_length_in_blocks"],
        )
        times: np.ndarray = np.linspace(0, simulation_length_in_blocks, nb_of_users_to_simulate, endpoint=False)
        return times

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns a random value following a Linear process.
        """
        if "nb_of_users_to_simulate" not in kwargs or "simulation_length_in_blocks" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected nb_of_users_to_simulate and simulation_length_in_blocks but got {kwargs.keys()}."""
            )
        nb_of_users_to_simulate, simulation_length_in_blocks = (
            kwargs["nb_of_users_to_simulate"],
            kwargs["simulation_length_in_blocks"],
        )

        def update(state: Tuple[int, int]) -> Tuple[Tuple[int, int], float]:
            nb_of_users_to_simulate, simulation_length_in_blocks = state
            next_transaction_time = simulation_length_in_blocks / nb_of_users_to_simulate
            return (nb_of_users_to_simulate, simulation_length_in_blocks), next_transaction_time

        return StatefulGenerator((nb_of_users_to_simulate, simulation_length_in_blocks), update)


class UniformProcess(ValueProcess):
    """
    A class representing a uniform process.
    Params :
        a (float): The lower bound of the uniform distribution.
        b (float): The upper bound of the uniform distribution.
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        """
        Returns a random path following a uniform process, shape argument is an integer.
        """
        if "min" not in kwargs or "max" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected min, max and shape but got {kwargs.keys()}."""
            )
        a, b, shape = kwargs["min"], kwargs["max"], kwargs["shape"]
        if self.use_antithetic_variates():
            x = b - self._my_rng.uniform(a, b, shape) + a
        else:
            x = self._my_rng.uniform(a, b, shape)
        values: np.ndarray = x
        return values

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns a random value following a uniform process.
        """
        if "min" not in kwargs or "max" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected min and max but got {kwargs.keys()}."""
            )
        a = kwargs["min"]
        b = kwargs["max"]

        def update(state: Tuple[float, float]) -> Tuple[Tuple[float, float], float]:
            a, b = state
            if self.use_antithetic_variates():
                return state, b - self._my_rng.uniform(a, b) + a
            else:
                return state, self._my_rng.uniform(a, b)

        return StatefulGenerator((a, b), update)


class VineCopulaProcess(ValueProcess):
    """
    A class representing a VineCopula
    Params :
        file_path: path to the json file containing the calibrated parameters
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        """
        Returns a random path following samples from a Vine Copula.
        """
        raise NotImplementedError

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns a random value from the copula distribution
        """
        if "model_params_file" not in kwargs or "x" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected model_params_file and x but got {kwargs.keys()}."""
            )

        file_path = kwargs["model_params_file"]
        x = np.array(kwargs["x"])

        def update(state: Tuple[str, np.ndarray]) -> Tuple[Tuple[str, np.ndarray], list[float]]:
            vine_copula = get_vine_copula()
            copula = vine_copula().get_protocol_copula(state[0])
            u_sim = copula.simulate(n=1, seeds=[self.seed])

            values = [float(np.quantile(state[1][:, i], u_sim[:, i])[0]) for i in range(0, state[1].shape[1])]

            return state, values

        return StatefulGenerator((file_path, x), update)


class NormalProcess(ValueProcess):
    """
    A class representing a normal process.
    Params :
        mean (float): The mean of the normal distribution.
        sigma (float): The standard deviation of the normal distribution.
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        """
        Returns a random path following a normal process. The shape argument is an integer.
        """
        if "mean" not in kwargs or "std" not in kwargs or "shape" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected mean, std and shape but got {kwargs.keys()}."""
            )
        mean, std, shape = kwargs["mean"], kwargs["std"], kwargs["shape"]
        if self.use_antithetic_variates():
            x = mean - self._my_rng.normal(0.0, std, shape)
        else:
            x = mean + self._my_rng.normal(0.0, std, shape)
        values: np.ndarray = x
        return values

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns a random value following a normal process.
        """
        if "mean" not in kwargs or "std" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected mean and std but got {kwargs.keys()}."""
            )
        mean = kwargs["mean"]
        std = kwargs["std"]

        def update(state: Tuple[float, float]) -> Tuple[Tuple[float, float], float]:
            mean, std = state
            if self.use_antithetic_variates():
                return state, mean - self._my_rng.normal(0.0, std)
            else:
                return state, mean + self._my_rng.normal(0.0, std)

        return StatefulGenerator((mean, std), update)


class LogNormalProcess(ValueProcess):
    """
    A class representing a lognormal process.
    Params :
        mu (float): The mu parameter of the lognormal distribution.
        sigma (float): The sigma parameter of the lognormal distribution.
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        """
        Returns a random path following a lognormal process. The shape argument is an integer.
        """
        if "mu" not in kwargs or "sigma" not in kwargs or "shape" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected mu, sigma and shape but got {kwargs.keys()}."""
            )
        mu, sigma, shape = kwargs["mu"], kwargs["sigma"], kwargs["shape"]
        if self.use_antithetic_variates():
            x = np.exp(mu - self._my_rng.normal(0.0, sigma, shape))
        else:
            x = np.exp(mu + self._my_rng.normal(0.0, sigma, shape))
        values: np.ndarray = x
        return values

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns a random value following a lognormal process.
        """
        if "mu" not in kwargs or "sigma" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected mu and sigma but got {kwargs.keys()}."""
            )
        mu = kwargs["mu"]
        sigma = kwargs["sigma"]

        def update(state: Tuple[float, float]) -> Tuple[Tuple[float, float], float]:
            mu, sigma = state
            if self.use_antithetic_variates():
                return state, np.exp(mu - self._my_rng.lognormal(0, sigma))
            else:
                return state, np.exp(mu + self._my_rng.lognormal(0, sigma))

        return StatefulGenerator((mu, sigma), update)


class MultiDimensionalStandardNormalProcess(ValueProcess):
    """
    A class representing a multidimensional standard Gaussian process.
    Params :
        mean (float): The mean of the normal distribution.
        sigma (float): The standard deviation of the normal distribution.
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        """
        Returns a random path following a normal process. The shape argument is an integer.
        """
        if "dim" not in kwargs or "shape" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected dim and shape but got {kwargs.keys()}."""
            )
        dim, shape = kwargs["dim"], kwargs["shape"]
        if self.use_antithetic_variates():
            x = -self._my_rng.standard_normal(size=(shape, dim))
        else:
            x = self._my_rng.standard_normal(size=(shape, dim))
        values: np.ndarray = x
        return values

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns a random value following a normal process.
        """
        if "dim" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected dim but got {kwargs.keys()}."""
            )
        dim = kwargs["dim"]

        def update(dim: int) -> Tuple[int, np.ndarray]:
            if self.use_antithetic_variates():
                return dim, -self._my_rng.standard_normal(size=(1, dim))
            else:
                return dim, self._my_rng.standard_normal(size=(1, dim))

        return StatefulGenerator(dim, update)


class UniformDiscreteProcess(ChoiceProcess):
    """
    A class representing a uniform discrete process.
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        """
        Returns an array of random values following a uniform discrete process. The shape argument is a tuple of ints.
        """
        if "bounds" not in kwargs or "shape" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected bounds and shape but got {kwargs.keys()}."""
            )
        bounds, shape = kwargs["bounds"], kwargs["shape"]
        values: np.ndarray = self._my_rng.integers(low=bounds[0], high=bounds[1], size=shape)
        return values

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns a random value following a uniform discrete process.
        """
        if "bounds" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected bounds but got {kwargs.keys()}."""
            )
        bounds = kwargs["bounds"]

        def update(bounds: Tuple[int, int]) -> Tuple[Tuple[int, int], int]:
            return bounds, self._my_rng.integers(low=bounds[0], high=bounds[1])

        return StatefulGenerator(bounds, update)


class DiscreteProcess(ChoiceProcess):
    """
    A class representing a discrete process.
    Params :
        weights (list): The weights of the discrete distribution.
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        """
        Returns an array of random values following a discrete process. The shape argument is a tuple of ints.
        """
        if "weights" not in kwargs or "shape" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected weights and shape but got {kwargs.keys()}."""
            )
        weights, shape = kwargs["weights"], kwargs["shape"]
        values: np.ndarray = self._my_rng.choice(len(weights), shape, p=weights)
        return values

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns a random value following a discrete process.
        """
        if "weights" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected weights but got {kwargs.keys()}."""
            )
        weights = kwargs["weights"]

        def update(weights: List[float]) -> Tuple[List[float], float]:
            return weights, self._my_rng.choice(len(weights), p=weights)

        return StatefulGenerator(weights, update)


class TwoDimensionalDiscreteProcess(ChoiceProcess):
    """
    A class representing two successive draws without replacement from
    a discrete process represented by a list of weights.
    """

    def __init__(self) -> None:
        super().__init__()

    def draw_multiple(self, **kwargs: Any) -> np.ndarray:
        """
        Returns a random path of two successive draws without replacement following a discrete process.
        """
        if "weights" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected weights but got {kwargs.keys()}."""
            )
        weights, shape = kwargs["weights"], kwargs["shape"]
        joint_probability = {
            (i, j): (p * q) / (1 - p) for (i, p), (j, q) in itertools.permutations(enumerate(weights), 2)
        }
        pairs = list(joint_probability.keys())
        probabilities = list(joint_probability.values())
        indices = self._my_rng.choice(len(pairs), shape, p=probabilities)
        return np.array([pairs[i] for i in indices])

    def draw_single(self, **kwargs: Any) -> PickableGenerator:
        """
        Returns a random value following a discrete process.
        """
        if "weights" not in kwargs:
            raise ValueError(
                f"""Parameters of the process have not been set correctly.
                Expected weights but got {kwargs.keys()}."""
            )
        weights = kwargs["weights"]

        def update(weights: List[float]) -> Tuple[list[float], Tuple[int, int]]:
            joint_probability = {
                (i, j): (p * q) / (1 - p) for (i, p), (j, q) in itertools.permutations(enumerate(weights), 2)
            }
            pairs = list(joint_probability.keys())
            probabilities = list(joint_probability.values())
            index = self._my_rng.choice(len(pairs), p=probabilities)
            return weights, pairs[index]

        return StatefulGenerator(weights, update)


class RandomGenerator:
    def __init__(self, process_dict: dict[str, Process] | None = None) -> None:
        """
        The RandomGenerator should be initialized from the environment with a dict of user-defined processes.
        """
        (
            poisson,
            uniform,
            normal,
            uniform_discrete,
            discrete,
            multidim_std_normal,
            two_dim_discrete,
            linear,
            fitted_poisson,
            negative_binomial,
            ecdf,
            lognormal,
            vine_copula,
        ) = (
            PoissonProcess(),
            UniformProcess(),
            NormalProcess(),
            UniformDiscreteProcess(),
            DiscreteProcess(),
            MultiDimensionalStandardNormalProcess(),
            TwoDimensionalDiscreteProcess(),
            LinearProcess(),
            FittedPoissonProcess(),
            NegativeBinomial(),
            ECDFProcess(),
            LogNormalProcess(),
            VineCopulaProcess(),
        )
        self.process_dict: dict[str, Process] = {
            "poisson": poisson,
            "uniform": uniform,
            "normal": normal,
            "uniform_discrete": uniform_discrete,
            "discrete": discrete,
            "multidim_std_normal": multidim_std_normal,
            "two_dim_discrete": two_dim_discrete,
            "linear": linear,
            "fitted_poisson": fitted_poisson,
            "negative_binomial": negative_binomial,
            "ecdf": ecdf,
            "lognormal": lognormal,
            "vine_copula": vine_copula,
        }
        if process_dict is not None:
            self.process_dict.update(process_dict)

    def set_seed(self, seed: int, use_antithetic_variates: bool) -> None:
        """
        Set the seed of the RandomGenerator.
        """
        for process in self.process_dict.values():
            process.set_seed(seed, use_antithetic_variates)

    def add_process(self, process_name: str, process: Process) -> None:
        """
        Add a process to the RandomGenerator.
        """
        if not isinstance(process, Process):
            raise ValueError("The process {process_name} is not an instance of Process.")
        self.process_dict[process_name] = process

    def remove_process(self, process_name: str) -> None:
        """
        Remove a process from the RandomGenerator.
        """
        if process_name not in self.process_dict:
            raise ValueError("The process {process_name} is not in the RandomGenerator.")
        self.process_dict.pop(process_name, None)

    def get_process(self, process_name: str) -> Process:
        """
        Get a process from the RandomGenerator.
        """
        return self.process_dict[process_name]
