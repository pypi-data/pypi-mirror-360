import numpy as np


def control_uint_type(array: np.array) -> np.dtype:
    if not issubclass(array.dtype.type, np.integer):
        # If the array is not an integer, return the same type
        return array.dtype

    min = np.min(array)
    max = np.max(array)

    if min >= 0 and max <= 255:
        return np.uint8
    elif min >= 0 and max <= 65535:
        return np.uint16
    elif min >= 0 and max <= 18446744073709551615:
        return np.uint64
    else:
        return array.dtype
