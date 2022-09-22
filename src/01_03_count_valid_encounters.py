from lib2to3.pgen2.token import SLASHEQUAL
from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.trajectory_utils import *

from parameters import *
import matplotlib.pyplot as plt
from tqdm import tqdm

from utils import (
    get_all_days,
    get_groups_thresholds,
    get_pedestrian_thresholds,
    get_social_values,
)

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:
        # print(f"- {env_name}")
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        encounters = pickle_load(
            f"../data/pickle/opposite_encounters_{env_name_short}.pkl"
        )

        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        n_encounters = {}

        for day in days:

            non_groups = env.get_pedestrians(
                days=[day], thresholds=thresholds_ped, sampling_time=500
            )

            groups = env.get_groups(
                size=2,
                days=[day],
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                with_social_binding=True,
                sampling_time=500,
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

                    overlap = False

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

                    pos_group = traj_group[:, 1:3]
                    pos_non_group = traj_non_group[:, 1:3]

                    d_G_NG = compute_interpersonal_distance(pos_group, pos_non_group)
                    traj_non_group_vicinity = traj_non_group[d_G_NG < VICINITY]
                    traj_group_vicinity = traj_group[d_G_NG < VICINITY]

                    if len(traj_group_vicinity) <= N_POINTS_MIN_VICINITY:
                        continue

                    # check if encounter is valid
                    for other_non_group in group_encounters:
                        other_non_group_id = other_non_group.get_id()

                        if other_non_group_id == non_group_id:
                            continue

                        trajectories = [
                            group_members[0].get_trajectory(),
                            group_members[1].get_trajectory(),
                            group_as_indiv.get_trajectory(),
                            other_non_group.get_trajectory(),
                        ]
                        [
                            _,
                            _,
                            other_traj_group,
                            traj_other_non_group,
                        ] = compute_simultaneous_observations(trajectories)

                        other_relative_direction = compute_relative_direction(
                            group_as_indiv.get_trajectory(),
                            other_non_group.get_trajectory(),
                        )

                        if other_relative_direction != "opposite":
                            continue

                        other_pos_group = other_traj_group[:, 1:3]
                        pos_other_non_group = traj_other_non_group[:, 1:3]

                        other_d_G_NG = compute_interpersonal_distance(
                            other_pos_group, pos_other_non_group
                        )
                        traj_other_non_group_vicinity = traj_other_non_group[
                            other_d_G_NG < VICINITY
                        ]
                        other_traj_group_vicinity = other_traj_group[
                            other_d_G_NG < VICINITY
                        ]

                        if len(other_traj_group_vicinity) <= N_POINTS_MIN_VICINITY:
                            continue

                        # [
                        #     traj_non_group_sim,
                        #     traj_other_non_group_sim,
                        # ] = compute_simultaneous_observations(
                        #     [traj_non_group, traj_other_non_group]
                        # )

                        if (
                            len(
                                compute_simultaneous_observations(
                                    [other_traj_group_vicinity, traj_group_vicinity]
                                )[0]
                            )
                            > N_POINTS_MIN_VICINITY
                        ):
                            overlap = True
                            break

                    if not overlap:
                        if relative_direction not in n_encounters:
                            n_encounters[relative_direction] = {}

                        if soc_binding not in n_encounters[relative_direction]:
                            n_encounters[relative_direction][soc_binding] = 0
                        n_encounters[relative_direction][soc_binding] += 1

        for dir in n_encounters:
            print(f"-> {dir}")
            if dir == "None":
                continue
            tot = 0
            for i in soc_binding_values:
                print(f"  - {soc_binding_names[i]}: {n_encounters[dir][i]}")
                tot += n_encounters[dir][i]
            print(f" Total: {tot}")
            print("--------")
        print("==============")
