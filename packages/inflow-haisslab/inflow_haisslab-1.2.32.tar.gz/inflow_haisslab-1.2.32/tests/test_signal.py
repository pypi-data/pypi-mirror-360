import pytest
import numpy as np

### FILTERS

from timelined_array import TimelinedArray
from Inflow.signal.filters import gaussian, filtfilt_hz

### FITS

from scipy.optimize import curve_fit
from Inflow.signal.fits import function_gauss_2d, fit_gauss_2d, fit_gauss_2d_guess_params, array_2d_to_xyz

### FILTERS


def test_gaussian():
    array = np.random.rand(10, 10, 10)
    sigma = 1.0
    filtered_array = gaussian(array, sigma=sigma)
    assert filtered_array.shape == array.shape
    assert isinstance(filtered_array, np.ndarray)


def test_gaussian_with_axis_values():
    array = np.random.rand(10, 10, 10)
    axis_values = (1.0, 1.0, 0.0)
    filtered_array = gaussian(array, axis_values=axis_values)
    assert filtered_array.shape == array.shape
    assert isinstance(filtered_array, np.ndarray)


def test_gaussian_with_timelined_array():
    array = TimelinedArray(np.random.rand(10, 10, 10), timeline=np.arange(10), time_dimension=0)
    sigma = 2.0
    filtered_array = gaussian(array, sigma=sigma)
    assert filtered_array.shape == array.shape
    assert isinstance(filtered_array, TimelinedArray)


def test_filtfilt_hz_lowpass():
    array = np.random.rand(100)
    fcut = 0.1
    fs = 1.0
    filtered_array = filtfilt_hz(array, fcut, fs, btype="low")
    assert filtered_array.shape == array.shape
    assert isinstance(filtered_array, np.ndarray)


def test_filtfilt_hz_highpass():
    array = np.random.rand(100)
    fcut = 0.1
    fs = 1.0
    filtered_array = filtfilt_hz(array, fcut, fs, btype="high")
    assert filtered_array.shape == array.shape
    assert isinstance(filtered_array, np.ndarray)


def test_filtfilt_hz_bandpass():
    array = np.random.rand(100)
    fcut = [0.1, 0.3]
    fs = 1.0
    filtered_array = filtfilt_hz(array, fcut, fs, btype="band")
    assert filtered_array.shape == array.shape
    assert isinstance(filtered_array, np.ndarray)


def test_filtfilt_hz_with_timelined_array():
    array = TimelinedArray(np.random.rand(100), timeline=np.arange(100))
    fcut = 0.1
    fs = 1.0
    filtered_array = filtfilt_hz(array, fcut, fs, btype="low")
    assert filtered_array.shape == array.shape
    assert isinstance(filtered_array, TimelinedArray)


### FITS


def test_function_gauss_2d():
    x = np.linspace(0, 10, 100)
    y = np.linspace(0, 10, 100)
    x, y = np.meshgrid(x, y)
    z = function_gauss_2d((x, y), 3, 5, 5, 1, 1, 0, 0)
    assert z.shape == (10000,)
    assert np.isclose(z.max(), 3, atol=0.1)


def test_fit_gauss_2d():
    x = np.linspace(0, 10, 100)
    y = np.linspace(0, 10, 100)
    x, y = np.meshgrid(x, y)
    z = function_gauss_2d((x, y), 3, 5, 5, 1, 1, 0, 0).reshape(100, 100)
    fitted_data, params = fit_gauss_2d(z)
    assert fitted_data.shape == (100, 100)
    assert np.isclose(params[0]["amplitude"], 3, atol=0.1)
    assert np.isclose(params[0]["x0"], 50, atol=0.1)
    assert np.isclose(params[0]["y0"], 50, atol=0.1)


def test_fit_gauss_2d_guess_params():
    array = np.random.rand(100, 100)
    params = fit_gauss_2d_guess_params(array, as_dict=True)
    assert "amplitude" in params
    assert "x0" in params
    assert "y0" in params
    assert "x_sigma" in params
    assert "y_sigma" in params
    assert "theta" in params
    assert "offset" in params


def test_array_2d_to_xyz():
    array = np.random.rand(100, 100)
    x, y, z = array_2d_to_xyz(array)
    assert x.shape == (100, 100)
    assert y.shape == (100, 100)
    assert z.shape == (10000,)


if __name__ == "__main__":
    pytest.main()
