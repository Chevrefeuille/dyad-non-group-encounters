from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.trajectory_utils import *
from pedestrians_social_binding.plot_utils import *

from utils import *


import numpy as np
from tqdm import tqdm
from scipy.spatial.distance import cdist

"""The goal of this script is to compare the trajectory of a group with the theoretical trajectory of the group.
The theoretical trajectory is the trajectory of the group if the group members were not interacting with each other.
"""

if __name__ == "__main__":

    for env_name in ["atc:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        xmin, xmax, ymin, ymax = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        encounters = pickle_load(
            f"../data/pickle/opposite_encounters_{env_name_short}.pkl"
        )
        splines = pickle_load(f"../data/pickle/splines_{env_name_short}.pkl")
        points = np.transpose(splines, axes=(0, 2, 1)).reshape(
            len(splines) * len(splines[0, 0]), 2
        )

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

                    first_pos_group = first_obs_group[1:3].reshape(1, 2)
                    last_pos_group = las_obs_group[1:3]

                    dist = cdist(first_pos_group, points)

                    spline_row = np.argmin(dist) // len(splines[0, 0])

                    spline_pos = splines[spline_row, ...].T
                    trajectory = np.zeros((len(spline_pos), 7))
                    trajectory[:, 1:3] = spline_pos

                    # plot_static_2D_trajectories(
                    #     [trajectory, traj_group],
                    #     boundaries=env.boundaries,
                    # )
