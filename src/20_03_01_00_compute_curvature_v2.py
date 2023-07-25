from copy import deepcopy
import os
from matplotlib import patches
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
from parameters import *
from scipy.stats import f_oneway

from tqdm import tqdm

"""The goal of this script is to compute the curvature of the pedestrians in the corridor environment.
The curvature is computed as the maximum lateral curvatureiation of the pedestrian from its baseline trajectory.
The baseline trajectory is the trajectory of the pedestrian using an average of the first 4 velocities vectors of the pedestrian.
    """


# Parameters


### Current parameters

# Minimum number of observations to compute the curvature
MIN_NUMBER_OBSERVATIONS_LOCAL = 25
# If we want to plot the trajectory to visualize the curvature
PLOT_VERIF = False
# If we want to plot (scatter) the mean curvature for each pedestrian
PLOT_MEAN_MAX_DEV = False

# Control the max smapling time for the trajectory
MAX_TIME = 1000
MAX_DISTANCE = MAX_DISTANCE_INTERVAL[0]

def compute_time_for_all_pedestrians(env_imput):
    """ This function computes the time for all pedestrians in the environment.
    
    Parameters
    ----------
    env : Environment
        The environment in which we want to compute the time for all pedestrians.
        
    Returns
    -------
        times_all : dict
            A dictionary containing the time for all pedestrians in the environment.
            The dictionary has the following structure:
                - times_all[day][group_id] = [time_1, time_2, ...]
                - times_all[day][non_group_id] = [time_1, time_2, ...]
                """
    print("Computing time for all pedestrians...")
    for env_name in env_imput:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]
        days = DAYS_ATC if env_name_short == "atc" else DAYS_DIAMOR
        times_all = {}

        for day in days:
            thresholds_ped = get_pedestrian_thresholds(env_name)
            thresholds_group = get_groups_thresholds()

            non_groups = env.get_pedestrians(
                days=[day],
                no_groups=True,
                thresholds=thresholds_ped,
                sampling_time=100
            )

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                sampling_time=100
            )

            times_all[day] = {"group": {}, "non_group": {}}

            print(f"  - Found {len(non_groups)} non groups.")
            print(f"  - Found {len(groups)} groups.")

            # find groups undisturbed trajectories
            for group in tqdm(groups):
                group_id = group.get_id()
                trajectory = group.get_center_of_mass_trajectory()

                times_all[day]["group"][group_id] = trajectory[:, 0]

            for non_group in tqdm(non_groups):
                non_group_id = non_group.get_id()
                all_trajectory = non_group.get_trajectory()

                if not len(all_trajectory):
                    continue

                times_all[day]["non_group"][
                    non_group_id
                ] = all_trajectory[:, 0]
    print("Done.")
    return times_all


if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        # Setup relevant variables
        env_name_short = env_name.split(":")[0]
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )
        days = DAYS_ATC if env_name_short == "atc" else DAYS_DIAMOR
        days = [days[0]]
        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )
        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        all_times = compute_time_for_all_pedestrians(["diamor:corridor"])
        disturbed_times = pickle_load(f"../data/pickle/disturbed_times_sampling_time.pkl")

        dict_curvature = {}

        # Create the dictionary that will store the curvature
        no_encounters_curvature = {
            "group": {},
            "non_group": {},
        }

        # Loop over the days
        for day in days:

            print(f"Day {day}:")

            non_groups = env.get_pedestrians(
                days=[day],
                no_groups=True,
                thresholds=thresholds_ped,
                sampling_time=  100
            )

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                sampling_time=100
            )

            number_of_group_filtered = 0
            print("number of groups:", len(groups))

            # compute curvature for all the groups
            for group in tqdm(groups):

                # get the times where the group is undisturbed
                group_id = group.get_id()
                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding not in soc_binding_values:
                    soc_binding = "other"
                if group_id not in all_times[day]["group"]:
                    continue
                group_all_times = all_times[day]["group"][group_id]

                # compute the curvature for each pedestrian in the group
                for pedestrian in group.get_members():

                    # get the trajectory of the pedestrian, filter it to keep only the times where the group is in the corridor
                    pedestrian_id = pedestrian.get_id()
                    no_encounters_curvature["group"][pedestrian_id] = {
                        "social_binding": soc_binding,
                        "curvature_list": [],
                    }
                    trajectory = pedestrian.get_trajectory()

                    if(group_id in disturbed_times[day]["group"]):
                        undisturbed_masque = np.isin(group_all_times, disturbed_times[day]["group"][group_id])
                        undisturbed_times = group_all_times[~undisturbed_masque]
                    else:
                        undisturbed_times = group_all_times

                    # We don't want trajectory with too few observations
                    if(undisturbed_times.shape[0] <= MIN_NUMBER_OBSERVATIONS_LOCAL):
                        continue

                    # get the trajectory of the pedestrian at the times where the group is undisturbed
                    pedestrian_undisturbed_trajectory = get_trajectory_at_times(
                        trajectory, undisturbed_times
                    )

                    list_of_sub_trajectories = [pedestrian_undisturbed_trajectory]
                    test_sub_pedestrian = np.diff(pedestrian_undisturbed_trajectory[:,0])

                    # Separate where there is a gap in time in the trajectory
                    if(np.any(test_sub_pedestrian > MAX_TIME)):
                        list_of_sub_trajectories = compute_continuous_sub_trajectories_using_time(pedestrian_undisturbed_trajectory, max_gap=MAX_TIME)
                        
                    sub_sub_trajectory = []
                    sub_length = []

                    # Separate where there is a gap in space in the trajectory, we want only continues trajectory of MAX_DISTANCE
                    for sub_trajectory in list_of_sub_trajectories:

                        result = compute_continuous_sub_trajectories_using_distance_v2(sub_trajectory, max_distance=MAX_DISTANCE, min_length=MIN_NUMBER_OBSERVATIONS_LOCAL)
                        if (result is None):
                            continue
                        add = result[0]
                        length = result[1]

                        sub_sub_trajectory += add
                        sub_length += length

                    # Compute the curvature for each sub trajectory
                    indice = 0
                    for trajectory in sub_sub_trajectory:
                        length = sub_length[indice]
                        indice += 1

                        mean_speed = np.nanmean(trajectory[:,4])/1000
                        if (mean_speed < 0.5):
                            continue
                        elif (mean_speed > 2.5):
                            continue

                        if(len(trajectory) < 4):
                            continue

                        max_curvature_sub = {"curvature_mean": float, "mean_velocity": np.ndarray, "length_of_trajectory": float, "time": float}

                        curv = compute_curvature_v2(trajectory)

                        max_curvature_sub["number_of_observations"] = trajectory.shape[0]
                        time_of_group_traj = trajectory[-1, 0] - trajectory[0, 0]
                        max_curvature_sub["mean_velocity"] = mean_speed
                        max_curvature_sub["time"] = time_of_group_traj
                        max_curvature_sub["length_of_trajectory"] = length
                        max_curvature_sub["curvature_mean"] = np.nanmean(curv)
                        max_curvature_sub["curvature_max"] = np.nanmax(curv)
                        max_curvature_sub["curvature_sum"] = np.nansum(curv)

                        no_encounters_curvature["group"][pedestrian_id]["curvature_list"].append(max_curvature_sub)

                        if (PLOT_VERIF):
                            plot_baseline(trajectory, max_curvature_sub, None, False, id = group_id)

                number_of_group_filtered += 1


            print("number of groups filtered:", number_of_group_filtered)
            print("number of non groups:", len(non_groups))

            number_of_non_group_filtered = 0

            # compute curvature for the non groups
            for non_group in tqdm(non_groups):

                non_group_id = non_group.get_id()
                if non_group_id not in all_times[day]["non_group"]:
                    continue
                non_group_all_times = all_times[day]["non_group"][
                    non_group_id
                ]
                no_encounters_curvature["non_group"][non_group_id] = {
                        "curvature_list":[]
                    }

                # get the trajectory of the pedestrian, filter it to keep only the times where the pedestrian is in the corridor
                trajectory = non_group.get_trajectory()

                if(non_group_id in disturbed_times[day]["non_group"]):
                    undisturbed_masque = np.isin(non_group_all_times, disturbed_times[day]["non_group"][non_group_id])
                    undisturbed_times = non_group_all_times[~undisturbed_masque]
                else:
                    undisturbed_times = non_group_all_times

                if(undisturbed_times.shape[0] <= MIN_NUMBER_OBSERVATIONS_LOCAL):
                    continue

                non_group_undisturbed_trajectory = get_trajectory_at_times(
                    trajectory,
                    undisturbed_times,
                )
                list_of_sub_trajectories = [non_group_undisturbed_trajectory]
                test_sub_non_group = np.diff(non_group_undisturbed_trajectory[:,0])

                # Separate where there is a gap in time in the trajectory
                if(np.any(test_sub_non_group > MAX_TIME)):
                    list_of_sub_trajectories = compute_continuous_sub_trajectories(non_group_undisturbed_trajectory, max_gap=MAX_TIME)


                sub_sub_trajectory = []
                sub_length = []

                # Separate where there is a gap in space in the trajectory, we want only continues trajectory of 4000 mm
                for sub_trajectory in list_of_sub_trajectories:
                    result = compute_continuous_sub_trajectories_using_distance_v2(sub_trajectory, max_distance=MAX_DISTANCE, min_length=MIN_NUMBER_OBSERVATIONS_LOCAL)
                    if (result is None):
                        continue
                    add = result[0]
                    length = result[1]

                    sub_sub_trajectory += add
                    sub_length += length

                for indice, trajectory in enumerate(sub_sub_trajectory):

                    length = sub_length[indice]
                    mean_speed = np.nanmean(trajectory[:,4])/1000
                    if (mean_speed < 0.5):
                        continue
                    elif (mean_speed > 2.5):
                        continue

                    max_curvature_sub = {"curvature_mean": float, "mean_velocity": np.ndarray, "length_of_trajectory": float, "time": float}
                    curv = compute_curvature_v2(trajectory)

                    max_curvature_sub["number_of_observations"] = len(curv)
                    time_of_non_group_traj = trajectory[-1, 0] - trajectory[0, 0]
                    max_curvature_sub["curvature_mean"] = np.nanmean(curv)
                    max_curvature_sub["curvature_max"] = np.nanmax(curv)
                    max_curvature_sub["curvature_sum"] = np.nansum(curv)
                    max_curvature_sub["mean_velocity"] = mean_speed
                    max_curvature_sub["time"] = time_of_non_group_traj
                    max_curvature_sub["length_of_trajectory"] = length

                    no_encounters_curvature["non_group"][non_group_id]["curvature_list"].append(max_curvature_sub)

                    if (PLOT_VERIF):
                        plot_baseline(trajectory, max_curvature_sub, None, False, id = non_group_id)

                number_of_non_group_filtered += 1

            print("number of non groups filtered:", number_of_non_group_filtered)

        dict_curvature = no_encounters_curvature


            #END OF COMPUTE DEVIATIONS

        pickle_save(f"../data/pickle/undisturbed_curvature_points_v2.pkl", dict_curvature)