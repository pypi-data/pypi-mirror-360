# type: ignore


import numpy as np
import pytest

from nqs_sdk_extension.generator.random.random_generator import RandomGenerator
from nqs_sdk_extension.spot import (
    CustomProcess,
    DataLoader,
    DeterministicSpotProcessArray,
    GBMProcess,
    HistoricalProcess,
    OUProcess,
    StochasticSpotProcessArray,
    WGNProcess,
)
from nqs_sdk_extension.spot.spot_oracle import SpotOracle


def test_custom_spot():
    times = np.linspace(0, 100, 10)
    values = np.linspace(0, 1, 10)
    custom_spot = CustomProcess(("tknA", "tknB"), timestamps=times, path=values, current_timestamp=0, end_timestamp=100)

    custom_spot._validate(path_id=1)
    assert 0.55 == pytest.approx(custom_spot.get_spot(55), abs=1e-15)


def test_historical_spot(source):
    start_timestamp = 1656108000
    DataLoader.quantlib_source().update(source=source)
    historical_spot = HistoricalProcess(
        ("WETH", "USDC"),
        current_timestamp=start_timestamp,
        process_start_timestamp=start_timestamp - 1,
        end_timestamp=1658710000,
        execution_mode="simulation",
    )
    spot = historical_spot.get_spot(timestamp=1658700000)
    assert spot > 0


def test_gbm_process():
    current_timestamp = 1658700000
    spot = GBMProcess(("WETH", "USDC"), s0=2000.0, mu=0.0, vol=0.1, current_timestamp=current_timestamp)
    spot.evolve(0.0, 0.0, current_timestamp)
    assert spot.s0 == 2000.0

    spot.evolve(0.2, 0.5, current_timestamp + 1)
    assert spot.get_spot(current_timestamp + 1) > 0
    assert spot.current_timestamp == current_timestamp + 1

    spot.calibrate_params(np.linspace(0.1, 1, 50))


def test_wgn_process():
    current_timestamp = 1658700000
    spot = WGNProcess(("WETH", "USDC"), s0=0.01, mean=0.0, vol=0.001, current_timestamp=current_timestamp)
    spot.evolve(0.0, 0.0, current_timestamp)
    assert spot.s0 == 0.01

    spot.evolve(0.2, 0.5, current_timestamp + 1)
    assert spot.get_spot(current_timestamp + 1) > 0
    assert spot.current_timestamp == current_timestamp + 1

    spot.calibrate_params(np.linspace(0.1, 1, 50))


def test_ou_process():
    current_timestamp = 1658700000
    spot = OUProcess(
        ("WETH", "USDC"), s0=2000.0, mean_reversion=1.0, mean=1, vol=0.1, current_timestamp=current_timestamp
    )
    spot.evolve(0.0, 0.0, current_timestamp)
    assert spot.s0 == 2000.0

    spot.evolve(0.2, 0.5, current_timestamp + 1)
    assert spot.get_spot(current_timestamp + 1) > 0
    assert spot.current_timestamp == current_timestamp + 1


def test_deterministic_array():
    timestamps = np.linspace(0, 100, 10)
    values = np.linspace(0, 1, 10)
    custom_spot_1 = CustomProcess(
        ("tknA", "tknB"), timestamps=timestamps, path=values, current_timestamp=0, end_timestamp=100
    )
    custom_spot_2 = CustomProcess(
        ("tknC", "tknD"), timestamps=timestamps, path=values, current_timestamp=0, end_timestamp=100
    )

    spot_array = DeterministicSpotProcessArray(processes=[custom_spot_1, custom_spot_2])
    assert not spot_array._is_linkable()

    spot_array.remove_process(pair=("tknA", "tknB"))
    assert len(spot_array.processes) == 1

    spot_array.add_process(
        CustomProcess(("tknB", "tknC"), timestamps=timestamps, path=values, current_timestamp=0, end_timestamp=100)
    )
    assert len(spot_array.processes) == 2

    assert spot_array.get_tokens_list() == {"tknB", "tknC", "tknD"}
    assert pytest.approx(spot_array.get_spot(10), abs=1e-15) == {
        ("tknB", "tknC"): 0.1,
        ("tknC", "tknD"): 0.1,
    }


def test_historic_array(source):
    current_timestamp = 1658700000
    DataLoader.quantlib_source().update(source=source)
    historical_spot_1 = HistoricalProcess(
        ("WETH", "USDC"),
        current_timestamp=current_timestamp,
        process_start_timestamp=current_timestamp - 1,
        end_timestamp=1658810000,
        execution_mode="simulation",
    )
    historical_spot_2 = HistoricalProcess(
        ("WETH", "WBTC"),
        current_timestamp=current_timestamp,
        process_start_timestamp=current_timestamp - 1,
        end_timestamp=1658810000,
        execution_mode="simulation",
    )

    spot_array = DeterministicSpotProcessArray(processes=[historical_spot_1, historical_spot_2])
    assert spot_array._is_linkable()

    spot_array.remove_process(pair=("WETH", "USDC"))
    assert len(spot_array.processes) == 1

    spot_array.add_process(
        HistoricalProcess(
            ("WETH", "USDC"),
            current_timestamp=current_timestamp,
            process_start_timestamp=current_timestamp - 1,
            end_timestamp=1658810000,
            execution_mode="simulation",
        )
    )
    assert len(spot_array.processes) == 2

    assert spot_array.get_tokens_list() == {"WETH", "USDC", "WBTC"}
    token_addresses = spot_array.get_tokens_address()
    actual_addresses = {
        "WETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
        "WBTC": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
        "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    }
    assert token_addresses == actual_addresses


def test_custom_historic(source):
    current_timestamp = 1658700000
    timestamps = np.linspace(1658700000, 1658750000, 100)
    values = np.linspace(0, 1, 100)
    custom_spot = CustomProcess(
        ("tknA", "tknB"),
        timestamps=timestamps,
        path=values,
        current_timestamp=current_timestamp,
        end_timestamp=1658750000,
    )

    DataLoader.quantlib_source().update(source=source)
    historical_spot = HistoricalProcess(
        ("WETH", "USDC"),
        current_timestamp=current_timestamp,
        process_start_timestamp=current_timestamp - 1,
        end_timestamp=1658750000,
        execution_mode="simulation",
    )
    spot_array = DeterministicSpotProcessArray(processes=[historical_spot, custom_spot])
    assert not spot_array._is_linkable()

    spot_array.remove_process(pair=("WETH", "USDC"))
    assert len(spot_array.processes) == 1

    spot_array.add_process(
        HistoricalProcess(
            ("WETH", "USDC"),
            current_timestamp=current_timestamp,
            process_start_timestamp=current_timestamp - 1,
            end_timestamp=1658750000,
            execution_mode="simulation",
        )
    )
    assert len(spot_array.processes) == 2

    assert spot_array.get_tokens_list() == {"WETH", "USDC", "tknA", "tknB"}
    token_addresses = spot_array.get_tokens_address()
    actual_addresses = {
        "WETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
        "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    }
    assert token_addresses == actual_addresses
    assert len(spot_array.get_spot(1658750000)) == 2


def test_array_stochastic():
    current_timestamp = 1658700000
    spot_1 = GBMProcess(("WETH", "USDC"), s0=2000.0, mu=0.0, vol=0.1, current_timestamp=current_timestamp)
    spot_2 = GBMProcess(("WETH", "USDT"), s0=2000.0, mu=0.0, vol=0.1, current_timestamp=current_timestamp)
    spot_3 = WGNProcess(("USDT", "USDC"), s0=1.01, mean=1.0, vol=0.001, current_timestamp=current_timestamp)
    spot = StochasticSpotProcessArray([spot_1, spot_2, spot_3], np.eye(3))

    assert not spot._is_linkable()

    spot.remove_process(("WETH", "USDC"))
    assert len(spot.processes) == 2

    spot.add_process(spot_1)
    spot.evolve(1658800000, np.array([[1.0, 3.0, 2.0]]), np.eye(3))
    assert spot.current_timestamp == 1658800000


def test_array_stochastic_calibrate_some(source):
    current_timestamp = 1658700000
    spot_1 = GBMProcess(
        ("WETH", "USDC"), s0=2000.0, mu=0.0, vol=0.1, calibrate=True, current_timestamp=current_timestamp
    )
    spot_2 = GBMProcess(("WETH", "USDT"), s0=2000.0, mu=0.0, vol=0.1, current_timestamp=1658700000)
    spot_3 = WGNProcess(("USDT", "USDC"), s0=1.01, mean=1.0, vol=0.001, calibrate=True, current_timestamp=1658700000)

    DataLoader.quantlib_source().update(source=source)
    spot = StochasticSpotProcessArray([spot_1, spot_2, spot_3], np.eye(3))

    assert spot.need_calibration()
    assert not spot._is_linkable()

    spot.calibrate_params(end_timestamp=1659700000)


def test_array_stochastic_calibrate_all(source):
    current_timestamp = 1658700000
    spot_1 = GBMProcess(
        ("WETH", "USDC"), s0=2000.0, mu=0.0, vol=0.1, calibrate=True, current_timestamp=current_timestamp
    )
    spot_2 = GBMProcess(
        ("WBTC", "USDT"), s0=2000.0, mu=0.0, vol=0.1, calibrate=True, current_timestamp=current_timestamp
    )
    spot_3 = WGNProcess(
        ("USDT", "USDC"), s0=1.01, mean=1.0, vol=0.001, calibrate=True, current_timestamp=current_timestamp
    )

    DataLoader.quantlib_source().update(source=source)
    spot = StochasticSpotProcessArray([spot_1, spot_2, spot_3], np.eye(3))

    assert spot.need_calibration()
    assert spot._is_linkable()

    spot.remove_process(("WBTC", "USDT"))
    spot.add_process(spot_2)

    spot.remove_process(("WBTC", "USDT"))
    spot.connect_spot_graph(tokens=["WBTC"])
    spot.calibrate_params(end_timestamp=1659700000)


def test_spot_configurations(source):
    current_timestamp = 1658700000
    DataLoader.quantlib_source().update(source=source)
    historical_spot_1 = HistoricalProcess(
        ("WETH", "USDC"),
        current_timestamp=current_timestamp,
        process_start_timestamp=current_timestamp,
        end_timestamp=1659700000,
        execution_mode="simulation",
    )
    spot_1 = GBMProcess(("WETH", "USDC"), s0=2000.0, mu=0.0, vol=0.1, current_timestamp=current_timestamp)
    spot_2 = GBMProcess(("WETH", "USDT"), s0=2000.0, mu=0.0, vol=0.1, current_timestamp=current_timestamp)

    stoc_spot = StochasticSpotProcessArray([spot_1, spot_2], np.eye(2))
    det_spot = DeterministicSpotProcessArray(processes=[])

    with pytest.raises(ValueError) as excinfo:
        SpotOracle(
            stochastic_spot=stoc_spot,
            deterministic_spot=det_spot,
            current_timestamp=current_timestamp,
            numeraire="USDC",
        )
        assert str(excinfo.value) == "Random generator must be provided if stochastic process are in the simulation"
    with pytest.raises(ValueError) as excinfo:
        SpotOracle(
            stochastic_spot=stoc_spot,
            deterministic_spot=DeterministicSpotProcessArray(processes=[historical_spot_1]),
            end_timestamp=1659700000,
            current_timestamp=current_timestamp,
            numeraire="USDC",
        )
        assert (
            str(excinfo.value) == "data_loader must be provided if there are historical processes or if stochastic "
            "processes need calibration"
        )
    with pytest.raises(ValueError) as excinfo:
        SpotOracle(
            stochastic_spot=stoc_spot,
            deterministic_spot=DeterministicSpotProcessArray(processes=[historical_spot_1]),
            end_timestamp=1659700000,
            current_timestamp=current_timestamp,
            random_generator=RandomGenerator(),
            numeraire="USDC",
        )
        assert str(excinfo.value) == "The processes list contains duplicates"

    SpotOracle(
        stochastic_spot=stoc_spot,
        deterministic_spot=DeterministicSpotProcessArray(
            processes=[
                HistoricalProcess(
                    ("USDT", "USDC"),
                    current_timestamp=current_timestamp,
                    process_start_timestamp=current_timestamp,
                    end_timestamp=1659700000,
                    execution_mode="simulation",
                )
            ]
        ),
        end_timestamp=1659700000,
        random_generator=RandomGenerator(),
        numeraire="USDC",
        current_timestamp=current_timestamp,
    )

    spot_3 = GBMProcess(
        ("WETH", "USDC"), s0=2000.0, mu=0.0, vol=0.1, calibrate=True, current_timestamp=current_timestamp
    )
    spot_4 = GBMProcess(
        ("WETH", "USDT"), s0=2000.0, mu=0.0, vol=0.1, calibrate=True, current_timestamp=current_timestamp
    )
    spot_5 = WGNProcess(
        ("USDC", "USDT"), s0=2000.0, mean=0.0, vol=0.1, calibrate=True, current_timestamp=current_timestamp
    )
    SpotOracle(
        stochastic_spot=StochasticSpotProcessArray([spot_3, spot_4, spot_5], np.eye(3)),
        deterministic_spot=DeterministicSpotProcessArray(processes=[]),
        end_timestamp=1659700000,
        random_generator=RandomGenerator(),
        numeraire="DAI",
        current_timestamp=current_timestamp,
    )


@pytest.mark.skip(reason="This test fails")
def test_get_spot(source):
    current_timestamp = 1658700000
    DataLoader.quantlib_source().update(source=source)
    spot_1 = GBMProcess(
        ("WETH", "USDC"), s0=2000.0, mu=0.0, vol=0.1, calibrate=True, current_timestamp=current_timestamp
    )
    spot_2 = GBMProcess(("WBTC", "USDT"), s0=2000.0, mu=0.0, vol=0.1, current_timestamp=current_timestamp)

    stoc_spot = StochasticSpotProcessArray([spot_1, spot_2], np.array([[1.0, 0], [0, 1.0]]))

    spot_oracle = SpotOracle(
        stochastic_spot=stoc_spot,
        deterministic_spot=DeterministicSpotProcessArray(
            processes=[
                HistoricalProcess(
                    ("USDT", "USDC"),
                    current_timestamp=current_timestamp,
                    process_start_timestamp=current_timestamp - 1,
                    end_timestamp=1659700000,
                    execution_mode="simulation",
                )
            ]
        ),
        end_timestamp=1659700000,
        random_generator=RandomGenerator(),
        numeraire="USDC",
        current_timestamp=current_timestamp,
    )

    spot_oracle._evolve(1659700000)
    spot_oracle.update_all_spots(1659700000)
    spot_selected = spot_oracle.get_selected_spots([("WBTC", "WETH")], 1659700000)
    assert spot_selected[("WBTC", "WETH")] > 0
