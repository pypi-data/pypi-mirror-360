from gymnasium.envs.registration import register
from .grid_world import GridWorldV0, GridWorldMapsIndex
from .point_maze import PointMazeV0, PointMazeMapsIndex
import os
import sys

__all__ = [
    "GridWorldV0", "GridWorldMapsIndex",
    "PointMazeV0", "PointMazeMapsIndex"
]

register(
    id="GridWorld-v0",
    entry_point="rlnav.grid_world.grid_world_v0:GridWorldV0",
    kwargs={},
)
register(
    id="PointMaze-v0",
    entry_point="rlnav.point_maze.point_maze_v0:PointMazeV0",
    kwargs={},
)

# From that point, everything is imported except AntMaze which uses mujoco_py.
# However, mujoco_py is no longer supported (as far as I know) and is not compatible with most recent versions of cython and python.
# Hence, we want to import AntMaze if and only if mujoco_py is installed.
# So we do this trick:
# Conditionally import AntMaze

# Disable prints caused by mujoco import / compilation for more readability
devnull = open(os.devnull, 'w')
old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = devnull
sys.stderr = devnull

# Try to import mujoco
try:

    import mujoco_py  # only to trigger ImportError if not available

    from .ant_maze import AntMazeV0, AntMazeMapsIndex

    register(
        id="AntMaze-v0",
        entry_point="rlnav.ant_maze.ant_maze_v0:AntMazeV0",
        kwargs={},
    )

    __all__.extend(["AntMazeV0", "AntMazeMapsIndex"])

except Exception as e:
    # print("WARNING, AntMaze has not been imported due to an exception while trying to import mujoco_py.")
    # Skip AntMaze if mujoco_py isn't installed
    pass

# Restore stdout and stderr.
sys.stdout = old_stdout
sys.stderr = old_stderr