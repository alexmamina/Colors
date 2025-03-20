from random import randint
from PIL import Image
from dataclasses import dataclass
from typing import Any, Optional
import colorsys
from vector_math import Vector
import sys
import matplotlib.pyplot as plt
from color_generator import RGB
import copy


STEP_SIZE = 15


def draw(points: list["HSL"]):
    print(points)
    figure = plt.figure().add_subplot(projection='3d')
    ax = plt.gca()
    ax.set_xlim(360.0)
    ax.set_ylim(100.0)

    for point in points:
        figure.scatter(
            point.h,
            point.s,
            point.l,
            c=point.to_hex()
        )

    plt.show()


@dataclass
class HSL:
    h: int
    s: int
    l: int

    def __init__(self, h: int, s: int, l: int):  # noqa: E741
        assert h <= 360 and s <= 100 and l <= 100
        assert h >= 0 and s >= 0 and l >= 0
        self.h = h
        self.s = s
        self.l = l  # noqa: E741

    def as_tuple(self) -> tuple[int, int, int]:
        return self.h, self.s, self.l

    def __repr__(self) -> str:
        return f"HSL(h={self.h}, s={self.s}, l={self.l})"

    def to_hls(self) -> tuple:
        return (self.h / 360, self.l / 100, self.s / 100)

    def to_hex(self) -> str:
        return self.to_rgb().to_hex()

    def to_rgb(self) -> RGB:
        return RGB(*[int(255 * x) for x in colorsys.hls_to_rgb(*self.to_hls())])

    @classmethod
    def from_list(cls, int_list: list[int]) -> "HSL":
        return HSL(int_list[0], int_list[1], int_list[2])

    @classmethod
    def from_tuple(cls, int_tuple: tuple[Any, Any, Any]) -> "HSL":
        return HSL(int(int_tuple[0]), int(int_tuple[1]), int(int_tuple[2]))

    @classmethod
    def coordinates_from_vector(cls, vec: Vector, head: "HSL", reverse: bool = False) -> "HSL":
        # print(vec.item_list[0] + head.h,
        #       vec.item_list[1] + head.s,
        #       vec.item_list[2] + head.l)
        if reverse:
            return HSL(
                vec.item_list[0] + head.h,
                vec.item_list[1] + head.s,
                vec.item_list[2] + head.l,
            )
        else:
            return HSL(
                head.h - vec.item_list[0],
                head.s - vec.item_list[1],
                head.l - vec.item_list[2],
            )


class ColorGenerator:
    def __init__(self, size: int):
        self.size = size

    def expand_colors_to_board(self, colors: list[list[Any]], mult: int = 200) -> list[list[Any]]:
        n = mult
        new_board = []
        for row in colors:
            new_row = []
            for color in row:
                new_row += [color] * n
            new_board += [new_row] * n
        return new_board

    def random_color(self) -> HSL:
        return HSL(randint(0, 360), randint(0, 100), randint(0, 100))

    def create_color_image(self, colors: list[list[str]], filename: Optional[str] = None):
        new = self.expand_colors_to_board(colors, 200)
        i = Image.new("RGBA", (len(new), len(new[0])))
        for r in range(len(new)):
            for c in range(len(new)):
                i.putpixel((r, c), RGB.from_hex(new[r][c]).as_tuple())
        if filename:
            i.save(filename)
        else:
            i.show()

    def linear_gradient(self, color1: HSL, color2: HSL, size: int) -> list[HSL]:
        result = []
        color_vector = Vector(color2.h - color1.h, color2.s - color1.s, color2.l - color1.l)
        # The size of the gradient step
        vector_step = [x / (size - 1) for x in color_vector.item_list]

        for x in range(size):
            color = [
                round(color1.h + x * vector_step[0]),
                round(color1.s + x * vector_step[1]),
                round(color1.l + x * vector_step[2])
            ]
            hsl = HSL.from_list(color)
            result.append(hsl)
        return result

    def generate_board(self, size: int) -> list[list[HSL]]:
        [tl, tr], [bl, br] = self.generate_starting_points()
        results = []
        rightcol = self.linear_gradient(tr, br, size)
        leftcol = self.linear_gradient(tl, bl, size)
        for i in range(len(rightcol)):
            results.append(self.linear_gradient(rightcol[i], leftcol[i], size))
        return results

    def rotate_points(self, points: list[list[HSL]]) -> list[list[HSL]]:
        random_direction = randint(1, 4)
        match random_direction:
            case 1:
                return points
            case 2:
                # Rotate 1 turn clockwise. Swap two rows, then transpose them
                points.reverse()
                points = [[row[i] for row in points] for i in range(len(points))]
            case 3:
                # Rotate 2 turns clockwise: swap two rows and everything inside them
                for row in points:
                    row.reverse()
                points.reverse()
            case 4:
                # Rotate 1 turn anticlockwise: transpose rows, then swap them
                points = [[row[i] for row in points] for i in range(len(points))]
                points.reverse()
        return points

    def generate_starting_points(self) -> list[list[HSL]]:
        saturation = randint(0, 100)
        points = [(randint(0, 360), randint(0, 100)) for _ in range(4)]
        # Sort based on the x-axis. First two points are on the left, last two - on the right
        points.sort(key=lambda x: x[1])
        sorted_y = copy.deepcopy(points)
        bottom = sorted_y[:2]  # Min Y
        top = sorted_y[2:]  # Max Y

        bottom.sort(key=lambda x: x[0])  # Min X, max X -> left, right
        top.sort(key=lambda x: x[0])  # Min X, max X -> left, right
        top = [HSL(h, saturation, l) for (h, l) in top]
        bottom = [HSL(h, saturation, l) for (h, l) in bottom]
        corners = self.rotate_points([top, bottom])
        print(f"Saturation: {saturation}, points: {[(y.h, y.l) for x in corners for y in x]}")
        return corners

    def generate_initial_color_board(self, size: int) -> list[list[str]]:
        b = self.generate_board(size)
        final_b = []
        for row in b:
            hex_row = []
            for col in row:
                hex_row.append(col.to_hex())
            final_b.append(hex_row)
        return final_b


if __name__ == "__main__":
    size = 10
    image_num = 10
    cg = ColorGenerator(size)
    testing = len(sys.argv) > 1 and sys.argv[1] == "t"
    skip_draw = len(sys.argv) > 1 and sys.argv[1] == "s"

    if testing:
        print("Testing")
        for j in range(3, size):
            print(f"Testing size {j}")
            for i in range(10000):
                try:
                    board = cg.generate_initial_color_board(size)
                except AssertionError:
                    print(f"#{i} for size {j} - out of bounds")
                    pass

    print("Drawing")
    for i in range(image_num):
        try:
            board = cg.generate_initial_color_board(size)
            if not skip_draw:
                cg.create_color_image(board)
        except AssertionError:
            print(f"#{i} for size {size} - out of bounds")
            pass
    draw(
        [
            HSL(h=247, s=100, l=50),
            HSL(h=17, s=100, l=50),
            HSL(h=351, s=100, l=56),
            HSL(h=310, s=100, l=50),
        ]
    )
