from PIL import Image
import numpy as np
import pandas as pd
import os


class BaseStorage:
    def __init__(self):
        pass

    def create(self, data, name, **kwargs):
        if isinstance(data, str):
            # check if is path or string
            if os.path.isfile(data):
                return self.create_from_path(data, name)
            return self.create_from_string(data, name)
        elif isinstance(data, Image.Image):
            return self.create_from_image(data, name)
        elif isinstance(data, np.ndarray):
            ext = name.split(".")[-1]
            if ext in ["tif", "tiff"]:
                if "ds" in kwargs:
                    return self.create_from_rasterio(data, name, kwargs["ds"])
                raise TypeError("Missing ds argument")
            elif ext == "npy":
                return self.create_from_array(data, name)
            else:
                raise TypeError("Not a valid array type")
        elif isinstance(data, pd.core.frame.DataFrame):
            ext = name.split(".")[-1]
            if ext == "parquet":
                return self.create_from_parquet(data, name)
            elif ext in ["shp", "kml", "kmz", "gml"]:
                return self.create_from_geo_file(data, name, ext)
            return self.create_from_dataframe(data, name)
            # ext = name.split(".")[-1]
            # if ext == "csv":
            #     return self.create_from_csv(data, name)
            # elif ext == "json":
            #     return self.create_from_json(data, name)
            # else:
            #     raise TypeError("Not a valid dataframe type")
        elif isinstance(data, dict):
            return self.create_from_dict(data, name)
        elif hasattr(data, "variables") and hasattr(data, "coords"):
            # Object is like a xr.Dataset
            ext = name.split(".")[-1]
            if ext == "zarr":
                return self.create_from_zarr(data, name)
            elif ext == "nc":
                return self.create_from_netcdf(data, name)
            elif ext == "tif":
                return self.create_from_rioxarray(data, name)
        else:
            raise TypeError("Not a valid type")

    def create_from_data(self, data, path):
        with open(path, "wb") as f:
            f.write(data.read())
        return path

    def read(self, name):
        ext = name.split(".")[-1]
        if ext == "npy":
            return self.read_from_array(name)
        elif ext in ["tif", "tiff"]:
            return self.read_from_rasterio(name)
        elif ext == "csv":
            return self.read_from_csv(name)
        elif ext == "json":
            return self.read_from_json(name)
        elif ext == "geojson":
            return self.read_from_geojson(name)
        elif ext == "parquet":
            return self.read_from_parquet(name)
        elif ext == "nc":
            return self.read_from_netcdf(name)
        elif ext == "zarr":
            return self.read_from_zarr(name)
        elif ext in ["shp", "gml"]:
            return self.read_from_geo_file(name, ext)
        raise TypeError("Not a valid type")

    def update(self):
        pass

    def delete(self):
        pass

    def list(self, pattern="*", recursive=True):
        pass

    def exists(self, name):
        pass

    def _create_dir(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    # stream files to download

    def read_file(self, name):
        pass

    async def data_stream(self, name):
        pass

    def object_info(self, name):
        pass
