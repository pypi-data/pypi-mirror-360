from collections import deque

import numpy as np
import pytest

from smoothiepy.filter.basefilter import Filter1D, Filter2D


class Filter1DImpl(Filter1D):
    def _process_next(self, buffer: np.array) -> float | int:
        return buffer[0].astype(float)


class TestFilter1D:
    @pytest.fixture
    def filter_instance(self):
        return Filter1DImpl(window_size=3)

    def test_invalid_window_size(self):
        with pytest.raises(ValueError, match="window_size must be greater than 0"):
            Filter1DImpl(window_size=0)
        with pytest.raises(ValueError, match="window_size must be greater than 0"):
            Filter1DImpl(window_size=-1)

    def test_init(self, filter_instance):
        assert filter_instance.window_size == 3
        assert len(filter_instance.buffer) == 0
        assert filter_instance.last_buffer_value == 0.0

    def test_next_updates_buffer(self, filter_instance):
        filter_instance.next(5.0)
        assert filter_instance.buffer == deque([5.0], maxlen=3)

    def test_next_returns_some_value(self, filter_instance):
        result = filter_instance.next(5.0)
        assert result is not None

    def test_buffer_does_not_exceed_max(self, filter_instance):
        for i in range(20):
            filter_instance.next(i)
        assert len(filter_instance.buffer) == 3

    def test_next_saves_last_value(self, filter_instance):
        filter_instance.next(5.0)
        filter_instance.next(6.0)
        filter_instance.next(7.0)
        filter_instance.next(8.0)
        filter_instance.next(9.0)
        assert filter_instance.last_buffer_value == 6.0


class Filter2DImpl(Filter2D):
    def _process_next(self, buffer_x: np.array, buffer_y: np.array) \
            -> tuple[float | int, float | int]:
        return buffer_x[0].astype(float), buffer_y[0].astype(float)


class TestFilter2D:
    @pytest.fixture
    def filter_instance(self):
        return Filter2DImpl(window_size_x=3, window_size_y=3)

    def test_invalid_window_size(self):
        with pytest.raises(ValueError, match="window_size_x and window_size_y must be greater than 0"):
            Filter2DImpl(window_size_x=0, window_size_y=3)
        with pytest.raises(ValueError, match="window_size_x and window_size_y must be greater than 0"):
            Filter2DImpl(window_size_x=3, window_size_y=-1)
        with pytest.raises(ValueError, match="window_size_x and window_size_y must be greater than 0"):
            Filter2DImpl(window_size_x=-1, window_size_y=-1)

    def test_init(self, filter_instance):
        assert filter_instance.window_size_x == 3
        assert filter_instance.window_size_y == 3
        assert len(filter_instance.buffer_x) == 0
        assert len(filter_instance.buffer_y) == 0

    def test_next_updates_buffer_x(self, filter_instance):
        filter_instance.next(5.0, 10.0)
        assert filter_instance.buffer_x == deque([5.0], maxlen=3)

    def test_next_updates_buffer_y(self, filter_instance):
        filter_instance.next(5.0, 10.0)
        assert filter_instance.buffer_y == deque([10.0], maxlen=3)

    def test_next_returns_some_value(self, filter_instance):
        result = filter_instance.next(5.0, 10.0)
        assert isinstance(result, tuple)
        assert result is not None

    def test_buffer_does_not_exceed_max_x(self, filter_instance):
        for i in range(20):
            filter_instance.next(i, i + 10)
        assert len(filter_instance.buffer_x) == 3

    def test_buffer_does_not_exceed_max_y(self, filter_instance):
        for i in range(20):
            filter_instance.next(i, i + 10)
        assert len(filter_instance.buffer_y) == 3
