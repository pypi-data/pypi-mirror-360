import datetime

import numpy as np

from nqs_sdk_extension.spot.utils import (
    datetime64_to_timestamp,
    string_to_datetime,
    timestamp_to_datetime,
    timestamp_to_string,
)


def test_timestamp_to_string() -> None:
    assert timestamp_to_string(0) == "1970-01-01T00:00:00+00:00"
    assert timestamp_to_string(1438269973) == "2015-07-30T15:26:13+00:00"


def test_timestamp_to_datetime() -> None:
    assert timestamp_to_datetime(0) == datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    assert timestamp_to_datetime(1438269973) == datetime.datetime(2015, 7, 30, 15, 26, 13, tzinfo=datetime.timezone.utc)


def test_datetime_to_timestamp() -> None:
    assert datetime64_to_timestamp(np.datetime64("2015-07-30T15:26:13")) == 1438269973


def test_string_to_datetime() -> None:
    assert string_to_datetime("2015-07-30T15:26:13+00:00") == datetime.datetime(
        2015, 7, 30, 15, 26, 13, tzinfo=datetime.timezone.utc
    )
