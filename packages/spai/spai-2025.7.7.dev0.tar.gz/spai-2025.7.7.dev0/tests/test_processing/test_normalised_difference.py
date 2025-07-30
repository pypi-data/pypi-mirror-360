import numpy as np
import pytest
from unittest import mock
from unittest.mock import patch

from spai.spai.processing import normalised_difference

# Test cases

def test_normalised_difference_simple():
    # Simple example with bands [1, 2]
    raster = np.array([
        [[1, 1], [0, 0]],   # Band 1
        [[0, 0], [1, 1]],   # Band 2
    ])

    result = normalised_difference(raster)
    expected_result = np.array([[1., 1.], [-1., -1.]])
    assert np.allclose(result, expected_result)
    assert result.shape == (2, 2)
    assert result.dtype == np.float64

def test_normalised_difference_less_than_two_bands():
    # Test normalised difference with a raster containing less than two bands
    raster = np.array([
        [[1, 2], [3, 4]],   # Only one band
    ])

    with pytest.raises(ValueError) as exc_info:
        normalised_difference(raster)

    assert str(exc_info.value) == "Function `normalised_difference` strictly expects at least a 2-band image. You provided a 1-band image instead."