import math
import matplotlib.pyplot as plt
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


# def perpendicular_vector(vector: Vector, length: float) -> Vector:
#     # Dot product of two vectors is 0.
#     red * vector[0] + green * vector[1] + blue * vector[2] = 0

def draw(points: list["RGB"]):
    figure = plt.figure().add_subplot(projection='3d')
    ax = plt.gca()
    ax.set_xlim(255.0)
    ax.set_ylim(255.0)

    for point in points:
        figure.scatter(point.r, point.g, point.b, c=point.to_hex())
    plt.show()
