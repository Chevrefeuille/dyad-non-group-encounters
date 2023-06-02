from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np
import matplotlib.pyplot as plt
import random as rnd
import tcod

from utils import *


directions = [
    np.array([0, 1]),  # up
    np.array([0, -1]),  # down
    np.array([-1, 0]),  # left
    np.array([1, 0]),  # right
    np.array([1, 1]),  # up-right
    np.array([1, -1]),  # down-right
    np.array([-1, -1]),  # down-left
    np.array([-1, 1]),  # up-left
    np.array([1, 2]),
    np.array([2, 1]),
    np.array([2, -1]),
    np.array([1, -2]),
    np.array([-1, -2]),
    np.array([-2, -1]),
    np.array([-2, 1]),
    np.array([-1, 2]),
]

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        grid_vel = pickle_load(f"../data/pickle/velocity_field_{env_name_short}.pkl")

        xmin, xmax, ymin, ymax = env.get_boundaries()

        # build the cost matrix
        # for each cell, the cost to go to an adjacent cell (diagonals included)
        # is minus the dot product between the vector from the center of the cell to
        # to the center of the adjacent cell and the velocity in the cell.
        # For to non adjacent cells, the cost is infinite

        h, w, _ = grid_vel.shape
        flow_graph = tcod.path.CustomGraph((h, w))

        c_max = 10
        s = 0.6 * c_max

        edge_costs = np.zeros((h, w, len(directions)))
        for i in range(h):
            for j in range(w):
                vel = grid_vel[i, j]
                for k, direction in enumerate(directions):
                    if np.linalg.norm(vel):
                        edge_cost = np.dot(
                            vel / np.linalg.norm(vel),
                            direction / np.linalg.norm(direction),
                        )
                        edge_cost = (
                            (-4 * s - c_max) * edge_cost**2
                            + (4 * s - c_max) * edge_cost
                            + c_max
                        )
                        edge_costs[i, j, k] = edge_cost

        # n_bin_x = int(np.ceil((xmax - xmin) / VEL_FIELD_CELL_SIZE) + 1)
        # n_bin_y = int(np.ceil((ymax - ymin) / VEL_FIELD_CELL_SIZE) + 1)
        # xi = np.linspace(0, (xmax - xmin) / 1000, n_bin_x)
        # yi = np.linspace(0, (ymax - ymin) / 1000, n_bin_y)

        # print(edge_costs[..., 6].shape)

        # plt.figure()
        # cmesh = plt.pcolormesh(
        #     xi, yi, edge_costs[..., 1].T, cmap="inferno_r", shading="auto"
        # )
        # plt.xlabel("x (m)")
        # plt.ylabel("y (m)")
        # axes = plt.gca()
        # # divider = make_axes_locatable(axes)
        # # cax = divider.append_axes("right", size="5%", pad=0.3)
        # plt.colorbar(cmesh)
        # axes.set_aspect("equal")
        # plt.show()

        # translate the cost to have only positive values
        edge_costs[edge_costs != 0] += -np.min(edge_costs) + 1

        # define cell that cannot be reached
        cost = np.ones((h, w), dtype=int)
        cost[grid_vel[..., 0] > 0] = 1

        # add edges to the graph
        for i in range(h):
            for j in range(w):
                vel = grid_vel[i, j]
                condition = np.zeros((h, w), dtype=int)
                condition[i, j] = 1
                for k, direction in enumerate(directions):
                    edge_cost = int(edge_costs[i, j, k] * 10)
                    # print(edge_cost)
                    if edge_cost:
                        flow_graph.add_edge(
                            tuple(direction), edge_cost, cost=cost, condition=condition
                        )

        # path_finder = tcod.path.Pathfinder(flow_graph)

        # for i in range(3):
        #     # find a random seed point with non null velocity
        #     non_null_v = np.argwhere(grid_vel[:, :, 0] > 0)
        #     random_vals = non_null_v[np.random.choice(non_null_v.shape[0], 2)]
        #     start = (random_vals[0, 0], random_vals[0, 1])
        #     end = (random_vals[1, 0], random_vals[1, 1])

        #     # print(start, end)
        #     path_finder = tcod.path.Pathfinder(flow_graph)
        #     path_finder.add_root(end)
        #     path = path_finder.path_from(start)

        #     trajectory = np.zeros((len(path), 7))
        #     trajectory[:, 1] = path[:, 0] * VEL_FIELD_CELL_SIZE + xmin
        #     trajectory[:, 2] = path[:, 1] * VEL_FIELD_CELL_SIZE + ymin

        #     background_path = (
        #         f"../data/images/velocity_field_{env_name.split(':')[0]}.png"
        #     )
        #     plot_animated_2D_trajectory(
        #         trajectory,
        #         boundaries=env.boundaries,
        #         colors=len(trajectory) * ["black"],
        #         background=background_path,
        #     )
