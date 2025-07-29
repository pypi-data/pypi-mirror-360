# -*- coding: utf-8 -*-

import numpy as np
from scipy.stats import zscore

from timelined_array import TimelinedArray


def non_zero_raw_fluorescence(array):
    return (array - array.min()) + 2


def delta_over_F(array, period: int | float | slice = 0, axis=0, time_period=True):
    """Performs deltaF over F0 ( with eq : DF0 = F - F0 / F0 )"""

    if array.min() <= 0:
        array = non_zero_raw_fluorescence(array)

    F0_indexer = []
    Span_indexer = []
    for dim in range(len(array.shape)):
        if dim == axis:
            F0_indexer.append(period)
            Span_indexer.append(np.newaxis)
        else:
            F0_indexer.append(slice(None))
            Span_indexer.append(slice(None))
    F0_indexer = tuple(F0_indexer)
    Span_indexer = tuple(Span_indexer)

    if isinstance(array, TimelinedArray) and time_period and array.time_dimension == axis:
        F0_frame = np.asarray(array.itime.__getitem__(period).mean(axis=axis))
    else:
        F0_frame = np.asarray(array.__getitem__(F0_indexer).mean(axis=axis))

    F0_frames = np.repeat(F0_frame.__getitem__(Span_indexer), repeats=array.shape[axis], axis=axis)

    return (array - F0_frames) / F0_frames


# def delta_over_F(array, F0_index = 0, sigma = None, optimize = "speed"):
#     from scipy.ndimage import gaussian_filter1d
#     #NOT A SINGLE OR AVERAGE OF MULTIPLE FRAMES BUT A TEMPORAL GAUSSIAN AROUND FRAME

#     if array.min() <= 0:
#         array = non_zero_raw_fluorescence(array.copy())

#     if sigma is not None :
#         F0_frame = gaussian_filter1d(array, sigma , axis = 0)[F0_index] #time as first index.
#          # Other dimensions after that
#     else :
#         F0_frame = array[F0_index]

#     if optimize == "speed":
#         F0_frame = np.repeat( F0_frame[np.newaxis], array.shape[0], axis = 0)
#         return (array - F0_frame) / F0_frame
#     elif optimize == "ram":
#         return_array = array.copy()
#         for i in range(return_array.shape[0]):
#             return_array[i] = (return_array[i] - F0_frame) / F0_frame
#         return return_array
#     else :
#         raise ValueError("optimize argument must either be 'speed' or 'ram'")

delta_over_f = delta_over_F
