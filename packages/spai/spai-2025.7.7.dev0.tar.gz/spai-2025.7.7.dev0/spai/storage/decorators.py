def with_rio(func):
    def wrapper(self, *args, **kwargs):
        try:
            import rasterio as rio
        except ImportError:
            raise ImportError(
                "The rasterio package is required for this function. Please install it with 'pip install rasterio' and try again."
            )
        
        return func(self, *args, **kwargs)

    return wrapper


def with_pyarrow(func):
    def wrapper(self, *args, **kwargs):
        try:
            import pyarrow as pa

        except ImportError:
            raise ImportError(
                "The pyarrow package is required for this function. Please install it with 'pip install pyarrow' and try again."
            )
        
        return func(self, pa, *args, **kwargs)

    return wrapper


def with_s3fs(func):
    def wrapper(self, *args, **kwargs):
        try:
            import s3fs

        except ImportError:
            raise ImportError(
                "The s3fs package is required for this function. Please install it with 'pip install s3fs' and try again."
            )
        
        return func(self, s3fs, *args, **kwargs)

    return wrapper


def with_xarray(func):
    def wrapper(self, *args, **kwargs):
        try:
            import xarray as xr
            import netCDF4

        except ImportError:
            raise ImportError(
                "The xarray and netcdf4 packages are required for this function. Please install it with 'pip install xarray netcdf4' and try again."
            )
        
        return func(self, xr, *args, **kwargs)

    return wrapper


def with_zarr(func):
    def wrapper(self, *args, **kwargs):
        try:
            import zarr

        except ImportError:
            raise ImportError(
                "The zarr package is required for this function. Please install it with 'pip install zarr' and try again."
            )
        
        return func(self, *args, **kwargs)

    return wrapper


def with_geopandas(func):
    def wrapper(self, *args, **kwargs):
        try:
            import geopandas as gpd
   
        except ImportError:
            raise ImportError(
                "The geopandas package is required for this function. Please install it with 'pip install geopandas' and try again."
            )
        
        return func(self, gpd, *args, **kwargs)

    return wrapper


def with_rioxarray(func):
    def wrapper(self, *args, **kwargs):
        try:
            import rioxarray as rxr

        except ImportError:
            raise ImportError(
                "The rioxarray package is required for this function. Please install it with 'pip install rioxarray' and try again."
            )
        
        return func(self, rxr, *args, **kwargs)

    return wrapper
