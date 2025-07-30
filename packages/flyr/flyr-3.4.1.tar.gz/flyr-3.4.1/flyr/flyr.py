#!/usr/bin/env python3

""" Main module containing the code that parses/unpacks a FLIR file.

    The most important function here for end users is `unpack()` which starts
    the unpacking sequence. It returns a `FlyrThermogram`, defined in
    thermogram.py, so check there for the main way to interface with the
    results.

    Much of the documentation needed to implement this was gotten from
    exiftool (https://exiftool.org/TagNames/FLIR.html).
"""

# FIXME stop depending on PIL and nptyping

# Standard library imports
from io import BufferedIOBase
from typing import Callable, Dict, List, BinaryIO, Tuple, TypeVar, Union
import os

# Self imports
from .camera_metadata import CameraMetadata
from .embedded_image import parse_embedded_image
from .measurement_info import Measurement, parse_measurements
from .palette_info import parse_palette_info
from .picture_in_picture import parse_pip_info
from .records import RecordIndex, extract_flir_app1, parse_flir_records
from .thermal import parse_camera_info, parse_raw_data
from .thermogram import FlyrThermogram


T = TypeVar("T")


def unpack(path_or_stream: Union[str, BinaryIO]) -> FlyrThermogram:
    """Unpacks the FLIR image, meaning that it will return the thermal data
    embedded in the image.

    Parameters
    ----------
    path_or_stream : Union[str, BinaryIO]
        Either a path (string) to a FLIR file, or a byte stream such as
        BytesIO or file opened as `open(file_path, "rb")`.

    Returns
    -------
    FlyrThermogram
        When successful, a FlyrThermogram object containing thermogram data.
    """
    if isinstance(path_or_stream, str) and os.path.isfile(path_or_stream):
        with open(path_or_stream, "rb") as flirh:
            thermogram = unpack(flirh)
        thermogram.path = path_or_stream
        return thermogram
    elif isinstance(path_or_stream, BufferedIOBase):
        stream = path_or_stream
        flir_app1_stream = extract_flir_app1(stream)
        flir_records = parse_flir_records(flir_app1_stream)
        stream.seek(0)
        thermogram = parse_thermogram(flir_app1_stream, flir_records, stream)

        return thermogram
    else:
        raise ValueError("Incorrect input")  # TODO improved error message


def parse_thermogram(
    thermal_stream: BinaryIO,
    records: Dict[int, Tuple[int, int, int, int]],
    file_stream: BinaryIO,
) -> FlyrThermogram:
    # FIXME Support formats other than subtype == PNG
    # Parse core thermal data: raw values and camera settings
    raw_data_md = records[RecordIndex.RAW_DATA.value]
    _, _, raw_data = parse_raw_data(thermal_stream, raw_data_md)

    camera_info_md = records[RecordIndex.CAMERA_INFO.value]
    camera_info = parse_camera_info(thermal_stream, camera_info_md)

    # Parse optional embedded information
    def _try(
        parse: Callable[[BinaryIO, Tuple[int, int, int, int]], T],
        index: RecordIndex,
        fallback: T,
    ) -> T:
        return _try_parse(thermal_stream, records, index, parse, fallback)

    embedded_image_ = _try(parse_embedded_image, RecordIndex.EMBEDDED_IMAGE, None)
    embedded_image = None if embedded_image_ is None else embedded_image_[2]
    palette_info = _try(parse_palette_info, RecordIndex.PALETTE_INFO, None)
    pip_info = _try(parse_pip_info, RecordIndex.PICTURE_IN_PICTURE_INFO, None)
    measurements: List[Measurement] = []
    measurements = _try(parse_measurements, RecordIndex.MEASUREMENT_INFO, measurements)

    # Finish with return object
    thermogram = FlyrThermogram(
        raw_data,
        camera_info,
        optical=embedded_image,
        palette=palette_info,
        picture_in_picture=pip_info,
        measurements=measurements,
        metadata_camera=CameraMetadata(file_stream),
    )
    return thermogram


def _try_parse(
    stream: BinaryIO,
    records: Dict[int, Tuple[int, int, int, int]],
    index: RecordIndex,
    parse: Callable[[BinaryIO, Tuple[int, int, int, int]], T],
    fallback: T,
) -> T:
    try:
        md = records[index.value]
        value = parse(stream, md)
    except:  # noqa: E722
        value = fallback
    return value


def main():
    import argparse
    import warnings
    import traceback as tb
    from pprint import pprint

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--camera-info", "-c", action="store_true", default=False, required=False
    )
    parser.add_argument("--palette-dest", default="", required=False)
    parser.add_argument("--render-dest", "-r", default="", required=False)
    parser.add_argument("--optical-dest", "-o", default="", required=False)
    parser.add_argument("--pnp-dest", "-p", default="", required=False)
    parser.add_argument("--emboss-dest", "-e", default="", required=False)
    parser.add_argument(
        "--print-measurements", "-m", action="store_true", default=False, required=False
    )
    parser.add_argument("thermogram")
    args = parser.parse_args()

    script = os.path.basename(__file__)
    if not os.path.isfile(args.thermogram):
        print(f"{script}: error: file {args.thermogram} doesn't exist")
        exit(1)

    try:
        thermogram = unpack(args.thermogram)

        if args.camera_info:
            pprint(thermogram.metadata)

        if args.palette_dest and thermogram.palette is not None:
            thermogram.palette.render_pil().save(args.palette_dest)
        elif args.palette_dest:
            warnings.warn(f"{script}: warning: no palette was extracted")

        if args.render_dest:
            thermogram.render_pil().save(args.render_dest)

        if args.optical_dest and thermogram.optical_pil is not None:
            thermogram.optical_pil.save(args.optical_dest)

        if args.pnp_dest:
            thermogram.picture_in_picture_pil().save(args.pnp_dest)

        if args.emboss_dest:
            thermogram.render_pil(edge_emphasis=0.275).save(args.emboss_dest)

        if args.print_measurements:
            for m in thermogram.measurements:
                ident = f"{m.tool.name.capitalize()} {m.label}".strip()
                print(f"{ident}: {m.params}")
    except Exception as e:
        msg = f"{tb.format_exc()}\n{script}: error: failed unpacking {args.thermogram}"
        print(msg)


if __name__ == "__main__":
    main()
