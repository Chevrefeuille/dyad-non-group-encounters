from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *
from pedestrians_social_binding.trajectory_utils import *


import numpy as np
from tqdm import tqdm

from utils import *

cross = lambda x, y, axis=None: np.cross(x, y, axis=axis)

if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        deviations = {}
        tortuosity = {}
        rbs = {}

        for day in tqdm(days):

            non_groups = env.get_pedestrians(
                days=[day], thresholds=thresholds_ped, no_groups=True
            )

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
                if soc_binding not in soc_binding_values:
                    continue

                if soc_binding not in deviations:
                    rbs[soc_binding] = []
                    deviations[soc_binding] = {
                        "int": [],
                        "ext": [],
                        "group": [],
                        "non_group": [],
                    }

                    tortuosity[soc_binding] = {
                        "int": [],
                        "ext": [],
                        "group": [],
                        "non_group": [],
                    }

                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    non_groups,
                    proximity_threshold=None,
                    alone=None,
                    skip=group_members_id,
                )

                for non_group in group_encounters:

                    non_group_id = non_group.get_id()

                    trajectories = [
                        group_members[0].get_trajectory(),
                        group_members[1].get_trajectory(),
                        group_as_indiv.get_trajectory(),
                        non_group.get_trajectory(),
                    ]
                    relative_direction = compute_relative_direction(
                        group_as_indiv.get_trajectory(), non_group.get_trajectory()
                    )

                    if relative_direction != "opposite":
                        continue

                    [
                        traj_A,
                        traj_B,
                        traj_group,
                        traj_non_group,
                    ] = compute_simultaneous_observations(trajectories)

                    in_vicinity = np.logical_and(
                        np.abs(traj_group[:, 1] - traj_non_group[:, 1]) <= 4000,
                        np.abs(traj_group[:, 2] - traj_non_group[:, 2]) <= 4000,
                    )

                    traj_A_vicinity = traj_A[in_vicinity]
                    traj_B_vicinity = traj_B[in_vicinity]
                    traj_group_vicinity = traj_group[in_vicinity]
                    traj_non_group_vicinity = traj_non_group[in_vicinity]

                    if len(traj_group_vicinity) < 3:
                        continue

                    distance_A = np.linalg.norm(
                        traj_A_vicinity[:, 1:3] - traj_non_group_vicinity[:, 1:3],
                        axis=1,
                    )
                    distance_B = np.linalg.norm(
                        traj_B_vicinity[:, 1:3] - traj_non_group_vicinity[:, 1:3],
                        axis=1,
                    )
                    mean_distance_A = np.mean(distance_A)
                    mean_distance_B = np.mean(distance_B)

                    # find interior/exterior group members
                    if mean_distance_A < mean_distance_B:
                        traj_int_vicinity, traj_ext_vicinity = (
                            traj_A_vicinity,
                            traj_B_vicinity,
                        )
                        distance_int, distance_ext = distance_A, distance_B
                    else:
                        traj_int_vicinity, traj_ext_vicinity = (
                            traj_B_vicinity,
                            traj_A_vicinity,
                        )
                        distance_int, distance_ext = distance_B, distance_A

                    # plot_static_2D_trajectories(
                    #     [
                    #         traj_A_vicinity,
                    #         traj_B_vicinity,
                    #         traj_group_vicinity,
                    #         traj_non_group_vicinity,
                    #     ],
                    #     boundaries=env.boundaries,
                    #     colors=[
                    #         "cornflowerblue",
                    #         "cornflowerblue",
                    #         "lightsteelblue",
                    #         "orange",
                    #     ],
                    # )

                    n_points_average = 4
                    max_dev_ng = compute_maximum_lateral_deviation_using_vel(
                        traj_non_group_vicinity, n_points_average, interpolate=True
                    )
                    deviations[soc_binding]["non_group"] += [max_dev_ng]
                    max_dev_ext = compute_maximum_lateral_deviation_using_vel(
                        traj_ext_vicinity, n_points_average, interpolate=True
                    )
                    deviations[soc_binding]["ext"] += [max_dev_ext]
                    max_dev_int = compute_maximum_lateral_deviation_using_vel(
                        traj_int_vicinity, n_points_average, interpolate=True
                    )
                    deviations[soc_binding]["int"] += [max_dev_int]
                    max_dev_group = compute_maximum_lateral_deviation_using_vel(
                        traj_group_vicinity, n_points_average, interpolate=True
                    )
                    deviations[soc_binding]["group"] += [max_dev_group]

                    tortuosity_ng = compute_straightness_index(
                        traj_non_group_vicinity[:, 1:3]
                    )
                    tortuosity_int = compute_straightness_index(
                        traj_int_vicinity[:, 1:3]
                    )
                    tortuosity_ext = compute_straightness_index(
                        traj_ext_vicinity[:, 1:3]
                    )
                    tortuosity_group = compute_straightness_index(
                        traj_group_vicinity[:, 1:3]
                    )
                    tortuosity[soc_binding]["non_group"] += [tortuosity_ng]
                    tortuosity[soc_binding]["ext"] += [tortuosity_ext]
                    tortuosity[soc_binding]["int"] += [tortuosity_int]
                    tortuosity[soc_binding]["group"] += [tortuosity_group]

                    traj_group_aligned, [
                        traj_non_group_aligned
                    ] = align_trajectories_at_origin(traj_group, [traj_non_group])

                    # plot_static_2D_trajectories(
                    #     [traj_group_aligned, traj_non_group_aligned]
                    # )

                    rb = compute_straight_line_minimum_distance_from_vel(
                        traj_non_group_aligned, vicinity=4000
                    )
                    if rb is None:
                        rb = np.nan

                    rbs[soc_binding] += [rb]

        pickle_save(f"../data/pickle/{env_name_short}_deviations.pkl", deviations)
        pickle_save(f"../data/pickle/{env_name_short}_tortuosity.pkl", tortuosity)
        pickle_save(f"../data/pickle/{env_name_short}_rbs.pkl", rbs)

        # plt.scatter(
        #     traj_non_group_vicinity[:, 1], traj_non_group_vicinity[:, 2]
        # )
        # plt.quiver(
        #     traj_non_group_vicinity[0, 1],
        #     traj_non_group_vicinity[0, 2],
        #     vel_non_group[0],
        #     vel_non_group[1],
        # )
        # plt.axis("equal")
        # plt.show()
