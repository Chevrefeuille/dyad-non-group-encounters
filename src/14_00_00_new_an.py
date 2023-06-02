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

                if soc_binding not in observed_minimum_distances:
                    observed_minimum_distances[soc_binding] = []
                    straight_line_minimum_distances[soc_binding] = []
                    group_sizes[soc_binding] = []
                    velocities[soc_binding] = []

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

                    # plot_static_2D_trajectories(
                    #     [
                    #         group_members[0].get_trajectory(),
                    #         group_members[1].get_trajectory(),
                    #         non_group.get_trajectory(),
                    #     ],
                    #     boundaries=env.boundaries,
                    #     labels=["group-A", "group-B", "non-group"],
                    # )

                    #             if len(traj_group) <= 1:
                    #                 continue

                    traj_group_aligned, [
                        traj_non_group_aligned
                    ] = align_trajectories_at_origin(traj_group, [traj_non_group])

                    plot_static_2D_trajectories(
                        [traj_group_aligned, traj_non_group_aligned],
                        boundaries={
                            "xmin": -8000,
                            "xmax": 8000,
                            "ymin": -8000,
                            "ymax": 8000,
                        },
                    )

        #             velocity = traj_non_group_aligned[:, 5:7]
        #             velocity_norm = np.linalg.norm(velocity, axis=1)
        #             # plt.plot(velocity_norm)
        #             # plt.show()

        #             rp = compute_straight_line_minimum_distance(traj_non_group_aligned)
        #             ro = compute_observed_minimum_distance(
        #                 traj_non_group_aligned, interpolate=True
        #             )

        #             if rp:
        #                 observed_minimum_distances[soc_binding] += [ro]
        #                 straight_line_minimum_distances[soc_binding] += [rp]
        #                 velocities[soc_binding] += [velocity_norm[0]]

        # for soc_binding in soc_binding_values:
        #     observed_minimum_distances[soc_binding] = np.array(
        #         observed_minimum_distances[soc_binding]
        #     )
        #     straight_line_minimum_distances[soc_binding] = np.array(
        #         straight_line_minimum_distances[soc_binding]
        #     )
        #     velocities[soc_binding] = np.array(velocities[soc_binding])

        # pickle_save(
        #     f"../data/pickle/observed_minimum_distance_{env_name_short}_with_interaction.pkl",
        #     observed_minimum_distances,
        # )
        # pickle_save(
        #     f"../data/pickle/straight_line_minimum_distance_{env_name_short}_with_interaction.pkl",
        #     straight_line_minimum_distances,
        # )
        # pickle_save(
        #     f"../data/pickle/velocities_{env_name_short}_with_interaction.pkl",
        #     velocities,
        # )
