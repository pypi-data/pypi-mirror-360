"""
Contains the Signal Smoother class which is the main class to smooth signals.
"""
from abc import ABC, abstractmethod
from smoothiepy.filter.basefilter import Filter, Filter1D, Filter2D


class Smoother(ABC):
    """
    Represents an abstract base class for smoothing signals by attaching and managing filters.

    This class is designed as a foundation for implementing specific signal smoothing
    strategies. It provides a structure for managing filters and implementing custom
    signal smoothing logic.

    :ivar filter_list: A list that holds the filters attached to this smoother.
    :type filter_list: list[Filter]
    """
    def __init__(self):
        self.filter_list: list[Filter] = []

    @abstractmethod
    def attach_filter(self, filter_obj: Filter) -> None:
        """
        Attaches a filter object to the implementing class.

        :param filter_obj: The filter object to attach.
        :type filter_obj: Filter
        """

    @abstractmethod
    def build(self):
        """
        Builds the final configuration of the smoother, setting up the filters
        and their parameters as needed.

        :raises NotImplementedError: If the subclass does not implement this method.
        """


class Smoother1D(Smoother, ABC):
    """
    Provides one-dimensional signal smoothing functionality.

    This class is an extension of the ``Smoother`` class designed specifically
    for one-dimensional signal data. It maintains a list of 1D filters and allows
    attachment of additional filters which must be of type Filter1D.

    :ivar filter_list: Stores instances of Filter1D for smoothing operations.
    :type filter_list: list[Filter1D]
    """
    def __init__(self):
        super().__init__()
        self.filter_list: list[Filter1D] = []

    def attach_filter(self, filter_obj: Filter) -> None:
        if not isinstance(filter_obj, Filter1D):
            raise TypeError("filter_obj must be an 1D filter")

        self.filter_list.append(filter_obj)


class Smoother1DContinuous(Smoother1D):
    """
    A class for continuously smoothing one-dimensional data.

    Provides functionality to smooth incoming data points in a continuous manner
    using a list of filters.
    The smoothed value is updated as new data points are added.

    :ivar last_filtered_value: Stores the most recent smoothed value.
    :type last_filtered_value: float | int
    """
    def __init__(self):
        super().__init__()
        self.last_filtered_value: float | int = 0.0

    def build(self):
        pass
        # self.filter_list[-1].set_buffer_size(1)
        # for cur_filter, next_filter in zip(self.filter_list, self.filter_list[1:]):
        #     cur_filter.set_buffer_size(next_filter.window_size)

    def add_and_get(self, data: float | int) -> float | int:
        """
        Adds the given data to the signal smoother and returns the filtered value.

        :param data: The numeric value to be added.
        :type data: float | int
        :return: Filtered value after the input has been added.
        :rtype: float | int
        """
        self.add(data)
        return self.get()

    def add(self, data: float | int) -> None:
        """
        Adds a new data point to the signal smoother.

        :param data: The data point to be added.
        :type data: float | int
        """
        temp_filtered_value = data
        for cur_filter in self.filter_list:
            temp_filtered_value = cur_filter.next(temp_filtered_value)

        self.last_filtered_value = temp_filtered_value

    def get(self) -> float | int:
        """
        Retrieves the smoothed value from the signal smoother.

        :return: The smoothed value.
        :rtype: float | int
        """
        return self.last_filtered_value


class Smoother2D(Smoother, ABC):
    """
    Provides two-dimensional signal smoothing functionality.

    This class is an extension of the ``Smoother`` class designed specifically
    for two-dimensional signal data. It maintains a list of 2D filters and allows
    attachment of additional filters which must be of type Filter2D.

    :ivar filter_list: Stores instances of Filter2D for smoothing operations.
    :type filter_list: list[Filter2D]
    """
    def __init__(self):
        super().__init__()
        self.filter_list: list[Filter2D] = []

    def attach_filter(self, filter_obj: Filter) -> None:
        if not isinstance(filter_obj, Filter2D):
            raise TypeError("filter_obj must be an 2D filter")

        self.filter_list.append(filter_obj)


class Smoother2DContinuous(Smoother2D):
    """
        A class for continuously smoothing two-dimensional data.

        Provides functionality to smooth incoming data points in a continuous manner
        using a list of filters.
        The smoothed value is updated as new data points are added.

        :ivar last_filtered_value: Stores the most recent smoothed value.
        :type last_filtered_value: float | int
        """
    def __init__(self):
        super().__init__()
        self.last_filtered_value: tuple[float | int, float | int] = (0.0, 0.0)

    def build(self):
        pass

    def add_and_get(self, data_x: float | int, data_y: float | int) \
            -> tuple[float | int, float | int]:
        """
        Adds the given data to the signal smoother and returns the filtered value.

        :param data_x: The first numeric value to be added.
        :type data_x: float | int
        :param data_y: The second numeric value to be added.
        :type data_y: float | int
        :return: Filtered value after the input has been added.
        :rtype: float | int
        """
        self.add(data_x=data_x, data_y=data_y)
        return self.get()

    def add(self, data_x: float | int, data_y: float | int) -> None:
        """
        Adds a new data point to the signal smoother.

         :param data_x: The first numeric value to be added.
        :type data_x: float | int
        :param data_y: The second numeric value to be added.
        :type data_y: float | int
        """
        temp_filtered_value = data_x, data_y
        for cur_filter in self.filter_list:
            temp_filtered_value = cur_filter.next(temp_filtered_value)

        self.last_filtered_value = temp_filtered_value

    def get(self) -> tuple[float | int, float | int]:
        """
        Retrieves the smoothed value from the signal smoother.

        :return: The smoothed value.
        :rtype: float | int
        """
        return self.last_filtered_value

# class SignalSmootherSeparateLists1D:
#     def filter_list(self, signal: list[float]) -> list[float]:
#         return signal
