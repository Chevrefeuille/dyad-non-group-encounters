from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np
from tqdm import tqdm

from utils import *


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        positions = {}

        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        for day in tqdm(days):
            all = env.get_pedestrians(days=[day], thresholds=thresholds_ped)

            groups = env.get_groups(
                size=2,
                days=[day],
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                with_social_binding=True,
            )

            # print(len(groups))

            for group in groups:
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()
                group_members_id = [m.get_id() for m in group.get_members()]

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding not in soc_binding_values:
                    continue

                if soc_binding not in positions:
                    positions[soc_binding] = {
                        "pos_Ax": [],
                        "pos_Ay": [],
                        "pos_Bx": [],
                        "pos_By": [],
                        "d": [],
                    }

                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    all,
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

                    # plot_animated_2D_trajectories(
                    #     [
                    #         group_members[0].get_trajectory(),
                    #         group_members[1].get_trajectory(),
                    #         non_group.get_trajectory(),
                    #     ],
                    #     boundaries=env.boundaries,
                    #     labels=["group-A", "group-B", "non-group"],
                    # )

                    # plot_static_2D_trajectories(
                    #     [
                    #         group_members[0].get_trajectory(),
                    #         group_members[1].get_trajectory(),
                    #         non_group.get_trajectory(),
                    #     ],
                    #     boundaries=env.boundaries,
                    #     labels=["group-A", "group-B", "non-group"],
                    # )

                    if len(traj_group) <= 1:
                        continue

                    traj_group_aligned, [
                        traj_non_group_aligned,
                        traj_A_aligned,
                        traj_B_aligned,
                    ] = align_trajectories_at_origin(
                        traj_group, [traj_non_group, traj_A, traj_B]
                    )

                    distance = np.linalg.norm(traj_non_group_aligned[:, 1:3], axis=1)

                    positions[soc_binding]["d"] += distance.tolist()
                    positions[soc_binding]["pos_Ax"] += traj_A_aligned[:, 1].tolist()
                    positions[soc_binding]["pos_Ay"] += traj_A_aligned[:, 2].tolist()
                    positions[soc_binding]["pos_Bx"] += traj_B_aligned[:, 1].tolist()
                    positions[soc_binding]["pos_By"] += traj_B_aligned[:, 2].tolist()

                    # plot_static_2D_trajectories(
                    #     [
                    #         traj_A_aligned,
                    #         traj_B_aligned,
                    #         # traj_non_group_aligned,
                    #     ],
                    #     labels=["A", "B"],
                    # )

        for soc_binding in soc_binding_values:
            positions[soc_binding]["d"] = np.array(positions[soc_binding]["d"])
            positions[soc_binding]["pos_Ax"] = np.array(
                positions[soc_binding]["pos_Ax"]
            )
            positions[soc_binding]["pos_Ay"] = np.array(
                positions[soc_binding]["pos_Ay"]
            )
            positions[soc_binding]["pos_Bx"] = np.array(
                positions[soc_binding]["pos_Bx"]
            )
            positions[soc_binding]["pos_By"] = np.array(
                positions[soc_binding]["pos_By"]
            )

        pickle_save(
            f"../data/pickle/positions_group_members_{env_name_short}_with_interaction.pkl",
            positions,
        )
