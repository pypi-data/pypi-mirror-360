import pytest

from smoothiepy.filter.basefilter import MovingAverageType
from smoothiepy.filter.filter2d_naive import (
    NaiveSimpleMovingAverageFilter2D,
    NaiveWeightedMovingAverageFilter2D,
    NaiveGaussianAverageFilter2D,
    NaiveMedianAverageFilter2D,
    NaiveExponentialMovingAverageFilter2D,
    NaiveCumulativeMovingAverageFilter2D,
    NaiveFixationSmoothFilter2D,
    NaiveMultiPassMovingAverage2D
)


class TestNaiveSimpleMovingAverageFilter2D:
    @pytest.fixture
    def filter_instance(self):
        return NaiveSimpleMovingAverageFilter2D(window_size=3, window_size_y=4)

    def test_window_size_2d_filter_is_one(self, filter_instance):
        assert filter_instance.window_size_x == 1
        assert filter_instance.window_size_y == 1

    def test_window_size_1d_filter_matches(self, filter_instance):
        assert filter_instance.filter_x.window_size == 3
        assert filter_instance.filter_y.window_size == 4

    def test_process_returns_some_value(self, filter_instance):
        result = filter_instance._process_next([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        assert isinstance(result, tuple)
        assert result is not None

    def test_window_size_y_defaults_to_window_size(self):
        filter_instance = NaiveSimpleMovingAverageFilter2D(window_size=5)
        assert filter_instance.filter_x.window_size == 5
        assert filter_instance.filter_y.window_size == 5


class TestNaiveWeightedMovingAverageFilter2D:
    @pytest.fixture
    def filter_instance(self):
        return NaiveWeightedMovingAverageFilter2D(window_size=3, window_size_y=4)

    def test_window_size_2d_filter_is_one(self, filter_instance):
        assert filter_instance.window_size_x == 1
        assert filter_instance.window_size_y == 1

    def test_window_size_1d_filter_matches(self, filter_instance):
        assert filter_instance.filter_x.window_size == 3
        assert filter_instance.filter_y.window_size == 4

    def test_process_returns_some_value(self, filter_instance):
        filter_instance.next(10.0, 40.0)
        filter_instance.next(20.0, 50.0)
        filter_instance.next(3.0, 6.0)
        result = filter_instance.next(9.0, 7.0)
        assert isinstance(result, tuple)
        assert result is not None

    def test_window_size_y_defaults_to_window_size(self):
        filter_instance = NaiveWeightedMovingAverageFilter2D(window_size=5)
        assert filter_instance.filter_x.window_size == 5
        assert filter_instance.filter_y.window_size == 5


class TestNaiveGaussianAverageFilter2D:
    @pytest.fixture
    def filter_instance(self):
        return NaiveGaussianAverageFilter2D(window_size=3, window_size_y=4, std_dev_x=1.0, std_dev_y=1.5)

    def test_window_size_2d_filter_is_one(self, filter_instance):
        assert filter_instance.window_size_x == 1
        assert filter_instance.window_size_y == 1

    def test_window_size_1d_filter_matches(self, filter_instance):
        assert filter_instance.filter_x.window_size == 3
        assert filter_instance.filter_y.window_size == 4

    def test_process_returns_some_value(self, filter_instance):
        result = filter_instance._process_next([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        assert isinstance(result, tuple)
        assert result is not None

    def test_window_size_y_defaults_to_window_size(self):
        filter_instance = NaiveGaussianAverageFilter2D(window_size=5, std_dev_x=1.0, std_dev_y=1.5)
        assert filter_instance.filter_x.window_size == 5
        assert filter_instance.filter_y.window_size == 5


class TestNaiveMedianAverageFilter2D:
    @pytest.fixture
    def filter_instance(self):
        return NaiveMedianAverageFilter2D(window_size=3, window_size_y=4)

    def test_window_size_2d_filter_is_one(self, filter_instance):
        assert filter_instance.window_size_x == 1
        assert filter_instance.window_size_y == 1

    def test_window_size_1d_filter_matches(self, filter_instance):
        assert filter_instance.filter_x.window_size == 3
        assert filter_instance.filter_y.window_size == 4

    def test_process_returns_some_value(self, filter_instance):
        result = filter_instance._process_next([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        assert isinstance(result, tuple)
        assert result is not None

    def test_window_size_y_defaults_to_window_size(self):
        filter_instance = NaiveMedianAverageFilter2D(window_size=5)
        assert filter_instance.filter_x.window_size == 5
        assert filter_instance.filter_y.window_size == 5


class TestNaiveExponentialMovingAverageFilter2D:
    @pytest.fixture
    def filter_instance(self):
        return NaiveExponentialMovingAverageFilter2D(alpha=0.5, alpha_y=0.7)

    def test_window_size_2d_filter_is_one(self, filter_instance):
        assert filter_instance.window_size_x == 1
        assert filter_instance.window_size_y == 1

    def test_process_returns_some_value(self, filter_instance):
        result = filter_instance._process_next([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        assert isinstance(result, tuple)
        assert result is not None

    def test_alpha_y_defaults_to_alpha_x(self):
        filter_instance = NaiveExponentialMovingAverageFilter2D(alpha=0.3)
        assert filter_instance.filter_x.alpha == 0.3
        assert filter_instance.filter_y.alpha == 0.3


class TestNaiveCumulativeMovingAverageFilter2D:
    @pytest.fixture
    def filter_instance(self):
        return NaiveCumulativeMovingAverageFilter2D()

    def test_window_size_2d_filter_is_one(self, filter_instance):
        assert filter_instance.window_size_x == 1
        assert filter_instance.window_size_y == 1

    def test_process_returns_some_value(self, filter_instance):
        result = filter_instance._process_next([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        assert isinstance(result, tuple)
        assert result is not None


class TestNaiveFixationSmoothFilter2D:
    @pytest.fixture
    def filter_instance(self):
        return NaiveFixationSmoothFilter2D(window_size=3, threshold=5.0, window_size_y=4, threshold_y=6.0)

    def test_window_size_2d_filter_is_one(self, filter_instance):
        assert filter_instance.window_size_x == 1
        assert filter_instance.window_size_y == 1

    def test_window_size_1d_filter_matches(self, filter_instance):
        assert filter_instance.filter_x.window_size == 3
        assert filter_instance.filter_y.window_size == 4

    def test_process_returns_some_value(self, filter_instance):
        result = filter_instance._process_next([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        assert isinstance(result, tuple)
        assert result is not None

    def test_window_size_y_defaults_to_window_size(self):
        filter_instance = NaiveFixationSmoothFilter2D(window_size=5, threshold=5.0, threshold_y=6.0)
        assert filter_instance.filter_x.window_size == 5
        assert filter_instance.filter_y.window_size == 5

    def test_threshold_y_defaults_to_threshold(self):
        filter_instance = NaiveFixationSmoothFilter2D(window_size=5, threshold=5.0)
        assert filter_instance.filter_x.threshold == 5.0
        assert filter_instance.filter_y.threshold == 5.0


class TestNaiveMultiPassMovingAverage2D:
    @pytest.fixture
    def filter_instance(self):
        return NaiveMultiPassMovingAverage2D(
            window_size=3, 
            num_passes=2, 
            window_size_y=4, 
            num_passes_y=3,
            average_filter_type_x=MovingAverageType.SIMPLE,
            average_filter_type_y=MovingAverageType.GAUSSIAN
        )

    def test_window_size_2d_filter_is_one(self, filter_instance):
        assert filter_instance.window_size_x == 1
        assert filter_instance.window_size_y == 1

    def test_window_size_1d_filter_matches(self, filter_instance):
        assert filter_instance.filter_x.smoother.filter_list[0].window_size == 3
        assert filter_instance.filter_y.smoother.filter_list[0].window_size == 4

    def test_process_returns_some_value(self, filter_instance):
        result = filter_instance._process_next([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        assert isinstance(result, tuple)
        assert result is not None

    def test_window_size_y_defaults_to_window_size(self):
        filter_instance = NaiveMultiPassMovingAverage2D(
            window_size=5,
            num_passes=2,
            num_passes_y=3,
            average_filter_type_x=MovingAverageType.SIMPLE,
            average_filter_type_y=MovingAverageType.GAUSSIAN
        )
        assert filter_instance.filter_x.smoother.filter_list[0].window_size == 5
        assert filter_instance.filter_y.smoother.filter_list[0].window_size == 5

    def test_num_passes_y_defaults_to_num_passes(self):
        filter_instance = NaiveMultiPassMovingAverage2D(
            window_size=5,
            num_passes=3,
            average_filter_type_x=MovingAverageType.SIMPLE,
            average_filter_type_y=MovingAverageType.GAUSSIAN
        )
        assert filter_instance.filter_x.num_passes == 3
        assert filter_instance.filter_y.num_passes == 3

    def test_average_filter_type_y_defaults_to_average_filter_type_x(self):
        filter_instance = NaiveMultiPassMovingAverage2D(
            window_size=5,
            num_passes=2,
            average_filter_type_x=MovingAverageType.GAUSSIAN
        )
        assert filter_instance.filter_x.average_filter_type == MovingAverageType.GAUSSIAN
        assert filter_instance.filter_y.average_filter_type == MovingAverageType.GAUSSIAN
