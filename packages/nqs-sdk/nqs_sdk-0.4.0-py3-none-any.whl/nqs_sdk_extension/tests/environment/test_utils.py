# type: ignore
import pytest
from dotenv import load_dotenv

from nqs_sdk_extension.run_configuration.utils import (
    make_mapping_block_number_timestamp,
    make_regular_mapping_block_number_timestamp,
    set_mapping_block_number_timestamp,
)
from nqs_sdk_extension.spot import DataLoader


def test_basic_mapping() -> None:
    block_start = 1
    block_end = 3
    block_spacing = 12
    expected_result = {
        1: 1438269973 + 1 * block_spacing,
        2: 1438269973 + 2 * block_spacing,
        3: 1438269973 + 3 * block_spacing,
    }
    assert (
        make_regular_mapping_block_number_timestamp(
            block_start=block_start, block_end=block_end, block_spacing=block_spacing
        )
        == expected_result
    )


def test_zero_spacing() -> None:
    block_start = 1
    block_end = 3
    block_spacing = 0
    expected_result = {1: 1438269973, 2: 1438269973, 3: 1438269973}
    assert (
        make_regular_mapping_block_number_timestamp(
            block_start=block_start, block_end=block_end, block_spacing=block_spacing
        )
        == expected_result
    )


def test_negative_spacing() -> None:
    block_start = 1
    block_end = 3
    block_spacing = -12
    expected_result = {1: 1438269973 - 12, 2: 1438269973 - 24, 3: 1438269973 - 36}
    assert (
        make_regular_mapping_block_number_timestamp(
            block_start=block_start, block_end=block_end, block_spacing=block_spacing
        )
        == expected_result
    )


def test_invalid_range() -> None:
    block_start = 5
    block_end = 3
    block_spacing = 12
    expected_result: dict[int, int] = {}
    assert (
        make_regular_mapping_block_number_timestamp(
            block_start=block_start, block_end=block_end, block_spacing=block_spacing
        )
        == expected_result
    )


def test_error_case() -> None:
    block_start = 18_725_000
    block_end = 18_735_000
    res = make_regular_mapping_block_number_timestamp(block_start, block_end)
    assert len(res) == 10_000 + 1
    assert res[18_725_162] is not None


@pytest.mark.skip(reason="TODO: check why dummy mappinng is different")
def test_dummy_mapping_block_number_timestamp() -> None:
    # dummy + blocks
    load_dotenv()  # get
    start_block = 18725000
    end_block = 18725000 + 10
    mapping = set_mapping_block_number_timestamp(block_number_start=start_block, block_number_end=end_block)
    dummy_mapping = make_regular_mapping_block_number_timestamp(block_start=start_block, block_end=end_block)
    assert set(mapping.keys()) == set(dummy_mapping.keys())
    assert len(mapping) == len(dummy_mapping)
    blocks = sorted(mapping.keys())
    for i in range(1, len(blocks)):
        real_diff = mapping[blocks[i]] - mapping[blocks[i - 1]]
        dummy_diff = dummy_mapping[blocks[i]] - dummy_mapping[blocks[i - 1]]
        assert real_diff == dummy_diff

    first_block = blocks[0]
    offset = mapping[first_block] - dummy_mapping[first_block]

    adjusted_dummy_mapping = {block: timestamp + offset for block, timestamp in dummy_mapping.items()}
    assert mapping == adjusted_dummy_mapping

    # dummy + timestamp
    timestamp_start = 1701871303
    timestamp_end = 1701874303
    mapping = set_mapping_block_number_timestamp(timestamp_start=timestamp_start, timestamp_end=timestamp_end)
    dummy_mapping = make_regular_mapping_block_number_timestamp(
        timestamp_start=timestamp_start, timestamp_end=timestamp_end
    )
    print(f"mapping: {mapping}")
    print(f"dummy_mapping: {dummy_mapping}")
    assert mapping == dummy_mapping


def test_quantlib_mapping_block_number_timestamp(source) -> None:
    d = DataLoader.quantlib_source()
    d.update(source=source)

    # quantlib + blocks
    start_block = 18725000
    end_block = 18725000 + 10
    mapping = set_mapping_block_number_timestamp(block_number_start=start_block, block_number_end=end_block)
    quantlib_mapping = make_mapping_block_number_timestamp(block_start=start_block, block_end=end_block)
    assert mapping == quantlib_mapping
    assert len(mapping) == 11
    assert list(mapping.keys())[0] == 18725000
    assert list(mapping.keys())[-1] == 18725000 + 10

    # quantlib + timestamp
    timestamp_start = 1701871303
    timestamp_end = 1701874303
    mapping = set_mapping_block_number_timestamp(timestamp_start=timestamp_start, timestamp_end=timestamp_end)
    dummy_mapping = make_mapping_block_number_timestamp(timestamp_start=timestamp_start, timestamp_end=timestamp_end)
    assert mapping == dummy_mapping
    assert len(mapping) == 242
    assert abs(list(mapping.values())[0] - timestamp_start) < 20
    assert abs(list(mapping.values())[-1] - timestamp_end) < 20
