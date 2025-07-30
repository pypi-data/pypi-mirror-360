import numpy as np
import math
import pandas as pd

from scipy.ndimage import median_filter
from skimage.exposure import equalize_hist

from ..processing import mask_raster
from ..processing import read_raster
from ..processing import colorize_raster
from ..processing import px_count
from ..processing import save_table
from ..processing import normalised_difference
from ..processing import convert_array_to_vector

from .utils import format_name

COLOR_MAPPING = {1: "green", 2: "yellow", 3: "red"}


def water_quality(
    image_name: str,
    date: str,
    storage,
    prefix: str = "",
    analytics_prefix: str = "",
    names: dict = {},
):
    """
    This function calculates the water quality of a given image.

    It calculates the following layers:
        - Normalized Difference Water Index (NDWI) - ndwi_{date}.tif, ndwi_masked_{date}.tif, ndwi_categorized_{date}.tif
        - Normalized Difference Turbidity Index (NDTI) - ndti_{date}.tif, ndti_masked_{date}.tif, ndti_categorized_{date}.tif
        - Normalized Difference Chlorophyll Index (NDCI) - ndci_{date}.tif, ndci_masked_{date}.tif, ndci_categorized_{date}.tif
        - Water Mask - water_mask_{date}.tif
        - Dissolved Organic Carbon (DOC) - DOC_{date}.tif, DOC_masked_{date}.tif, DOC_categorized_{date}.tif

    It also calculates the following analytics:
        - Water Extent (in hectares and percentage) - table_water_extent.json
        - Water Turbidity (in hectares and percentage) - table_turbidity_Ha.json, table_turbidity_percent.json
        - Water Chlorophyll (in hectares and percentage) - table_chlorophyll_Ha.json, table_chlorophyll_percent.json
        - Water DOC (in hectares and percentage) - table_DOC_Ha.json, table_DOC_percent.json

    Parameters
    ----------
    image_name : str
        The name of the image to be processed.
    date: str
        The date of the image to be processed.
    storage : Storage
        The Storage object.
    prefix : str
        The prefix to be added to the name of the layers.
    analytics_prefix : str
        The prefix to be added to the name of the analytics.
    names : dict
        The names of the layers and analytics to be saved.

    Returns
    -------
    dict
        A dictionary with the pulse, the images, the layers, and the analytics.

    """
    default_names = {
        "ndwi": "ndwi_{date}.tif",
        "ndwi_masked": "ndwi_masked_{date}.tif",
        "ndwi_categorized": "ndwi_categorized_{date}.tif",
        "ndti": "ndti_{date}.tif",
        "ndti_masked": "ndti_masked_{date}.tif",
        "ndti_categorized": "ndti_categorized_{date}.tif",
        "ndti_categorized_rgb": "ndti_categorized_rgb_{date}.tif",
        "ndci": "ndci_{date}.tif",
        "ndci_masked": "ndci_masked_{date}.tif",
        "ndci_categorized": "ndci_categorized_{date}.tif",
        "ndci_categorized_rgb": "ndci_categorized_rgb_{date}.tif",
        "water_mask": "water_mask_{date}.tif",
        "DOC": "DOC_{date}.tif",
        "DOC_masked": "DOC_masked_{date}.tif",
        "DOC_categorized": "DOC_categorized_{date}.tif",
        "DOC_categorized_rgb": "DOC_categorized_rgb_{date}.tif",
        "turbidity_Ha": "table_turbidity_Ha.json",
        "turbidity_percent": "table_turbidity_percent.json",
        "chlorophyll_Ha": "table_chlorophyll_Ha.json",
        "chlorophyll_percent": "table_chlorophyll_percent.json",
        "DOC_Ha": "table_DOC_Ha.json",
        "DOC_percent": "table_DOC_percent.json",
        "water_extent": "table_water_extent.json",
    }
    names = {**default_names, **names}

    # read_raster image
    dataset, raster = read_raster(image_name, storage, bands=[3, 4, 5, 8])

    """ LAYERS """
    # NDWI

    # calculate ndwi
    ndwi = normalised_difference(raster, [1, 4])

    # save_raster ndwi
    raster_name_ndwi = format_name(names["ndwi"], prefix, date)
    storage.create(ndwi, raster_name_ndwi, ds=dataset)

    # NDTI
    # calculate ndti
    ndti = normalised_difference(raster, [2, 1])

    # save_raster ndti
    raster_name_ndti = format_name(names["ndti"], prefix, date)
    storage.create(ndti, raster_name_ndti, ds=dataset)

    # NDCI
    # calculate ndci
    ndci = normalised_difference(raster, [3, 2])
    ndci = equalize_hist(ndci)

    # save_raster ndci
    raster_name_ndci = format_name(names["ndci"], prefix, date)
    storage.create(ndci, raster_name_ndci, ds=dataset)

    # Calculate water mask and smooth it
    # threshold on 0
    water_mask = ndwi >= 0
    # If there is no water, stop processing
    if not water_mask.any():
        print("No water detected in the area of interest.")
        return {
            "pulse": "water-quality",
            "images": [f"{image_name}"],
            "layers": [],
            "analytics": [],
        }
    water_mask = median_filter(water_mask, size=(10, 5))

    # save_raster water_mask
    raster_name_water_mask = format_name(names["water_mask"], prefix, date)
    storage.create(water_mask, raster_name_water_mask, ds=dataset)

    # DOC
    # calculate doc
    # Control if the image is in a subdirectory of the storage. This is to avoid errors when the name is a subdirectory
    # when running in the Builder
    pattern = (
        image_name.replace(f"_{date}", "*")
        if "/" in image_name
        else "sentinel-2-l2a*.tif"
    )
    stored_images = storage.list(pattern)
    doc_layers_array, doc_values_array, dataset = compute_doc(stored_images, storage)

    # save_raster doc
    raster_name_doc = format_name(names["DOC"], prefix, date)
    storage.create(doc_layers_array[0], raster_name_doc, ds=dataset)

    """ MASK LAYERS """
    shp = convert_array_to_vector(water_mask, storage.get_path(raster_name_water_mask))

    # mask_raster ndwi with aoi_mask
    ndwi_masked, _ = mask_raster(raster_name_ndwi, shp, storage)

    # save_raster ndwi_masked
    raster_name_ndwi_masked = format_name(names["ndwi_masked"], prefix, date)
    storage.create(ndwi_masked, raster_name_ndwi_masked, ds=dataset)

    # mask_raster ndti with aoi_mask
    ndti_masked, _ = mask_raster(raster_name_ndti, shp, storage)

    # save_raster ndti_masked
    raster_name_ndti_masked = format_name(names["ndti_masked"], prefix, date)
    storage.create(ndti_masked, raster_name_ndti_masked, ds=dataset)

    # mask_raster ndci with aoi_mask
    ndci_masked, _ = mask_raster(raster_name_ndci, shp, storage)

    # save_raster ndci_masked
    raster_name_ndci_masked = format_name(names["ndci_masked"], prefix, date)
    storage.create(ndci_masked, raster_name_ndci_masked, ds=dataset)

    # mask_raster doc with aoi_mask
    doc_masked, _ = mask_raster(raster_name_doc, shp, storage)

    # save_raster doc_masked
    raster_name_doc_masked = format_name(names["DOC_masked"], prefix, date)
    storage.create(doc_masked, raster_name_doc_masked, ds=dataset)

    """ ANALYTICS """
    # Water Extent
    extent_has = np.divide(water_mask.sum().max(), 100)
    water_table_name = format_name(names["water_extent"], analytics_prefix, date)
    update_extent_table(water_table_name, extent_has, date, storage)

    # Water Turbidity
    ndti_masked = np.where(ndti_masked == 0, -9999, ndti_masked)  # replace 0 with -9999
    ndti_categories = np.digitize(ndti_masked, [-1, -0.2, 0.4, 1])
    raster_name_ndti_categorized = format_name(names["ndti_categorized"], prefix, date)
    storage.create(ndti_categories, raster_name_ndti_categorized, ds=dataset)

    ndti_colorized = colorize_raster(ndti_categories, colors=COLOR_MAPPING)
    raster_name_ndti_colorized = format_name(
        names["ndti_categorized_rgb"], prefix, date
    )
    storage.create(ndti_colorized, raster_name_ndti_colorized, ds=dataset)

    ndti_px_counted = px_count(ndti_categories, [1, 2, 3])
    ndti_has = np.divide(
        ndti_px_counted,
        100,
        out=np.zeros_like(ndti_px_counted, dtype=np.float64),
        where=100 != 0,
    )
    # save_table turbidity hectareas
    turbidity_table_name = format_name(names["turbidity_Ha"], analytics_prefix, date)
    turbidity_columns = ["Good [Has]", "Careful [Has]", "Bad [Has]", "Total"]
    save_table(
        data=ndti_has,
        columns=turbidity_columns,
        table_name=turbidity_table_name,
        date=date,
        storage=storage,
    )
    ndti_percent = [
        np.divide(ndti_has[i], ndti_has[-1]) * 100 for i in range(len(ndti_has) - 1)
    ]
    # save_table turbidity percent
    turbidity_percent_table_name = format_name(
        names["turbidity_percent"], analytics_prefix, date
    )
    turbidity_percent_columns = ["Good [%]", "Careful [%]", "Bad [%]"]
    save_table(
        data=ndti_percent,
        columns=turbidity_percent_columns,
        table_name=turbidity_percent_table_name,
        date=date,
        storage=storage,
    )

    # Water Chlorophyll
    ndci_masked = np.where(ndci_masked == 0, -9999, ndci_masked)
    ndci_categories = np.digitize(ndci_masked, [-1, 0, 0.5, 1])
    raster_name_ndci_categorized = format_name(names["ndci_categorized"], prefix, date)
    storage.create(ndci_categories, raster_name_ndci_categorized, ds=dataset)

    ndci_colorized = colorize_raster(ndci_categories, colors=COLOR_MAPPING)
    raster_name_ndci_colorized = format_name(
        names["ndci_categorized_rgb"], prefix, date
    )
    storage.create(ndci_colorized, raster_name_ndci_colorized, ds=dataset)

    ndci_px_counted = px_count(ndci_categories, [1, 2, 3])
    ndci_has = np.divide(
        ndci_px_counted,
        100,
        out=np.zeros_like(ndci_px_counted, dtype=np.float64),
        where=100 != 0,
    )
    # save_table chlorophyll hectareas
    chlorophyll_table_name = format_name(
        names["chlorophyll_Ha"], analytics_prefix, date
    )
    chlorophyll_columns = ["Good [Has]", "Careful [Has]", "Bad [Has]", "Total"]
    save_table(
        data=ndci_has,
        columns=chlorophyll_columns,
        table_name=chlorophyll_table_name,
        date=date,
        storage=storage,
    )
    ndci_percent = [
        np.divide(ndci_has[i], ndci_has[-1]) * 100 for i in range(len(ndci_has) - 1)
    ]
    # save_table chlorophyll percent
    chlorophyll_percent_table_name = format_name(
        names["chlorophyll_percent"], analytics_prefix, date
    )
    chlorophyll_percent_columns = ["Good [%]", "Careful [%]", "Bad [%]"]
    save_table(
        data=ndci_percent,
        columns=chlorophyll_percent_columns,
        table_name=chlorophyll_percent_table_name,
        date=date,
        storage=storage,
    )

    # DOC
    # Compute the mean of the doc values
    mean_mean_doc = np.mean([dict["mean_doc"] for dict in doc_values_array])
    mean_std_doc = np.mean([dict["std_doc"] for dict in doc_values_array])

    # Categorize the doc values
    a = 1
    min_to_N0 = 0
    N0_to_N1 = mean_mean_doc + 2 * mean_std_doc / a
    N1_to_N3 = mean_mean_doc + 4 * mean_std_doc / a
    N3_to_max = np.inf

    doc_masked = np.where(doc_masked == 0, -9999, doc_masked)
    doc_categories = np.digitize(doc_masked, [min_to_N0, N0_to_N1, N1_to_N3, N3_to_max])
    raster_name_doc_categorized = format_name(names["DOC_categorized"], prefix, date)
    storage.create(doc_categories, raster_name_doc_categorized, ds=dataset)

    doc_colorized = colorize_raster(doc_categories, colors=COLOR_MAPPING)
    raster_name_doc_colorized = format_name(names["DOC_categorized_rgb"], prefix, date)
    storage.create(doc_colorized, raster_name_doc_colorized, ds=dataset)

    doc_px_counted = px_count(doc_categories, [1, 2, 3])
    doc_has = np.divide(
        doc_px_counted,
        100,
        out=np.zeros_like(doc_px_counted, dtype=np.float64),
        where=100 != 0,
    )
    # save_table DOC hectareas
    doc_table_name = format_name(names["DOC_Ha"], analytics_prefix, date)
    doc_columns = ["Good [Has]", "Careful [Has]", "Bad [Has]", "Total"]
    save_table(
        data=doc_has,
        columns=doc_columns,
        table_name=doc_table_name,
        date=date,
        storage=storage,
    )
    doc_percent = [
        np.divide(doc_has[i], doc_has[-1]) * 100 for i in range(len(doc_has) - 1)
    ]
    # save_table DOC percent
    doc_percent_table_name = format_name(names["DOC_percent"], analytics_prefix, date)
    doc_percent_columns = ["Good [%]", "Careful [%]", "Bad [%]"]
    save_table(
        data=doc_percent,
        columns=doc_percent_columns,
        table_name=doc_percent_table_name,
        date=date,
        storage=storage,
    )
    return {
        "pulse": "water-quality",
        "images": [f"{image_name}"],
        "layers": [
            f"{raster_name_ndwi}",
            f"{raster_name_ndti}",
            f"{raster_name_ndci}",
            f"{raster_name_water_mask}",
            f"{raster_name_doc}",
            f"{raster_name_ndwi_masked}",
            f"{raster_name_ndti_masked}",
            f"{raster_name_ndci_masked}",
            f"{raster_name_doc_masked}",
            f"{raster_name_ndti_categorized}",
            f"{raster_name_ndci_categorized}",
            f"{raster_name_doc_categorized}",
            f"{raster_name_ndti_colorized}",
            f"{raster_name_ndci_colorized}",
            f"{raster_name_doc_colorized}",
        ],
        "analytics": [
            f"{water_table_name}",
            f"{turbidity_table_name}",
            f"{turbidity_percent_table_name}",
            f"{chlorophyll_table_name}",
            f"{chlorophyll_percent_table_name}",
            f"{doc_table_name}",
            f"{doc_percent_table_name}",
        ],
    }


""" 
Methods for Layers: DOC
"""


def compute_doc(stored_images, storage):
    doc_layers_array = []
    doc_values_array = []
    dataset = None
    for path in stored_images:
        # image_name = path.split("/")[-1]
        # read raster
        dataset, raster = read_raster(path, storage, bands=[3, 4, 5, 8])

        # calculate doc for each image
        # calculate doc
        bands = [1, 2]
        bands = np.array(bands) - 1
        # Separate the bands
        band1 = raster[bands[0], :, :]
        band2 = raster[bands[1], :, :]
        # convert the bands to floats
        band1 = band1.astype(float)
        band2 = band2.astype(float)
        doc = 432 * pow(math.e, -2.24 * band1 / band2)
        mean_doc = np.nanmean(doc)
        max_doc = np.nanmax(doc)
        min_doc = np.nanmin(doc)
        std_doc = np.nanstd(doc)
        doc_values_dict = {
            "mean_doc": mean_doc,
            "max_doc": max_doc,
            "min_doc": min_doc,
            "std_doc": std_doc,
        }
        doc_values_array.append(doc_values_dict)
        doc_layers_array.append(doc)
    return doc_layers_array, doc_values_array, dataset


"""
Methods for Analytics: Water Extent
"""


def update_df(df):
    df["Total"] = df["Water [Has]"].max()
    df["Not Water [Has]"] = df["Total"] - df["Water [Has]"]
    df["Percentage [%]"] = df["Water [Has]"] / df["Total"] * 100
    return df


def update_extent_table(water_table_name, extent_has, date, storage):
    if water_table_name not in storage.list():
        df = pd.DataFrame(
            {
                "Water [Has]": extent_has,
                "Not Water [Has]": 0,
                "Total": extent_has,
                "Percentage [%]": 100,
            },
            index=[date],
        )
        df = update_df(df)
    else:
        df = storage.read(water_table_name)
        if date in df.index:
            df.loc[date, "Water [Has]"] = extent_has
            update_df(df)
            return df
        if isinstance(df.index, pd.DatetimeIndex):
            # Handle pd.DateTimeIndex, converting index to string
            df.index = df.index.strftime("%Y-%m-%d")
        new_row = pd.DataFrame(
            {
                "Water [Has]": extent_has,
                "Not Water [Has]": 0,
                "Total": 0,
                "Percentage [%]": 0,
            },
            index=[date],
        )
        df = pd.concat([new_row, df.loc[:]])
        df = update_df(df)
    storage.create(df, water_table_name)
    return df
