import math
from random import randint
from typing import Any


class Vector():
    def __init__(self, x: Any, y: Any, z: Any):
        self.x = x
        self.y = y
        self.z = z

    @property
    def item_list(self) -> list[int]:
        return [self.x, self.y, self.z]


def coords_from_circle(center: tuple[int, int], radius: int, angle: float) -> tuple[int, int]:
    a, b = center
    random_angle = math.radians(angle)
    x = round(radius * math.cos(random_angle) + a)
    y = round(radius * math.sin(random_angle) + b)
    return x, y


def points_on_a_circle(center: tuple[int, int], radius: int):
    corners = []
    random_angle_degrees = randint(0, 360)
    wiggle_room = range(-3, 3)
    # We don't want the points to be exactly aligned with either axis, as that would mean a very
    # similar color in multiple corners, differentiated by lightness. Add some finger-in-the-air
    # "wiggle room" where the angle is not allowed to be in. The wiggle room is around the 45
    # degree mark for perfectly aligned squares, and the 90 degree mark for perfect rhombuses.
    # Calculate a random angle to ensure different color locations in the final gradient
    while random_angle_degrees % 45 in wiggle_room or random_angle_degrees % 90 in wiggle_room:
        random_angle_degrees = randint(0, 360)
    # Create points at different corners
    for delta in [0, 90, 270, 180]:
        corners.append(coords_from_circle(center, radius, random_angle_degrees + delta))
    return corners
