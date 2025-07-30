import matplotlib
import numpy as np
from warnings import warn


def colorize_raster(raster, colors, nodata_value=None, colorize_zero=False):
    """
    Colorize a raster image based on unique values in the raster.

    Parameters
    ----------
    raster : numpy.ndarray
        A 2-dimensional or 3-dimensional array representing a raster image.
    colors : dict or list
        A dictionary mapping unique values in the raster to colors in the format {value: color} or a list of colors.
        If a list is provided, the colors will be assigned to unique values in the raster in ascending order.
    nodata_value : int, float, optional
        The value representing nodata in the raster. If None, nodata is assumed to be np.nan.
    colorize_zero : bool, optional
        Whether to colorize 0 values in the raster. Default is False.

    Returns
    -------
    numpy.ndarray
        A 4-dimensional array representing the colorized raster image with shape (4, height, width).
    """
    # If raster has 3 dimensions, select the first band
    if raster.ndim == 3:
        raster = raster[0, :, :]
    elif raster.ndim != 2:
        raise ValueError("Input raster must be a 2-dimensional or 3-dimensional array")

    # Create a mask for nodata values
    if nodata_value is None:
        nodata_mask = np.isnan(raster)
    else:
        nodata_mask = raster == nodata_value

    # Get unique values in the raster excluding 0 if colorize_zero is False
    if not colorize_zero:
        unique_values = np.unique(raster[~nodata_mask])
        unique_values = unique_values[unique_values > 0]
    else:
        unique_values = np.unique(raster[~nodata_mask])

    if isinstance(colors, dict):
        color_mapping = colors
        # Ensure all unique values have a color in the mapping
        for value in unique_values:
            if value not in color_mapping:
                warn(
                    f"No color provided for raster value {value} in the color mapping."
                )
    else:
        if len(unique_values) != len(colors):
            warn(
                f"The number of unique values in the raster ({len(unique_values)}) does not match the number of colors provided ({len(colors)})."
            )
        color_mapping = {value: color for value, color in zip(unique_values, colors)}

    # Create an array for colors with 4 bands (RGB + Alpha)
    colored_image = np.zeros((raster.shape[0], raster.shape[1], 4), dtype=np.uint8)

    # Map colors to the image
    for value, color in color_mapping.items():
        rgb_color = np.array(matplotlib.colors.to_rgb(color)) * 255
        colored_image[raster == value, :3] = rgb_color

    # Initialize the alpha channel to 255 (fully opaque)
    colored_image[:, :, 3] = 255

    if not colorize_zero:
        # Set alpha to 0 where RGB values are [0, 0, 0] or nodata
        mask = np.all(colored_image[:, :, :3] == 0, axis=-1) | nodata_mask
        colored_image[mask, 3] = 0
    else:
        # Ensure nodata values are fully transparent
        colored_image[nodata_mask, 3] = 0

    # transpose
    colored_image = np.transpose(colored_image, (2, 0, 1))

    return colored_image
