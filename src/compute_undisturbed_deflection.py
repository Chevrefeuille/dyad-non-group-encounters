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

"""The goal of this script is to compute the deflection of the pedestrians in the corridor environment.
The deflection is computed as the maximum lateral deviation of the pedestrian from its baseline trajectory.
The baseline trajectory is the trajectory of the pedestrian using an average of the first 4 velocities vectors of the pedestrian.
    """


# Parameters

# Minimum number of observations to compute the deflection
MIN_NUMBER_OBSERVATIONS_LOCAL = 5

# If we want to plot the trajectory to visualize the deflection
PLOT_VERIF = False

# If we want to plot (scatter) the mean deflection for each pedestrian
PLOT_MEAN_MAX_DEV = False

# If we want to plot the mean deflection for each pedestrian or for just undisturbed pedestrians
UNDISTURBED_COMPUTE = False

# If we want to plot the mean deflection for each pedestrian for an interval of speed
SPEED_INTERVAL = False

# If we want to write a filte with ANOVA test
ANOVA = False

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
                sampling_time=500
            )

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                sampling_time=500
            )

            times_all[day] = {"group": {}, "non_group": {}}

            print(f"  - Found {len(non_groups)} non groups.")
            print(f"  - Found {len(groups)} groups.")

            # find groups undisturbed trajectories
            for group in tqdm(groups):
                group_id = group.get_id()
                trajectory = group.get_center_of_mass_trajectory()
            
                if not len(trajectory):
                    continue

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
        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )
        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        str_trajectory = ""

        # Load the data of undisurbed times of groups and non groups
        if(UNDISTURBED_COMPUTE):
            str_trajectory = "undisturbed"
            times_undisturbed = pickle_load(
                f"../data/pickle/undisturbed_times_{env_name_short}.pkl"
            )
        else:
            str_trajectory = "all"
            times_undisturbed = compute_time_for_all_pedestrians(["diamor:corridor"])

        dict_deflection = {
            "MAX_DISTANCE": {}
        }

        # Loop over the maximum distance for each trajectory to compute the deflection  
        for MAX_DISTANCE in MAX_DISTANCE_INTERVAL:
            print("MAX_DISTANCE", MAX_DISTANCE)

                    # Create the dictionary that will store the deflection
            no_encounters_deviations = {
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
                    sampling_time=  500
                )

                groups = env.get_groups(
                    days=[day],
                    size=2,
                    ped_thresholds=thresholds_ped,
                    group_thresholds=thresholds_group,
                    sampling_time=500
                )

                number_of_group_filtered = 0

                # compute deflection for all the groups
                print("number of groups:", len(groups))
                for group in tqdm(groups):

                    # get the times where the group is undisturbed
                    group_id = group.get_id()
                    soc_binding = group.get_annotation(soc_binding_type)
                    if soc_binding not in soc_binding_values:
                        soc_binding = "other"
                    if group_id not in times_undisturbed[day]["group"]:
                        continue
                    group_times_undisturbed = times_undisturbed[day]["group"][group_id]

                    # compute the deflection for each pedestrian in the group
                    for pedestrian in group.get_members():

                        # get the trajectory of the pedestrian, filter it to keep only the times where the group is in the corridor
                        pedestrian_id = pedestrian.get_id()
                        no_encounters_deviations["group"][str(pedestrian_id)] = {
                            "social_binding": soc_binding,
                            "max_dev": [],
                        }
                        trajectory = pedestrian.get_trajectory()
                        masque = np.isin(group_times_undisturbed,trajectory[:,0])
                        filter_pedestrian_times_undisturbed = group_times_undisturbed[masque]

                        # We don't want trajectory with too few observations
                        if(filter_pedestrian_times_undisturbed.shape[0] <= MIN_NUMBER_OBSERVATIONS_LOCAL):
                        #     print("not enough observations for pedestrian", filter_pedestrian_times_undisturbed.shape[0])
                        #     plt.plot(trajectory[:,1],trajectory[:,2])
                        #     plt.show()
                            continue

                        # get the trajectory of the pedestrian at the times where the group is undisturbed
                        pedestrian_undisturbed_trajectory = get_trajectory_at_times(
                            trajectory, filter_pedestrian_times_undisturbed
                        )

                        list_of_sub_trajectories = [pedestrian_undisturbed_trajectory]
                        test_sub_pedestrian = np.diff(pedestrian_undisturbed_trajectory[:,0])

                        # Separate where there is a gap in time in the trajectory
                        if(np.any(test_sub_pedestrian > 2000)):
                            list_of_sub_trajectories = compute_continuous_sub_trajectories_using_time(pedestrian_undisturbed_trajectory)
                            
                        # Debug plot to see the trajectory we don't want
                        # else :
                            # if(pedestrian_undisturbed_trajectory.shape[0] <= MIN_NUMBER_OBSERVATIONS_LOCAL):
                            #     print("not enough observations for pedestrian_2", pedestrian_undisturbed_trajectory.shape[0])
                            #     plt.scatter(trajectory[:,1],trajectory[:,2])
                            #     plt.show()
                            #     plt.scatter(pedestrian_undisturbed_trajectory[:,1],pedestrian_undisturbed_trajectory[:,2])
                            #     plt.show()
                            #     continue

                        sub_sub_trajectory = []
                        sub_length = []

                        # Separate where there is a gap in space in the trajectory, we want only continues trajectory of MAX_DISTANCE
                        for sub_trajectory in list_of_sub_trajectories:
                            result = compute_continuous_sub_trajectories_using_distance(sub_trajectory, max_distance=MAX_DISTANCE, min_length=MIN_NUMBER_OBSERVATIONS_LOCAL)
                            if (result == None):
                                continue
                            add = result[0]
                            length = result[1]
                            
                            sub_sub_trajectory += add
                            sub_length += length

                        # Compute the deflection for each sub trajectory
                        indice = 0
                        for trajectory in sub_sub_trajectory:
                            length = sub_length[indice]
                            indice += 1
                            
                            mean_speed = np.nanmean(trajectory[:,4])/1000 
                            if (mean_speed < 0.5):
                                continue
                            elif (mean_speed > 2.5):
                                continue

                            n_points_average = 4
                            max_dev_sub = compute_maximum_lateral_deviation_using_vel_2(
                            trajectory, n_points_average, interpolate=False, length = length)

                            if (max_dev_sub == None):
                                continue

                            time_of_group_traj = trajectory[-1, 0] - trajectory[0, 0]
                            max_dev_sub["mean_velocity"] = mean_speed
                            max_dev_sub["time"] = time_of_group_traj

                            no_encounters_deviations["group"][str(pedestrian_id)]["max_dev"].append(max_dev_sub)


                            if (PLOT_VERIF):
                                plot_baseline(trajectory = trajectory,max_dev = max_dev_sub,soc_binding = soc_binding,group = True, id = pedestrian_id, boundaries = env.boundaries, colors = colors,
                                              n_average = n_points_average)
                    
                    number_of_group_filtered += 1


                print("number of groups filtered:", number_of_group_filtered)
                print("number of non groups:", len(non_groups))

                number_of_non_group_filtered = 0
                # compute deflection for the non groups    
                for non_group in tqdm(non_groups):

                    non_group_id = non_group.get_id()
                    if non_group_id not in times_undisturbed[day]["non_group"]:
                        continue
                    non_group_times_undisturbed = times_undisturbed[day]["non_group"][
                        non_group_id
                    ]
                    no_encounters_deviations["non_group"][str(non_group_id)] = {
                            "max_dev":[]
                        }
                    
                    # get the trajectory of the pedestrian, filter it to keep only the times where the pedestrian is in the corridor
                    trajectory = non_group.get_trajectory()
                    masque = np.isin(non_group_times_undisturbed,trajectory[:,0])
                    filter_non_group_times_undisturbed = non_group_times_undisturbed[masque]

                    if(filter_non_group_times_undisturbed.shape[0] <= MIN_NUMBER_OBSERVATIONS_LOCAL):
                        continue

                    non_group_undisturbed_trajectory = get_trajectory_at_times(
                        trajectory,
                        filter_non_group_times_undisturbed,
                    )
                    list_of_sub_trajectories = [non_group_undisturbed_trajectory]
                    test_sub_non_group = np.diff(non_group_undisturbed_trajectory[:,0])
                    
                    # Separate where there is a gap in time in the trajectory
                    if(np.any(test_sub_non_group > 2000)):
                        list_of_sub_trajectories = compute_continuous_sub_trajectories(non_group_undisturbed_trajectory)


                    sub_sub_trajectory = []
                    sub_length = []

                    # Separate where there is a gap in space in the trajectory, we want only continues trajectory of 4000 mm
                    for sub_trajectory in list_of_sub_trajectories:
                        result = compute_continuous_sub_trajectories_using_distance(sub_trajectory, max_distance=MAX_DISTANCE, min_length=MIN_NUMBER_OBSERVATIONS_LOCAL)
                        if (result == None):
                            continue
                        add = result[0]
                        length = result[1]
                        
                        sub_sub_trajectory += add
                        sub_length += length

                    indice = 0
                    for trajectory in sub_sub_trajectory:
                        length = sub_length[indice]
                        indice += 1

                        mean_speed = np.nanmean(trajectory[:,4])/1000
                        if (mean_speed < 0.5):
                            continue
                        elif (mean_speed > 2.5):
                            continue
                        
                        n_points_average = 4
                        max_dev_sub = compute_maximum_lateral_deviation_using_vel_2(
                        trajectory, n_points_average, interpolate=False, length=length)

                        if(len(max_dev_sub)==0):
                            continue

                        time_of_non_group_traj = trajectory[-1, 0] - trajectory[0, 0]

                        max_dev_sub["mean_velocity"] = mean_speed
                        max_dev_sub["time"] = time_of_non_group_traj

                        no_encounters_deviations["non_group"][str(non_group_id)]["max_dev"].append(max_dev_sub)

                        if (PLOT_VERIF):
                            plot_baseline(trajectory, max_dev_sub, None, False, id = non_group_id)

                    number_of_non_group_filtered += 1

                print("number of non groups filtered:", number_of_non_group_filtered)

            dict_deflection["MAX_DISTANCE"][MAX_DISTANCE] = no_encounters_deviations

        
            #END OF COMPUTE DEVIATIONS
        
        if(UNDISTURBED_COMPUTE) :
            pickle_save(f"../data/pickle/undisturbed_deflection_MAX_DISTANCE.pkl", dict_deflection)
        else :
            pickle_save(f"../data/pickle/deflection_MAX_DISTANCE.pkl", dict_deflection)
