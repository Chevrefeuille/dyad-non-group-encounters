from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.environment import Environment
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

""" The goal of this script is print statistics about the encounters between pedestrians in the corridor environment. 
"""

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

        n_encounters_soc = {}
        n_encounters_dir = {}
        n_encounters = {}


        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        for day in days:

            non_groups = env.get_pedestrians(
                days=[day], thresholds=thresholds_ped, sampling_time=500, no_groups=True
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

                if soc_binding not in n_encounters_soc:
                    n_encounters_soc[soc_binding] = 0

                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    non_groups, proximity_threshold=4000, skip=group_members_id, alone=True
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

                    if relative_direction not in n_encounters_dir:
                        n_encounters_dir[relative_direction] = 0

                    if relative_direction not in n_encounters:
                        n_encounters[relative_direction] = {}

                    if soc_binding not in n_encounters[relative_direction]:
                        n_encounters[relative_direction][soc_binding] = 0

                    # if relative_direction != "opposite":
                    #     continue


                    pos_A = traj_A[:, 1:3]
                    pos_B = traj_B[:, 1:3]
                    pos_group = traj_group[:, 1:3]
                    pos_non_group = traj_non_group[:, 1:3]

                    d_G_NG = compute_interpersonal_distance(pos_group, pos_non_group)

                    traj_A_encounter = traj_A[d_G_NG < VICINITY]
                    traj_B_encounter = traj_B[d_G_NG < VICINITY]
                    traj_group_encounter = traj_group[d_G_NG < VICINITY]
                    pos_A_encounter = pos_A[d_G_NG < VICINITY]
                    pos_B_encounter = pos_B[d_G_NG < VICINITY]
                    pos_group_encounter = pos_group[d_G_NG < VICINITY]
                    pos_non_group_encounter = pos_non_group[d_G_NG < VICINITY]

                    if len(pos_group_encounter) <= N_POINTS_MIN_VICINITY:
                        continue


                    n_encounters_soc[soc_binding] += 1
                    n_encounters[relative_direction][soc_binding] += 1


                    # if soc_binding != 0:
                    n_encounters_dir[relative_direction] += 1 

        print(env_name_short)
        print("Social binding")
        tot = 0
        for i in soc_binding_values:
            print(f"  - {soc_binding_names[i]}: {n_encounters_soc[i]}")
            tot += n_encounters_soc[i]
        print(f" Total: {tot}")
        print("--------")
        print("Rel dir")
        tot = 0
        for dir in n_encounters_dir:
            if dir == "None":
                continue
            print(f"  - {dir}: {n_encounters_dir[dir]}")
            tot += n_encounters_dir[dir]
        print(f" Total: {tot}")
        print("==============")
        
        print("both")
        for dir in n_encounters_dir:
            print(f"-> {dir}")
            if dir == "None":
                continue
            tot = 0
            for i in soc_binding_values:
                if i not in n_encounters[dir]:
                    continue
                print(f"  - {soc_binding_names[i]}: {n_encounters[dir][i]}")
                tot += n_encounters[dir][i]
            print(f" Total: {tot}")
            print("--------")
        print("==============")




                