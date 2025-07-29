"""
Contains the one-dimensional filters used for signal processing.
"""
import warnings
from abc import ABC, abstractmethod
import numpy as np

from smoothiepy.filter.basefilter import MovingAverageType, Filter1D
from smoothiepy.smoother.builder import SmootherBuilder


# TODO versions for list data -> also account for future data

class UselessFilter1D(Filter1D):
    """
    A filter that does not perform any filtering.
    It simply returns the input data as is.
    """
    def __init__(self):
        warnings.warn("The UselessFilter1D class is deprecated.")
        super().__init__(window_size=1)

    def _process_next(self, buffer: np.array) -> float | int:
        return buffer[0]


class OffsetFilter1D(Filter1D):
    """
    A filter that applies a constant offset to the input data.

    :param offset: The constant value to be added to the input data.
    :type offset: float | int
    """
    def __init__(self, offset: float | int):
        super().__init__(window_size=1)
        self.offset = offset

    def _process_next(self, buffer: np.array) -> float | int:
        return buffer[0] + self.offset


class KernelMovingAverageFilter1D(Filter1D, ABC):
    """
    KernelMovingAverageFilter1D is an abstract base class that implements a kernel-based moving
    average filter in one dimension.

    This class processes data using weights constructed for the filter,
    providing a weighted average over a defined window size. The weights are
    normalized automatically during processing.

    :ivar weights: Weights for the kernel moving average filter, calculated by
        the `_construct_weights` method.
    :type weights: np.array
    :ivar weights_sum: Precomputed sum of the weights, used for normalization in
        the filtering process.
    :type weights_sum: float
    """
    def __init__(self, window_size: int):
        super().__init__(window_size)
        self.weights = self._construct_weights()
        self.weights_sum = self.weights.sum()

    def _process_next(self, buffer: np.array) -> float | int:
        if len(buffer) < self.window_size:
            offset = self.window_size - len(buffer)
            weighted_sum = np.sum(buffer * self.weights[offset:])
            cur_weights_sum = self.weights[offset:].sum()
            if cur_weights_sum == 0:
                return 0.0
            return weighted_sum / cur_weights_sum

        weighted_sum = np.sum(buffer * self.weights)
        return weighted_sum / self.weights_sum

    @abstractmethod
    def _construct_weights(self) -> np.array:
        """
        Constructs the weights for the kernel moving average filter.
        This method should be implemented by subclasses to define
        how the weights are calculated based on the window size.

        The weights don't have to sum up to 1, they are normalized
        during the processing step.

        :return: An array of weights for the kernel moving average filter.
        :rtype: np.array
        """


class SimpleMovingAverageFilter1D(KernelMovingAverageFilter1D):
    """
    A filter that computes the average of the input data over a specified window size.
    No weighting is applied, and the average is computed
    as a simple arithmetic mean of the values in the buffer.

    If not enough data points are available to fill the window,
    it computes the average of the available data points.

    :ivar window_size: The size of the window for averaging.
    :type window_size: int
    """
    def _construct_weights(self) -> np.array:
        return np.ones(self.window_size) / self.window_size

class WeightedMovingAverageFilter1D(KernelMovingAverageFilter1D):
    """
    A filter that computes a weighted average of the input data over a specified window size.
    The weights are linearly decreasing from 1 to 0, applied to the most recent data points.

    If not enough data points are available to fill the window,
    it computes the weighted average of the available data points.

    :ivar window_size: The size of the sliding window used for the filter.
    :type window_size: int
    """
    def _construct_weights(self) -> np.array:
        return np.linspace(1, 0, self.window_size)


class GaussianAverageFilter1D(KernelMovingAverageFilter1D):
    """
    Implements a Gaussian Average Filter for one-dimensional data.

    Incorporating a Gaussian weighting function applied over a sliding window of data.
    It is used for smoothing data by placing higher importance on values closer more
    recent values of the window while progressively down-weighting values farther away.
    The Gaussian distribution is controlled via the window size and standard deviation parameters.

     If not enough data points are available to fill the window,
    it computes the gaussian average of the available data points with
    a trimmed gaussian filter.

    The filter is only relying on previous data values in the buffer, not future values
     which would result in a delay / offset in the output.

    :param window_size: Size of the sliding window used for the filter.
    :type window_size: int
    :param std_dev: The standard deviation of the Gaussian distribution that determines the spread.
        Must be a positive value.
    :type std_dev: float
    :raises ValueError: If std_dev is negative.
    """
    def __init__(self, window_size: int, std_dev: float = None):
        if std_dev is None:
            std_dev = window_size / 3
        if std_dev <= 0:
            raise ValueError("std_dev must be a positive value")
        self.std_dev = std_dev
        super().__init__(window_size)

    def _construct_weights(self) -> np.array:
        """
        Constructs Gaussian weights based on the specified window size
        and standard deviation.The weights are not centered around zero,
        but rather they are computed from the window size down to zero.
        The most recent data points are given more weight than older ones.

        :return: Computed array of Gaussian weights with length equal to the window size
        :rtype: np.array
        """
        lin_space = np.linspace(self.window_size, 0, self.window_size) \
            if self.window_size % 2 == 0 else np.linspace(self.window_size, 0, self.window_size)
        gaussian = np.exp(-0.5 * (lin_space / self.std_dev) ** 2)
        return gaussian


class MedianAverageFilter1D(Filter1D):
    def _process_next(self, buffer: np.array) -> float | int:
        return np.median(buffer).astype(float)


class ExponentialMovingAverageFilter1D(Filter1D):
    """
    Implements a one-dimensional exponential moving average filter.

    This filter applies exponential moving average weights
     to the current and the previous filtered data point.
    The smoothing factor (alpha) determines the weight given to the most recent data point
    compared to the previous filtered value.

    :ivar alpha: The smoothing factor. Must be between 0 and 1 (inclusive).
    :type alpha: float
    """
    def __init__(self, alpha: float):
        super().__init__(window_size=1)
        if not 0 <= alpha <= 1:
            raise ValueError("Alpha must be between 0 and 1")

        self.alpha = alpha
        self.__inverted_alpha = 1 - alpha
        self.latest_filtered_value: float | int = 0.0

    def _process_next(self, buffer: np.array) -> float | int:
        if not self.latest_filtered_value:
            self.latest_filtered_value = buffer[0]
            return buffer[0]

        self.latest_filtered_value = ((self.alpha * buffer[0])
                                      + (self.__inverted_alpha * self.latest_filtered_value))
        return self.latest_filtered_value


class CumulativeMovingAverageFilter1D(Filter1D):
    """
    Implements a one-dimensional cumulative moving average filter.

    This filter computes the cumulative average of the input data points
    as they are processed, updating the average with each new data point.

    :ivar cumulative_average: The current cumulative average of the input data.
    :type cumulative_average: float | int
    """
    def __init__(self):
        super().__init__(window_size=1)
        self.cumulative_average = 0.0
        self.count = 0

    def _process_next(self, buffer: np.array) -> float | int:
        self.count += 1
        self.cumulative_average += (buffer[0] - self.cumulative_average) / self.count
        return self.cumulative_average


class FixationSmoothFilter1D(Filter1D):
    """
    A filter class to smooth fixation-like data in 1D. This is a type of deadband filter.

    It uses a weighted averaging mechanism in conjunction with standard deviation-based
    thresholding to determine whether to maintain or update the fixation value. The purpose
    of this filter is to smooth out noise while preserving significant data trends.

    The noise will be reduced by checking the standard deviation of the data in the buffer
    and comparing the latest data value with the current fixation value. If both checks pass,
    the current fixation value is returned. Otherwise, a new fixation value is computed
    using a weighted average of the data in the buffer.

    Note that this filter cuts out noise totally. It will not smooth out noise.

    An example for the threshold would be calculated using the following formula:
    ``{screen_width_px} * 0.004 + sqrt({window_size})``.
    Where `screen_width_px` is the width of the screen in pixels and
    `window_size` is the size of the sliding window used for the filter.
    This could be used for eye-tracking data to smooth out noise when you fixate on a point
    for a longer period of time.

    :ivar window_size: The size of the sliding window for the filter.
    :type window_size: int
    :ivar threshold: The threshold value used for standard deviation and fixation value difference
                     checks.
    :type threshold: float
    :ivar fixation_value: The current fixation value being tracked by the filter.
    :type fixation_value: float
    :ivar average_weights: A numpy array of weights used for computing weighted averages
                           over the input data buffer.
    :type average_weights: numpy.ndarray
    """
    def __init__(self, window_size: int, threshold: float):
        super().__init__(window_size)
        self.threshold = threshold
        self.fixation_value = 0.0
        self.average_weights = np.linspace(0.2, 1.0, window_size)

    def _process_next(self, buffer: np.array) -> float | int:
        std_dev = np.std(buffer)
        latest_data_value = buffer[-1]

        if (abs(std_dev) <= self.threshold
                and abs(self.fixation_value - latest_data_value) <= self.threshold):
            return self.fixation_value

        if len(buffer) < self.window_size:
            offset = self.window_size - len(buffer)
            self.fixation_value = np.average(buffer, weights=self.average_weights[offset:])
        else:
            self.fixation_value = np.average(buffer, weights=self.average_weights)
        return latest_data_value


class MultiPassMovingAverage1D(Filter1D):
    """
    This class implements a one-dimensional multi-pass moving average filter.

    The MultiPassMovingAverage1D class applies a user-defined number of passes
    over the data using the specified moving average filter type. It allows
    different types of moving averages, such as simple, weighted, Gaussian,
    and median.

    :param window_size: The size of the sliding window for the filter.
    :type window_size: int
    :param num_passes: Number of passes to apply to the moving average filter.
    :type num_passes: int
    :param average_filter_type: The type of moving average filter to use.
    :type average_filter_type: MovingAverageType
    """
    def __init__(self, window_size: int, num_passes: int,
                 average_filter_type: MovingAverageType = MovingAverageType.SIMPLE):
        super().__init__(window_size=1)
        if num_passes <= 0:
            raise ValueError("num_passes must be greater than 0")

        self.num_passes = num_passes
        self.average_filter_type = average_filter_type

        smoother = (
            SmootherBuilder()
                .one_dimensional()
                .continuous()
            )
        for _ in range(num_passes):
            if average_filter_type == MovingAverageType.SIMPLE:
                smoother.attach_filter(SimpleMovingAverageFilter1D(window_size))
            elif average_filter_type == MovingAverageType.WEIGHTED:
                smoother.attach_filter(WeightedMovingAverageFilter1D(window_size))
            elif average_filter_type == MovingAverageType.GAUSSIAN:
                smoother.attach_filter(GaussianAverageFilter1D(window_size,
                                                               std_dev=window_size / 3))
            elif average_filter_type == MovingAverageType.MEDIAN:
                smoother.attach_filter(MedianAverageFilter1D(window_size))
            else:
                raise ValueError(f"Unsupported average filter type: {average_filter_type}")
        self.smoother = smoother.build()

    def _process_next(self, buffer: np.array) -> float | int:
        return self.smoother.add_and_get(buffer[0])
