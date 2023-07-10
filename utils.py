from enum import Enum


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    NONE = (0, 0)


class ScoreType(Enum):
    DOT = 10
    POWERUP = 50
    GHOST = 400


class GhostBehaviour(Enum):
    CHASE = 1
    PATROL = 2


def translate_to_maze(coords, size=32):
    return int(coords[0] / size), int(coords[1] / size)


def translate_to_screen(coords, size=32):
    return coords[0] * size, coords[1] * size
