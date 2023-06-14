from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *
from pedestrians_social_binding.trajectory_utils import *


import numpy as np
from tqdm import tqdm

from utils import *

cross = lambda x, y, axis=None: np.cross(x, y, axis=axis)

VICINITY_SIZE = 4000

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

                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    non_groups,
                    proximity_threshold=None,
                    alone=None,
                    skip=group_members_id,
                )

                for non_group in group_encounters:
                    non_group_id = non_group.get_id()

                    # if f"{group_id}_{non_group_id}" not in [
                    #     "1135330011353500_11361300",
                    #     "1124460011244700_11252400",
                    #     "1116540011165401_11165903",
                    #     "1116070011161000_11162101",
                    # ]:
                    #     continue

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

                    distance_GNG = np.linalg.norm(
                        traj_group[:, 1:3] - traj_non_group[:, 1:3],
                        axis=1,
                    )

                    in_vicinity = distance_GNG <= VICINITY_SIZE

                    traj_A_vicinity = traj_A[in_vicinity]
                    traj_B_vicinity = traj_B[in_vicinity]
                    traj_group_vicinity = traj_group[in_vicinity]
                    traj_non_group_vicinity = traj_non_group[in_vicinity]

                    if len(traj_group_vicinity) < 3:
                        continue

                    plot_static_2D_trajectories(
                        [
                            traj_A,
                            traj_B,
                            traj_non_group,
                            traj_A_vicinity,
                            traj_B_vicinity,
                            traj_non_group_vicinity,
                        ],
                        boundaries=env.boundaries,
                        colors=[
                            "cornflowerblue",
                            "cornflowerblue",
                            "orange",
                            "green",
                            "green",
                            "green",
                        ],
                        # save_path=f"../data/trajectory_gifs/ped/{group_id}_{non_group_id}.mp4",
                        show=True,
                    )
