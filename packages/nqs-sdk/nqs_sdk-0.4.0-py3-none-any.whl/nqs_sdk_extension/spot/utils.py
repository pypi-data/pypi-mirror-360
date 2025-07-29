from datetime import datetime, timezone
from typing import Any, Tuple

import numpy as np
from numpy.typing import NDArray

from nqs_sdk_extension.token_utils import wrap_token


def get_wrapped_spot(spot: Tuple[str, str]) -> Tuple[str, str]:
    ccy1, ccy2 = spot[0], spot[1]
    return wrap_token(ccy1), wrap_token(ccy2)


def volatility(s: NDArray[np.float64], lookback_period: int = -1) -> Any | NDArray[np.float64]:
    """
    Returns the volatility of a time serie
    :param s: time series to compute with
    :param lookback_period:
    :return:
    """
    # compute volatility using Pandas rolling and std methods
    if lookback_period == -1:
        lookback_period = 30
    delta_t = 1.0 / 365

    s_shifted = np.zeros(len(s))
    s_shifted[1:] = s[:-1]
    returns = np.array([np.log(x / x_shifted) if x_shifted > 0 else np.inf for x, x_shifted in zip(s, s_shifted)])
    np.nan_to_num(returns, copy=False, posinf=0, neginf=0)

    # Create a 2D view of the array with shape (num_windows, window)
    returns_view = np.lib.stride_tricks.sliding_window_view(returns, (lookback_period,))

    return 100 * np.std(returns_view, axis=-1, ddof=1) / np.sqrt(delta_t)


def drift(s: NDArray[np.float64], lookback_period: int = -1, window_size: int = -1) -> Any | NDArray[np.float64]:
    """
    Return the drift of a time serie
    :param s: time series to compute with
    :param lookback_period:
    :param window_size:
    :return:
    """
    # compute drift using Pandas rolling and std methods
    if lookback_period == -1:
        lookback_period = len(s) - 1
        # print(f"lookback_period defaulted to {lookback_period}")
    if window_size == -1:
        window_size = len(s) - lookback_period
        # print(f"window_size defaulted to {window_size}")

    assert (s > 0).all()
    s_shifted = np.zeros(len(s))
    s_shifted[lookback_period:] = s[:-lookback_period]
    returns = [np.log(x / x_shifted) if x_shifted > 0 else np.inf for x, x_shifted in zip(s, s_shifted)]
    returns = returns[lookback_period:]
    assert window_size <= len(returns)
    # Create a 2D view of the array with shape (num_windows, window)
    returns_view = np.lib.stride_tricks.sliding_window_view(returns, (window_size,))

    return 100 * np.mean(returns_view, axis=-1) / lookback_period


def timestamp_to_string(timestamp: int) -> str:
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def timestamp_to_datetime(timestamp: int) -> datetime:
    return string_to_datetime(timestamp_to_string(timestamp))


def datetime64_to_timestamp(dt: np.datetime64) -> int:
    return int(dt.astype(datetime).replace(tzinfo=timezone.utc).timestamp())


def string_to_datetime(string: str) -> datetime:
    return datetime.fromisoformat(string).replace(tzinfo=timezone.utc)


def datetime_to_timestamp(dt_str: str) -> int:
    import pytz  # type: ignore

    dt_str_clean = dt_str.replace(" UTC", "")
    dt_obj = datetime.strptime(dt_str_clean, "%Y-%m-%d %H:%M:%S")
    dt_obj = pytz.UTC.localize(dt_obj)
    timestamp = int(dt_obj.timestamp())
    return timestamp
