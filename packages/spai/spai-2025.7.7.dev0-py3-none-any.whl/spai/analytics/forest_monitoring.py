import numpy as np
import geopandas as gpd
from ..processing import (
    read_raster,
    normalised_difference,
    mask_raster,
    autocategorize1D,
    px_count,
    colorize_raster,
    save_table,
)
import rasterio
from .utils import format_name

COLORS_MAPPING = {1: "orangered", 2: "yellow", 3: "lawngreen", 4: "darkgreen"}


def forest_monitoring(
    image_name: str,
    date: str,
    aoi_mask: dict,
    storage,
    prefix: str = "",
    analytics_prefix: str = "",
    names: dict = {},
) -> dict:
    """
    Monitor forest areas by analyzing satellite imagery.

    Parameters
    ----------
    image_name : str
        The name of the input raster image.
    date : str
        The date of the image in the format 'YYYYMMDD'.
    aoi_mask : dict
        The area of interest mask in GeoJSON format.
    storage : object
        Storage handler for saving and reading rasters and analytics.
    prefix : str, optional
        Prefix for the raster filenames. Default is an empty string.
    analytics_prefix : str, optional
        Prefix for the analytics filenames. Default is an empty string.
    names : dict, optional
        Custom names for the output raster and analytics files. Default is an empty dictionary.

    Returns
    -------
    dict
        A dictionary containing metadata about the processed layers and analytics.
    """
    # Default names for the output files
    default_names = {
        "ndvi": "ndvi_{date}.tif",
        "ndvi_masked": "ndvi_masked_{date}.tif",
        "ndvi_categorized": "ndvi_categorized_{date}.tif",
        "vegetation": "vegetation_{date}.tif",
        "vegetation_masked": "vegetation_masked_{date}.tif",
        "vegetation_masked_rgb": "vegetation_masked_rgb_{date}.tif",
        "quality_masked": "quality_masked_{date}.tif",
        "quality_masked_rgb": "quality_masked_rgb_{date}.tif",
        "vegetation_growth": "AOI_Vegetation_Growth.json",
        "vegetation_quality": "AOI_Vegetation_Quality.json",
    }
    names = {**default_names, **names}

    # Read the raster image with specified bands
    ds, raster = read_raster(image_name, storage, bands=[8, 4])

    # Calculate NDVI (Normalized Difference Vegetation Index)
    ndvi = normalised_difference(raster)

    # Save NDVI raster
    raster_name_ndvi = format_name(names["ndvi"], prefix, date)
    storage.create(ndvi, raster_name_ndvi, ds=ds)

    # Convert AOI mask to GeoDataFrame
    aoi_mask_gdf = gpd.GeoDataFrame.from_features(aoi_mask, crs=4326)

    # Mask the NDVI raster using the AOI mask
    ndvi_masked, _ = mask_raster(raster_name_ndvi, aoi_mask_gdf, storage)

    # Save masked NDVI raster
    raster_name_ndvi_masked = format_name(names["ndvi_masked"], prefix, date)
    storage.create(ndvi_masked, raster_name_ndvi_masked, ds=ds)

    # Categorize NDVI values
    ndvi_categorized = autocategorize1D(ndvi)

    # Save categorized NDVI raster
    raster_name_ndvi_categorized = format_name(names["ndvi_categorized"], prefix, date)
    storage.create(ndvi_categorized, raster_name_ndvi_categorized, ds=ds)

    # Apply threshold to categorize vegetation
    vegetation = (ndvi_categorized >= 3).astype(np.uint8)

    # If there is no vegetation, stop processing
    if not vegetation.any():
        print("No vegetation detected in the area of interest.")
        return {
            "pulse": "forest-monitoring",
            "images": [f"{image_name}"],
            "layers": [],
            "analytics": [],
        }

    # Save vegetation raster
    raster_name_vegetation = format_name(names["vegetation"], prefix, date)
    storage.create(vegetation, raster_name_vegetation, ds=ds)

    # Mask the vegetation raster using the AOI mask
    vegetation_masked, _ = mask_raster(raster_name_vegetation, aoi_mask_gdf, storage)

    # Save masked vegetation raster
    raster_name_vegetation_masked = format_name(
        names["vegetation_masked"], prefix, date
    )
    storage.create(vegetation_masked, raster_name_vegetation_masked, ds=ds)

    # Colorize the masked vegetation raster
    vegetation_masked_rgb = colorize_raster(vegetation_masked, colors=["darkgreen"])

    # Save colorized masked vegetation raster
    raster_name_vegetation_masked_rgb = format_name(
        names["vegetation_masked_rgb"], prefix, date
    )
    storage.create(vegetation_masked_rgb, raster_name_vegetation_masked_rgb, ds=ds)

    # Mask the categorized NDVI raster using the AOI mask
    quality_mask, _ = mask_raster(raster_name_ndvi_categorized, aoi_mask_gdf, storage)

    # Save quality mask raster
    raster_name_quality_mask = format_name(names["quality_masked"], prefix, date)
    storage.create(quality_mask, raster_name_quality_mask, ds=ds)

    # Colorize the quality mask raster
    quality_mask_rgb = colorize_raster(quality_mask, colors=COLORS_MAPPING)

    # Save colorized quality mask raster
    raster_name_quality_mask_rgb = format_name(
        names["quality_masked_rgb"], prefix, date
    )
    storage.create(quality_mask_rgb, raster_name_quality_mask_rgb, ds=ds)

    # Count pixels in masked vegetation raster
    # Make sure we only count pixels inside de AoI
    # To do this, we create a rasterized mask of the AoI
    mask = rasterio.features.rasterize(
        [(geom, 1) for geom in aoi_mask_gdf.geometry],
        out_shape=ds.shape,
        transform=ds.transform,
        fill=0,
        dtype="uint8",
    )
    mask = mask.astype(bool)

    # Convert the pixels outside the mask to 100
    vegetation_masked_nan = np.where(mask, vegetation_masked, 100)
    growth = px_count(vegetation_masked_nan, values=[0, 1])

    # Convert growth pixel count to hectares
    growth_hectares = np.divide(
        growth, 100, out=np.zeros_like(growth, dtype=np.float64), where=100 != 0
    )

    # Save growth analytics table
    growth_table_name = format_name(names["vegetation_growth"], analytics_prefix, date)
    growth_columns = ["Not Vegetation Ha", "Vegetation Ha", "Total"]
    save_table(
        data=growth_hectares,
        columns=growth_columns,
        table_name=growth_table_name,
        date=date,
        storage=storage,
    )

    # Count pixels in quality mask
    quality_mask_nan = np.where(mask, quality_mask, 100)  # Convert out pixels to 100
    quality = px_count(quality_mask_nan, values=[1, 2, 3, 4])

    # Convert quality pixel count to hectares
    quality_hectares = np.divide(
        quality, 100, out=np.zeros_like(quality, dtype=np.float64), where=100 != 0
    )

    # Save quality analytics table
    quality_table_name = format_name(
        names["vegetation_quality"], analytics_prefix, date
    )
    quality_columns = [
        "Bare Ground",
        "Sparse or Unhealthy Vegetation",
        "Healthy Vegetation",
        "Very Healthy Vegetation",
        "Total",
    ]
    save_table(
        data=quality_hectares,
        table_name=quality_table_name,
        columns=quality_columns,
        date=date,
        storage=storage,
    )

    # Return metadata about the processed layers and analytics
    return {
        "pulse": "forest-monitoring",
        "images": [f"{image_name}"],
        "layers": [
            f"{raster_name_ndvi}",
            f"{raster_name_ndvi_masked}",
            f"{raster_name_ndvi_categorized}",
            f"{raster_name_vegetation}",
            f"{raster_name_vegetation_masked}",
            f"{raster_name_vegetation_masked_rgb}",
            f"{raster_name_quality_mask}",
            f"{raster_name_quality_mask_rgb}",
        ],
        "analytics": [f"{growth_table_name}", f"{quality_table_name}"],
    }
