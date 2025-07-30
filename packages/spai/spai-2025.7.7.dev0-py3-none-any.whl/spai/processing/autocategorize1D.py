import numpy as np
from .utils import control_uint_type


def autocategorize1D(
    raster: np.ndarray, iterations: int = 200, centers: list = [0.1, 0.35, 0.50, 0.70]
) -> np.ndarray:
    """
    Categorize raster pixels into clusters based on initial center values using iterative mean adjustment.

    Parameters
    ----------
    raster : numpy.ndarray
        A 2-dimensional array representing the raster image.
    iterations : int, optional
        Number of iterations for the clustering process. Default is 200.
    centers : list, optional
        Initial center values for the clustering process. Default is [0.1, 0.35, 0.50, 0.70].

    Returns
    -------
    numpy.ndarray
        A 2-dimensional array with the same shape as the input raster, where pixel values represent cluster categories.
    """
    # Ensure the number of iterations is within a valid range
    iterations = max(1, min(iterations, 200))
    shape = raster.shape
    raster = raster.reshape(-1, 1)

    # Iteratively adjust cluster centers
    for _ in range(iterations):
        clusters = np.argmin(np.abs(raster - centers), axis=1)
        centers = [np.mean(raster[clusters == j]) for j in range(len(centers))]

    # Reshape clusters back to original raster shape and adjust values to avoid 0
    array_categorized = clusters.reshape(shape) + 1  # Add 1 to avoid 0 values
    dtype = control_uint_type(array_categorized)  # Control uint type
    array_categorized = array_categorized.astype(dtype)

    return array_categorized
