from dataclasses import dataclass
import colorsys
from PIL import ImageColor


@dataclass
class RGB:
    r: int
    b: int
    g: int

    def __init__(self, r: int, g: int, b: int):
        assert r <= 255 and g <= 255 and b <= 255
        assert r >= 0 and g >= 0 and b >= 0
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self) -> str:
        return f"RGB(r={self.r}, g={self.g}, b={self.b})"

    def to_hex(self) -> str:
        return '#{:02x}{:02x}{:02x}'.format(self.r, self.g, self.b)

    def as_tuple(self) -> tuple[int, int, int]:
        return self.r, self.g, self.b

    @classmethod
    def from_hex(cls, hex_number: str) -> "RGB":
        red, green, blue = ImageColor.getcolor(hex_number, "RGB")
        return RGB(red, green, blue)


@dataclass
class HSL:
    # Pinned saturation: palettes from bright to pastel, more visible changes per step
    # Pinned lightness: more uniform gradient, less visible changes between colors
    h: int
    s: int
    l: int

    def __init__(self, h: int, s: int, l: int):  # noqa: E741
        assert h <= 360 and s <= 100 and l <= 100
        assert h >= 0 and s >= 0 and l >= 0
        self.h = h
        self.s = s
        self.l = l  # noqa: E741

    def __repr__(self) -> str:
        return f"HSL(h={self.h}, s={self.s}, l={self.l})"

    def to_hls(self) -> tuple:
        return (self.h / 360, self.l / 100, self.s / 100)

    def to_hex(self) -> str:
        rgb = RGB(*[int(255 * x) for x in colorsys.hls_to_rgb(*self.to_hls())])
        return rgb.to_hex()

    def min_distance_to_bounds(self) -> int:
        # H: 0-360
        # S: 0-100
        # L: 0-100
        min_h = min(self.h, 360 - self.h)
        min_s = min(self.s, 100 - self.s)
        min_l = min(self.l, 100 - self.l)
        return min(min_h, min_s, min_l)

    @classmethod
    def from_list(cls, int_list: list[int]) -> "HSL":
        return HSL(int_list[0], int_list[1], int_list[2])

    @classmethod
    def average(cls, one: "HSL", two: "HSL") -> "HSL":
        return HSL(
            round((one.h + two.h) / 2), round((one.s + two.s) / 2), round((one.l + two.l) / 2)
        )
