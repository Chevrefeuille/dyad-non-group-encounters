from copy import deepcopy
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

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
                if soc_binding != 3 :
                    continue
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

                    cs = CubicSpline(pedestrian_undisturbed_trajectory[:, 0], pedestrian_undisturbed_trajectory[:, 1:3])
                    xs = np.linspace(pedestrian_undisturbed_trajectory[0, 0], pedestrian_undisturbed_trajectory[-1, 0], 100)
                    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
                    ax.set_aspect("equal", "box")
                    ax.plot(pedestrian_undisturbed_trajectory[:, 1], pedestrian_undisturbed_trajectory[:, 2], 'o', label='data')
                    ax.plot(cs(xs)[:, 0], cs(xs)[:, 1], label="S")

                    ax.legend(loc='lower left', ncol=2)
                    plt.show()



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

        
            #END OF COMPUTE DEVIATIONS
        
        pickle_save(f"../data/pickle/undisturbed_curvature_MAX_DISTANCE_2.pkl", dict_curvature)

