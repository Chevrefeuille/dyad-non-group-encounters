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
The deflection is the angle between the direction of the pedestrian and the direction of the group. The deflection for non_group_id is
the angle between the direction of the pedestrian and the direction of the same pedestrian at a next time step.
The data will be stored in a dictionary in the file data/deflection/deflection_{env_name}.pkl .
The dictionary will have the following structure:
    - deflection[day][group_id] = [deflection_1, deflection_2, ...]
    - deflection[day][group_members_id] = [deflection_1, deflection_2, ...]
    - deflection[day][non_group_id] = [deflection_1, deflection_2, ...]
    """

MIN_NUMBER_OBSERVATIONS_LOCAL = 5
MAX_DISTANCE = 4000
PLOT_VERIF = False
PLOT_MEAN_MAX_DEV = True

def plot_baseline(trajectory, max_dev, soc_binding, group, id=None):
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



    ## plot the trajectory
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
        plot_verif = True
        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )
        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        # Load the data of undisurbed times of groups and non groups
        times_undisturbed = pickle_load(
            f"../data/pickle/undisturbed_times_{env_name_short}.pkl"
        )

        # Create the dictionary that will store the deflection
        # TODO: change the structure of the dictionary
        no_encounters_deviations = {
            "group": {},
            "non_group": {},
        }

        for MAX_DISTANCE in [2000,3000,4000,5000,6000]:
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

                        if(filter_pedestrian_times_undisturbed.shape[0] <= MIN_NUMBER_OBSERVATIONS_LOCAL):
                        #     print("not enough observations for pedestrian", filter_pedestrian_times_undisturbed.shape[0])
                        #     plt.plot(trajectory[:,1],trajectory[:,2])
                        #     plt.show()
                            continue

                        pedestrian_undisturbed_trajectory = get_trajectory_at_times(
                            trajectory, filter_pedestrian_times_undisturbed
                        )
                        list_of_sub_trajectories = [pedestrian_undisturbed_trajectory]
                        test_sub_pedestrian = np.diff(pedestrian_undisturbed_trajectory[:,0])

                        # Separate where there is a gap in time in the trajectory
                        if(np.any(test_sub_pedestrian > 2000)):
                            list_of_sub_trajectories = compute_continuous_sub_trajectories_using_time(pedestrian_undisturbed_trajectory)
                            
                        else :
                            # if(pedestrian_undisturbed_trajectory.shape[0] <= MIN_NUMBER_OBSERVATIONS_LOCAL):
                            #     print("not enough observations for pedestrian_2", pedestrian_undisturbed_trajectory.shape[0])
                            #     plt.scatter(trajectory[:,1],trajectory[:,2])
                            #     plt.show()
                            #     plt.scatter(pedestrian_undisturbed_trajectory[:,1],pedestrian_undisturbed_trajectory[:,2])
                            #     plt.show()
                            #     continue

                            sub_sub_trajectory = []

                            # Separate where there is a gap in space in the trajectory, we want only continues trajectory of 4000 mm
                            for sub_trajectory in list_of_sub_trajectories:
                                add = compute_continuous_sub_trajectories_using_distance(sub_trajectory, max_distance=MAX_DISTANCE, min_length=MIN_NUMBER_OBSERVATIONS_LOCAL)
                                if (add == None):
                                    continue
                                sub_sub_trajectory += add

                            # Compute the deflection for each sub trajectory
                            for trajectory in sub_sub_trajectory:

                                n_points_average = 4
                                max_dev_sub = compute_maximum_lateral_deviation_using_vel_2(
                                trajectory, n_points_average, interpolate=False)

                                # if(np.all(np.isnan(max_dev_sub["max_lateral_deviation"])) ):
                                #     continue

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
                    test_sub_non_group = np.diff(non_group_undisturbed_trajectory[:,0])
                    
                    # Separate where there is a gap in time in the trajectory
                    if(np.any(test_sub_non_group > 2000)):

                        list_of_sub_trajectories = compute_continuous_sub_trajectories(non_group_undisturbed_trajectory)

                    else :
                        if(non_group_undisturbed_trajectory.shape[0] <= MIN_NUMBER_OBSERVATIONS_LOCAL):
                            continue

                        # if (np.all(non_group_undisturbed_trajectory)):
                        #     continue

                        sub_sub_trajectory = []

                        # Separate where there is a gap in space in the trajectory, we want only continues trajectory of 4000 mm
                        for sub_trajectory in list_of_sub_trajectories:
                            add = compute_continuous_sub_trajectories_using_distance(sub_trajectory, max_distance=MAX_DISTANCE, min_length=MIN_NUMBER_OBSERVATIONS_LOCAL)
                            if (add == None):
                                continue
                            sub_sub_trajectory += add

                        for trajectory in sub_sub_trajectory:

                            n_points_average = 4
                            max_dev_sub = compute_maximum_lateral_deviation_using_vel_2(
                            trajectory, n_points_average, interpolate=False)

                            # if(np.all(np.isnan(max_dev_sub["max_lateral_deviation"])) ):
                            #     continue

                            if(len(max_dev_sub)==0):
                                continue

                            no_encounters_deviations["non_group"][str(non_group_id)]["max_dev"].append(max_dev_sub)

                            if (PLOT_VERIF):
                                plot_baseline(trajectory, max_dev_sub, None, False, id = non_group_id)

                    number_of_non_group_filtered += 1

                print("number of non groups filtered:", number_of_non_group_filtered)

            #Compute the mean max_deviation for all pedestrians
            list_global_mean_max_dev_group = [0,0,0,0,0]
            l = 0
            for group_id in no_encounters_deviations["group"]:
                no_encounters_deviations["group"][group_id]["mean_max_dev"] = -1
                no_encounters_deviations["group"][group_id]["mean_velocity"] = -1
                mean_max_dev_group = 0
                mean_velocity_group = 0
                max_dev = no_encounters_deviations["group"][group_id]["max_dev"]
                # print("max_dev", max_dev)
                if len(max_dev) == 0:
                    continue
                k = 0
                j = 0
                for i in range(len(max_dev)):
                    intermediate = max_dev[i]["max_lateral_deviation"]
                    if(intermediate > MAX_DISTANCE):
                        continue
                    else :
                        mean_max_dev_group += intermediate
                        j += 1
                        mean_velocity_group += max_dev[i]["start_vel"]
                        k += 1

                if(k != 0):
                    mean_velocity_group = mean_velocity_group/k
                if(j != 0):
                    mean_max_dev_group = mean_max_dev_group/j
                no_encounters_deviations["group"][group_id]["mean_max_dev"] = mean_max_dev_group
                no_encounters_deviations["group"][group_id]["mean_velocity"] = mean_velocity_group


                list_global_mean_max_dev_group[social_binding] += mean_max_dev_non_group
                l += 1
            for i in range(len(list_global_mean_max_dev_group)):
                list_global_mean_max_dev_group[i] = list_global_mean_max_dev_group[i]/l

            #Compute the mean max_deviation for all non groups
            global_mean_max_dev_non_group = 0
            l = 0
            for non_group_id in no_encounters_deviations["non_group"]:
                no_encounters_deviations["non_group"][non_group_id]["mean_max_dev"] = -1
                no_encounters_deviations["non_group"][non_group_id]["mean_velocity"] = -1
                mean_max_dev_non_group = 0
                mean_velocity_non_group = 0
                max_dev = no_encounters_deviations["non_group"][non_group_id]["max_dev"]
            
                if len(max_dev) == 0:
                    continue
                j = 0
                k = 0
                
                for i in range(len(max_dev)):
                    intermediate = max_dev[i]["max_lateral_deviation"]
                    if(intermediate > MAX_DISTANCE):
                        continue
                    else:
                        mean_max_dev_non_group += intermediate
                        j += 1
                        mean_velocity_non_group += max_dev[i]["start_vel"]
                        k+=1

                if(k != 0):
                    mean_velocity_non_group = mean_velocity_non_group/k
                if(j != 0):
                    mean_max_dev_non_group = mean_max_dev_non_group/j
                no_encounters_deviations["non_group"][non_group_id]["mean_max_dev"] = mean_max_dev_non_group
                no_encounters_deviations["non_group"][non_group_id]["mean_velocity"] = mean_velocity_non_group

                social_binding = no_encounters_deviations["group"][group_id]["social_binding"]
                if(social_binding == "other"):
                    social_binding = 4
                global_mean_max_dev_non_group[social_binding] += mean_max_dev_non_group
                l += 1
            global_mean_max_dev_non_group = global_mean_max_dev_non_group/l

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
                    global_velocity = abs(velocity[0]) + abs(velocity[1])
                    if(social_binding == "other") :
                        color = "black"
                    else :
                        color = colors[social_binding]
                    plt.scatter(global_velocity,mean_max_dev_group, c = color, marker = "o", label = "Group")
                plt.xlabel("Mean velocity")
                plt.ylabel("Mean max deviation (mm)")
                plt.title("Mean max deviation for each pedestrians with trip of {0} meters".format(MAX_DISTANCE/1000))
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
                    global_velocity = abs(velocity[0]) + abs(velocity[1])

                    plt.scatter(global_velocity,mean_max_dev_non_group, c = "purple", marker = "o", label = "Non group")
                # # plt.xlabel("Non group ID")
                # plt.ylabel("Mean max deviation (mm)")
                # plt.title("Mean max deviation for all non groups")
            plt.show()

            list_of_social_binding = ["0", "1", "2", "3", "other"]
            for i in range(len(list_of_social_binding)):
                continue
                



        #Plot the mean max_deviation for all pedestrians
        # if (PLOT_MEAN_MAX_DEV):
            


