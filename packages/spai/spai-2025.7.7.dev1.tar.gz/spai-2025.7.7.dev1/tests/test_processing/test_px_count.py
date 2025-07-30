import numpy as np

from spai.spai.processing.px_count import px_count


# Test px_count function

# Test case 1: Basic test with default values
def test_px_count_default():
    raster = np.array([[1, 2, 1], [3, 1, 4]])
    result = px_count(raster)
    assert np.array_equal(result, [0, 3, 1, 1, 1, 6])

# Test case 2: Test with specific values provided
def test_px_count_with_values():
    raster = np.array([[1, 2, 1], [3, 1, 4]])
    values = [1, 3]
    result = px_count(raster, values)
    assert np.array_equal(result, [3, 1, 4])

# Test case 3: Test with empty values provided
def test_px_count_with_empty_values():
    raster = np.array([[1, 2, 1], [3, 1, 4]])
    values = []
    result = px_count(raster, values)
    assert np.array_equal(result, [0, 3, 1, 1, 1, 4])

# Test case 4: Test with values larger than the count array
def test_px_count_with_large_values():
    raster = np.array([[1, 2, 1], [3, 1, 4]])
    values = [10, 20]
    result = px_count(raster, values)
    assert np.array_equal(result, [0, 0, 0])

# Test case 5: Test with all zeros in the raster
def test_px_count_all_zeros():
    raster = np.zeros((10, 10))
    result = px_count(raster)
    assert np.array_equal(result, [100, 100])