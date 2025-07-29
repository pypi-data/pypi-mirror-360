import unittest
from typing import Any

import numpy as np

from nqs_sdk.utils.pickable_generator import NoneGenerator, PickableGenerator
from nqs_sdk_extension.generator.random.random_generator import (
    DiscreteProcess,
    LinearProcess,
    NormalProcess,
    PoissonProcess,
    Process,
    RandomGenerator,
    UniformDiscreteProcess,
    UniformProcess,
)


class TestRandomGenerator(unittest.TestCase):
    def test_poisson_process(self) -> None:
        poisson = PoissonProcess()
        nb_users = 1000
        poisson_params = {"nb_of_users_to_simulate": nb_users}
        draw = poisson.draw_multiple(**poisson_params, simulation_length_in_blocks=100)
        self.assertTrue(np.all(draw <= 100), "Times should not exceed 100")
        new_draw = poisson.draw_multiple(**poisson_params, simulation_length_in_blocks=100)
        self.assertTrue((draw.shape != new_draw.shape) or (np.any(draw != new_draw)), "Draws should be different")

    def test_uniform_process(self) -> None:
        uniform = UniformProcess()
        min, max = 0, 100
        uniform_params = {"min": min, "max": max}
        draw = uniform.draw_multiple(**uniform_params, shape=100)
        self.assertTrue(np.all(draw <= max), "Draws should not exceed max")
        self.assertTrue(np.all(draw >= min), "Draws should not be lower than min")
        new_draw = uniform.draw_multiple(**uniform_params, shape=100)
        self.assertFalse(np.all(draw == new_draw), "Draws should be different")
        single_draw = next(uniform.draw_single(**uniform_params))
        self.assertTrue(min <= single_draw <= max, "Draw should be between min and max")
        new_single_draw = next(uniform.draw_single(**uniform_params))
        self.assertNotEqual(single_draw, new_single_draw, "Draws should be different")

    def test_normal_process(self) -> None:
        normal = NormalProcess()
        mean, std = 0, 1
        normal_params = {"mean": mean, "std": std}
        draw = normal.draw_multiple(**normal_params, shape=100)
        new_draw = normal.draw_multiple(**normal_params, shape=100)
        self.assertFalse(np.all(draw == new_draw), "Draws should be different")
        single_draw = next(normal.draw_single(**normal_params))
        new_single_draw = next(normal.draw_single(**normal_params))
        self.assertNotEqual(single_draw, new_single_draw, "Draws should be different")

    def test_discrete_process(self) -> None:
        discrete = DiscreteProcess()
        weights = [0.1, 0.2, 0.3, 0.4]
        discrete_params = {"weights": weights}
        single_draw = next(discrete.draw_single(**discrete_params))
        self.assertTrue(0 <= single_draw < len(weights), "Draw should be between 0 and 3")

        shape = (2, 3)
        discrete_params_multiple = {"weights": weights, "shape": shape}
        multiple_draws = discrete.draw_multiple(**discrete_params_multiple)
        self.assertTrue(
            np.all(0 <= multiple_draws) and np.all(multiple_draws <= 3),
            f"Draw should be between {0} (inclusive) and {len(weights)} (exclusive)",
        )

    def test_uniform_discrete_process(self) -> None:
        uniform_discrete = UniformDiscreteProcess()
        bounds = (3, 19)
        uniform_discrete_params = {"bounds": bounds}
        single_draw = next(uniform_discrete.draw_single(**uniform_discrete_params))
        self.assertTrue(
            bounds[0] <= single_draw < bounds[1],
            f"Draw should be between {bounds[0]} (inclusive) and {bounds[1]} (exclusive)",
        )

        shape = (2, 3)
        uniform_discrete_params_multiple = {"bounds": bounds, "shape": shape}
        multiple_draws = uniform_discrete.draw_multiple(**uniform_discrete_params_multiple)
        self.assertTrue(
            np.all(bounds[0] <= multiple_draws) and np.all(multiple_draws < bounds[1]),
            f"Draw should be between {bounds[0]} (inclusive) and {bounds[1]} (exclusive)",
        )

    def test_linear_process(self) -> None:
        linear = LinearProcess()
        linear_params = {"nb_of_users_to_simulate": 100, "simulation_length_in_blocks": 10000}
        draw = linear.draw_multiple(**linear_params)
        self.assertTrue(np.all(draw <= 10000), "Times should not exceed 10000")
        self.assertTrue(len(draw) == 100, "Draws should be of length 1000")
        new_draw = linear.draw_multiple(**linear_params)
        self.assertTrue(np.all(draw == new_draw), "Draws should be the same")
        single_draw = next(linear.draw_single(**linear_params))
        self.assertEqual(
            single_draw,
            linear_params["simulation_length_in_blocks"] / linear_params["nb_of_users_to_simulate"],
            "Draw should be the same as the average",
        )
        new_single_draw = next(linear.draw_single(**linear_params))
        self.assertEqual(single_draw, new_single_draw, "Draws should be the same")
        # draw n times using single and compare to multiple
        n = 100
        # single draw values should accumulate to the same as multiple draw
        single_draws = np.array([0] + [next(linear.draw_single(**linear_params)) for _ in range(n - 1)])
        cumulative_single_draws = np.cumsum(single_draws)
        multiple_draws = linear.draw_multiple(**linear_params)
        self.assertTrue(np.all(cumulative_single_draws == multiple_draws), "Draws should be the same")

    def test_draw_through_random_generator(self) -> None:
        this_random_generator = RandomGenerator()
        poisson_params = {"nb_of_users_to_simulate": 1000}
        draw = this_random_generator.process_dict["poisson"].draw_multiple(
            **poisson_params, simulation_length_in_blocks=100
        )
        self.assertTrue(np.all(draw <= 100), "Times should not exceed 100")

        uniform_params = {"min": 0, "max": 100}
        draw = this_random_generator.process_dict["uniform"].draw_multiple(**uniform_params, shape=100)
        self.assertTrue(np.all(draw <= 100), "Draws should not exceed 100")
        self.assertTrue(np.all(draw >= 0), "Draws should not be lower than 0")
        new_draw = this_random_generator.process_dict["uniform"].draw_multiple(**uniform_params, shape=100)
        self.assertFalse(np.all(draw == new_draw), "Draws should be different")

        normal_params = {"mean": 0, "std": 1}
        draw = this_random_generator.process_dict["normal"].draw_multiple(**normal_params, shape=100)
        new_draw = this_random_generator.process_dict["normal"].draw_multiple(**normal_params, shape=100)
        self.assertFalse(np.all(draw == new_draw), "Draws should be different")

    def test_implement_new_process(self) -> None:
        this_random_generator = RandomGenerator()

        class Custom(Process):
            def __init__(self) -> None:
                return None

            def draw_multiple(self, **kwargs: Any) -> np.ndarray:
                shape: int = kwargs["shape"]
                return shape * np.array([1, 2, 3])

            def draw_single(self, **kwargs: Any) -> PickableGenerator:
                return NoneGenerator()

            def use_antithetic_variates(self) -> bool:
                return False

        custom_process = Custom()
        this_random_generator.add_process("custom", custom_process)
        args = {"shape": 1}
        draw = this_random_generator.process_dict["custom"].draw_multiple(**args)
        self.assertTrue(np.all(draw == np.array([1, 2, 3])), "Draws should be [1,2,3]")


if __name__ == "__main__":
    unittest.main()
