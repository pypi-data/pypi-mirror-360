"""
Contains the two-dimensional naive filter implementation using
two 1D filters in x and y directions.
"""
from abc import ABC
import numpy as np

from smoothiepy.filter.basefilter import Filter2D, Filter1D, MovingAverageType
from smoothiepy.filter.filter1d import (
    SimpleMovingAverageFilter1D, WeightedMovingAverageFilter1D,
    GaussianAverageFilter1D, MedianAverageFilter1D,
    ExponentialMovingAverageFilter1D, CumulativeMovingAverageFilter1D,
    FixationSmoothFilter1D, MultiPassMovingAverage1D
)


class NaiveFilter2D(Filter2D, ABC):
    """
    Provides a basic 2D filtering mechanism, where input data is processed
    through two 1D filters (`filter_x` and `filter_y`). It is intended to serve as
     a straightforward 2D filtering implementation that deals with basic
     use cases of filtering in two dimensions.

    :ivar filter_x: A 1D filter is applied on the x-buffer data.
    :type filter_x: Filter1D | None
    :ivar filter_y: A 1D filter is applied on the y-buffer data.
    :type filter_y: Filter1D | None
    """
    def __init__(self):
        super().__init__(window_size_x=1, window_size_y=1)
        self.filter_x: Filter1D | None = None
        self.filter_y: Filter1D | None = None

    def _process_next(self, buffer_x: np.array, buffer_y: np.array) \
            -> tuple[float | int, float | int]:
        avg_x = self.filter_x.next(buffer_x[0])
        avg_y = self.filter_y.next(buffer_y[0])
        return avg_x, avg_y


class NaiveSimpleMovingAverageFilter2D(NaiveFilter2D):
    """
    The NaiveSimpleMovingAverageFilter2D class implements a 2D simple moving
    average filter. It smooths sequential data points along both x and y
    axes using separate 1D simple moving average filters.

    :param window_size: The size of the moving average window for the x-axis.
        Must be a positive integer.
        If the y-axis window size is not provided, the
        x-axis window size will be used for both axes.
    :type window_size: int
    :param window_size_y: The size of the moving average window for the y-axis.
        Must be a positive integer.
        If not provided, it defaults to the x-axis window size.
    :type window_size_y: int
    """
    def __init__(self, window_size, window_size_y=None):
        if window_size_y is None:
            window_size_y = window_size
        super().__init__()
        self.filter_x = SimpleMovingAverageFilter1D(window_size=window_size)
        self.filter_y = SimpleMovingAverageFilter1D(window_size=window_size_y)


class NaiveWeightedMovingAverageFilter2D(NaiveFilter2D):
    """
    A 2D filter that computes a weighted average of the input data over a specified window size
    in both x and y directions. The weights are linearly decreasing from 1 to 0, applied to the
    most recent data points.

    :param window_size: The size of the weighted moving average window for the x-axis.
        Must be a positive integer.
        If the y-axis window size is not provided, the
        x-axis window size will be used for both axes.
    :type window_size: int
    :param window_size_y: The size of the weighted moving average window for the y-axis.
    :type window_size_y: int
    """
    def __init__(self, window_size: int, window_size_y: int = None):
        if window_size_y is None:
            window_size_y = window_size
        super().__init__()
        self.filter_x = WeightedMovingAverageFilter1D(window_size=window_size)
        self.filter_y = WeightedMovingAverageFilter1D(window_size=window_size_y)


class NaiveGaussianAverageFilter2D(NaiveFilter2D):
    """
    A 2D filter that implements a Gaussian Average Filter for two-dimensional data.
    It applies a Gaussian weighting function over
    a sliding window of data in both x and y directions.

    :param window_size: The size of the Gaussian window for the x-axis.
        Must be a positive integer.
        If the y-axis window size is not provided, the
        x-axis window size will be used for both axes.
    :type window_size: int
    :param window_size_y: The size of the Gaussian window for the y-axis.
        Must be a positive integer.
        If not provided, it defaults to the x-axis window size.
    :type window_size_y: int
    :param std_dev_x: The standard deviation of the Gaussian distribution for the x-axis.
        Must be a positive value. If not provided, it defaults to one-third of the window size.
    :type std_dev_x: float
    :param std_dev_y: The standard deviation of the Gaussian distribution for the y-axis.
        Must be a positive value. If not provided, it defaults to one-third of the window size_y.
    :type std_dev_y: float
    """
    def __init__(self, window_size: int, window_size_y: int = None,
                 std_dev_x: float = None, std_dev_y: float = None):
        if window_size_y is None:
            window_size_y = window_size
        super().__init__()
        self.filter_x = GaussianAverageFilter1D(window_size=window_size, std_dev=std_dev_x)
        self.filter_y = GaussianAverageFilter1D(window_size=window_size_y, std_dev=std_dev_y)


class NaiveMedianAverageFilter2D(NaiveFilter2D):
    """
    A 2D filter that computes the median of the input data over a specified
    window size in both x and y directions.

    :param window_size: The size of the median window for the x-axis.
        Must be a positive integer.
        If the y-axis window size is not provided, the
        x-axis window size will be used for both axes.
    :type window_size: int
    :param window_size_y: The size of the median window for the y-axis.
        Must be a positive integer.
        If not provided, it defaults to the x-axis window size.
    :type window_size_y: int
    """
    def __init__(self, window_size: int, window_size_y: int = None):
        if window_size_y is None:
            window_size_y = window_size
        super().__init__()
        self.filter_x = MedianAverageFilter1D(window_size=window_size)
        self.filter_y = MedianAverageFilter1D(window_size=window_size_y)


class NaiveExponentialMovingAverageFilter2D(NaiveFilter2D):
    """
    A 2D filter that implements an exponential moving average filter for two-dimensional data.
    It applies exponential moving average weights to the current and
    the previous filtered data points in both x and y directions.

    :param alpha: The smoothing factor for the x-axis. Must be between 0 and 1 (inclusive).
        If `alpha_y` is not provided, it will be set to the same value as `alpha`.
    :type alpha: float
    :param alpha_y: The smoothing factor for the y-axis. Must be between 0 and 1 (inclusive).
        If not provided, it defaults to the x-axis alpha value.
    :type alpha_y: float
    """
    def __init__(self, alpha: float, alpha_y: float = None):
        if alpha_y is None:
            alpha_y = alpha
        super().__init__()
        self.filter_x = ExponentialMovingAverageFilter1D(alpha=alpha)
        self.filter_y = ExponentialMovingAverageFilter1D(alpha=alpha_y)


class NaiveCumulativeMovingAverageFilter2D(NaiveFilter2D):
    """
    A 2D filter that implements a cumulative moving average filter for two-dimensional data.
    It computes the cumulative average of the input data points as they are processed,
    updating the average with each new data point in both x and y directions.
    """
    def __init__(self):
        super().__init__()
        self.filter_x = CumulativeMovingAverageFilter1D()
        self.filter_y = CumulativeMovingAverageFilter1D()


class NaiveFixationSmoothFilter2D(NaiveFilter2D):
    """
    A 2D filter that implements a fixation smooth filter for two-dimensional data.
    It uses a weighted averaging mechanism in conjunction with
    standard deviation-based thresholding to determine whether to maintain
     or update the fixation value in both x and y directions.

    An example for the threshold would be calculated using the following formula:
    ``{screen_width_px} * 0.004 + sqrt({window_size})``.
    Where `screen_width_px` is the width of the screen in pixels and
    `window_size` is the size of the sliding window used for the filter.
    This could be used for eye-tracking data to smooth out noise when you fixate on a point
    for a longer period of time.

    :param window_size: The size of the sliding window for the x-axis.
        Must be a positive integer.
        If the y-axis window size is not provided, it will be set to the
        same value as `window_size`.
    :type window_size: int
    :param window_size_y: The size of the sliding window for the y-axis.
        Must be a positive integer.
        If not provided, it defaults to the x-axis window size.
    :type window_size_y: int
    :param threshold: The threshold value for the x-axis.
    :type threshold: float
    :param threshold_y: The threshold value for the y-axis.
    :type threshold_y: float
    """
    def __init__(self, window_size: int, threshold: float,
                 window_size_y: int = None, threshold_y: float = None):
        if window_size_y is None:
            window_size_y = window_size
        if threshold_y is None:
            threshold_y = threshold
        super().__init__()
        self.filter_x = FixationSmoothFilter1D(window_size=window_size, threshold=threshold)
        self.filter_y = FixationSmoothFilter1D(window_size=window_size_y, threshold=threshold_y)


class NaiveMultiPassMovingAverage2D(NaiveFilter2D):
    """
    A 2D filter that implements a multi-pass moving average filter for two-dimensional data.
    It applies a user-defined number of passes over the data using the
    specified moving average filter type in both x and y directions.

    :param window_size: The size of the sliding window for the x-axis.
        Must be a positive integer.
        If the y-axis window size is not provided, it will be set to the
        same value as `window_size`.
    :type window_size: int
    :param window_size_y: The size of the sliding window for the y-axis.
        Must be a positive integer.
        If not provided, it defaults to the x-axis window size.
    :type window_size_y: int
    :param num_passes: Number of passes to apply to the moving average filter for the x-axis.
        Must be a positive integer.
        If `num_passes_y` is not provided, it will be set to the same value as `num_passes`.
    :type num_passes: int
    :param num_passes_y: Number of passes to apply to the moving average filter for the y-axis.
        Must be a positive integer.
        If not provided, it defaults to the x-axis number of passes.
    :type num_passes_y: int
    :param average_filter_type_x: The type of moving average filter to use for the x-axis.
        Defaults to ``MovingAverageType.SIMPLE``.
        If `average_filter_type_y` is not provided, it will be set to the
        same value as `average_filter_type_x`.
    :type average_filter_type_x: MovingAverageType
    :param average_filter_type_y: The type of moving average filter to use for the y-axis.
        If not provided, it defaults to the x-axis average filter type.
    :type average_filter_type_y: MovingAverageType
    """
    def __init__(self, window_size: int, num_passes: int,
                 window_size_y: int = None, num_passes_y: int = None,
                 average_filter_type_x: MovingAverageType = MovingAverageType.SIMPLE,
                 average_filter_type_y: MovingAverageType = None):
        if window_size_y is None:
            window_size_y = window_size
        if num_passes_y is None:
            num_passes_y = num_passes
        if average_filter_type_y is None:
            average_filter_type_y = average_filter_type_x

        super().__init__()
        self.filter_x = MultiPassMovingAverage1D(
            window_size=window_size,
            num_passes=num_passes,
            average_filter_type=average_filter_type_x
        )
        self.filter_y = MultiPassMovingAverage1D(
            window_size=window_size_y,
            num_passes=num_passes_y,
            average_filter_type=average_filter_type_y
        )
