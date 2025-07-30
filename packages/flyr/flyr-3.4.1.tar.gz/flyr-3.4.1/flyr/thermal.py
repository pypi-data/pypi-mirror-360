from io import BytesIO
import struct
from typing import BinaryIO, Dict, Tuple, Union

import numpy as np
from nptyping import Array
from PIL import Image


def parse_camera_info(
    stream: BinaryIO, metadata: Tuple[int, int, int, int]
) -> Dict[str, Union[int, float]]:
    (_, _, offset, _) = metadata
    stream.seek(offset + 32)

    emissivity = stream.read(4)
    object_distance = stream.read(4)
    refl_app_temp = stream.read(4)
    atmos_temp = stream.read(4)
    ir_window_temp = stream.read(4)
    ir_window_transm = stream.read(4)

    stream.seek(offset + 60)
    rel_humidity = stream.read(4)

    stream.seek(offset + 88)
    planck_r1 = stream.read(4)
    planck_b = stream.read(4)
    planck_f = stream.read(4)

    stream.seek(offset + 112)
    atmospheric_trans_alpha1 = stream.read(4)
    atmospheric_trans_alpha2 = stream.read(4)
    atmospheric_trans_beta1 = stream.read(4)
    atmospheric_trans_beta2 = stream.read(4)
    atmospheric_trans_x = stream.read(4)

    cam_temp_range_max = stream.read(4)
    cam_temp_range_min = stream.read(4)

    stream.seek(offset + 776)
    planck_o = stream.read(4)
    planck_r2 = stream.read(4)

    stream.seek(offset + 784)
    raw_value_range_min = stream.read(2)
    raw_value_range_max = stream.read(2)

    stream.seek(offset + 824)
    raw_value_median = stream.read(4)
    raw_value_range = stream.read(4)

    # Create result dictionary
    float_from_bytes = lambda v: struct.unpack("f", v)[0]  # noqa: E731
    camera_info = {
        "emissivity": float_from_bytes(emissivity),
        "object_distance": float_from_bytes(object_distance),
        "atmospheric_temperature": float_from_bytes(atmos_temp),
        "ir_window_temperature": float_from_bytes(ir_window_temp),
        "ir_window_transmission": float_from_bytes(ir_window_transm),
        "reflected_apparent_temperature": float_from_bytes(refl_app_temp),
        "relative_humidity": float_from_bytes(rel_humidity),
        "planck_r1": float_from_bytes(planck_r1),
        "planck_r2": float_from_bytes(planck_r2),
        "planck_b": float_from_bytes(planck_b),
        "planck_f": float_from_bytes(planck_f),
        "planck_o": struct.unpack("i", planck_o)[0],
        "atmospheric_trans_alpha1": float_from_bytes(atmospheric_trans_alpha1),
        "atmospheric_trans_alpha2": float_from_bytes(atmospheric_trans_alpha2),
        "atmospheric_trans_beta1": float_from_bytes(atmospheric_trans_beta1),
        "atmospheric_trans_beta2": float_from_bytes(atmospheric_trans_beta2),
        "atmospheric_trans_x": float_from_bytes(atmospheric_trans_x),
        "raw_value_range_min": struct.unpack("H", raw_value_range_min)[0],
        "raw_value_range_max": struct.unpack("H", raw_value_range_max)[0],
        "raw_value_median": struct.unpack("i", raw_value_median)[0],
        "raw_value_range": struct.unpack("i", raw_value_range)[0],
        "camera_temperature_range_max": float_from_bytes(cam_temp_range_max),
        "camera_temperature_range_min": float_from_bytes(cam_temp_range_min),
    }

    to_round = [
        "atmospheric_temperature",
        "ir_window_temperature",
        "reflected_apparent_temperature",
    ]
    camera_info = {k: round(v, 2) if k in to_round else v for k, v in camera_info.items()}

    return camera_info


def parse_raw_data(
    stream: BinaryIO, metadata: Tuple[int, int, int, int]
) -> Tuple[int, int, Array[np.uint8, ..., ...]]:
    (_, _, offset, length) = metadata
    stream.seek(offset)

    # from PIL import ImageFile  # Uncomment to enable loading corrupt PNGs
    # ImageFile.LOAD_TRUNCATED_IMAGES = True

    stream.seek(2, 1)  # Skip first two bytes, TODO Explain the why of the skip
    width = int.from_bytes(stream.read(2), "little")
    height = int.from_bytes(stream.read(2), "little")

    # Read the bytes with the raw thermal data and decode using PIL
    length = min(width * height * 2, length)
    stream.seek(offset + 2 * 16)  # TODO document why 2 * 16
    thermal_bytes = stream.read(length)
    thermal_stream = BytesIO(thermal_bytes)

    # Some thermograms have the raw data stored as PNG files, others simply the
    # sequence of bytes
    if thermal_bytes[:4] != b"\x89PNG":
        u16s = []
        u16 = thermal_stream.read(2)
        while u16:
            u16s.append(int.from_bytes(u16, "little"))
            u16 = thermal_stream.read(2)
        thermal_np = np.array(u16s).reshape((height, width))
    else:
        # FLIR PNG data is in the wrong byte order
        thermal_img = Image.open(thermal_stream)
        thermal_np = np.array(thermal_img)  # type: ignore
        fix_byte_order = np.vectorize(lambda x: (x >> 8) + ((x & 0x00FF) << 8))
        thermal_np = fix_byte_order(thermal_np)

    # Check shape
    if thermal_np.shape != (height, width):
        msg = "Invalid FLIR: metadata's width and height don't match thermal data's actual width and height ({} vs ({}, {})"
        msg = msg.format(thermal_np.shape, height, width)
        raise ValueError(msg)

    return width, height, thermal_np
