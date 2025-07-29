# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 15:43:19 2023

@author: tjostmou
"""
import numpy as np
from scipy.signal import butter, filtfilt
from timelined_array import TimelinedArray
import time
from logging import getLogger

from typing import Callable


def gaussian(array, sigma=None, axis=(1, 2), axis_values=None):
    """
    Gaussian filter on Ndim data

    Parameters
    ----------
    signal : ndarray
        DESCRIPTION.
    sigma : int or float
        sigma value for the gaussian filtering (homogeneous gaussian on all dimensions in axis argument).
    axis : int or tuple of ints
        axis on wich to perform gaussian filter.
        If you want to apply 2D filter on 3D data with time as first axis, for example, axis must be : (1,2)
    axis_values : tuple of int or floats
        direct supply of axis_values for gaussian_filter. Must be the same number of items as there is dimensions
        in your array

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    logger = getLogger("gaussian_filter")

    start_time = time.time()

    if axis_values is None:
        if sigma is None:
            raise ValueError("Must supply a sigma value if no axis_values are given")
        if isinstance(axis, int):
            axis = (axis,)
        axis_values = []
        for i in range(len(array.shape)):
            if i in axis:
                axis_values.append(sigma)
            else:
                axis_values.append(0)

    try:
        from cupyx.scipy.ndimage import gaussian_filter
        import cupy as cp

        cp_array = cp.asarray(array)
        filtered_cp_data = gaussian_filter(cp_array, axis_values, mode="nearest")
        filtered_data = cp.asnumpy(filtered_cp_data)
        del cp_array, filtered_cp_data
        cp._default_memory_pool.free_all_blocks()
    except Exception:
        from scipy.ndimage import gaussian_filter

        filtered_data = gaussian_filter(array, axis_values, mode="nearest")

    end_time = time.time()
    if end_time - start_time > 3:
        logger.info(
            f"Finished gaussian filtering on {filtered_data.shape}D array in {end_time - start_time:.2f} seconds"
        )

    if isinstance(array, TimelinedArray):
        filtered_data = TimelinedArray(filtered_data, timeline=array.timeline, time_dimension=array.time_dimension)

    return filtered_data


def filtfilt_hz(
    array, fcut, fs, *, axis=-1, order=3, btype="low", padlen=None, padtype="odd", method="pad", irlen=None
):
    """Apply a digital filter forward and backward to a signal,
    using a frequency cut defined in sampling frequency units. (Hz most commonly)

    Args:
        array (_type_): The array of data to be filtered.
        fcut (_type_): The critical frequency or frequencies.
            For lowpass and highpass filters, fcut is a scalar.
            For bandpass and bandstop filters, fcut is a length-2 sequence.
            (start, stop of the band, supports a single band)
            For a Butterworth filter, fcut is the point at which the gain drops to 1/sqrt(2)
            that of the passband (the “-3 dB point”).
            fcut must be is in the same units as fs.
        fs (_type_): The sampling frequency of the digital system. Must be in the same unit as fcut.
        axis (int, optional): The axis of x to which the filter is applied. Defaults to -1.
        order (int, optional): The order of the filter.
            For `bandpass` and `bandstop` filters,
            the resulting order of the final second-order sections (`sos`) matrix is 2*order,
            with `order`, the number of biquad sections of the desired system. Defaults to 3.
        btype (str, optional): The type of filter. Default is `lowpass`. Defaults to `low`.
        padtype (str, optional): Must be `odd`, `even`, `constant`, or None.
            This determines the type of extension to use for the padded signal to which the filter is applied.
            If padtype is None, no padding is used. The default is `odd`.. Defaults to 'odd'.
        padlen (_type_, optional): The number of elements by which to extend x at both ends of axis
            before applying the filter. This value must be less than x.shape[axis] - 1. padlen=0 implies no padding.
            The default value is 3 * max(len(a), len(b)).. Defaults to None.
        method (str, optional): Determines the method for handling the edges of the signal, either “pad” or “gust”.
            When method is “pad”, the signal is padded; the type of padding is determined by padtype and padlen,
            and irlen is ignored. When method is “gust”, Gustafsson’s method is used,
            and padtype and padlen are ignored. Defaults to 'pad'.
        irlen (_type_, optional): When method is “gust”, irlen specifies the length of the impulse response
            of the filter. If irlen is None, no part of the impulse response is ignored.
            For a long signal, specifying irlen can significantly improve the performance of the filter.
            Defaults to None.

    Example:
        for a signal you know was acquired at 30Hz, if you want to cutoff frequencies higher than 15Hz using a lowpass :
        ```python
        filtered_array = filtfilt_hz(array, 15, 30, btype = 'low' )
        ```
    """

    b, a = butter(order, fcut, btype=btype, fs=fs, output="ba", analog=False)
    # analog=False is necessary above, True would is only be usefull for educational/hardware determination purposes.
    # A computer filter can only be digital.
    filtered_array = filtfilt(
        b,
        a,
        array,
        padlen=padlen,
        padtype=padtype,
        method=method,
        irlen=irlen,
        axis=axis,
    )
    if isinstance(array, TimelinedArray):
        filtered_array = TimelinedArray(filtered_array, array.timeline)
    return filtered_array


def aggregate_over_window(
    data_2D: np.ndarray, range, width=0.1, minimum_points=2, return_all=False, aggregation="median"
):
    """From a scattered "point cloud", tried to make a continuous array
    by using an aggregation method on each bunch of points. The range defines the successive centers around wich to
    agrgegate, and the width specifies how large to aggregate the values. If the points in a "box" are less than
    minimum_points, np.nan is returned. If return_all is True, instead of aggregating,
    we retun list of values for the box (to do statistics). aggregation specifies the numpy function to aggregate
    (like median or mean, std, etc).

    Args:
        data_2D (np.ndarray): A 2D array where the first column represents the x-coordinates and the second column
                              represents the y-coordinates of the data points.
        range (iterable): An iterable defining the centers around which to aggregate the data points.
        width (float, optional): The width of the window around each center in which to aggregate data points.
                                 Defaults to 0.1.
        minimum_points (int, optional): The minimum number of points required in a window to perform aggregation.
                                        Defaults to 2.
        return_all (bool, optional): If True, returns a list of values for each window instead of aggregating them.
                                     Defaults to False.
        aggregation (str, optional): The numpy aggregation function to use (e.g., "median", "mean", "std").
                                     Defaults to "median".

    Returns:
        np.ndarray: If return_all is False, returns a 2D array where the first column contains the window centers and
                    the second column contains the aggregated values or np.nan if there are fewer than minimum_points.
                    If return_all is True, returns a tuple of two arrays: the first array contains lists of values for
                    each window, and the second array contains the window centers.
    """
    values = []
    locations = []
    for start in range:
        stop = start + width
        locations.append(start - (width / 2))
        mask = (data_2D.T[0] < stop) & (data_2D.T[0] > start)
        selection = data_2D[mask]
        if not len(selection) or len(selection) < minimum_points:
            values.append([]) if return_all else values.append(np.nan)
        else:
            numpy_aggregation_method: Callable[(np.ndarray,), np.ndarray] = getattr(np, f"nan{aggregation}")
            (
                values.append(selection.T[1].tolist())
                if return_all
                else values.append(numpy_aggregation_method(selection.T[1]))
            )

    return (np.array(values, dtype=object), np.array(locations)) if return_all else np.array([locations, values]).T
