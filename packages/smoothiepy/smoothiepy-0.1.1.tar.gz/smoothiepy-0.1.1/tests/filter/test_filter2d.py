import pytest

from smoothiepy.filter.filter2d import OffsetFilter2D


class TestOffsetFilter2D:
    @pytest.fixture
    def filter_instance(self):
        return OffsetFilter2D(offset=5.0, offset_y=10.0)

    def test_init(self, filter_instance):
        assert filter_instance.offset_x == 5.0
        assert filter_instance.offset_y == 10.0

    def test_offset_y_defaults_to_offset(self):
        filter_instance = OffsetFilter2D(offset=5.0)
        assert filter_instance.offset_x == 5.0
        assert filter_instance.offset_y == 5.0

    @pytest.mark.parametrize(
        "offset_x, offset_y, data_x, data_y, expected_x, expected_y",
        [
            (1.0, 2.0, 3.0, 5.0, 4.0, 7.0),
            (3.5, 4.5, 1.0, 1.0, 4.5, 5.5),
            (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            (-1.0, -2.0, -1.0, -1.5, -2.0, -3.5)
        ]
    )
    def test_process_next(self, offset_x, offset_y, data_x, data_y, expected_x, expected_y):
        filter_instance = OffsetFilter2D(offset=offset_x, offset_y=offset_y)
        result = filter_instance.next(data_x, data_y)
        assert result == (expected_x, expected_y)
