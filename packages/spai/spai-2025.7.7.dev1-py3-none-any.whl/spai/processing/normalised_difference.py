import numpy as np


def normalised_difference(raster, bands=[1, 2]):
    # convertir bandas a float
    if raster.shape[-3] < 2:
        raise ValueError(
            f"Function `normalised_difference` strictly expects at least a 2-band image. "
            f"You provided a {raster.shape[-3]}-band image instead."
        )

    bands = np.array(bands) - 1
    # Separate the bands
    band1 = raster[bands[0], :, :]
    band2 = raster[bands[1], :, :]
    # convert the bands to floats
    band1 = band1.astype(float)
    band2 = band2.astype(float)
    # calculate the ndvi
    numerator = band1 - band2
    denominator = band1 + band2 + 1e-8

    return numerator / denominator
