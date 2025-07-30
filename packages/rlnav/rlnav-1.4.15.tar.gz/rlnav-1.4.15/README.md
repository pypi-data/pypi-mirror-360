# NavigationRLEnvironments
A set of reinforcement learning environments for navigation tasks (Try to choose the best sequence of actions to move an agent to a given goal position).

## Environments

### GridEnv

A simple grid navigation environment where the agent have to reach a goal (or the closest rewarding state) using discrete actions (top, right, bottom, left) to move on the grid.

### PointEnv

The agent is a point moving in continuous space.
In all the versions bellow, a gaussian noise is added to the action depending on a hyperparameter "noise_mean".


 - PointEnv-V1
   - actions: x, y modification of the agent current position.
   - observation: agent's x, y position.
 - PointEnv-V2
   - actions: angular and linear velocity. The agent rotate according to the given angular velocity, then move following the linear velocity.
   - observation: agent's x, y position and agent's orientation.
 - PointEnv-V3
   - actions: modification of the agent's angular and linear velocity. 
        The agent rotate according to it's angular velocity, then move following the linear velocity.
   - observation: agent's x, y position and agent's orientation.

### AntMaze

The mujoco gym "Ant" but it is navigating in a maze.
Compared to the more known AntMaze environment, with this one you can build maze maps from a list of 0 and 1. More, you can reset anywhere the ant position or choose a specific initial position.
The goal is reset anywhere in the reachable space at each episode. The agent have to be close to the goal to reach, not just in its tile like in the classic Ant-Maze.
These differences actually make a huge difference for the performances as you can se here: https://openreview.net/pdf?id=PkHkPQMTxg Appendix H page 29.

