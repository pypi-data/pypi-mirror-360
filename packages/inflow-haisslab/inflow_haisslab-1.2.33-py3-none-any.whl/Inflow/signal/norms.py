import numpy as np


def normalize(values, outmin=0, outmax=1, min_val=None, max_val=None):
    """This function normalizes the input values between a specified range [min, max].

    If percentiles are provided, the normalization is based on the range between the provided percentiles.
    The output values can then be out of the range defined by min and max.
    Otherwise (default) the normalisation is maes on the minimum and maximum value of the data.

    Args:
        values (array_like): The input values to be normalized.
        min (float, optional): The lower boundary of the output range. Defaults to 0.
        max (float, optional): The upper boundary of the output range. Defaults to 1.

    Raises:
        ValueError: If the provided min is not strictly inferior to max.

    Returns:
        array_like: The normalized values.
    """
    if outmin >= outmax:
        raise ValueError("min must be strictly inferior to max")

    values = np.asarray(values)

    min_val = values.min() if min_val is None else min_val
    max_val = values.max() if max_val is None else max_val

    ampl = max_val - min_val
    norm = (values - min_val) / ampl  # normalisation between 0 and 1
    target_ampl = outmax - outmin
    norm = (norm * target_ampl) + outmin  # normalization between arbitraty values
    return norm


def non_activity_epochs(array, activity_percentile=99.5):
    low_percentile = 100 - activity_percentile
    high_percentile = activity_percentile
    non_activity_mean = array[
        (array < np.percentile(array, high_percentile)) & (array > np.percentile(array, low_percentile))
    ].mean()
    return non_activity_mean


def center_normalize(array, outmin=0, outmax=1, pre_mean_callback=non_activity_epochs, percentile=None, **kwargs):
    """Normalizes and centers an input array around its mean. Thus the mean will be at equidistance of outmin and outmax
    The output array values range between specified minimum and maximum values.
    This function, center_normalize, accepts an input array, subtracts its mean (thus centering it around zero),
    and then normalizes it to be within a specified range (outmin and outmax).
    By default, the output array values will range between 0 and 1.

    Args:
        array (numpy.ndarray): Input array to be centered and normalized.
        outmin (float, optional): Minimum value for the output normalized array. Defaults to 0.
        outmax (float, optional): Maximum value for the output normalized array. Defaults to 1.
        externally_supplied_mean (float, optional): Wether to use mean calculated internally for mean centering,
            or a more refined mean supplied by the user via this argument, if not set to None.
            This can be used for example to calculate mean over non activity epochs. Defaults to None.

    Returns:
        numpy.ndarray: Normalized and centered array with values ranging between specified minimum and maximum values.
    """
    if pre_mean_callback:
        mean = pre_mean_callback(array, **kwargs).mean()
    else:
        mean = array.mean()
    centered_array = array - mean
    if percentile:
        outermost_bound = max(
            abs(np.percentile(centered_array, 100 - percentile)), abs(np.percentile(centered_array, percentile))
        )
    else:
        outermost_bound = max(abs(centered_array.min()), abs(centered_array.max()))
    return normalize(centered_array, min_val=-outermost_bound, max_val=outermost_bound, outmin=outmin, outmax=outmax)
