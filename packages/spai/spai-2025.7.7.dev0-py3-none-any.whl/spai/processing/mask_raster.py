import rasterio


def mask_raster(raster_name, gdf, storage):
    # crop image to geometry
    ds = storage.read(raster_name)
    if ds is None:
        raise Exception("Raster not found")
    geometry = gdf.geometry
    return rasterio.mask.mask(ds, geometry)  # importar así para testing
