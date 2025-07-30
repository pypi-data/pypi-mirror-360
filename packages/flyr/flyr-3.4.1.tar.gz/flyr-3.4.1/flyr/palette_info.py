from typing import BinaryIO, List, Tuple
from nptyping import Array

from PIL import Image
import numpy as np

from .palettes.embedded import ycc_to_rgb


class Palette:
    num_colors: int
    above_color: Tuple[int, int, int]
    below_color: Tuple[int, int, int]
    overflow_color: Tuple[int, int, int]
    underflow_color: Tuple[int, int, int]
    isotherm1_color: Tuple[int, int, int]
    isotherm2_color: Tuple[int, int, int]
    method: int
    stretch: int
    file_name: str
    name: str
    yccs: List[Tuple[int, int, int]]
    rgbs: List[Tuple[int, int, int]]

    def __init__(
        self,
        num_colors: int,
        above_color: Tuple[int, int, int],
        below_color: Tuple[int, int, int],
        overflow_color: Tuple[int, int, int],
        underflow_color: Tuple[int, int, int],
        isotherm1_color: Tuple[int, int, int],
        isotherm2_color: Tuple[int, int, int],
        method: int,
        stretch: int,
        file_name: str,
        name: str,
        yccs: List[Tuple[int, int, int]],
    ):
        self.num_colors = num_colors
        self.above_color = above_color
        self.below_color = below_color
        self.overflow_color = overflow_color
        self.underflow_color = underflow_color
        self.isotherm1_color = isotherm1_color
        self.isotherm2_color = isotherm2_color
        self.method = method
        self.stretch = stretch
        self.file_name = file_name
        self.name = name
        self.yccs = yccs
        self.rgbs = [ycc_to_rgb(*yccs[i]) for i in range(num_colors)]

        assert len(self.yccs) > 0
        assert len(self.yccs) == len(self.rgbs)

    def render(self) -> Array[np.uint8, ..., ..., 3]:
        img = np.zeros((20, self.num_colors * 2, 3), dtype=np.uint8)
        for i, (r, g, b) in enumerate(self.rgbs):
            img[:, i * 2 : (i + 1) * 2, 0] = r
            img[:, i * 2 : (i + 1) * 2, 1] = g
            img[:, i * 2 : (i + 1) * 2, 2] = b
        return img

    def render_pil(self) -> Image.Image:
        return Image.fromarray(self.render())


def parse_palette_info(stream: BinaryIO, metadata: Tuple[int, int, int, int]) -> Palette:
    (_, _, offset, _) = metadata

    stream.seek(offset)
    num_colors = int.from_bytes(stream.read(6), "little")

    def read_color_tuple(stream):
        c1 = int.from_bytes(stream.read(1), "little")
        c2 = int.from_bytes(stream.read(1), "little")
        c3 = int.from_bytes(stream.read(1), "little")
        return (c1, c2, c3)

    above = read_color_tuple(stream)
    below = read_color_tuple(stream)
    overflow = read_color_tuple(stream)
    underflow = read_color_tuple(stream)
    isotherm1 = read_color_tuple(stream)
    isotherm2 = read_color_tuple(stream)
    stream.read(2)
    method = int.from_bytes(stream.read(1), "little")
    stretch = int.from_bytes(stream.read(1), "little")

    stream.seek(offset + 112)
    palette: bytes = stream.read(num_colors * 3)
    palette_ycc: List[Tuple[int, int, int]] = [
        (palette[i], palette[i + 1], palette[i + 2]) for i in range(0, len(palette), 3)
    ]

    return Palette(
        num_colors,
        above,
        below,
        overflow,
        underflow,
        isotherm1,
        isotherm2,
        method,
        stretch,
        "",  # TODO Read palette file name
        "",  # TODO Read palette name
        palette_ycc,
    )
