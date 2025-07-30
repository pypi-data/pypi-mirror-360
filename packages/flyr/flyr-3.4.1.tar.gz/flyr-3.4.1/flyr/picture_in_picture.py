import struct
from typing import BinaryIO, Tuple


class PictureInPicture:
    real_to_ir: float
    offset_x: int
    offset_y: int
    pip_x1: int
    pip_x2: int
    pip_y1: int
    pip_y2: int

    def __init__(
        self,
        real_to_ir: float,
        offset_x: int,
        offset_y: int,
        pip_x1: int,
        pip_x2: int,
        pip_y1: int,
        pip_y2: int,
    ):
        self.real_to_ir = real_to_ir
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.pip_x1 = pip_x1
        self.pip_x2 = pip_x2
        self.pip_y1 = pip_y1
        self.pip_y2 = pip_y2

    @property
    def crop_box(self) -> Tuple[int, int, int, int]:
        return (self.pip_x1, self.pip_y1, self.pip_x2, self.pip_y2)


def parse_picture_in_picture_info(
    stream: BinaryIO, metadata: Tuple[int, int, int, int]
) -> PictureInPicture:
    (_, _, offset, _) = metadata

    stream.seek(offset)

    ratio = stream.read(4)
    real_to_ir = struct.unpack("f", ratio)[0]
    offset_x = int.from_bytes(stream.read(2), "little", signed=True)
    offset_y = int.from_bytes(stream.read(2), "little", signed=True)
    pip_x1 = int.from_bytes(stream.read(2), "little", signed=True)
    pip_x2 = int.from_bytes(stream.read(2), "little", signed=True)
    pip_y1 = int.from_bytes(stream.read(2), "little", signed=True)
    pip_y2 = int.from_bytes(stream.read(2), "little", signed=True)

    return PictureInPicture(
        real_to_ir, offset_x, offset_y, pip_x1, pip_x2, pip_y1, pip_y2
    )


def parse_pip_info(
    stream: BinaryIO, metadata: Tuple[int, int, int, int]
) -> PictureInPicture:
    return parse_picture_in_picture_info(stream, metadata)
