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

            dict_deflection["MAX_DISTANCE"][MAX_DISTANCE] = no_encounters_deviations

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


            pickle_save(f"../data/pickle/{env_name_short}no_encounters_deviations.pkl", no_encounters_deviations)
            #END OF COMPUTE DEVIATIONS
            #START OF PLOT DEVIATIONS



            #Compute the mean max_deviation / mean_velocity / mean_length of the trajectory for all pedestrians

            list_global_mean_max_dev_group = [[] for i in range(5)]
            list_global_mean_length_pedestrian = [[] for i in range(6)]
            list_global_mean_velocity_pedestrian = [[] for i in range(6)]
            list_global_mean_time_pedestrian = [[] for i in range(6)]


            for group_id in no_encounters_deviations["group"]:
                no_encounters_deviations["group"][group_id]["mean_max_dev"] = -1
                no_encounters_deviations["group"][group_id]["mean_velocity"] = None
                no_encounters_deviations["group"][group_id]["mean_length"] = -1
                no_encounters_deviations["group"][group_id]["mean_time"] = -1
                mean_max_dev_group = 0
                mean_velocity_group = 0
                mean_length_group = 0
                mean_time_group = 0
                max_dev = no_encounters_deviations["group"][group_id]["max_dev"]
                # print("max_dev", max_dev)
                if len(max_dev) == 0:
                    continue
                k = 0

                for i in range(len(max_dev)):
                    intermediate = max_dev[i]["max_lateral_deviation"]
                    if(intermediate > MAX_DISTANCE):
                        continue
                    else :
                        k += 1
                        mean_max_dev_group += intermediate
                        mean_velocity_group += max_dev[i]["mean_velocity"]
                        
                        mean_length_group += max_dev[i]["length_of_trajectory"]
                        mean_time_group += max_dev[i]["time"]


                if(k != 0):
                    mean_velocity_group = mean_velocity_group/k
                    mean_max_dev_group = mean_max_dev_group/k
                    mean_length_group = mean_length_group/k
                    mean_time_group = mean_time_group/k

                if (mean_max_dev_group > 800):
                    mean_max_dev_group = -1

                
                no_encounters_deviations["group"][group_id]["mean_max_dev"] = mean_max_dev_group
                no_encounters_deviations["group"][group_id]["mean_velocity"] = mean_velocity_group
                no_encounters_deviations["group"][group_id]["mean_length"] = mean_length_group
                no_encounters_deviations["group"][group_id]["mean_time"] = mean_time_group

                social_binding = no_encounters_deviations["group"][group_id]["social_binding"]
                if(social_binding == "other"):
                    social_binding = 4
                
                # the goal of these list_global is to compute the mean max_deviation / legnth of the trajectory for each social binding
                if (mean_max_dev_group != -1) :
                    list_global_mean_max_dev_group[social_binding].append(mean_max_dev_group)
                    list_global_mean_length_pedestrian[social_binding].append(mean_length_group)
                    list_global_mean_velocity_pedestrian[social_binding].append(mean_velocity_group)
                    list_global_mean_time_pedestrian[social_binding].append(mean_time_group)

            #Compute the mean max_deviation for all non groups
            # The same process but for non_groups
            list_mean_max_dev_non_group = []
            for non_group_id in no_encounters_deviations["non_group"]:
                no_encounters_deviations["non_group"][non_group_id]["mean_max_dev"] = -1
                no_encounters_deviations["non_group"][non_group_id]["mean_velocity"] = None
                no_encounters_deviations["non_group"][non_group_id]["mean_length"] = -1
                no_encounters_deviations["non_group"][non_group_id]["mean_time"] = -1
                mean_max_dev_non_group = 0
                mean_velocity_non_group = 0
                mean_length_non_group = 0
                mean_time_non_group = 0
                max_dev = no_encounters_deviations["non_group"][non_group_id]["max_dev"]
            
                if len(max_dev) == 0:
                    continue
                k = 0
                for i in range(len(max_dev)):
                    intermediate = max_dev[i]["max_lateral_deviation"]
                    if(intermediate > MAX_DISTANCE):
                        continue
                    else:
                        k += 1
                        mean_max_dev_non_group += intermediate
                        mean_velocity_non_group += max_dev[i]["mean_velocity"]

                        mean_length_non_group += max_dev[i]["length_of_trajectory"]
                        mean_time_non_group += max_dev[i]["time"]

                if(k != 0):
                    mean_velocity_non_group = mean_velocity_non_group/k
                    mean_max_dev_non_group = mean_max_dev_non_group/k
                    mean_length_non_group = mean_length_non_group/k
                    mean_time_non_group = mean_time_non_group/k
                
                no_encounters_deviations["non_group"][non_group_id]["mean_max_dev"] = mean_max_dev_non_group
                no_encounters_deviations["non_group"][non_group_id]["mean_velocity"] = mean_velocity_non_group
                no_encounters_deviations["non_group"][non_group_id]["mean_length"] = mean_length_non_group
                no_encounters_deviations["non_group"][non_group_id]["mean_time"] = mean_time_non_group

                if (mean_max_dev_non_group != -1) :
                    list_mean_max_dev_non_group.append(mean_max_dev_non_group)
                    list_global_mean_length_pedestrian[5].append(mean_length_non_group)
                    list_global_mean_velocity_pedestrian[5].append(mean_velocity_non_group)
                    list_global_mean_time_pedestrian[5].append(mean_time_non_group)

            #Compute the mean max_deviation for all pedestrians
            flatten_list = [value for sublist in list_global_mean_length_pedestrian for value in sublist]
            if (len(flatten_list) == 0):
                print("error flatten list", flatten_list)
                print("error list_global_mean_length", list_global_mean_length_pedestrian)

            average = sum(flatten_list) / len(flatten_list)
            total_mean_length_pedestrian = np.around(average,decimals=4)/1000

            flatten_list_time = [value for sublist in list_global_mean_time_pedestrian for value in sublist]
            average_time = sum(flatten_list_time) / len(flatten_list_time)
            total_mean_time_pedestrian = np.around(average_time,decimals=4)/1000

            #Scatter the mean max_deviation for all pedestrians
            if (PLOT_MEAN_MAX_DEV):
                for group_id in no_encounters_deviations["group"]:
                    mean_max_dev_group = no_encounters_deviations["group"][group_id]["mean_max_dev"]
                    if(mean_max_dev_group == -1):
                        continue
                    if (np.all(np.isnan(mean_max_dev_group))):
                        continue
                    social_binding = no_encounters_deviations["group"][group_id]["social_binding"]
                    velocity = no_encounters_deviations["group"][group_id]["mean_velocity"]
                    if(social_binding == "other") :
                        color = "black"
                    else :
                        color = colors[social_binding]
                    plt.scatter(velocity,mean_max_dev_group, c = color, marker = "o", label = "Group", s=30, alpha=0.8)
                plt.xlabel("Mean velocity")
                plt.ylabel("Mean max deviation (mm)")
                plt.title("Mean max deviation for each pedestrians with {0}_trajectory of {1} meters".format(str_trajectory,total_mean_length_pedestrian))
                plt.legend(
                    handles=[
                        patches.Patch(color=colors[0], label="interaction 0"),
                        patches.Patch(color=colors[1], label="1"),
                        patches.Patch(color=colors[2], label="2"),
                        patches.Patch(color=colors[3], label="3"),
                        patches.Patch(color="black", label="other (non classified)"),
                        patches.Patch(color="purple", label="Non group pedestrian"),
                    ]
                )
                for non_group_id in no_encounters_deviations["non_group"]:
                    mean_max_dev_non_group = no_encounters_deviations["non_group"][non_group_id]["mean_max_dev"]
                    velocity = no_encounters_deviations["non_group"][non_group_id]["mean_velocity"]
                    if(mean_max_dev_non_group == -1):
                        continue
                    if (np.all(np.isnan(mean_max_dev_non_group))):
                        continue

                    plt.scatter(velocity,mean_max_dev_non_group, c = "purple", label = "Non group", s=30, alpha = 0.8)
                # # plt.xlabel("Non group ID")
                # plt.ylabel("Mean max deviation (mm)")
                # plt.title("Mean max deviation for all non groups")
                if (UNDISTURBED_COMPUTE) :
                    plt.savefig("../data/figures/deflection/will/scatter/undisturbed_trajectories/mean_max_deviation_for_all_pedestrians_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory, MAX_DISTANCE/1000))
                else :
                    plt.savefig("../data/figures/deflection/will/scatter/all_trajectories/mean_max_deviation_for_all_pedestrians_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory, MAX_DISTANCE/1000))

                plt.close()


            # Plot the boxplot of the mean max_deviation for each social binding
            data = [list_global_mean_max_dev_group[0], list_global_mean_max_dev_group[1], list_global_mean_max_dev_group[2], list_global_mean_max_dev_group[3], list_global_mean_max_dev_group[4], list_mean_max_dev_non_group]
            num_data = [len(d) for d in data]

            list_of_social_binding = ["0", "1", "2", "3", "other", "alone"]
            for i in range(6) :
                list_of_social_binding[i] = list_of_social_binding[i] + " / " + str(num_data[i])
            
            fig, ax = plt.subplots()

            boxplot = ax.boxplot(data, labels = list_of_social_binding
                     ,showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                       , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                       boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            ax.set_title(f"boxplot of mean max deviation, trip of {total_mean_length_pedestrian} meters | {total_mean_time_pedestrian} seconds")

            plt.ylabel("Mean max deviation (mm)")
            plt.xlabel("Social binding / Number of pedestrians")
                
            if (UNDISTURBED_COMPUTE) :
                plt.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/boxplot_mean_max_deviation_for_all_pedestrians_with_{0}_trip_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000))
            else :
                plt.savefig("../data/figures/deflection/will/boxplot/all_trajectories/boxplot_mean_max_deviation_for_all_pedestrians_with_{0}_trip_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000))
            plt.close()

            # Do the ANOVA thing
            if(ANOVA):
                name_of_the_file = ""
                if (UNDISTURBED_COMPUTE) :
                    name_of_the_file = "../data/report_text/deflection/will/undisturbed_trajectories/ANOVA_for_mean_max_deviation_undisturbed.txt"
                else :
                    name_of_the_file = "../data/report_text/deflection/will/all_trajectories/ANOVA_for_mean_max_deviation.txt"
                if not os.path.exists(name_of_the_file):
                    with open(name_of_the_file, "a") as f :
                        f.write("-----------------------------------------------------------\n")
                        result = f_oneway(*data)
                        f.write("ANOVA for mean max deviation for {0} trajectory of {1} meters\n".format(str_trajectory, MAX_DISTANCE/1000))
                        f.write("F-value : {0}\n".format(result[0]))
                        f.write("p-value : {0}\n".format(result[1]))
                        f.write("-----------------------------------------------------------\n")


            # This one is for group/non group only
            new_data = []
            intermediate_data = []
            for i in range(len(data) - 1) :
                intermediate_data += data[i]

            new_data.append(intermediate_data)
            new_data.append(data[5])

            new_label = ["group", "alone"]
            for i in range(2) :
                new_label[i] = new_label[i] + " / " + str(len(new_data[i]))

            fig, ax = plt.subplots()
            boxplot = ax.boxplot(new_data, labels = new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                          , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            ax.set_title(f"boxplot of mean max deviation, trip of {total_mean_length_pedestrian} meters | {total_mean_time_pedestrian} seconds")

            plt.ylabel("Mean max deviation (mm)")
            plt.xlabel("Social binding / Number of pedestrians")

            if (UNDISTURBED_COMPUTE) :
                plt.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000))
            else :
                plt.savefig("../data/figures/deflection/will/boxplot/all_trajectories/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000))

            plt.close()

            if(SPEED_INTERVAL) :
                # Create a dictionnary with the speed interval as key and the mean max deviation for each social binding
                speed_interval = [(0.5,0.75),(0.75,1),(1,1.25),(1.25,1.5),(1.5,2),(2,2.5)]
                dict_speed_interval = {}
                for i in range(len(speed_interval)) :
                    dict_speed_interval[speed_interval[i]] = {"0" : [], "1" : [], "2" : [], "3" : [], "other" : [], "alone" : []}

                for group_id in no_encounters_deviations["group"] :
                    velocity = no_encounters_deviations["group"][group_id]["mean_velocity"]
                    social_binding = no_encounters_deviations["group"][group_id]["social_binding"]
                    if velocity is None:
                        continue
                    for i in range(len(speed_interval)) :
                        if (velocity >= speed_interval[i][0] and velocity < speed_interval[i][1]) :
                            dict_speed_interval[speed_interval[i]][str(social_binding)].append(no_encounters_deviations["group"][group_id]["mean_max_dev"])
                            break
                
                for group_id in no_encounters_deviations["non_group"] :
                    velocity = no_encounters_deviations["non_group"][group_id]["mean_velocity"]
                    if velocity is None:
                        continue
                    for i in range(len(speed_interval)) :
                        if (velocity >= speed_interval[i][0] and velocity < speed_interval[i][1]) :
                            dict_speed_interval[speed_interval[i]]["alone"].append(no_encounters_deviations["non_group"][group_id]["mean_max_dev"])
                            break

            
                mean_max_dev_per_velocity = []
                list_of_average = []
                indice = 0
                for elt in speed_interval :
                    elt_elt = dict_speed_interval[elt]
                    mean_max_dev_per_velocity += elt_elt["0"], elt_elt["1"], elt_elt["2"], elt_elt["3"], elt_elt["other"], elt_elt["alone"]
                    flatten_list = [value for sublist in mean_max_dev_per_velocity for value in sublist]
                    if (len(flatten_list) == 0) :
                        list_of_average.append(None)
                        continue
                    average = sum(flatten_list) / len(flatten_list)
                    list_of_average.append(average)

                    if (MAX_DISTANCE == 1500):
                        fig, ax = plt.subplots()
                        label = ["0", "1", "2", "3", "other", "alone"]
                        for i in range(len(label)) :
                            label[i] = label[i] + " / " + str(len(elt_elt[label[i]]))
                        boxplot = ax.boxplot([elt_elt["0"], elt_elt["1"], elt_elt["2"], elt_elt["3"], elt_elt["other"], elt_elt["alone"]], labels = label,
                                            showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                                                , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)

                        ax.set_title(f"mean max deviation, trip of {total_mean_length_pedestrian} meters, speed interval of {elt} m/s")  
                        ax.set_xlabel("Social binding / Number of pedestrians")
                        ax.set_ylabel("Mean max deviation (mm)")  

                        if (UNDISTURBED_COMPUTE) :
                            fig.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/speed/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval_of_{2}_m_s.png".format(str_trajectory,MAX_DISTANCE/1000,elt))                
                        else :
                            fig.savefig("../data/figures/deflection/will/boxplot/all_trajectories/speed/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval_of_{2}_m_s.png".format(str_trajectory,MAX_DISTANCE/1000,elt))

                        plt.close()

                fig2, ax2 = plt.subplots()
                print("list of average", list_of_average)
                print("speed interval", speed_interval)
                str_speed_interval = []
                for elt in speed_interval :
                    str_speed_interval.append(str(elt))
                ax2.plot(str_speed_interval, list_of_average)
                ax2.set_title(f"mean max deviation, trip of {total_mean_length_pedestrian} meters")
                ax2.set_xlabel("Speed interval (m/s)")
                ax2.set_ylabel("Mean max deviation (mm)")

                if (UNDISTURBED_COMPUTE) :
                    fig2.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/speed/mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval.png".format(str_trajectory,MAX_DISTANCE/1000))
                else :
                    fig2.savefig("../data/figures/deflection/will/boxplot/all_trajectories/speed/mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval.png".format(str_trajectory,MAX_DISTANCE/1000))

                plt.close()
        
        if(UNDISTURBED_COMPUTE) :
            pickle_save(f"../data/pickle/undisturbed_deflection_MAX_DISTANCE.plk", dict_deflection)
        else :
            pickle_save(f"../data/pickle/deflection_MAX_DISTANCE.plk", dict_deflection)
