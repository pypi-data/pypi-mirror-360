import unittest

from dotenv import load_dotenv

from nqs_sdk_extension.run_configuration.utils import make_mapping_block_number_timestamp
from nqs_sdk_extension.spot import DataLoader
from tests.utils.utils import data_source_from_environment


class TestMakeMappingBlockNumberTimestamp(unittest.TestCase):
    def test_make_mapping_block_number_timestamp(self) -> None:
        load_dotenv()
        DataLoader.quantlib_source().update(source=data_source_from_environment())
        start = 1709247600
        end = 1711839600
        mapping_block_number_timestamp = make_mapping_block_number_timestamp(timestamp_start=start, timestamp_end=end)
        self.assertLessEqual(
            min(mapping_block_number_timestamp.keys()),
            start,
            "First timestamp should be less than the start timestamp",
        )
        self.assertLessEqual(
            max(mapping_block_number_timestamp.keys()),
            end,
            "Last timestamp should be less than the end timestamp",
        )


if __name__ == "__main__":
    unittest.main()
