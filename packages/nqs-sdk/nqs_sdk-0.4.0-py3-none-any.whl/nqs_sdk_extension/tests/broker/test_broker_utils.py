import numpy as np

from nqs_sdk_extension.miner.utils import deduplicate_time_series


def test_numpy_searchsorted() -> None:
    """
    numppy.searchsorted() is used by the broker to deduplicate timeseries for microlanguage
    """
    timestamps = np.array([1, 2, 2, 3, 3, 3, 4, 4, 4, 4])
    values = np.array([10, 11, 12, 13, 14, 15, 16, 17, 18, 19])

    timestamps_unique, values_unique = deduplicate_time_series(timestamps=timestamps, values=values)
    assert np.array_equal(values_unique, [10, 12, 15, 19])
