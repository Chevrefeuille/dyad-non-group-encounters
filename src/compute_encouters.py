from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *

from tqdm import tqdm

""""""
PLOT_VERIF = False

PLOT_DIFF_DEVIATION = True

PLOT_SOC_DEVIATION = True

if __name__ == "__main__":
    for env_name in ["diamor:corridor"]:
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )
        env_name_short = env_name.split(":")[0]

        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )
        days = get_all_days(env_name)

        dict_deviation = {
            "group": {},
        }

        thresholds_indiv = get_pedestrian_thresholds(env_name)
        thresholds_groups = get_groups_thresholds()

        for day in days:
            print(f"Day {day}:")

            non_groups = env.get_pedestrians(
                days=[day], no_groups=True, thresholds=thresholds_indiv
            )

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_indiv,
                group_thresholds=thresholds_groups,
            )

            all_pedestrians = env.get_pedestrians(
                days=[day], no_groups=False, thresholds=thresholds_indiv
            )

            for group in tqdm(groups):
                group_id = group.get_id()
                group_members_id = [m.get_id() for m in group.get_members()]
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()
                soc_binding = group.get_annotation(soc_binding_type)
                
                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    all_pedestrians, proximity_threshold=VICINITY, skip=group_members_id
                )

                if not group_encounters:
                    continue

                dict_deviation["group"][group_id] = {
                    "group deviation": [],
                    "social_binding": soc_binding,
                    "encounters deviation": [],
                }

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

                    if (len(traj_group_vicinity) < 6 or len(traj_non_group_vicinity) < 6):
                        continue

                    if(PLOT_VERIF) :
                        plot_static_2D_trajectories(
                        [
                            traj_A_vicinity,
                            traj_B_vicinity,
                            traj_group_vicinity,
                            traj_non_group_vicinity,
                        ],
                        boundaries=env.boundaries,
                        colors=[
                            "cornflowerblue",
                            "cornflowerblue",
                            "lightsteelblue",
                            "orange",
                        ],
                    )

                    mean_group_speed = np.nanmean(traj_group_vicinity[:,4])/1000 
                    if (mean_group_speed < 0.5):
                        continue
                    elif (mean_group_speed > 2.5):
                        continue    

                    encounter_speed = np.nanmean(traj_non_group_vicinity[:,4])/1000
                    if (encounter_speed < 0.5):
                        continue
                    elif (encounter_speed > 2.5):
                        continue
                    
                    n_points_average = 4
                    length_non_group = compute_length(traj_non_group_vicinity)
                    max_dev_ng = compute_maximum_lateral_deviation_using_vel_2(
                        traj_non_group_vicinity, n_points_average, interpolate=False, length=length_non_group
                    )

                    length_group = compute_length(traj_group_vicinity)
                    max_dev_group = compute_maximum_lateral_deviation_using_vel_2(
                        traj_group_vicinity, n_points_average, interpolate=False, length=length_group
                    )

                    max_dev_group["start_velocity"] = mean_group_speed
                    max_dev_ng["start_velocity"] = encounter_speed
                    dict_deviation["group"][group_id]["group deviation"].append(max_dev_group)
                    dict_deviation["group"][group_id]["encounters deviation"].append(max_dev_ng)

    print(dict_deviation)
    pickle_save(f"../data/pickle/{env_name_short}_encounters_deviations.pkl", dict_deviation)
            






