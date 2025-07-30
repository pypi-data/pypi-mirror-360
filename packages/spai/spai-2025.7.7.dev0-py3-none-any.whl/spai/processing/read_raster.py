# Updated read_raster function to handle invalid extensions
def read_raster(image_name, storage, bands=None):
    ds = storage.read(image_name)
    if ds is None:
        raise TypeError("Not a valid raster file")
    if not bands:
        raster = ds.read()
    else:
        raster = ds.read(bands)
    return ds, raster
