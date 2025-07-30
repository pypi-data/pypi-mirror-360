import os
from glob import glob
from pathlib import Path
import numpy as np
import pandas as pd
import shutil
import json
from datetime import datetime

from .BaseStorage import BaseStorage
from .decorators import (
    with_rio,
    with_geopandas,
    with_xarray,
    with_rioxarray,
    with_pyarrow,
    with_zarr,
)

DRIVER_MAP = {"shp": "ESRI Shapefile", "gml": "GML"}


class LocalStorage(BaseStorage):
    def __init__(self, path="data"):
        super().__init__()
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            print(f"'{self.path}' created")
        else:
            print(f"'{self.path}' folder ready to use")

    def exists(self, name):
        return os.path.exists(self.get_path(name))

    def get_path(self, name):
        return os.path.join(self.path, name)

    def delete(self, name):
        if os.path.isdir(self.get_path(name)):
            shutil.rmtree(self.get_path(name))
        else:
            os.remove(self.get_path(name))

    def create_from_path(self, data, name):
        dst_path = self.get_path(name)
        shutil.move(data, dst_path)  # porque se hace un move en vez de un copy?
        return dst_path

    def create_from_dict(self, data, name):
        if name.endswith(".json") or name.endswith(".geojson"):
            dst_path = self.get_path(name)
            self._create_dir(dst_path)
            with open(dst_path, "w") as f:
                json.dump(data, f)
            return dst_path
        else:
            raise TypeError("Not a valid dict type extension")

    def create_from_string(self, data, name):
        dst_path = self.get_path(name)
        self._create_dir(dst_path)
        with open(dst_path, "w") as f:
            f.write(data)
        return dst_path

    def create_from_dataframe(self, data, name):
        if name.endswith(".csv"):
            dst_path = self.get_path(name)
            self._create_dir(dst_path)
            data.to_csv(dst_path)
            return dst_path
        elif name.endswith(".json"):
            dst_path = self.get_path(name)
            self._create_dir(dst_path)
            data.to_json(dst_path)
            return dst_path
        elif name.endswith(".geojson"):
            dst_path = self.get_path(name)
            self._create_dir(dst_path)
            data.to_file(dst_path)
            return dst_path

    def create_from_image(self, data, name):
        dst_path = self.get_path(name)
        self._create_dir(dst_path)
        data.save(dst_path)
        return dst_path

    @with_rio
    def create_from_rasterio(self, rio, x, name, ds, window=None):
        dst_path = self.get_path(name)
        self._create_dir(dst_path)
        kwargs = ds.meta.copy()
        transform = ds.transform if window is None else ds.window_transform(window)
        kwargs.update(
            driver="GTiff",
            count=1 if x.ndim < 3 else x.shape[0],
            height=x.shape[0] if x.ndim < 3 else x.shape[1],
            width=x.shape[1] if x.ndim < 3 else x.shape[2],
            dtype=np.uint8 if x.dtype == "bool" else x.dtype,
            crs=ds.crs,
            transform=transform,
            # nbits=1 if x.dtype == 'bool' else
        )
        with rio.open(dst_path, "w", **kwargs) as dst:
            bands = 1 if x.ndim < 3 else [i + 1 for i in range(x.shape[0])]
            dst.write(x, bands)
        return dst_path

    def create_from_array(self, data, name):
        dst_path = self.get_path(name)
        self._create_dir(dst_path)
        np.save(dst_path, data)
        return dst_path

    def create_from_csv(self, data, name):
        dst_path = self.get_path(name)
        self._create_dir(dst_path)
        data.to_csv(dst_path)
        return dst_path

    def create_from_json(self, data, name):
        dst_path = self.get_path(name)
        self._create_dir(dst_path)
        data.to_json(dst_path)
        return dst_path

    @with_pyarrow
    def create_from_parquet(self, pa, data, name):
        dst_path = self.get_path(name)
        self._create_dir(dst_path)
        data.to_parquet(dst_path, engine="pyarrow")
        return dst_path

    @with_zarr
    def create_from_zarr(self, data, name):
        dst_path = self.get_path(name)
        self._create_dir(dst_path)
        data.to_zarr(dst_path)
        return dst_path

    @with_xarray
    def create_from_netcdf(self, xr, data, name):
        dst_path = self.get_path(name)
        self._create_dir(dst_path)
        data.to_netcdf(dst_path)

        return dst_path

    @with_rioxarray
    def create_from_rioxarray(self, rxr, data, name):
        dst_path = self.get_path(name)
        self._create_dir(dst_path)
        data.rio.to_raster(dst_path)
        return dst_path

    def list(self, pattern="*", recursive=True):
        base_path = Path(self.path)
        paths = base_path.rglob(pattern) if recursive else base_path.glob(pattern)
        
        object_names = set()
        zarr_roots = set()

        for path in paths:
            relative_path = path.relative_to(base_path).as_posix()

            if path.is_dir():
                continue

            if ".zarr" in relative_path:
                zarr_roots.add(relative_path.split(".zarr")[0] + ".zarr")
            else:
                object_names.add(relative_path)

        return list(zarr_roots | object_names)

    def read_from_array(self, name, path=None):
        if path is None:
            path = self.get_path(name)
        return np.load(path)

    @with_rio
    def read_from_rasterio(self, rio, name):
        return rio.open(self.get_path(name))

    def read_from_csv(self, name):
        return pd.read_csv(self.get_path(name), index_col=0)

    def read_from_json(self, name):
        return pd.read_json(self.get_path(name))

    @with_geopandas
    def read_from_geojson(self, gpd, name):
        return gpd.read_file(self.get_path(name))

    @with_geopandas
    @with_pyarrow
    def read_from_parquet(self, pa, gpd, name):
        df = pd.read_parquet(self.get_path(name), engine="pyarrow")
        if "geometry" in df.columns or "geom" in df.columns:
            from shapely import wkb

            geom_column = "geometry" if "geometry" in df.columns else "geom"

            df[geom_column] = df[geom_column].apply(wkb.loads)
            gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geom_column)

            return gdf

    @with_geopandas
    def read_from_geo_file(self, gpd, name, driver):
        return gpd.read_file(self.get_path(name), driver=DRIVER_MAP[driver])

    @with_geopandas
    def create_from_geo_file(self, gpd, data, name, driver):
        dst_path = self.get_path(name)
        self._create_dir(dst_path)
        data.to_file(dst_path, driver=DRIVER_MAP[driver])
        return dst_path

    @with_xarray
    def read_from_netcdf(self, xr, name):
        return xr.open_dataset(self.get_path(name), decode_timedelta=True)

    @with_zarr
    @with_xarray
    def read_from_zarr(self, xr, name):
        return xr.open_zarr(self.get_path(name), decode_timedelta=True)

    def read_file(self, name):
        return open(self.get_path(name), "r").read()

    async def data_stream(self, name):
        with open(self.get_path(name), "rb") as file:
            while True:
                chunk = file.read(1024 * 1024)  # Read in chunks of 1MB
                if not chunk:
                    break
                yield chunk

    def object_info(self, name):
        file_stat = os.stat(self.get_path(name))
        return {
            "size": file_stat.st_size,
            "content_type": file_stat.st_mode,
        }
