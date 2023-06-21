from copy import deepcopy
from matplotlib import patches
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
from parameters import *

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
UNDISTURBED_COMPUTE = True

# If we want to plot the mean deflection for each pedestrian for an interval of speed
SPEED_INTERVAL = True

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
            )

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
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

def plot_baseline(trajectory, max_dev, soc_binding, group, id=None):

    """ This function plots the baseline trajectory of a pedestrian.

    Parameters
    ----------
    trajectory : np.array
        The trajectory of the pedestrian.
    max_dev : dict
        A dictionary containing the maximum lateral deviation of the pedestrian.
        The dictionary has the following structure:
            - max_dev["max lateral deviation"] = max_deviation
            - max_dev["position of max lateral deviation"] = [time, x, y]  
            - max_dev["start_vel"] = [x, y]
    soc_binding : str
        The social binding of the pedestrian.
    group : bool
        True if the pedestrian is in a group, False otherwise.
    id : int
        The id of the pedestrian or the group.
    """

    point_of_max_deviation = max_dev["position of max lateral deviation"]
    start_vel = max_dev["start_vel"]
    x_start_plot = trajectory[0,1]
    y_start_plot = trajectory[0,2]
    x_end_plot = start_vel[0] * 1000 + x_start_plot
    y_end_plot = start_vel[1] * 1000 + y_start_plot

    vel_perpandicular = np.array([start_vel[1], -start_vel[0]])
    x_start_perp_plot = point_of_max_deviation[1]
    y_start_perp_plot = point_of_max_deviation[2]
    x_end_perp_plot = vel_perpandicular[0] * 1000 + x_start_perp_plot
    y_end_perp_plot = vel_perpandicular[1] * 1000 + y_start_perp_plot
    x_second_end_perp_plot = -vel_perpandicular[0] * 1000 + x_start_perp_plot
    y_second_end_perp_plot = -vel_perpandicular[1] * 1000 + y_start_perp_plot


    # plot the trajectory
    if (group):
        if(soc_binding == "other") :
            color = "pink"
        else:
            color = colors[soc_binding]
    else:
        color = "blue"
    boundaries = env.boundaries
    fig = plt.figure(figsize=(15, 10))
    plt.xlim([boundaries["xmin"] / 1000, boundaries["xmax"] / 1000])
    plt.ylim([boundaries["ymin"] / 1000, boundaries["ymax"] / 1000])
    plt.scatter(trajectory[:,1] / 1000,trajectory[:,2] / 1000, s=10, c=color)
    plt.scatter(point_of_max_deviation[1] / 1000, point_of_max_deviation[2] / 1000, s=10, c="black")
    plt.plot([x_start_plot / 1000, x_end_plot / 1000], [y_start_plot / 1000, y_end_plot / 1000], c="purple", label="velocity")
    plt.xlabel('X Coord', fontsize=12, fontweight='bold')
    plt.ylabel('Y Coord', fontsize=12, fontweight='bold')
    if(group):
        plt.title('Plot of the baseline for group ' + str(id))
    else:
        plt.title('Plot of the baseline for non group pedestrian ' + str(id))
    plt.plot([x_end_perp_plot / 1000, x_second_end_perp_plot / 1000], [y_end_perp_plot / 1000, y_second_end_perp_plot/1000]
                , c="green", label="perpendicular of the vector of velocity")
    plt.legend()
    plt.show()


  

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

        # Create the dictionary that will store the deflection
        no_encounters_deviations = {
            "group": {},
            "non_group": {},
        }

        # Loop over the maximum distance for each trajectory to compute the deflection  
        for MAX_DISTANCE in [1500,2500,3000,4000,5000,6000]:
            print("MAX_DISTANCE", MAX_DISTANCE)

            # Loop over the days
            for day in days:
                print(f"Day {day}:")

                non_groups = env.get_pedestrians(
                    days=[day],
                    no_groups=True,
                    thresholds=thresholds_ped,
                    sampling_time=500,
                )

                groups = env.get_groups(
                    days=[day],
                    size=2,
                    ped_thresholds=thresholds_ped,
                    group_thresholds=thresholds_group,
                    sampling_time=500,
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

                            n_points_average = 4
                            max_dev_sub = compute_maximum_lateral_deviation_using_vel_2(
                            trajectory, n_points_average, interpolate=False, length = length)

                            no_encounters_deviations["group"][str(pedestrian_id)]["max_dev"].append(max_dev_sub)

                            if (PLOT_VERIF):
                                plot_baseline(trajectory, max_dev_sub, soc_binding, True, id = pedestrian_id)
                    
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

                        n_points_average = 4
                        max_dev_sub = compute_maximum_lateral_deviation_using_vel_2(
                        trajectory, n_points_average, interpolate=False, length=length)

                        # if(np.all(np.isnan(max_dev_sub["max_lateral_deviation"])) ):
                        #     continue

                        if(len(max_dev_sub)==0):
                            continue

                        no_encounters_deviations["non_group"][str(non_group_id)]["max_dev"].append(max_dev_sub)

                        if (PLOT_VERIF):
                            plot_baseline(trajectory, max_dev_sub, None, False, id = non_group_id)

                    number_of_non_group_filtered += 1

                print("number of non groups filtered:", number_of_non_group_filtered)



            #END OF COMPUTE DEVIATIONS
            #START OF PLOT DEVIATIONS



            #Compute the mean max_deviation / mean_velocity / mean_length of the trajectory for all pedestrians

            list_global_mean_max_dev_group = [[] for i in range(5)]
            list_global_mean_length_pedestrian = [[] for i in range(6)]

            for group_id in no_encounters_deviations["group"]:
                no_encounters_deviations["group"][group_id]["mean_max_dev"] = -1
                no_encounters_deviations["group"][group_id]["mean_velocity"] = None
                no_encounters_deviations["group"][group_id]["mean_length"] = -1
                mean_max_dev_group = 0
                mean_velocity_group = 0
                mean_length_group = 0
                max_dev = no_encounters_deviations["group"][group_id]["max_dev"]
                # print("max_dev", max_dev)
                if len(max_dev) == 0:
                    continue
                k = 0
                j = 0
                l = 0
                for i in range(len(max_dev)):
                    intermediate = max_dev[i]["max_lateral_deviation"]
                    if(intermediate > MAX_DISTANCE):
                        continue
                    else :
                        mean_max_dev_group += intermediate
                        j += 1
                        mean_velocity_group += max_dev[i]["start_vel"]
                        k += 1
                        mean_length_group += max_dev[i]["length_of_trajectory"]
                        l += 1

                if(k != 0):
                    mean_velocity_group = mean_velocity_group/k
                if(j != 0):
                    mean_max_dev_group = mean_max_dev_group/j
                if(l != 0):
                    mean_length_group = mean_length_group/l

                if (mean_max_dev_group > 800):
                    mean_max_dev_group = -1

                
                no_encounters_deviations["group"][group_id]["mean_max_dev"] = mean_max_dev_group
                no_encounters_deviations["group"][group_id]["mean_velocity"] = mean_velocity_group
                no_encounters_deviations["group"][group_id]["mean_length"] = mean_length_group

                social_binding = no_encounters_deviations["group"][group_id]["social_binding"]
                if(social_binding == "other"):
                    social_binding = 4
                
                # the goal of these list_global is to compute the mean max_deviation / legnth of the trajectory for each social binding
                # TODO: Maybe do the same for speed
                if (mean_max_dev_group != -1) :
                    list_global_mean_max_dev_group[social_binding].append(mean_max_dev_group)
                    list_global_mean_length_pedestrian[social_binding].append(mean_length_group)

            #Compute the mean max_deviation for all non groups
            # The same process but for non_groups
            list_mean_max_dev_non_group = []
            for non_group_id in no_encounters_deviations["non_group"]:
                no_encounters_deviations["non_group"][non_group_id]["mean_max_dev"] = -1
                no_encounters_deviations["non_group"][non_group_id]["mean_velocity"] = None
                no_encounters_deviations["non_group"][non_group_id]["mean_length"] = -1
                mean_max_dev_non_group = 0
                mean_velocity_non_group = 0
                mean_length_non_group = 0
                max_dev = no_encounters_deviations["non_group"][non_group_id]["max_dev"]
            
                if len(max_dev) == 0:
                    continue
                j = 0
                k = 0
                l = 0
                for i in range(len(max_dev)):
                    intermediate = max_dev[i]["max_lateral_deviation"]
                    if(intermediate > MAX_DISTANCE):
                        continue
                    else:
                        mean_max_dev_non_group += intermediate
                        j += 1
                        mean_velocity_non_group += max_dev[i]["start_vel"]
                        k += 1
                        mean_length_non_group += max_dev[i]["length_of_trajectory"]
                        l += 1

                if(k != 0):
                    mean_velocity_non_group = mean_velocity_non_group/k
                if(j != 0):
                    mean_max_dev_non_group = mean_max_dev_non_group/j
                if(l != 0):
                    mean_length_non_group = mean_length_non_group/l
                if (mean_max_dev_non_group > 800) :
                    mean_max_dev_non_group = -1
                
                no_encounters_deviations["non_group"][non_group_id]["mean_max_dev"] = mean_max_dev_non_group
                no_encounters_deviations["non_group"][non_group_id]["mean_velocity"] = mean_velocity_non_group
                no_encounters_deviations["non_group"][non_group_id]["mean_length"] = mean_length_non_group

                if (mean_max_dev_non_group != -1) :
                    list_mean_max_dev_non_group.append(mean_max_dev_non_group)
                    list_global_mean_length_pedestrian[5].append(mean_length_non_group)

            #Compute the mean max_deviation for all pedestrians
            flatten_list = [value for sublist in list_global_mean_max_dev_group for value in sublist]
            average = sum(flatten_list) / len(flatten_list)

            total_mean_length_pedestrian = np.around(average,0)

            #Plot the mean max_deviation for all pedestrians
            if (PLOT_MEAN_MAX_DEV):
                for group_id in no_encounters_deviations["group"]:
                    mean_max_dev_group = no_encounters_deviations["group"][group_id]["mean_max_dev"]
                    if(mean_max_dev_group == -1):
                        continue
                    if (np.all(np.isnan(mean_max_dev_group))):
                        continue
                    social_binding = no_encounters_deviations["group"][group_id]["social_binding"]
                    velocity = no_encounters_deviations["group"][group_id]["mean_velocity"]
                    global_velocity = np.sqrt(velocity[0]**2 + velocity[1]**2)
                    if(social_binding == "other") :
                        color = "black"
                    else :
                        color = colors[social_binding]
                    plt.scatter(global_velocity / 1000,mean_max_dev_group, c = color, marker = "o", label = "Group", s=30, alpha=0.8)
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
                    global_velocity = np.sqrt(velocity[0]**2 + velocity[1]**2)

                    plt.scatter(global_velocity/1000,mean_max_dev_non_group, c = "purple", label = "Non group", s=30, alpha = 0.8)
                # # plt.xlabel("Non group ID")
                # plt.ylabel("Mean max deviation (mm)")
                # plt.title("Mean max deviation for all non groups")
                if (UNDISTURBED_COMPUTE) :
                    plt.savefig("../data/figures/deflection/will/scatter/undisturbed_trajectories/mean_max_deviation_for_all_pedestrians_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory, MAX_DISTANCE/1000))
                else :
                    plt.savefig("../data/figures/deflection/will/scatter/all_trajectories/mean_max_deviation_for_all_pedestrians_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory, MAX_DISTANCE/1000))

                plt.close()

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
            ax.set_title(f"boxplot of mean max deviation for social binding for trip of {total_mean_length_pedestrian} meters")

            plt.ylabel("Mean max deviation (mm)")
            plt.xlabel("Social binding / Number of pedestrians")
                
            if (UNDISTURBED_COMPUTE) :
                plt.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/boxplot_mean_max_deviation_for_all_pedestrians_with_{0}_trip_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000))
            else :
                plt.savefig("../data/figures/deflection/will/boxplot/all_trajectories/boxplot_mean_max_deviation_for_all_pedestrians_with_{0}_trip_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000))
            plt.close()

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
            ax.set_title(f"boxplot of mean max deviation for social binding for trip of {total_mean_length_pedestrian} meters")

            plt.ylabel("Mean max deviation (mm)")
            plt.xlabel("Social binding / Number of pedestrians")

            if (UNDISTURBED_COMPUTE) :
                plt.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000))
            else :
                plt.savefig("../data/figures/deflection/will/boxplot/all_trajectories/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000))

            plt.close()

            if(SPEED_INTERVAL and MAX_DISTANCE == 1500) :
                speed_interval = [(0,0.5),(0.5,0.75),(0.75,1),(1,1.25),(1.25,1.5),(1.5,2),(2,2.5)]
                dict_speed_interval = {}
                for i in range(len(speed_interval)) :
                    dict_speed_interval[speed_interval[i]] = {"0" : [], "1" : [], "2" : [], "3" : [], "other" : [], "alone" : []}

                for group_id in no_encounters_deviations["group"] :
                    velocity = no_encounters_deviations["group"][group_id]["mean_velocity"]
                    social_binding = no_encounters_deviations["group"][group_id]["social_binding"]
                    if velocity is None:
                        continue
                    global_velocity = np.sqrt(velocity[0]**2 + velocity[1]**2)/1000
                    for i in range(len(speed_interval)) :
                        if (global_velocity >= speed_interval[i][0] and global_velocity < speed_interval[i][1]) :
                            dict_speed_interval[speed_interval[i]][str(social_binding)].append(no_encounters_deviations["group"][group_id]["mean_max_dev"])
                            break
                
                for group_id in no_encounters_deviations["non_group"] :
                    velocity = no_encounters_deviations["non_group"][group_id]["mean_velocity"]
                    if velocity is None:
                        continue
                    global_velocity = np.sqrt(velocity[0]**2 + velocity[1]**2)/1000
                    for i in range(len(speed_interval)) :
                        if (global_velocity >= speed_interval[i][0] and global_velocity < speed_interval[i][1]) :
                            dict_speed_interval[speed_interval[i]]["alone"].append(no_encounters_deviations["non_group"][group_id]["mean_max_dev"])
                            break

            

                fig2, ax2 = plt.subplots()
                mean_max_dev_per_velocity = []
                list_of_average = []
                indice = 0
                for elt in speed_interval :
                    print("speed interval", elt)
                    elt_elt = dict_speed_interval[elt]
                    mean_max_dev_per_velocity += elt_elt["0"], elt_elt["1"], elt_elt["2"], elt_elt["3"], elt_elt["other"], elt_elt["alone"]
                    flatten_list = [value for sublist in mean_max_dev_per_velocity for value in sublist]
                    average = sum(flatten_list) / len(flatten_list)
                    list_of_average.append(average)
                    print("mean for a speed interval", average)
                    fig, ax = plt.subplots()
                    label = ["0", "1", "2", "3", "other", "alone"]
                    for i in range(len(label)) :
                        label[i] = label[i] + " / " + str(len(elt_elt[label[i]]))
                    boxplot = ax.boxplot([elt_elt["0"], elt_elt["1"], elt_elt["2"], elt_elt["3"], elt_elt["other"], elt_elt["alone"]], labels = label,
                                         showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                                            , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)

                    ax.set_title(f"boxplot of mean max deviation for social binding for trip of {total_mean_length_pedestrian} meters and speed interval of {elt} m/s")  
                    ax.set_xlabel("Social binding / Number of pedestrians")
                    ax.set_ylabel("Mean max deviation (mm)")  

                    if (UNDISTURBED_COMPUTE) :
                        fig.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/speed/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval_of_{2}_m_s.png".format(str_trajectory,MAX_DISTANCE/1000,elt))                
                    else :
                        fig.savefig("../data/figures/deflection/will/boxplot/all_trajectories/speed/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval_of_{2}_m_s.png".format(str_trajectory,MAX_DISTANCE/1000,elt))

                    plt.close()

                print("list of average", list_of_average)
                print("speed interval", speed_interval)
                str_speed_interval = []
                for elt in speed_interval :
                    str_speed_interval.append(str(elt))
                ax2.plot(str_speed_interval, list_of_average)
                ax2.set_title(f"mean max deviation for social binding for trip of {total_mean_length_pedestrian} meters and speed interval of {elt} m/s")
                ax2.set_xlabel("Speed interval (m/s)")
                ax2.set_ylabel("Mean max deviation (mm)")

                if (UNDISTURBED_COMPUTE) :
                    fig2.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/speed/mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval.png".format(str_trajectory,MAX_DISTANCE/1000))
                else :
                    fig2.savefig("../data/figures/deflection/will/boxplot/all_trajectories/speed/mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval.png".format(str_trajectory,MAX_DISTANCE/1000))

                plt.close()
