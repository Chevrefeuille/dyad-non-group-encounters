from tkinter import N
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np

from utils import *
from scipy.spatial.distance import cdist


def find_wall_trajectory(position, walls_cells):

    cell_x = np.ceil((position[:, 0] - XMIN) / VEL_FIELD_CELL_SIZE).astype(int)
    cell_y = np.ceil((position[:, 1] - YMIN) / VEL_FIELD_CELL_SIZE).astype(int)

    traj_cell_coordinates = np.stack((cell_x, cell_y), axis=1)
    distance_to_walls = cdist(traj_cell_coordinates, walls_cells)

    closest_wall_cells = walls_cells[np.argmin(distance_to_walls, axis=1)]

    wall_trajectory = np.zeros((len(position), 2))
    wall_trajectory[:, 0] = closest_wall_cells[:, 0] * VEL_FIELD_CELL_SIZE + XMIN
    wall_trajectory[:, 1] = closest_wall_cells[:, 1] * VEL_FIELD_CELL_SIZE + YMIN

    return wall_trajectory


def find_closest_wall_cell(cell_x, cell_y, walls):
    cell = np.array([cell_x, cell_y])
    walls_coordinates = np.argwhere(walls)
    distance_to_walls = cdist([cell], walls_coordinates)
    closest_wall_cell = walls_coordinates[np.argmin(distance_to_walls)]
    return closest_wall_cell


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values = get_social_values(
            env_name
        )

        encounters = pickle_load(
            f"../data/pickle/opposite_encounters_{env_name_short}.pkl"
        )
        walls = pickle_load(f"../data/pickle/walls_{env_name_short}.pkl")
        walls_cells = np.argwhere(walls)
        wall_img = f"../data/images/walls_{env_name_short}.png"

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

            for group in groups:
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

                    wall_traj_group = find_wall_trajectory(
                        traj_group[:, 1:3], walls_cells
                    )

                    first_obs_group = traj_group[0]
                    las_obs_group = traj_group[-1]

                    first_pos_group = first_obs_group[1:3]
                    last_pos_group = las_obs_group[1:3]

                    first_cell_x = int(
                        np.ceil((first_pos_group[0] - XMIN) / VEL_FIELD_CELL_SIZE)
                    )
                    first_cell_y = int(
                        np.ceil((first_pos_group[1] - YMIN) / VEL_FIELD_CELL_SIZE)
                    )

                    # last_cell_x = int(
                    #     np.ceil((last_pos_group[0] - xmin) / VEL_FIELD_CELL_SIZE)
                    # )
                    # last_cell_y = int(
                    #     np.ceil((last_pos_group[1] - ymin) / VEL_FIELD_CELL_SIZE)
                    # )

                    walls[walls > 0] = -1
                    background = plt.imread(wall_img)
                    plt.imshow(background, extent=[XMIN, XMAX, YMIN, YMAX])
                    print(traj_group)
                    plt.scatter(traj_group[:, 1], traj_group[:, 2], color="red", s=4)
                    # plt.scatter(
                    #     walls_coordinates[:, 0] * VEL_FIELD_CELL_SIZE + xmin,
                    #     walls_coordinates[:, 1] * VEL_FIELD_CELL_SIZE + ymin,
                    #     color="blue",
                    # )
                    plt.scatter(
                        wall_traj_group[:, 0], wall_traj_group[:, 1], color="blue", s=4
                    )
                    plt.xlim([XMIN, XMAX])
                    plt.ylim([YMIN, YMAX])
                    plt.show()

                    # path_finder = tcod.path.Pathfinder(flow_graph)

                    # path_finder.add_root([first_cell_x, first_cell_y])
                    # path = path_finder.path_to([last_cell_x, last_cell_y])

                    # if len(path) <= 1:
                    #     continue

                    # trajectory = np.zeros((len(path), 7))
                    # # trajectory[:, 0] = traj_group[: len(trajectory), 0]
                    # trajectory[:, 1] = path[:, 0] * VEL_FIELD_CELL_SIZE + xmin
                    # trajectory[:, 2] = path[:, 1] * VEL_FIELD_CELL_SIZE + ymin

                    # # print(trajectory.shape, trajectory[:, 1:3])

                    # plot_animated_2D_trajectory(
                    #     trajectory,
                    #     boundaries=env.boundaries,
                    #     colors=len(red) * ["black"],
                    #     background=walls_image,
                    # )
