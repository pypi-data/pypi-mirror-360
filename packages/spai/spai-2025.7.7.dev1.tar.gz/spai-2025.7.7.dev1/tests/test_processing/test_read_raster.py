from unittest import mock
from unittest.mock import patch
import pytest

from spai.spai.processing.read_raster import read_raster

def test_read_raster_from_rasterio():
    storage = mock.Mock()
    ds = mock.Mock()
    storage.read.return_value = ds
    ds.read.return_value = "raster"
    assert read_raster("image_name", storage) == (ds, "raster")

def test_read_raster_if_ds_is_none():
    storage = mock.Mock()
    ds = mock.Mock()
    storage.read.return_value = None
    with pytest.raises(TypeError) as exc_info:
        read_raster("image_name", storage)
    assert str(exc_info.value) == "Not a valid raster file"
    storage.read.assert_called_once_with("image_name")
    ds.read.assert_not_called()
