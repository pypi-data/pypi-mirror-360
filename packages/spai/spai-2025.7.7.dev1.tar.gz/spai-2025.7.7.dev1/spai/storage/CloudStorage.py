import fnmatch
from io import BytesIO
import numpy as np
import pandas as pd

from .minio import get_client
from .BaseStorage import BaseStorage
from .decorators import with_rio


# ESTA ES LA IMPLEMENTACIÓN VIEJA, PERO QUE SE PUEDE APROVECHAR PARA LA NUEVA S3Storage


class CloudStorage(BaseStorage):
    # store in s3
    def __init__(self, bucket="spai"):
        super().__init__()
        self.client = get_client()
        self.bucket = bucket
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)
            print(f"{bucket} created")

    def get_url(self, name):
        return self.client.presigned_get_object(self.bucket, name)

    def create_from_path(self, data, name):
        self.client.fput_object(self.bucket, name, data)
        return self.get_url(name)

    def create_from_image(self, data, name):
        image_bytes = BytesIO()
        # get format from file extension
        format = name.split(".")[-1]
        data.save(image_bytes, format=format)
        image_bytes.seek(0)
        self.client.put_object(
            self.bucket, name, image_bytes, len(image_bytes.getvalue())
        )
        return self.get_url(name)

    @with_rio
    def create_from_rasterio(self, rio, x, name, ds, window=None):
        transform = ds.transform if window is None else ds.window_transform(window)
        with rio.io.MemoryFile() as memfile:
            with memfile.open(
                driver="GTiff",
                count=1 if x.ndim < 3 else x.shape[0],
                height=x.shape[0] if x.ndim < 3 else x.shape[1],
                width=x.shape[1] if x.ndim < 3 else x.shape[2],
                dtype=np.uint8 if x.dtype == "bool" else x.dtype,
                crs=ds.crs,
                transform=transform,
                # nbits=1 if x.dtype == 'bool' else
            ) as dest_ds:
                bands = 1 if x.ndim < 3 else [i + 1 for i in range(x.shape[0])]
                dest_ds.write(x, bands)
            self.client.put_object(
                self.bucket, name, memfile, length=-1, part_size=10 * 1024 * 1024
            )
        return self.get_url(name)

    def create_from_array(self, data, name):
        array_bytes = BytesIO()
        np.save(array_bytes, data)
        array_bytes.seek(0)
        self.client.put_object(
            self.bucket, name, array_bytes, len(array_bytes.getvalue())
        )
        return self.get_url(name)

    def create_from_csv(self, data, name):
        csv_bytes = BytesIO()
        data.to_csv(csv_bytes)
        csv_bytes.seek(0)
        self.client.put_object(self.bucket, name, csv_bytes, len(csv_bytes.getvalue()))
        return self.get_url(name)

    def create_from_json(self, data, name):
        json_bytes = BytesIO()
        data.to_json(json_bytes)
        json_bytes.seek(0)
        self.client.put_object(
            self.bucket, name, json_bytes, len(json_bytes.getvalue())
        )
        return self.get_url(name)

    def list(self, pattern="*"):
        return fnmatch.filter(  # need to test
            [
                obj.object_name
                for obj in self.client.list_objects(self.bucket, recursive=True)
            ],
            pattern,
        )

    def read_object(self, name):
        return BytesIO(self.client.get_object(self.bucket, name).read())

    def read_from_array(self, name):
        return np.load(self.read_object(name))

    @with_rio
    def read_from_rasterio(self, rio, name):
        return rio.open(self.read_object(name))

    def read_from_csv(self, name):
        return pd.read_csv(self.read_object(name), index_col=0)

    def read_from_json(self, name):
        return pd.read_json(self.read_object(name))
