from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np

from utils import *


if __name__ == "__main__":

    # for env_name in ["atc:corridor", "diamor:corridor"]:
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

        observed_minimum_distances = {}
        straight_line_minimum_distances = {}
        group_sizes = {}
        velocities = {}

        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        for day in days:
            non_groups = env.get_pedestrians(
                days=[day], thresholds=thresholds_ped, no_groups=True
            )

            for non_group in non_groups:
                non_group_id = non_group.get_id()

                encounters = non_group.get_encountered_pedestrians(
                    non_groups,
                    proximity_threshold=None,
                    alone=None,
                    skip=[non_group_id],
                )

                for other_non_group in encounters:

                    non_group_id = non_group.get_id()

                    trajectories = [
                        non_group.get_trajectory(),
                        other_non_group.get_trajectory(),
                    ]
                    relative_direction = compute_relative_direction(
                        non_group.get_trajectory(), other_non_group.get_trajectory()
                    )

                    if relative_direction != "opposite":
                        continue

                    [
                        traj_non_group,
                        traj_other_non_group,
                    ] = compute_simultaneous_observations(trajectories)

                    traj_non_group_aligned, [
                        traj_other_non_group_aligned
                    ] = align_trajectories_at_origin(
                        traj_non_group, [traj_other_non_group]
                    )

                    # center_of_mass = compute_center_of_mass(trajectories)

                    # plot_static_2D_trajectory(center_of_mass, boundaries=env.boundaries)

                    d = np.linalg.norm(
                        traj_non_group[:, 1:3] - traj_other_non_group[:, 1:3], axis=1
                    )
                    traj_non_group_in_vicinity = traj_non_group[d < 8000]
                    traj_other_non_group_in_vicinity = traj_other_non_group[d < 8000]
                    print(
                        traj_other_non_group_in_vicinity,
                        traj_other_non_group_in_vicinity[::-1, :],
                    )

                    d_inv = (
                        np.linalg.norm(
                            traj_non_group_in_vicinity[:, 1:3]
                            - traj_other_non_group_in_vicinity[::-1, 1:3],
                            axis=1,
                        )
                        / 1000
                    )

                    d_v = (
                        np.linalg.norm(
                            traj_non_group_in_vicinity[:, 1:3]
                            - traj_other_non_group_in_vicinity[:, 1:3],
                            axis=1,
                        )
                        / 1000
                    )

                    # v_non_group = traj_non_group_in_vicinity[:, 5:7]
                    # v_other_non_group = traj_other_non_group_in_vicinity[:, 5:7]

                    # angles = np.arctan2(
                    #     v_non_group[:, 1], v_non_group[:, 0]
                    # ) - np.arctan2(v_other_non_group[:, 1], v_other_non_group[:, 0])

                    # angles[angles > np.pi] -= 2 * np.pi
                    # angles[angles < -np.pi] += 2 * np.pi

                    # angles = np.abs(np.degrees(angles))

                    # if len(traj_non_group_in_vicinity) > 2 and np.min(d) < 2000:

                    #     plot_animated_2D_trajectories(
                    #         [
                    #             traj_non_group_in_vicinity,
                    #             traj_other_non_group_in_vicinity,
                    #         ],
                    #     )

                    #     fig, ax = plt.subplots()
                    #     ax.plot(d_inv)
                    #     ax.plot(d_v)
                    #     ax.set_ylim([0, 4])
