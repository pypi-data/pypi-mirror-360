from enum import Enum


class Direction(Enum):
    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3


class Colors(Enum):
    EMPTY = [250, 250, 250]
    WALL = [50, 54, 51]
    START = [213, 219, 214]
    TRAP = [73, 179, 101]
    TILE_BORDER = [50, 54, 51]
    AGENT = [0, 0, 255]
    GOAL = [255, 0, 0]
    REWARD = [255, 215, 0]  # Added missing REWARD color (gold)


class TileType(Enum):
    EMPTY = 0
    WALL = 1
    START = 2
    REWARD = 3
    TRAP = 4


class PointMazeMapsIndex(Enum):
    EMPTY = "empty_room"
    FOUR_ROOMS = "four_rooms"
    MEDIUM = "medium_maze"
    JOIN_ROOM_MEDIUM = "join_room_medium"
    HARD = "hard_maze"
    EXTREME = "extreme_maze"
    IMPOSSIBLE = "impossible_maze"
