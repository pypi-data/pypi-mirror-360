from rasterio.mask import mask


def mask_a_raster(ds, geometry):
    return mask(ds, geometry, crop=True)
