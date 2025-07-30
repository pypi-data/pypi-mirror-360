from io import BytesIO
from typing import BinaryIO, Tuple
from nptyping import Array

import numpy as np
from PIL import Image


def parse_embedded_image(
    stream: BinaryIO, metadata: Tuple[int, int, int, int]
) -> Tuple[int, int, Array[np.uint8, ..., ...]]:
    (entry_idx, _, offset, length) = metadata
    stream.seek(offset)

    # from PIL import ImageFile  # Uncomment to enable loading corrupt PNGs
    # ImageFile.LOAD_TRUNCATED_IMAGES = True

    stream.seek(2, 1)  # Skip first two bytes, TODO Explain the why of the skip
    width = int.from_bytes(stream.read(2), "little")
    height = int.from_bytes(stream.read(2), "little")

    stream.seek(offset + 2 * 16)  # TODO document why 2 * 16

    # Read the bytes with the embedded image and decode using PIL
    optical_bytes = stream.read(length)
    optical_stream = BytesIO(optical_bytes)
    optical_img = Image.open(optical_stream)
    optical_np = np.array(optical_img)

    # Check shape
    if optical_np.shape[:2] != (height, width):
        msg = "Invalid FLIR: metadata's width and height don't match optical data's actual width and height ({} vs ({}, {})"
        msg = msg.format(optical_np.shape, height, width)
        raise ValueError(msg)

    return width, height, optical_np
