import math
# import matplotlib.pyplot as plt
# from matplotlib.pyplot import Circle
from random import randint
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from color_generator import RGB


class Vector():
    def __init__(self, x: Any, y: Any, z: Any):
        self.x = x
        self.y = y
        self.z = z

    @property
    def item_list(self) -> list[int]:
        return [self.x, self.y, self.z]

    @property
    def length(self) -> float:
        return math.sqrt(sum([x ** 2 for x in self.item_list]))

    def normalize(self) -> "Vector":
        length = self.length
        return Vector(self.x / length, self.y / length, self.z / length)


def vector(head: "RGB", tail: "RGB") -> Vector:
    return Vector(head.r - tail.r, head.g - tail.g, head.b - tail.b)


def dot(one: Vector, two: Vector) -> int:
    return sum([one.item_list[i] * two.item_list[i] for i in range(3)])


def cross(one: Vector, two: Vector) -> Vector:
    return Vector(one.item_list[1] * two.item_list[2] - one.item_list[2] * two.item_list[1],
                  one.item_list[2] * two.item_list[0] - one.item_list[0] * two.item_list[2],
                  one.item_list[0] * two.item_list[1] - one.item_list[1] * two.item_list[0])


def coords_from_circle(center: tuple[int, int], radius: int, angle: float) -> tuple[int, int]:
    a, b = center
    random_angle = math.radians(angle)
    x = round(radius * math.cos(random_angle) + a)
    y = round(radius * math.sin(random_angle) + b)
    return x, y


def points_on_a_circle(center: tuple[int, int], radius: int):
    corners = []
    random_angle_degrees = randint(0, 360)
    # Create points at different corners
    for delta in [0, 90, 270, 180]:
        corners.append(coords_from_circle(center, radius, random_angle_degrees + delta))
    return corners
