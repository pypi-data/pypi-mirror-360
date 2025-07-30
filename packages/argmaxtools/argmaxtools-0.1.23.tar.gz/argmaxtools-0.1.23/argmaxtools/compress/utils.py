#
# For licensing see accompanying LICENSE.md file.
# Copyright (C) 2023 Argmax, Inc. All Rights Reserved.
#

import numpy as np


# TODO(atila): Guard against data having OOB values
def compress_subbyte_data(data: np.ndarray, count: int, nbits: int) -> np.ndarray:
    return np.packbits(np.reshape(np.unpackbits(data), (count, 8))[:, -nbits:])


# TODO(atila): Guard against invalid values for nbits and count
def decompress_subbyte_data(data: np.ndarray, count: int, nbits: int) -> np.ndarray:
    return np.packbits(
        np.concatenate([
            np.zeros((count, 8 - nbits), np.uint8),
            np.reshape(np.unpackbits(data, count=count * nbits), (count, nbits))
        ], axis=1)
    )
