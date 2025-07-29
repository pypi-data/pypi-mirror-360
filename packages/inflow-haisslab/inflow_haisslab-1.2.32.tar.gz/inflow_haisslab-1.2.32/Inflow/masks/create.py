import numpy as np
import math
from shapely.vectorized import contains
from shapely.geometry import MultiPoint, Polygon, Point
from cv2 import (
    findContours,
    RETR_LIST,
    RETR_EXTERNAL,
    CHAIN_APPROX_SIMPLE,
    CHAIN_APPROX_NONE,
)


def hex_vertices():
    return [
        (1, 0),
        (math.cos(math.pi / 3), math.sin(math.pi / 3)),
        (math.cos(2 * math.pi / 3), math.sin(2 * math.pi / 3)),
        (-1, 0),
        (math.cos(4 * math.pi / 3), math.sin(4 * math.pi / 3)),
        (math.cos(5 * math.pi / 3), math.sin(5 * math.pi / 3)),
    ]


def hex_x_y_from_z(z):
    """
    Returns the coordinates x,y of the 2D points on the edges of a hexagon.
    The hegaxon H, of circumradius = 1, is inscribed inside the unit circle,
    (origin at 0,0 ,radius 1) for a given value of z (in radians).
    - z is the angle of the line L which passes through the origin 0,0.
    - x and y are the coordinates where the hexagon H crosses the line L.
    Accepts values from 0 radians up to 2*pi radians.
    """
    step_angle = math.pi / 3
    if z >= 0 and z < step_angle:
        # The first segment, interval z = 0 to z < (pi/3)
        # this segment as a positive angle.
        t = z / (step_angle)
        x = 1 - t * math.cos(step_angle)
        y = -t * math.sin(step_angle)
    elif z >= step_angle and z < 2 * step_angle:
        # The 2nd segment, interval z = (pi/3) to z < 2*(pi/3)
        # this segment is flat on the x axis (no variable on x)
        t = 2 * (z - step_angle) / step_angle
        x = 0.5 - t * math.cos(step_angle)
        y = -math.sin(math.pi / 3)

    elif z >= 2 * step_angle and z < 3 * step_angle:
        # The 3rd segment, interval z = 2*(pi/3) to z < 3*(pi/3)
        # this segment as a negative angle.
        t = (z - 2 * step_angle) / step_angle
        x = t * math.cos(step_angle) - 1
        y = -t * math.sin(step_angle)

    elif z >= 3 * step_angle and z < 4 * step_angle:
        # The 4th segment, interval z = 3*(pi/3) to z < 4*(pi/3)
        # this segment as a positive angle.
        t = (z - 3 * step_angle) / step_angle
        x = t * math.cos(step_angle) - 1
        y = t * math.sin(step_angle)

    elif z >= 4 * step_angle and z < 5 * step_angle:
        # The 5th segment, interval z = 4*(pi/3) to z < 5*(pi/3)
        # this segment is flat on the x axis (no variable on x)
        t = 2 * (z - 4 * step_angle) / (step_angle)
        x = 0.5 - t * math.cos(step_angle)
        y = math.sin(math.pi / 3)
    elif z >= 5 * step_angle and z <= 6 * step_angle:
        # The 6th segment, interval z = 5*(pi/3) to z < 6*(pi/3)
        # this segment as a negative angle.
        t = (z - 5 * step_angle) / (step_angle)
        x = 1 - t * math.cos(step_angle)
        y = t * math.sin(step_angle)
    else:
        raise ValueError("z value must be comprised between 0 and 2*pi (inclusive)")
    return x, y


def draw_hexagon(size, *, step=0.0001, rot=0, fill=True, content_value=False):
    """
    Draws a hexagon with the specified size and rotation.

    Args:
        size (int): The size of the hexagon to draw.
        step (float, optional): The step size to use when drawing the hexagon. Defaults to 0.0001.
        rot (int, optional): The rotation angle of the hexagon in degrees. Defaults to 0.
        fill (bool, optional): Whether to fill the hexagon or just draw its edges. Defaults to True.
        content_value (bool, optional): The value to fill the hexagon with. Defaults to False.

    Returns:
        numpy.ndarray: A 2D array representing the hexagon.
    """
    # step size 0.0001 is sufficient for array dimensions up to 1000, you may need to tune a bit if you go higher.
    array = np.full((size, size), not content_value)
    radius = (size / 2) - 1
    middle = (size - 2) / 2
    middle_int = int(middle)
    # array[middle,middle] = False
    max_x, max_y = 0, 0
    min_x, min_y = 0, 0
    # Make the contour of the hexagon
    for z in np.arange(0, (math.pi) * 2, step=step):
        try:
            x, y = hex_x_y_from_z(z)
        except ValueError:
            continue
        max_x = x if x > max_x else max_x
        max_y = y if y > max_y else max_y
        min_x = x if x < min_x else min_x
        min_y = y if y < min_y else min_y

        x_bound = round((x * radius) + middle)
        y_bound = round((y * radius) + middle)
        if array[y_bound, x_bound] == content_value:
            continue  # we skip fill steps if this pixel is already set to content_value to save time
        try:
            if fill:
                # make edge and fill the line up to the y center
                if y_bound <= middle:
                    array[y_bound:middle_int, x_bound] = content_value
                else:
                    array[middle_int:y_bound, x_bound] = content_value
            else:
                array[y_bound, x_bound] = content_value
        except IndexError:
            pass

    if rot:
        array = np.rot90(array, 1)
    return array


def pad_to_shape(array, shape, background_value=True):
    """
    Pads an array with a specified shape to a desired shape with a given background value.

    Args:
    - array (numpy.ndarray): Input array to be padded.
    - shape (tuple): Desired shape for the output padded array.
    - background_value (bool): Value to fill the padded area, default is True.

    Returns:
    - numpy.ndarray: Padded array with the desired shape.
    """
    diff = np.subtract(shape, array.shape)

    # Calculate the padding sizes for each dimension
    pad_sizes = (
        (diff[0] // 2, diff[0] - (diff[0] // 2)),
        (diff[1] // 2, diff[1] - (diff[1] // 2)),
    )

    # Pad the array with zeros using the calculated pad sizes
    padded_arr = np.pad(array, pad_sizes, mode="constant", constant_values=background_value)
    return padded_arr


def offset_mask(array, x_offset, y_offset, background_value=True):
    """
    Offsets an input array by a given amount in the x and y directions.

    Parameters:
    -----------
    array : numpy.ndarray
        The input array to be offset.
    x_offset : float
        The amount to offset the array in the x direction.
    y_offset : float
        The amount to offset the array in the y direction.
    background_value : bool, optional
        The value to be used as the background in the output array

    Returns:
    --------
    numpy.ndarray
        The offset array.

    Notes:
    ------
    - The offset is performed by calculating the new indices of the array elements after the offset.
    - The out-of-bounds indices are set to the background value.
    """

    # Calculate the new indices after offsetting
    new_indices_x = np.arange(array.shape[1]) + round(x_offset)
    new_indices_y = np.arange(array.shape[0]) + round(y_offset)

    # Create a meshgrid of the new indices
    new_x, new_y = np.meshgrid(new_indices_x, new_indices_y)

    # Create a mask for the new indices that are outside the original array
    mask = (new_x < 0) | (new_x >= array.shape[1]) | (new_y < 0) | (new_y >= array.shape[0])

    # Initialize a new array of ones
    new_arr = np.full(array.shape, background_value)

    # Copy the original array to the new array at the new indices, ignoring the out-of-bounds indices
    new_arr[new_y[~mask], new_x[~mask]] = array[~mask]
    return new_arr


def draw_hexagon_mask(
    mask_shape,
    hexagon_x,
    hexagon_y,
    hexagon_size,
    *,
    content_value=True,
    rot=0,
    step=0.0001,
):
    """
    Draw a hexagon mask of a specified shape and size, centered at a given position.

    Parameters:
    -----------
    mask_shape : tuple
        The desired shape of the output mask, in (height, width) order. Expressed in pixels.
    hexagon_x : float
        The x-coordinate of the center of the hexagon, relative to the center of the mask. Expressed in pixels.
    hexagon_y : float
        The y-coordinate of the center of the hexagon, relative to the center of the mask. Expressed in pixels.
    hexagon_size : float
        The size of the hexagon inscribed circle "diameter". Expressed in pixels.
    content_value : bool, optional
        Whether the content of the hexagon should be set to True or False (default True).
    rot : float, optional
        Rotate the hexagon by 90° or not (default 0).
    step : float, optional
        The step size for the hexagon drawing algorithm (default 0.0001n works well for up to 1500 pixels hexagon_size).
        In radians.

    Returns:
    --------
    numpy.ndarray
        A binary mask of the specified shape, with the hexagon drawn at the specified location.
    """

    hexagon = draw_hexagon(hexagon_size, step=step, rot=rot, fill=True, content_value=content_value)
    mask_shape_y, mask_shape_x = mask_shape
    hexagon = pad_to_shape(hexagon, mask_shape, background_value=not content_value)
    hexagon = offset_mask(
        hexagon,
        x_offset=(-mask_shape_x / 2) + hexagon_x,
        y_offset=(-mask_shape_y / 2) + hexagon_y,
        background_value=not content_value,
    )
    return hexagon


def draw_hexagon_vertices(radius: float = 1, rotation: float = 0, center=[0, 0]) -> np.ndarray:
    hexagon_vertices = []
    for theta_deg in np.linspace(0, 360, 6, endpoint=False) + rotation:
        theta_rad = np.radians(theta_deg)
        x = radius * np.cos(theta_rad)
        y = radius * np.sin(theta_rad)
        hexagon_vertices.append([x, y])

    hexagon_vertices = np.array(hexagon_vertices)
    hexagon_vertices = np.concatenate([hexagon_vertices, hexagon_vertices[0][np.newaxis]])
    return hexagon_vertices + center


def shape_to_mask(polygon, mask_shape):
    """Takes a shapely polygon and a 2D mask shape as input, returns the 2D array of boolean, with True where shape sits

    Args:
        polygon (shapely.Polygon): The shapely 2D polygon to "imprint" into a mask.
        mask_shape (tuple, list): two values of the size of the 2D mask to make.

    Returns:
        np.ndarray: Boolean 2D array mask with inprinted shape.
    """
    y, x = np.indices(mask_shape)
    x, y = x.ravel(), y.ravel()
    mask_1D = ~contains(polygon, x, y)

    mask_2D = np.empty(mask_shape, bool)
    mask_2D[y, x] = mask_1D

    return mask_2D


def mask_to_shape(mask, as_type="Polygon", padding_size=2):
    """Takes a (boolean) 2D mask as input and returns a shapely Polygon from the shapes found in this mask

    Args:
        mask (np.ndarray): Boolean 2D array mask with inprinted shape.
        as_type (str, optional): desired output type for the shape.
            Defaults to "Polygon" wich makes the functio nreturn a shapely.Polygon object.
        padding_size (int, optional): Size of padding on all 4 sides, in pixels,
            to prevent an error in closing the shape if it touches the edges of the mask. Defaults to 2.

    Raises:
        ValueError: if as_type argument is invalid.

    Returns:
        shapely.Polygon: The shapely 2D polygon extracted from the mask
    """
    # pad with 1,1 True to avoid problems if mask is touching edge of the frame
    mask = np.pad(
        mask,
        pad_width=((padding_size, padding_size), (padding_size, padding_size)),
        mode="constant",
        constant_values=True,
    )
    contours, _ = findContours(mask.astype(np.uint8), RETR_LIST, CHAIN_APPROX_SIMPLE)
    # x-1 y-1 to come back to values before padding
    shape_from_bool = [
        Point(x - padding_size, y - padding_size) for contour in contours for [[x, y]] in contour if len(contour) > 4
    ]
    if as_type == "MultiPoint":
        func = MultiPoint
    elif as_type == "Polygon":
        func = Polygon
    else:
        raise ValueError("as_type is MultiPoint or Polygon")
    return func(shape_from_bool)
