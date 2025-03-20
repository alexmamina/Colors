from random import randint
from PIL import ImageColor, Image
from dataclasses import dataclass
from math import floor
# from colour import Color
from typing import Any, Optional
# from functools import partial
import colorsys
from vector_math import vector, dot, cross, Vector
import math

STEP_SIZE = 15


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

    def as_tuple(self) -> tuple[int, int, int]:
        return self.r, self.g, self.b

    def __repr__(self) -> str:
        return f"RGB(r={self.r}, g={self.g}, b={self.b})"

    def close_to(self, other: "RGB") -> bool:
        close_red = self.r <= other.r + STEP_SIZE and self.r >= other.r - STEP_SIZE
        close_green = self.g <= other.g + STEP_SIZE and self.g >= other.g - STEP_SIZE
        close_blue = self.b <= other.b + STEP_SIZE and self.b >= other.b - STEP_SIZE
        return close_red or close_green or close_blue

    def close_to_any(self, others: list["RGB"]) -> bool:
        for other in others:
            if self.close_to(other):
                return True
        return False

    def to_hex(self) -> str:
        return '#{:02x}{:02x}{:02x}'.format(self.r, self.g, self.b)

    @classmethod
    def from_list(cls, int_list: list[int]) -> "RGB":
        return RGB(int_list[0], int_list[1], int_list[2])

    @classmethod
    def from_hex(cls, hex_number: str) -> "RGB":
        # Take the first two, mid two, last two chars of the hex and convert from 16 base
        # red, green, blue = [int(hex_number[i:i + 2], 16) for i in (0, 2, 4)]
        red, green, blue = ImageColor.getcolor(hex_number, "RGB")
        return RGB(red, green, blue)

    @classmethod
    def from_tuple(cls, int_tuple: tuple[Any, Any, Any]) -> "RGB":
        return RGB(int(int_tuple[0]), int(int_tuple[1]), int(int_tuple[2]))

    @classmethod
    def coordinates_from_vector(cls, vector: Vector, head: "RGB", reverse: bool = False) -> "RGB":
        print(vector.item_list[0] + head.r,
              vector.item_list[1] + head.g,
              vector.item_list[2] + head.b)
        if reverse:
            return RGB(
                vector.item_list[0] + head.r,
                vector.item_list[1] + head.g,
                vector.item_list[2] + head.b,
            )
        else:
            return RGB(
                head.r - vector.item_list[0],
                head.g - vector.item_list[1],
                head.b - vector.item_list[2],
            )


class ColorGenerator:
    def __init__(self, size: int):
        self.size = size
        # self.starting_points = self.generate_starting_points(size)
        # self.colors = self.generate_initial_colors()

    def generate_starting_points(self, num_points: int = 4) -> list[RGB]:
        points = []
        for _ in range(num_points):
            new_color = self.random_color()
            while new_color.close_to_any(points):
                print(new_color, points)
                new_color = self.random_color()

            points.append(new_color)
            # points.append([])
            # for j in range(num_points):
            #     points[i].append(self.random_color())
        return points

    def sort_starting_points(self, points: list[RGB]) -> list[RGB]:
        top_left = points[0]
        return sorted(points, key=lambda p: math.atan2(p.g - top_left.g, p.r - top_left.r))

    def expand_colors_to_board(self, colors: list[list[Any]], mult: int = 200) -> list[list[Any]]:
        n = mult
        new_board = []
        for row in colors:
            new_row = []
            for color in row:
                new_row += [color] * n
            new_board += [new_row] * n
        return new_board

    def random_color(self) -> RGB:
        return RGB.from_list([randint(0, 255) for _ in range(3)])

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

    def generate_color_square(self) -> list[list[RGB]]:
        tl = self.random_color()
        tr = self.random_color()
        col_diff = round((tr.r - tl.r) / (self.size - 1))
        max_step = round(255 / (255 - max(tr.as_tuple())))

        # Pick 2 colors for our future steps and the gradient
        while abs(col_diff) < STEP_SIZE or col_diff > max_step:
            tr = self.random_color()
            col_diff = round((tr.r - tl.r) / (self.size - 1))
            max_step = round(255 / (255 - max(tr.as_tuple())))
        print(max_step)
        hvec = vector(tr, tl)
        vvec = Vector(hvec.x, -1 * hvec.y, hvec.z)
        bl = RGB.coordinates_from_vector(vvec, tl, reverse=True)
        br = RGB.coordinates_from_vector(hvec, bl, reverse=True)

        return self.linear_gradient_color_board(tl, tr, bl, br)

    def generate_gradient_from_plane(self) -> list[list[RGB]]:
        tl = self.random_color()
        tr = self.random_color()
        # bl = self.random_color()
        # br = self.random_color()
        col_diff = round((tr.r - tl.r) / (self.size - 1))

        # Pick 2 colors for our future steps and the gradient
        while abs(col_diff) < 15:
            tr = self.random_color()
            col_diff = round((tr.r - tl.r) / (self.size - 1))
        # min_step = 15
        # max_step = floor((255 - max(tl.as_tuple())) / (self.size - 1))
        # while max_step <= min_step:
        #     tl = self.random_color()
        #     max_step = floor((255 - max(tl.as_tuple())) / (self.size - 1))
        # print(max_step)
        # print(tl)
        # col_diff = randint(min_step, max_step)
        # print(col_diff)
        # tr = RGB(tl.r + col_diff * (self.size - 1), randint(0, 255), randint(0, 255))

        hvec_top = vector(tr, tl)
        len_htop = hvec_top.length
        print(f"tl {tl}, tr {tr}")
        # draw([tl, tr])
        print(f"Vector: {hvec_top.item_list}")
        x_unit = Vector(1, 0, 0)
        is_x_axis_parallel = \
            dot(hvec_top, x_unit) == hvec_top.length * x_unit.length
        if is_x_axis_parallel:
            unit = Vector(0, 1, 0)
        else:
            unit = Vector(1, 0, 0)

        unnormalised_perpendicular = cross(hvec_top, unit)
        perpendicular = unnormalised_perpendicular.normalize()
        vvec = Vector(round(perpendicular.x * len_htop),
                      round(perpendicular.y * len_htop),
                      round(perpendicular.z * len_htop))

        bl = RGB.coordinates_from_vector(vvec, tl)
        br = RGB.coordinates_from_vector(hvec_top, bl)

        # vvec_left = vector(bl, tl)
        # hvec_bottom = vector(br, bl)
        # vvec_right = vector(br, tr)

        # while dot(hvec_top, vvec_left) != 0 or dot(hvec_bottom, vvec_right) != 0:
        #     bl = self.random_color()
        #     br = self.random_color()

        #     hvec_top = vector(tr, tl)
        #     vvec_left = vector(bl, tl)
        #     hvec_bottom = vector(br, bl)
        #     vvec_right = vector(br, tr)
        #    # draw([tl, tr, bl, br])

        print(tl, tr, bl, br)
        # draw([tl, tr, bl, br])

        return self.linear_gradient_color_board(tl, tr, bl, br)

    def linear_gradient(self, color1: RGB, color2: RGB, size: int) -> list[RGB]:
        result = []
        color_vector = vector(color2, color1)
        # The size of the gradient step
        vector_step = [x / (size - 1) for x in color_vector.item_list]

        for x in range(size):
            color = [
                round(color1.r + x * vector_step[0]),
                round(color1.g + x * vector_step[1]),
                round(color1.b + x * vector_step[2])
            ]
            rgb = RGB.from_list(color)
            result.append(rgb)
        new = result

        return new

    def uniform_gradient_board(self) -> list[list[RGB]]:
        min = 15
        step = randint(min, floor(255 / self.size - 1))
        shift = randint(0, floor(255 / self.size - 1))
        # step = 15
        board = []
        for i in range(self.size):
            board.append([])
            for j in range(self.size):
                board[i].append(RGB(i * step + shift, j * step + shift, (i + j) * step + shift))
        return board

    def linear_gradient_color_board(self, tl: RGB, tr: RGB, bl: RGB, br: RGB) -> list[list[RGB]]:
        size = self.size
        board = []
        for _ in range(size):
            board.append([RGB(0, 0, 0)] * size)

        col1 = self.linear_gradient(tl, bl, size)
        col2 = self.linear_gradient(tr, br, size)

        for row in range(size):
            board[row] = self.linear_gradient(col1[row], col2[row], size)
        return board

    def board_split_complementary(self) -> list[list[RGB]]:
        # At least 15, fails on assert same index (row of identical colors)
        one = self.random_color()
        one_hsl = colorsys.rgb_to_hls(one.r, one.g, one.b)
        two = (one_hsl[0] * 360 + 90) % 360 / 360, one_hsl[1], one_hsl[2]
        three = (one_hsl[0] * 360 + 180) % 360 / 360, one_hsl[1], one_hsl[2]
        four = (one_hsl[0] * 360 + 270) % 360 / 360, one_hsl[1], one_hsl[2]

        board = [[one, RGB.from_tuple(colorsys.hls_to_rgb(two[0], two[1], two[2]))],
                 [RGB.from_tuple(colorsys.hls_to_rgb(three[0], three[1], three[2])),
                 RGB.from_tuple(colorsys.hls_to_rgb(four[0], four[1], four[2]))]]

        return self.linear_gradient_color_board(board[0][0], board[0][1], board[1][0], board[1][1])

    def generate_initial_color_board(self, size: int) -> list[list[str]]:
        # There's a gray stripe across the middle as this goes across the circle center
        # Usable but make gray uncheckable
        # b = self.board_split_complementary()
        # Low success rate, weird colors
        # b = self.generate_gradient_from_plane()
        b = self.generate_color_square()
        # Nearly identical colors, med success rate?
        # b = self.uniform_gradient_board()
        # Colors completely random, could be identical and unsorted
        corners = self.sort_starting_points(self.generate_starting_points())

        b = self.linear_gradient_color_board(corners[0], corners[1], corners[2], corners[3])
        result = []
        for r in range(size):
            result.append([])
            for c in range(size):
                result[r].append(b[r][c].to_hex())
        return result


if __name__ == "__main__":
    size = 10
    cg = ColorGenerator(size)

    for i in range(10):
        try:
            board = cg.generate_initial_color_board(size)

            cg.create_color_image(board)
        except AssertionError:
            print(f"{i} - bounds")
            pass
    # draw([RGB(r=203, g=94, b=60), RGB(r=58, g=241, b=178), RGB(r=5, g=105, b=63),
    #       RGB(r=22, g=249, b=125)])
