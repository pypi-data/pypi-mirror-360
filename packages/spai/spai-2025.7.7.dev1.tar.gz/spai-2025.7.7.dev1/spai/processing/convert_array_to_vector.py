import rasterio as rio
from rasterio.features import shapes
import numpy as np
import geopandas as gpd


def convert_array_to_vector(mask: np.array, img_path: str) -> gpd.GeoDataFrame:
    """Convert masked array to vector file(.shp).

    Args:
        binary_mask: Output predicted binary mask.
        img_path: Path of the raster file used for the prediction.

    Returns:
        shp: GeoPandas DataFrame.

    """
    with rio.open(img_path, mode='r') as src:

        # create a dict of features generator
        features = (
            {'properties': {'value': value}, 'geometry': shape}
            for (shape, value) in shapes(
                mask.astype(np.uint8), mask=mask, transform=src.transform
            )
        )

        shp = gpd.GeoDataFrame.from_features(
            features,
            crs=src.crs,  # no need to convert to string
            columns=['geometry', 'value']
        )

    return shp