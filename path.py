import numpy as np
from node import astar


class Path:
    def __init__(self, in_arr):
        self.maze = np.array(in_arr, dtype=np.bool_).tolist()

    def get_path(self, from_x, from_y, to_x, to_y) -> object:
        res = astar(self.maze, (from_y, from_x), (to_y, to_x))
        if res is None:
            return []
        return [(sub[1], sub[0]) for sub in res]

