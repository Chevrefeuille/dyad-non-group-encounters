from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.trajectory_utils import *
from pedestrians_social_binding.plot_utils import *

from utils import *


import numpy as np
import tcod
from tqdm import tqdm


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


def create_flow_graph(grid_vel):
    h, w, _ = grid_vel.shape
    flow_graph = tcod.path.CustomGraph((h, w))

    c_max = 10
    s = 0.3 * c_max

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

    return flow_graph


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        xmin, xmax, ymin, ymax = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values = get_social_values(
            env_name
        )

        encounters = pickle_load(
            f"../data/pickle/opposite_encounters_{env_name_short}.pkl"
        )
        velocity_field = f"../data/images/velocity_field_{env_name_short}.png"
        grid_vel = pickle_load(f"../data/pickle/velocity_field_{env_name_short}.pkl")

        flow_graph = create_flow_graph(grid_vel)

        for day in days:

            thresholds_ped = get_pedestrian_thresholds(env_name)
            thresholds_group = get_groups_thresholds()

            non_groups = env.get_pedestrians(days=[day], thresholds=thresholds_ped)

            groups = env.get_groups(
                size=2,
                days=[day],
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                with_social_binding=True,
            )

            for group in tqdm(groups):
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()
                group_members_id = [m.get_id() for m in group.get_members()]

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding is None:
                    continue

                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    non_groups, proximity_threshold=None, skip=group_members_id
                )

                if not group_encounters:
                    continue

                for non_group in group_encounters:

                    non_group_id = non_group.get_id()

                    trajectories = [
                        group_members[0].get_trajectory(),
                        group_members[1].get_trajectory(),
                        group_as_indiv.get_trajectory(),
                        non_group.get_trajectory(),
                    ]
                    [
                        traj_A,
                        traj_B,
                        traj_group,
                        traj_non_group,
                    ] = compute_simultaneous_observations(trajectories)

                    relative_direction = compute_relative_direction(
                        group_as_indiv.get_trajectory(), non_group.get_trajectory()
                    )

                    if relative_direction != "opposite":
                        continue

                    if len(traj_group) <= 1:
                        continue

                    first_obs_group = traj_group[0]
                    las_obs_group = traj_group[-1]

                    first_pos_group = first_obs_group[1:3]
                    last_pos_group = las_obs_group[1:3]

                    first_cell_x = int(
                        np.ceil((first_pos_group[0] - xmin) / VEL_FIELD_CELL_SIZE)
                    )
                    first_cell_y = int(
                        np.ceil((first_pos_group[1] - ymin) / VEL_FIELD_CELL_SIZE)
                    )

                    last_cell_x = int(
                        np.ceil((last_pos_group[0] - xmin) / VEL_FIELD_CELL_SIZE)
                    )
                    last_cell_y = int(
                        np.ceil((last_pos_group[1] - ymin) / VEL_FIELD_CELL_SIZE)
                    )

                    path_finder = tcod.path.Pathfinder(flow_graph)

                    path_finder.add_root([first_cell_x, first_cell_y])
                    path = path_finder.path_to([last_cell_x, last_cell_y])

                    if len(path) <= 1:
                        continue

                    trajectory = np.zeros((len(path), 7))
                    # trajectory[:, 0] = traj_group[: len(trajectory), 0]
                    trajectory[:, 1] = path[:, 0] * VEL_FIELD_CELL_SIZE + xmin
                    trajectory[:, 2] = path[:, 1] * VEL_FIELD_CELL_SIZE + ymin

                    # print(trajectory.shape, trajectory[:, 1:3])

                    plot_animated_2D_trajectory(
                        trajectory,
                        boundaries=env.boundaries,
                        colors=len(trajectory) * ["black"],
                        background=velocity_field,
                    )
