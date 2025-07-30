import numpy as np
from unittest.mock import patch
from unittest import mock

from spai.spai.processing import autocategorize1D


@patch('numpy.argmin', side_effect=lambda arr, axis: np.zeros(arr.shape[0], dtype=int))
@patch('numpy.mean', side_effect=lambda arr: 0.5)
def test_autocategorize1D_defaults(mocked_mean, mocked_argmin):
    raster = np.array([
        [[1, 1], [0, 0]],   # Band 1
        [[0, 0], [1, 1]],   # Band 2
    ])

    autocategorize1D(raster)  # Call the function with the raster

    # Assertions
    assert mocked_argmin.call_count == 200
    assert mocked_mean.call_count == 4*200

@patch('numpy.argmin', side_effect=lambda arr, axis: np.zeros(arr.shape[0], dtype=int))
@patch('numpy.mean', side_effect=lambda arr: 0.5)
def test_autocategorize1D_with_attr(mocked_mean, mocked_argmin):
    raster = np.array([
        [[1, 1], [0, 0]],   # Band 1
        [[0, 0], [1, 1]],   # Band 2
    ])

    autocategorize1D(raster, iterations=10, centers=[0.1, 0.2, 0.3]) # Call the function with the raster and the optional arguments

    # Assertions
    assert mocked_argmin.call_count == 10
    assert mocked_mean.call_count == 3*10