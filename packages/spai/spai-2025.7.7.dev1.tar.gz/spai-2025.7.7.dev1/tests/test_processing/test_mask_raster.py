from unittest import mock
from unittest.mock import patch
import pytest

from spai.spai.processing.mask_raster import mask_raster

# Test mask_raster function
@patch('rasterio.mask.mask')
def test_mask_raster(mocked):
    storage = mock.Mock()
    storage.read.return_value = "ds"
    gdf = mock.Mock()
    gdf.geometry = "geometry"
    mocked.return_value = "mask"
    assert mask_raster("raster_name", gdf, storage) == "mask"
    storage.read.assert_called_once_with("raster_name")
    mocked.assert_called_once_with("ds", "geometry")

# Test mask_raster function if ds is None
@patch('rasterio.mask.mask')
def test_mask_raster_if_ds_is_none(mocked):
    storage = mock.Mock()
    storage.read.return_value = None
    gdf = mock.Mock()
    gdf.geometry = "geometry"
    mocked.return_value = "mask"
    with pytest.raises(Exception) as exc_info:
        mask_raster("raster_name", gdf, storage)
    assert str(exc_info.value) == "Raster not found"
    storage.read.assert_called_once_with("raster_name")
    mocked.assert_not_called()