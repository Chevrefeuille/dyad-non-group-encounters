from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *

from tqdm import tqdm

""""""
PLOT_VERIF = False

ALL_TRAJECTORY = True

MIN_NUMBER_OBSERVATIONS_LOCAL = 5

if __name__ == "__main__":
    for env_name in ["diamor:corridor"]:
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )
        env_name_short = env_name.split(":")[0]

        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )
        days = get_all_days(env_name)
        days = [days[0]]

        if(ALL_TRAJECTORY):
            dict_deviation = {
                "group": {},
            }
        else :
            dict_deviation = {
                "MAX_DISTANCE": {"group": {}, },
            }
            for max_distance in MAX_DISTANCE_INTERVAL:
                    dict_deviation["MAX_DISTANCE"][max_distance] = {
                        "group": {},
                    }

        thresholds_indiv = get_pedestrian_thresholds(env_name)
        thresholds_groups = get_groups_thresholds()

        for day in days:
            print(f"Day {day}:")

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_indiv,
                group_thresholds=thresholds_groups,
                sampling_time=500
            )

            all_pedestrians = env.get_pedestrians(
                days=[day], no_groups=False, thresholds=thresholds_indiv, sampling_time=500
            )

            for group in tqdm(groups):
                group_id = group.get_id()
                group_members_id = [m.get_id() for m in group.get_members()]
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()
                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding not in soc_binding_values:
                    soc_binding = "other"
                
                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    all_pedestrians, proximity_threshold=VICINITY, skip=group_members_id
                )

                if not group_encounters:
                    continue

                if(ALL_TRAJECTORY):
                    dict_deviation["group"][group_id] = {
                        "group deviation": [],
                        "social_binding": soc_binding,
                        "encounters deviation": [],
                    }
                else :
                    for max_distance in MAX_DISTANCE_INTERVAL:
                        dict_deviation["MAX_DISTANCE"][max_distance]["group"][group_id] = {
                            "group deviation": [],
                            "social_binding": soc_binding,
                            "encounters deviation": [],
                        }

                print(group_encounters)
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

                    time_of_group_traj = traj_group_vicinity[-1, 0] - traj_group_vicinity[0, 0]
                    time_of_non_group_traj = traj_non_group_vicinity[-1, 0] - traj_non_group_vicinity[0, 0]
                        
                    if(ALL_TRAJECTORY):
                        n_points_average = 4
                        length_non_group = compute_length(traj_non_group_vicinity)
                        max_dev_ng = compute_maximum_lateral_deviation_using_vel_2(
                            traj_non_group_vicinity, n_points_average, interpolate=False, length=length_non_group
                        )

                        length_group = compute_length(traj_group_vicinity)
                        max_dev_group = compute_maximum_lateral_deviation_using_vel_2(
                            traj_group_vicinity, n_points_average, interpolate=False, length=length_group
                        )
                        if(PLOT_VERIF) :
                            fig, ax = plot_baseline(trajectory = traj_group_vicinity , max_dev = max_dev_group,soc_binding = soc_binding,group = True, id = group_id, boundaries = env.boundaries, colors = colors,ax = None,
                                                n_average = n_points_average, show = False)
                            plot_baseline(trajectory = traj_non_group_vicinity , max_dev = max_dev_ng,soc_binding = soc_binding,group = False, id = non_group_id, boundaries = env.boundaries, colors = colors, ax = ax, fig = fig,
                                        show = True
                            )
                            plt.close() 

                        max_dev_group["mean_velocity"] = mean_group_speed
                        max_dev_ng["mean_velocity"] = encounter_speed

                        max_dev_group["time"] = time_of_group_traj
                        max_dev_ng["time"] = time_of_non_group_traj

                        dict_deviation["group"][group_id]["group deviation"].append(max_dev_group)
                        dict_deviation["group"][group_id]["encounters deviation"].append(max_dev_ng)

                    else:
                        for MAX_DISTANCE in MAX_DISTANCE_INTERVAL:

                            result = compute_continuous_sub_trajectories_using_distance(traj_group_vicinity, max_distance=MAX_DISTANCE, min_length=MIN_NUMBER_OBSERVATIONS_LOCAL)
                            if (result == None):
                                continue
                            list_sub_traj_group = result[0]
                            list_sub_length_group = result[1]

                            result = compute_continuous_sub_trajectories_using_distance(traj_non_group_vicinity, max_distance=MAX_DISTANCE, min_length=MIN_NUMBER_OBSERVATIONS_LOCAL)
                            if (result == None):
                                continue
                            list_sub_traj_non_group = result[0]
                            list_sub_length_non_group = result[1]
                            indice = -1

                            for sub_traj_group in list_sub_traj_group:
                                indice += 1
                                n_points_average = 4
                              
                                max_dev_group = compute_maximum_lateral_deviation_using_vel_2(
                                    sub_traj_group, n_points_average, interpolate=False, length=list_sub_length_group[indice]
                                )

                                max_dev_group["mean_velocity"] = mean_group_speed
                                
                                max_dev_group["time"] = time_of_group_traj

                                dict_deviation["MAX_DISTANCE"][MAX_DISTANCE]["group"][group_id]["group deviation"].append(max_dev_group)

                            indice = -1
                            for sub_traj_non_group in list_sub_traj_non_group :
                                indice += 1
                                n_points_average = 4

                                max_dev_ng = compute_maximum_lateral_deviation_using_vel_2(
                                    sub_traj_non_group, n_points_average, interpolate=False, length=list_sub_length_non_group[indice]
                                )

                                max_dev_ng["mean_velocity"] = encounter_speed

                                max_dev_ng["time"] = time_of_non_group_traj

                                dict_deviation["MAX_DISTANCE"][MAX_DISTANCE]["group"][group_id]["encounters deviation"].append(max_dev_ng)


    if(ALL_TRAJECTORY):
        pickle_save(f"../data/pickle/{env_name_short}_encounters_deviations.pkl", dict_deviation)

    else:
        pickle_save(f"../data/pickle/{env_name_short}_encounters_deviations_MAX_DISTANCE.pkl", dict_deviation)
            






