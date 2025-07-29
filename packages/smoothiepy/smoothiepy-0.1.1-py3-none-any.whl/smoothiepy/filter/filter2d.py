"""
Contains the two-dimensional filters used for signal processing.
"""

import numpy as np

from smoothiepy.filter.basefilter import Filter2D


class OffsetFilter2D(Filter2D):
    """
    A 2D filter that applies a fixed offset to input data on both x and y axes.
    Can be used in scenarios where a shift in data coordinates is required.

    :param offset: Offset value to be applied to the x-axis data.
        If `offset_y` is not provided, it will be set to the same value as `offset`.
    :type offset: int | float
    :param offset_y: Offset value to be applied to the y-axis data.
        If not provided, it defaults to the same value as `offset`.
    :type offset_y: int | float
    """
    def __init__(self, offset, offset_y = None):
        if offset_y is None:
            offset_y = offset
        super().__init__(window_size_x=1, window_size_y=1)
        self.offset_x = offset
        self.offset_y = offset_y

    def _process_next(self, buffer_x: np.array, buffer_y: np.array) \
            -> tuple[float | int, float | int]:
        """
        Processes the next data point by applying an offset to the input buffers.

        :param buffer_x: The current buffer data for the x-axis.
        :type buffer_x: np.array
        :param buffer_y: The current buffer data for the y-axis.
        :type buffer_y: np.array
        :return: A tuple containing the processed values for x and y axes.
        :rtype: tuple[float | int, float | int]
        """
        return buffer_x[0] + self.offset_x, buffer_y[0] + self.offset_y
