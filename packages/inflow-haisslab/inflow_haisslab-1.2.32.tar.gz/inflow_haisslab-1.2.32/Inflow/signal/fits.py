# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 14:51:23 2023

@author: tjostmou
"""
import numpy as np
from typing import overload, Tuple, Dict, Any


def function_gauss_2d(xdata_tuple, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    """
    Function that can model a 2D gaussian with parameters xy as a tuple, amplitude as
    the peak of the gaussian, x0,y0 as the initiation points (coordinates of the peak)
    of the gaussian, sigma x, y as the 2d srinking facots on the two dimensions for
    non uniform gaussians, theta as the angle of this non uniformity, and offset for
    the level of the tangent anymptote compared to 0

    Returns
    -------
    z : array shaped as x, y coordinates provided.
    The value of the gaussian at xy coordinated given as inputs.

    """
    (x, y) = xdata_tuple
    xo = float(xo)
    yo = float(yo)
    theta = theta  # in radians
    a = (np.cos(theta) ** 2) / (2 * sigma_x**2) + (np.sin(theta) ** 2) / (2 * sigma_y**2)
    b = -(np.sin(2 * theta)) / (4 * sigma_x**2) + (np.sin(2 * theta)) / (4 * sigma_y**2)
    c = (np.sin(theta) ** 2) / (2 * sigma_x**2) + (np.cos(theta) ** 2) / (2 * sigma_y**2)
    g = offset + amplitude * np.exp(-(a * ((x - xo) ** 2) + 2 * b * (x - xo) * (y - yo) + c * ((y - yo) ** 2)))
    return g.ravel()


def fit_gauss_2d(array, maxfev=2000, remove_mask_values=False, as_dict=True):
    from scipy.optimize import curve_fit

    def params_as_dict(params):
        return {
            key: value
            for key, value in zip(
                ["amplitude", "x0", "y0", "x_sigma", "y_sigma", "theta", "offset"],
                params,
            )
        }
        # x0, y0, x_sigma and y_sigma values are expressed in pixels

    x, y, z = array_2d_to_xyz(array)

    initial_params = fit_gauss_2d_guess_params(array)

    if remove_mask_values:
        raise NotImplementedError
        # TODO : remove values from tuples that corresponds to indices of masked values in array

        # nonmasked_indices = np.where(data.mask == 0)
        # nonan_xy = np.squeeze(xy[:,nonmasked_indices])
        # nonan_z = (z[nonmasked_indices].data) - z.min()
    else:
        # BUG there is an issue here with dimensions, need to investigate
        if (nan_mask := np.isnan(z)).any():
            x_f = x[~nan_mask]
            y_f = y[~nan_mask]
            z_f = z[~nan_mask]
        else:
            x_f, y_f, z_f = x, y, z
        optimal_params, pcov = curve_fit(function_gauss_2d, (x_f, y_f), z_f, p0=initial_params, maxfev=maxfev)
        data_fitted = function_gauss_2d((x, y), *optimal_params)
        # % (2*np.pi)to get theta in radians
    if as_dict:
        optimal_params, initial_params = params_as_dict(optimal_params), params_as_dict(initial_params)
    return data_fitted.reshape(*array.shape), (optimal_params, initial_params)


@overload
def fit_gauss_2d_guess_params(array, as_dict=False) -> Dict[str, float]: ...


@overload
def fit_gauss_2d_guess_params(array, as_dict=False) -> Tuple[float, ...]: ...


def fit_gauss_2d_guess_params(array, as_dict=False) -> Dict[str, float] | Tuple[float, ...]:
    def params_as_dict(params):
        return {
            key: value
            for key, value in zip(
                ["amplitude", "x0", "y0", "x_sigma", "y_sigma", "theta", "offset"],
                params,
            )
        }

    xo, yo = (
        array.shape[1] / 2,
        array.shape[0] / 2,
    )  # np.unravel_index(array.argmax(), array.shape)
    sigma = np.mean([array.shape[1] / 2, array.shape[0] / 2])
    amplitude = np.percentile(array, 98)
    offset = np.mean(array)
    angle = 0
    initial_params = (amplitude, xo, yo, sigma, sigma, angle, offset)

    return params_as_dict(initial_params) if as_dict else initial_params


def array_2d_to_xyz(array):
    x = np.linspace(0, array.shape[1], array.shape[1])
    y = np.linspace(0, array.shape[0], array.shape[0])
    x, y = np.meshgrid(x, y)
    z = array.ravel(order="C")
    return x, y, z
