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



UNDISTURBED_COMPUTE = False
PLOT_MEAN_MAX_DEV = False
SPEED_INTERVAL = True
ANOVA = True

PLOT_SPEED = True
PLOT_TIME = True
PLOT_LENGTH = True


if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env_name_short = env_name.split(":")[1]
        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )
        str_trajectory = ""

        if(UNDISTURBED_COMPUTE):
            str_trajectory = "undisturbed"
            pre_dict = pickle_load(f"../data/pickle/undisturbed_deflection_MAX_DISTANCE.pkl")
            
        else:
            str_trajectory = "all"
            pre_dict = pickle_load(f"../data/pickle/deflection_MAX_DISTANCE.pkl")
            



        for MAX_DISTANCE in MAX_DISTANCE_INTERVAL:
            print("MAX_DISTANCE", MAX_DISTANCE)
            no_encounters_deviations = pre_dict["MAX_DISTANCE"][MAX_DISTANCE]


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
            total_mean_length_pedestrian = np.around(average,decimals=0)/1000

            flatten_list_time = [value for sublist in list_global_mean_time_pedestrian for value in sublist]
            average_time = sum(flatten_list_time) / len(flatten_list_time)
            total_mean_time_pedestrian = np.around(average_time,decimals=0)/1000


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
                    plt.savefig("../data/figures/deflection/will/scatter/undisturbed_trajectories/{2}/mean_max_deviation_for_all_pedestrians_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory, MAX_DISTANCE/1000, MAX_DISTANCE))
                else :
                    plt.savefig("../data/figures/deflection/will/scatter/all_trajectories/{2}/mean_max_deviation_for_all_pedestrians_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory, MAX_DISTANCE/1000, MAX_DISTANCE))

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
                plt.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/{2}/boxplot_mean_max_deviation_for_all_pedestrians_with_{0}_trip_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000, MAX_DISTANCE))
            else :
                plt.savefig("../data/figures/deflection/will/boxplot/all_trajectories/{2}/boxplot_mean_max_deviation_for_all_pedestrians_with_{0}_trip_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000, MAX_DISTANCE))
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
                plt.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/{2}/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000, MAX_DISTANCE))
            else :
                plt.savefig("../data/figures/deflection/will/boxplot/all_trajectories/{2}/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters.png".format(str_trajectory,MAX_DISTANCE/1000, MAX_DISTANCE))

            plt.close()


            if(PLOT_SPEED): 
                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                ax.set_title(f"Speed in function of the social binding / {total_mean_length_pedestrian} meters  |  {total_mean_time_pedestrian} s")
                ax.set_xlabel("Social binding / Participants / Situation")
                ax.set_ylabel("Speed (m/s)")

                ax.boxplot(list_global_mean_velocity_pedestrian, labels=list_of_social_binding, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                            , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
                if (UNDISTURBED_COMPUTE) :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_trajectories/{MAX_DISTANCE}/boxplot_speed_for_all_pedestrians_with_{str_trajectory}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
                else :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/all_trajectories/{MAX_DISTANCE}/boxplot_speed_for_all_pedestrians_with_{str_trajectory}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
                plt.close()

            if(PLOT_LENGTH):
                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                ax.set_title(f"Length in function of the social binding / {total_mean_length_pedestrian} meters  |  {total_mean_time_pedestrian} s")
                ax.set_xlabel("Social binding / Participants / Situation")
                ax.set_ylabel("Length (m)")

                ax.boxplot(list_global_mean_length_pedestrian, labels=list_of_social_binding, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                            , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
                if (UNDISTURBED_COMPUTE) :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_trajectories/{MAX_DISTANCE}/boxplot_length_for_all_pedestrians_with_{str_trajectory}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
                else :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/all_trajectories/{MAX_DISTANCE}/boxplot_length_for_all_pedestrians_with_{str_trajectory}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
                plt.close()


            if(PLOT_TIME):
                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                ax.set_title(f"Time in function of the social binding / {total_mean_length_pedestrian} meters  |  {total_mean_time_pedestrian} s")
                ax.set_xlabel("Social binding / Participants / Situation")
                ax.set_ylabel("Time (s)")

                ax.boxplot(list_global_mean_time_pedestrian, labels=list_of_social_binding, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                            , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
                if (UNDISTURBED_COMPUTE) :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_trajectories/{MAX_DISTANCE}/boxplot_time_for_all_pedestrians_with_{str_trajectory}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
                else :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/all_trajectories/{MAX_DISTANCE}/boxplot_time_for_all_pedestrians_with_{str_trajectory}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
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
        