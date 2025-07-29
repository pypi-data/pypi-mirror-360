"""
Base module that defines the abstract base class for all signal filters.
"""
import enum
from abc import ABC, abstractmethod
from collections import deque
import numpy as np


class Filter(ABC):
    """
    Abstract base class for all signal filters.
    """


class Filter1D(Filter, ABC):
    """
    Abstract base class for all one-dimensional signal filters.
    :param window_size: The size of the window for the filter. Must be a positive integer.
    :type window_size: int
    :ivar window_size: The size of the window for the filter.
    :type window_size: int
    :raises ValueError: If window_size is not a positive integer.
    """
    def __init__(self, window_size: int):
        if window_size <= 0:
            raise ValueError("window_size must be greater than 0")
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)
        self.last_buffer_value: float | int = 0.0

    def next(self, data: float | int) -> float | int:
        """
        Processes the next data point by adding it to the buffer
        and calling the internal processing method.

        :param data: The next data point to be processed.
        :type data: float | int
        :return: The filtered value.
        :rtype: float | int
        """
        self.last_buffer_value = self.buffer[0] if self.buffer else 0.0
        self.buffer.append(data)
        return self._process_next(np.array(self.buffer))

    @abstractmethod
    def _process_next(self, buffer: np.array) -> float | int:
        """
        Processes the next data point using the current buffer data.

        :param buffer: The current buffer data.
        :type buffer: list[float | int]
        :return: The processed value.
        :rtype: float | int
        """


class Filter2D(Filter, ABC):
    """
    Abstract base class for all two-dimensional signal filters.
    This class is currently a placeholder and does not implement any methods.
    It serves as a base for future two-dimensional filter implementations.
    """
    def __init__(self, window_size_x: int, window_size_y: int):
        """
        Initializes the 2D filter with specified window sizes.

        :param window_size_x: The size of the window in the x-direction. Must be a positive integer.
        :type window_size_x: int
        :param window_size_y: The size of the window in the y-direction. Must be a positive integer.
        :type window_size_y: int
        """
        if window_size_x <= 0 or window_size_y <= 0:
            raise ValueError("window_size_x and window_size_y must be greater than 0")
        self.window_size_x = window_size_x
        self.window_size_y = window_size_y
        self.buffer_x = deque(maxlen=window_size_x)
        self.buffer_y = deque(maxlen=window_size_y)

    def next(self, data_x: float | int, data_y: float | int) -> tuple[float | int, float | int]:
        """
        Processes the next data point in both x and y dimensions by adding
        them to their respective buffers and calling the internal processing method.

        :param data_x: The next data point in the x dimension.
        :type data_x: float | int
        :param data_y: The next data point in the y dimension.
        :type data_y: float | int
        :return: A tuple containing the filtered values for x and y dimensions.
        :rtype: tuple[float | int, float | int]
        """
        self.buffer_x.append(data_x)
        self.buffer_y.append(data_y)
        return self._process_next(np.array(self.buffer_x), np.array(self.buffer_y))

    @abstractmethod
    def _process_next(self, buffer_x: np.array, buffer_y: np.array) \
            -> tuple[float | int, float | int]:
        """
        Processes the next data points using the current buffer data in both x and y dimensions.

        :param buffer_x: The current buffer data in the x dimension.
        :type buffer_x: np.array
        :param buffer_y: The current buffer data in the y dimension.
        :type buffer_y: np.array
        :return: A tuple containing the processed values for x and y dimensions.
        :rtype: tuple[float | int, float | int]
        """


class MovingAverageType(enum.Enum):
    """
    Enum for different types of moving averages.

    This enum defines the types of moving averages that can be applied to signals.
    """
    SIMPLE = "simple"
    WEIGHTED = "weighted"
    GAUSSIAN = "gaussian"
    MEDIAN = "median"
    EXPONENTIAL = "exponential"
    CUMULATIVE = "cumulative"
