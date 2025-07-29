# type: ignore
import logging

import pytest

from nqs_sdk import preload as preload
from tests.utils.utils import data_source_from_environment


@pytest.fixture
def source() -> str:
    source = data_source_from_environment()
    logging.info(str(source))
    return source
