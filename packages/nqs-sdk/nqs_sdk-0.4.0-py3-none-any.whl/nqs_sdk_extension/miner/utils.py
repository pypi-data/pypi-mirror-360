from typing import Tuple

import numpy as np


def deduplicate_time_series(timestamps: np.ndarray, values: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    # keep unique timestamps
    timestamps_unique, _ = np.unique(timestamps, return_index=True)
    last_index = np.searchsorted(timestamps, timestamps_unique, side="right") - 1
    values_unique = values[last_index]
    return timestamps_unique, values_unique
