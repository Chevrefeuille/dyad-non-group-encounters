import os
from matplotlib import patches
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
from parameters import *
from scipy.stats import f_oneway


### Current parameters
UNDISTURBED_COMPUTE = True
LIST_OF_SOCIAL_BINDING = ["0", "1", "2", "3", "other", "alone"]


### Old parameters
SCATTER_PLOT = False
SPEED_INTERVAL = False
GROUP_PLOT = False
ANOVA = False
PLOT_SPEED = False
PLOT_TIME = False
PLOT_LENGTH = False


if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env_name_short = env_name.split(":")[1]
        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )

        if UNDISTURBED_COMPUTE:
            STR_TRAJECTORY = "undisturbed"
            pre_dict = pickle_load("../data/pickle/undisturbed_deflection_MAX_DISTANCE.pkl")

        else:
            STR_TRAJECTORY = "all"
            pre_dict = pickle_load("../data/pickle/deflection_MAX_DISTANCE.pkl")

        for MAX_DISTANCE in MAX_DISTANCE_INTERVAL:

            print("MAX_DISTANCE", MAX_DISTANCE)
            no_encounters_deviations = pre_dict["MAX_DISTANCE"][MAX_DISTANCE]

            # These lists are used to compute metrics (1 value for each group or pedestrian)
            list_global_mean_max_dev_group = [[] for i in range(6)]
            list_global_mean_length_pedestrian = [[] for i in range(6)]
            list_global_mean_velocity_pedestrian = [[] for i in range(6)]
            list_global_mean_time_pedestrian = [[] for i in range(6)]

            # These lists are used to compute metrics (various values for each group or pedestrian)
            list_all_dev = [[] for i in range(6)]
            list_all_length = [[] for i in range(6)]

            for group_id in no_encounters_deviations["group"]:

                mean_max_dev_group = []
                mean_velocity_group = []
                mean_length_group = []
                mean_time_group = []
                max_dev = no_encounters_deviations["group"][group_id]["max_dev"]
                if len(max_dev) == 0:
                    continue
                social_binding = no_encounters_deviations["group"][group_id]["social_binding"]

                if social_binding == "other":
                    social_binding = 4

                for i,deviation in enumerate(max_dev):

                    intermediate = max_dev[i]["max_lateral_deviation"]
                    if intermediate > MAX_DISTANCE:
                        continue
                    else :
                        mean_max_dev_group.append(intermediate)
                        list_all_dev[social_binding].append(intermediate)
                        list_all_length[social_binding].append(max_dev[i]["length_of_trajectory"])
                        mean_velocity_group.append(max_dev[i]["mean_velocity"])

                        mean_length_group.append(max_dev[i]["length_of_trajectory"])
                        mean_time_group.append(max_dev[i]["time"])


                if len(mean_max_dev_group) != 0:
                    mean_velocity_group = np.nanmean(mean_velocity_group)
                    mean_max_dev_group = np.nanmean(mean_max_dev_group)
                    mean_length_group = np.nanmean(mean_length_group)
                    mean_time_group = np.nanmean(mean_time_group)

                    if mean_max_dev_group < MAX_DISTANCE:
                        list_global_mean_max_dev_group[social_binding].append(mean_max_dev_group)
                        list_global_mean_length_pedestrian[social_binding].append(mean_length_group)
                        list_global_mean_velocity_pedestrian[social_binding].append(mean_velocity_group)
                        list_global_mean_time_pedestrian[social_binding].append(mean_time_group)



            #Compute the mean max_deviation for all non groups
            # The same process but for non_groups
            for non_group_id in no_encounters_deviations["non_group"]:

                mean_max_dev_non_group = []
                mean_velocity_non_group = []
                mean_length_non_group = []
                mean_time_non_group = []
                max_dev = no_encounters_deviations["non_group"][non_group_id]["max_dev"]

                if len(max_dev) == 0:
                    continue
                for i, deviation in enumerate(max_dev):
                    intermediate = max_dev[i]["max_lateral_deviation"]
                    if intermediate > MAX_DISTANCE:
                        continue
                    else:
                        list_all_dev[5].append(intermediate)
                        list_all_length[5].append(max_dev[i]["length_of_trajectory"])
                        mean_max_dev_non_group.append(intermediate)
                        mean_velocity_non_group.append(max_dev[i]["mean_velocity"])
                        mean_length_non_group .append(max_dev[i]["length_of_trajectory"])
                        mean_time_non_group.append(max_dev[i]["time"])

                if len(mean_max_dev_non_group) != 0 :
                    mean_velocity_non_group = np.nanmean(mean_velocity_non_group)
                    mean_max_dev_non_group = np.nanmean(mean_max_dev_non_group)
                    mean_length_non_group = np.nanmean(mean_length_non_group)
                    mean_time_non_group = np.nanmean(mean_time_non_group)

                    if mean_max_dev_non_group < MAX_DISTANCE :
                        list_global_mean_max_dev_group[5].append(mean_max_dev_non_group)
                        list_global_mean_length_pedestrian[5].append(mean_length_non_group)
                        list_global_mean_velocity_pedestrian[5].append(mean_velocity_non_group)
                        list_global_mean_time_pedestrian[5].append(mean_time_non_group)


             #Compute the mean max_deviation for all pedestrians
            flatten_list = [value for sublist in list_global_mean_length_pedestrian
                            for value in sublist]
            # In this case, the mean is computed for each social binding
            all_mean_length_pedestrian = np.around(np.mean(flatten_list),decimals=0)/1000
            # In this case, the mean is computed for each pedestrian
            total_mean_length_pedestrian = np.around(np.mean([np.mean(elt)
                    for elt in list_global_mean_length_pedestrian]),decimals=0)/1000

            flatten_list_time = [value for sublist in list_global_mean_time_pedestrian for value in sublist]
            all_mean_time_pedestrian = np.around(np.mean(flatten_list_time),decimals=0)/1000
            total_mean_time_pedestrian = np.around(np.mean([np.mean(elt)
                    for elt in list_global_mean_time_pedestrian]),decimals=0)/1000




            # Plot the boxplot of the mean max_deviation for each social binding
            plot_data = list_global_mean_max_dev_group.copy()
            len_data = [len(d) for d in plot_data]
            len_all_list = [len(list_all_dev[i]) for i in range(len(list_all_dev))]

            plot_list = LIST_OF_SOCIAL_BINDING.copy()
            for i in range(6):
                plot_list[i] = plot_list[i] + " / " + str(len_data[i])

            del plot_list[4]
            del plot_data[4]

            fig, ax = plt.subplots(1 , 1, figsize=(10, 10))
            boxplot = ax.boxplot(plot_data, labels = plot_list
                    ,showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o',
                    markeredgecolor='black', markerfacecolor='black'), medianprops = dict(color = "black"),
                    whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                    boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            plt.ylabel("Mean max deviation (mm)")
            plt.xlabel("Social binding / Pedestrians")

            if UNDISTURBED_COMPUTE :
                ax.set_title(f"boxplot of mean max deviation for undisturbed pedestrian, trip of {total_mean_length_pedestrian} meters | {total_mean_time_pedestrian} seconds")
                plt.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/{2}/mean_data/boxplot_mean_max_deviation_for_undisturbed_pedestrians_with_{0}_trip_of_{1}_meters.png".format(STR_TRAJECTORY,MAX_DISTANCE/1000, MAX_DISTANCE))
            else :
                ax.set_title(f"boxplot of mean max deviation for all pedestrian, trip of {total_mean_length_pedestrian} meters | {total_mean_time_pedestrian} seconds")
                plt.savefig("../data/figures/deflection/will/boxplot/all_trajectories/{2}/boxplot_mean_max_deviation_for_all_pedestrians_with_{0}_trip_of_{1}_meters.png".format(STR_TRAJECTORY,MAX_DISTANCE/1000, MAX_DISTANCE))
            plt.close()

            all_data = list_all_dev.copy()
            all_list = LIST_OF_SOCIAL_BINDING.copy()
            for i in range(6) :
                all_list[i] = all_list[i] + " / " + str(len(all_data[i]))

            del all_data[4]
            del all_list[4]

            fig, ax = plt.subplots(1 , 1, figsize=(10, 10))

            boxplot = ax.boxplot(all_data, labels = all_list, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                    , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                    boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            plt.ylabel("Mean max deviation (mm)")
            plt.xlabel("Social binding / Data used")

            if UNDISTURBED_COMPUTE :
                ax.set_title(f"boxplot of mean max deviation for undisturbed pedestrian, trip of {all_mean_length_pedestrian} meters | {all_mean_time_pedestrian} seconds")
                plt.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/{2}/all_data/boxplot_mean_max_deviation_for_undisturbed_pedestrians_with_{0}_trip_of_{1}_meters.png".format(STR_TRAJECTORY,MAX_DISTANCE/1000, MAX_DISTANCE))




            if SCATTER_PLOT:
            #Scatter the mean max_deviation for all pedestrians
                for group_id in no_encounters_deviations["group"]:
                    mean_max_dev_group = no_encounters_deviations["group"][group_id]["mean_max_dev"]
                    if mean_max_dev_group == -1:
                        continue
                    if np.all(np.isnan(mean_max_dev_group)):
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
                plt.title("Mean max deviation for each pedestrians with {0}_trajectory of {1} meters".format(STR_TRAJECTORY,total_mean_length_pedestrian))
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
                    if mean_max_dev_non_group == -1:
                        continue
                    if np.all(np.isnan(mean_max_dev_non_group)):
                        continue

                    plt.scatter(velocity,mean_max_dev_non_group, c = "purple", label = "Non group", s=30, alpha = 0.8)
                # # plt.xlabel("Non group ID")
                # plt.ylabel("Mean max deviation (mm)")
                # plt.title("Mean max deviation for all non groups")
                if UNDISTURBED_COMPUTE :
                    plt.savefig("../data/figures/deflection/will/scatter/undisturbed_trajectories/{2}/mean_max_deviation_for_all_pedestrians_with_{0}_trajectory_of_{1}_meters.png".format(STR_TRAJECTORY, MAX_DISTANCE/1000, MAX_DISTANCE))
                else :
                    plt.savefig("../data/figures/deflection/will/scatter/all_trajectories/{2}/mean_max_deviation_for_all_pedestrians_with_{0}_trajectory_of_{1}_meters.png".format(STR_TRAJECTORY, MAX_DISTANCE/1000, MAX_DISTANCE))

                plt.close()

            if ANOVA:
                data = list_global_mean_max_dev_group.copy()
                # Do the ANOVA thing
                name_of_the_file = ""
                if UNDISTURBED_COMPUTE :
                    name_of_the_file = "../data/report_text/deflection/will/undisturbed_trajectories/ANOVA_for_mean_max_deviation_undisturbed.txt"
                else :
                    name_of_the_file = "../data/report_text/deflection/will/all_trajectories/ANOVA_for_mean_max_deviation.txt"
                if not os.path.exists(name_of_the_file):
                    with open(name_of_the_file, "a") as f :
                        f.write("-----------------------------------------------------------\n")
                        result = f_oneway(*data)
                        f.write("ANOVA for mean max deviation for {0} trajectory of {1} meters\n".format(STR_TRAJECTORY, MAX_DISTANCE/1000))
                        f.write("F-value : {0}\n".format(result[0]))
                        f.write("p-value : {0}\n".format(result[1]))
                        f.write("-----------------------------------------------------------\n")

            if GROUP_PLOT:
                for elt in plot_data :
                    print(np.mean(elt))
                    print("-----------------------------------------------------------")

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

                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                boxplot = ax.boxplot(new_data, labels = new_label, showmeans = True, meanline = True,
                        showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                        boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                ax.set_title(f"boxplot of mean max deviation, trip of {total_mean_length_pedestrian} meters | {total_mean_time_pedestrian} seconds")

                plt.ylabel("Mean max deviation (mm)")
                plt.xlabel("Social binding / Number of pedestrians")

                if UNDISTURBED_COMPUTE :
                    plt.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/{2}/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters.png".format(STR_TRAJECTORY,MAX_DISTANCE/1000, MAX_DISTANCE))
                else :
                    plt.savefig("../data/figures/deflection/will/boxplot/all_trajectories/{2}/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters.png".format(STR_TRAJECTORY,MAX_DISTANCE/1000, MAX_DISTANCE))

                plt.close()

            if PLOT_SPEED :
                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                ax.set_title(f"Speed in function of the social binding / {total_mean_length_pedestrian} meters  |  {total_mean_time_pedestrian} s")
                ax.set_xlabel("Social binding / Participants / Situation")
                ax.set_ylabel("Speed (m/s)")

                ax.boxplot(list_global_mean_velocity_pedestrian, labels=LIST_OF_SOCIAL_BINDING, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                            , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
                if UNDISTURBED_COMPUTE :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_trajectories/{MAX_DISTANCE}/boxplot_speed_for_all_pedestrians_with_{STR_TRAJECTORY}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
                else :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/all_trajectories/{MAX_DISTANCE}/boxplot_speed_for_all_pedestrians_with_{STR_TRAJECTORY}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
                plt.close()

            if PLOT_LENGTH :
                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                ax.set_title(f"Length in function of the social binding / {total_mean_length_pedestrian} meters  |  {total_mean_time_pedestrian} s")
                ax.set_xlabel("Social binding / Participants / Situation")
                ax.set_ylabel("Length (m)")

                ax.boxplot(list_global_mean_length_pedestrian, labels=LIST_OF_SOCIAL_BINDING, showmeans = True,
                        meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black',markerfacecolor='black')
                        ,medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                        boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
                if UNDISTURBED_COMPUTE :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_trajectories/{MAX_DISTANCE}/boxplot_length_for_all_pedestrians_with_{STR_TRAJECTORY}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
                else :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/all_trajectories/{MAX_DISTANCE}/boxplot_length_for_all_pedestrians_with_{STR_TRAJECTORY}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
                plt.close()

            if PLOT_TIME:
                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                ax.set_title(f"Time in function of the social binding / {total_mean_length_pedestrian} meters  |  {total_mean_time_pedestrian} s")
                ax.set_xlabel("Social binding / Participants / Situation")
                ax.set_ylabel("Time (s)")

                ax.boxplot(list_global_mean_time_pedestrian, labels=LIST_OF_SOCIAL_BINDING, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                            , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
                if UNDISTURBED_COMPUTE :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_trajectories/{MAX_DISTANCE}/boxplot_time_for_all_pedestrians_with_{STR_TRAJECTORY}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
                else :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/all_trajectories/{MAX_DISTANCE}/boxplot_time_for_all_pedestrians_with_{STR_TRAJECTORY}_trajectory_of_{MAX_DISTANCE/1000}_meters.png")
                plt.close()

            if SPEED_INTERVAL :
                # Create a dictionnary with the speed interval as key and the mean max deviation for each social binding
                speed_interval = [(0.5,0.75),(0.75,1),(1,1.25),(1.25,1.5),(1.5,2),(2,2.5)]
                dict_speed_interval = {}
                for i in range(len(speed_interval)) :
                    dict_speed_interval[speed_interval[i]] = {"0" : [], "1" : [],
                         "2" : [], "3" : [], "other" : [], "alone" : []}

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
                        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
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
                            fig.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/speed/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval_of_{2}_m_s.png".format(STR_TRAJECTORY,MAX_DISTANCE/1000,elt))
                        else :
                            fig.savefig("../data/figures/deflection/will/boxplot/all_trajectories/speed/boxplot_mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval_of_{2}_m_s.png".format(STR_TRAJECTORY,MAX_DISTANCE/1000,elt))

                        plt.close()

                fig2, ax2 = plt.subplots(1, 1, figsize=(10, 10))
                print("list of average", list_of_average)
                print("speed interval", speed_interval)
                str_speed_interval = []
                for elt in speed_interval :
                    str_speed_interval.append(str(elt))
                ax2.plot(str_speed_interval, list_of_average)
                ax2.set_title(f"mean max deviation, trip of {total_mean_length_pedestrian} meters")
                ax2.set_xlabel("Speed interval (m/s)")
                ax2.set_ylabel("Mean max deviation (mm)")

                if UNDISTURBED_COMPUTE :
                    fig2.savefig("../data/figures/deflection/will/boxplot/undisturbed_trajectories/speed/mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval.png".format(STR_TRAJECTORY,MAX_DISTANCE/1000))
                else :
                    fig2.savefig("../data/figures/deflection/will/boxplot/all_trajectories/speed/mean_max_deviation_for_group_non_group_with_{0}_trajectory_of_{1}_meters_and_speed_interval.png".format(STR_TRAJECTORY,MAX_DISTANCE/1000))

                plt.close()
    