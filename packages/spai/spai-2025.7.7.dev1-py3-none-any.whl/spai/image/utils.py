import rasterio as rio
import numpy as np
from PIL import Image


# TODO: should know the source in order to generate the rgb thumbnail
def thumbnail(image, storage=None, sensor="S2L2A", size=None, factor=1):
    ds = rio.open(image)
    if sensor == "S2L2A" or sensor == "S2L1C":
        rgb = ds.read((4, 3, 2)) / 4000
        rgb = np.clip(rgb, 0, 1)
        rgb = np.moveaxis(rgb, 0, -1)
        rgb = (rgb * 255).astype(np.uint8)
        image = Image.fromarray(rgb)
    elif sensor == "S1":
        ds = rio.open(image)
        vv = ds.read(1)
        vh = ds.read(2)
        # vv = np.clip(2.0 * vv, 0, 1)
        rgb = np.stack([(5.5 * vh > 0.5).astype(float), vv, 8 * vh], axis=-1)
        # db = 10 * np.log10(vv)
        # print(db.shape, db.min(), db.max())
        # db = np.clip(db, -30, 0) * (-8.4)
        # print(db.shape, db.min(), db.max())
        rgb = np.clip(rgb, 0, 1)
        rgb = (rgb * 255.0).astype(np.uint8)
        image = Image.fromarray(rgb)
    else:
        raise Exception(f"sensor {sensor} not supported")
    if size:
        image.thumbnail(size)
    elif factor != 1:
        assert factor > 0, "factor must be greater than 0"
        image = image.resize((int(image.width // factor), int(image.height // factor)))
    if storage is None:
        return image
    return storage.create(image, "thumbnail.png")
