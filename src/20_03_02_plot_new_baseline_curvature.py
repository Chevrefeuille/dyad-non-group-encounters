import os
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
from parameters import *
from scipy.stats import f_oneway


### Current parameters
LIST_OF_SOCIAL_BINDING = ["0", "1", "2", "3", "alone"]
SOCIAL_BINDING_VALUES = [0, 1, 2, 3]
SOCIAL_BINDING = {"0" : 0, "1" : 1, "2" : 2, "3" : 3, "alone" : 4}
SOC_BINDING_NAMES = ["0", "1", "2", "3", "alone"]



MEDIUM_SAVE = f"curvature/"
ANOVA_SAVE = f"curvature/"



### Old parameters
SCATTER_PLOT = False
SPEED_INTERVAL = False
GROUP_PLOT = True
ANOVA = True
PLOT_SPEED = False
PLOT_TIME = False
PLOT_LENGTH = False


if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env_name_short = env_name.split(":")[1]
        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )

        str_trajectory = "undisturbed"
        no_encounters_curvature = pickle_load(f"../data/pickle/undisturbed_curvature_MAX_DISTANCE_2.pkl")
        MAX_DISTANCE = MAX_DISTANCE_INTERVAL[0]
            
        print("MAX_DISTANCE", MAX_DISTANCE)

        # These lists are used to compute metrics (1 value for each group or pedestrian)
        observation_new_baseline_soc = [[] for i in range(5)]
        mean_curv_new_baseline_soc = [[] for i in range(5)]
        mean_length_new_baseline_soc = [[] for i in range(5)]
        mean_velocity_new_baseline_soc = [[] for i in range(5)]
        mean_time_new_baseline_soc = [[] for i in range(5)]

        # These lists are used to compute metrics (various values for each group or pedestrian)
        curv_sum_new_baseline_soc = [[] for i in range(5)]
        curv_new_baseline_soc = [[] for i in range(5)]
        curv_max_new_baseline_soc = [[] for i in range(5)]
        length_new_baseline_soc = [[] for i in range(5)]
        velocity_new_baseline_soc = [[] for i in range(5)]
        time_new_baseline_soc = [[] for i in range(5)]

        for group_id in no_encounters_curvature["group"]:

            social_binding = no_encounters_curvature["group"][group_id]["social_binding"]
            if social_binding not in SOCIAL_BINDING_VALUES:
                print(social_binding, type(social_binding))
                continue

            curvature_list = no_encounters_curvature["group"][group_id]["curvature_list"]
            if len(curvature_list) == 0:
                continue
            indice = social_binding

            intermediate = []
            intermediate_sum = []
            intermediate_max = []
            intermediate_length = []
            intermediate_velocity = []
            intermediate_time = []


            for i,curvature in enumerate(curvature_list):
                intermediate.append(curvature_list[i]["curvature_mean"])
                intermediate_sum.append(curvature_list[i]["curvature_sum"])
                intermediate_max.append(curvature_list[i]["curvature_max"])
                intermediate_length.append(curvature_list[i]["length_of_trajectory"])
                intermediate_velocity.append(curvature_list[i]["mean_velocity"])
                intermediate_time.append(curvature_list[i]["time"])
                
                curv_new_baseline_soc[indice].append(curvature_list[i]["curvature_mean"])
                curv_sum_new_baseline_soc[indice].append(curvature_list[i]["curvature_sum"])
                curv_max_new_baseline_soc[indice].append(curvature_list[i]["curvature_max"])
                length_new_baseline_soc[indice].append(curvature_list[i]["length_of_trajectory"])
                velocity_new_baseline_soc[indice].append(curvature_list[i]["mean_velocity"])
                time_new_baseline_soc[indice].append(curvature_list[i]["time"])
                observation_new_baseline_soc[indice].append(curvature_list[i]["number_of_observations"])

            mean_curv_new_baseline_soc[indice].append(np.nanmean(intermediate))
            mean_length_new_baseline_soc[indice].append(np.nanmean(intermediate_length))
            mean_velocity_new_baseline_soc[indice].append(np.nanmean(intermediate_velocity))
            mean_time_new_baseline_soc[indice].append(np.nanmean(intermediate_time))
            


        #Compute the mean curvature_listness for all non groups
        # The same process but for non_groups
        for non_group_id in no_encounters_curvature["non_group"]:

            curvature_list = no_encounters_curvature["non_group"][non_group_id]["curvature_list"]
            if len(curvature_list) == 0:
                continue

            intermediate = []
            intermediate_sum = []
            intermediate_max = []
            intermediate_length = []
            intermediate_velocity = []
            intermediate_time = []

            for i, curvature in enumerate(curvature_list):

                intermediate.append(curvature_list[i]["curvature_mean"])
                intermediate_sum.append(curvature_list[i]["curvature_sum"])
                intermediate_max.append(curvature_list[i]["curvature_max"])
                intermediate_length.append(curvature_list[i]["length_of_trajectory"])
                intermediate_velocity.append(curvature_list[i]["mean_velocity"])
                intermediate_time.append(curvature_list[i]["time"])

                curv_new_baseline_soc[-1].append(curvature_list[i]["curvature_mean"])
                curv_sum_new_baseline_soc[-1].append(curvature_list[i]["curvature_sum"])
                curv_max_new_baseline_soc[-1].append(curvature_list[i]["curvature_max"])
                length_new_baseline_soc[-1].append(curvature_list[i]["length_of_trajectory"])
                velocity_new_baseline_soc[-1].append(curvature_list[i]["mean_velocity"])
                time_new_baseline_soc[-1].append(curvature_list[i]["time"])
                observation_new_baseline_soc[-1].append(curvature_list[i]["number_of_observations"])

            mean_curv_new_baseline_soc[-1].append(np.nanmean(intermediate))
            mean_length_new_baseline_soc[-1].append(np.nanmean(intermediate_length))
            mean_velocity_new_baseline_soc[-1].append(np.nanmean(intermediate_velocity))
            mean_time_new_baseline_soc[-1].append(np.nanmean(intermediate_time))
    

        global_mean_mean_new_baseline_length = np.around(np.nanmean([np.nanmean(mean_length_new_baseline_soc[i]) for i in range(5)]), 2) /1000
        global_mean_mean_new_baseline_curv = np.around(np.nanmean([np.nanmean(mean_curv_new_baseline_soc[i]) for i in range(5)]), 2)
        global_mean_mean_new_baseline_velocity = np.around(np.nanmean([np.nanmean(mean_velocity_new_baseline_soc[i]) for i in range(5)]), 2)
        global_mean_mean_new_baseline_time = np.around(np.nanmean([np.nanmean(mean_time_new_baseline_soc[i]) for i in range(5)]), 2) /1000
        global_mean_mean_new_baseline_observation = np.around(np.nanmean([np.nanmean(observation_new_baseline_soc[i]) for i in range(5)]), 2)

        flattened_new_baseline_length = [item for sublist in length_new_baseline_soc for item in sublist]
        global_mean_all_new_baseline_length = np.around(np.nanmean(flattened_new_baseline_length), 2) /1000

        flattened_new_baseline_curv_max = [item for sublist in curv_max_new_baseline_soc for item in sublist]
        global_mean_all_new_baseline_curv_max = np.around(np.nanmean(flattened_new_baseline_curv_max), 2)

        flattened_new_baseline_curv_sum = [item for sublist in curv_sum_new_baseline_soc for item in sublist]
        global_mean_all_new_baseline_curv_sum = np.around(np.nanmean(flattened_new_baseline_curv_sum), 2)

        flattened_new_baseline_curv = [item for sublist in curv_new_baseline_soc for item in sublist]
        global_mean_all_new_baseline_curv = np.around(np.nanmean(flattened_new_baseline_curv), 2)

        flattened_new_baseline_velocity = [item for sublist in velocity_new_baseline_soc for item in sublist]
        global_mean_all_new_baseline_velocity = np.around(np.nanmean(flattened_new_baseline_velocity), 2)

        flattened_new_baseline_time = [item for sublist in time_new_baseline_soc for item in sublist]
        global_mean_all_new_baseline_time = np.around(np.nanmean(flattened_new_baseline_time), 2) /1000
        flattened_new_baseline_observation = [item for sublist in observation_new_baseline_soc for item in sublist]
        global_mean_all_new_baseline_observation = np.around(np.nanmean(flattened_new_baseline_observation), 2)


        # Plot the boxplot of the mean curvature_listness for each social binding
        plot_data = mean_curv_new_baseline_soc.copy()
        len_data = [len(d) for d in plot_data]
        len_all_list = [len(curv_new_baseline_soc[i]) for i in range(len(curv_new_baseline_soc))]

        plot_list = LIST_OF_SOCIAL_BINDING.copy()
        for i in range(5):
            plot_list[i] = plot_list[i] + " / " + str(len_data[i])


        fig, ax = plt.subplots(1 , 1, figsize=(10, 10))
        boxplot = ax.boxplot(plot_data, labels = plot_list
                ,showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
        plt.ylabel("Mean max curvature (mm)")
        plt.xlabel("Social binding / Pedestrians")

        ax.set_title(f"boxplot of mean max curvature for undisturbed pedestrian, trip of {global_mean_mean_new_baseline_length} meters | {global_mean_mean_new_baseline_time} seconds | {global_mean_all_new_baseline_observation} points")
        plt.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_trajectories/2/{MAX_DISTANCE}/mean_data/{MEDIUM_SAVE}/boxplot_mean_curvature_listness_for_new_baseline_with_{str_trajectory}_trip_of_{MAX_DISTANCE/1000}_meters.png")
        plt.close()

        all_data = curv_new_baseline_soc.copy()
        all_list = LIST_OF_SOCIAL_BINDING.copy()
        for i in range(5) :
            all_list[i] = all_list[i] + " / " + str(len(all_data[i]))

        fig, ax = plt.subplots(1 , 1, figsize=(10, 10))

        boxplot = ax.boxplot(all_data, labels = all_list, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
        plt.ylabel("Mean max curvature (mm)")
        plt.xlabel("Social binding / Data used")

        ax.set_title(f"boxplot of mean max curvature for undisturbed pedestrian, trip of {global_mean_all_new_baseline_length} meters | {global_mean_all_new_baseline_time} seconds | {global_mean_all_new_baseline_observation} points")
        plt.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_trajectories/2/{MAX_DISTANCE}/all_data/{MEDIUM_SAVE}boxplot_mean_curvature_listness_for_all_pedestrians_with_{str_trajectory}_trip_of_{MAX_DISTANCE/1000}_meters.png")
        plt.close()

        all_data = curv_max_new_baseline_soc.copy()
        all_list = LIST_OF_SOCIAL_BINDING.copy()
        for i in range(5) :
            all_list[i] = all_list[i] + " / " + str(len(all_data[i]))

        fig, ax = plt.subplots(1 , 1, figsize=(10, 10))

        boxplot = ax.boxplot(all_data, labels = all_list, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
        plt.ylabel("Mean max curvature (mm)")
        plt.xlabel("Social binding / Data used")

        ax.set_title(f"boxplot of mean max curvature for undisturbed pedestrian, trip of {global_mean_all_new_baseline_length} meters | {global_mean_all_new_baseline_time} seconds | {global_mean_all_new_baseline_observation} points")
        plt.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_trajectories/2/{MAX_DISTANCE}/all_data/{MEDIUM_SAVE}boxplot_max_curvature_listness_for_all_pedestrians_with_{str_trajectory}_trip_of_{MAX_DISTANCE/1000}_meters.png")
        plt.close()

        if(ANOVA) :
            # Do the ANOVA thing
            name_of_the_file = f"../data/report_text/deflection/will/undisturbed_trajectories/set_1/{ANOVA_SAVE}ANOVA_for_mean_curvature_listness_new_baseline.txt"
            if os.path.exists(name_of_the_file):
                os.remove(name_of_the_file)
            with open(name_of_the_file, "a") as f :
                f.write("-----------------------------------------------------------\n")
                result = f_oneway(*all_data)
                f.write("ANOVA for mean max curvature for 0/1/2/3/alone in new baseline situation for all data\n")
                f.write("F-value : {0}\n".format(result[0]))
                f.write("p-value : {0}\n".format(result[1]))
                f.write("-----------------------------------------------------------\n")

            name_of_the_file = f"../data/report_text/deflection/will/undisturbed_trajectories/set_1/{ANOVA_SAVE}ANOVA_for_mean_curvature_listness_new_baseline_with_mean.txt"
            if os.path.exists(name_of_the_file):
                os.remove(name_of_the_file)
            with open(name_of_the_file, "a") as f :
                f.write("-----------------------------------------------------------\n")
                result = f_oneway(*plot_data)
                f.write("ANOVA for mean max curvature for 0/1/2/3/alone in new baseline situation for mean data\n")
                f.write("F-value : {0}\n".format(result[0]))
                f.write("p-value : {0}\n".format(result[1]))
                f.write("-----------------------------------------------------------\n")


            name_of_the_file = f"../data/report_text/deflection/will/undisturbed_trajectories/set_3/{ANOVA_SAVE}ANOVA_for_mean_curvature_listness_new_baseline.txt"
            if os.path.exists(name_of_the_file):
                os.remove(name_of_the_file)
            with open(name_of_the_file, "a") as f :
                f.write("-----------------------------------------------------------\n")
                result = f_oneway(*all_data[:-1])
                f.write("ANOVA for mean max curvature for 0/1/2/3 in new baseline situation for all data\n")
                f.write("F-value : {0}\n".format(result[0]))
                f.write("p-value : {0}\n".format(result[1]))
                f.write("-----------------------------------------------------------\n")

            name_of_the_file = f"../data/report_text/deflection/will/undisturbed_trajectories/set_3/{ANOVA_SAVE}ANOVA_for_mean_curvature_listness_new_baseline_with_mean.txt"
            if os.path.exists(name_of_the_file):
                os.remove(name_of_the_file)
            with open(name_of_the_file, "a") as f :
                f.write("-----------------------------------------------------------\n")
                result = f_oneway(*plot_data[:-1])
                f.write("ANOVA for mean max curvature for 0/1/2/3 in new baseline situation for mean data\n")
                f.write("F-value : {0}\n".format(result[0]))
                f.write("p-value : {0}\n".format(result[1]))
                f.write("-----------------------------------------------------------\n")

        if(GROUP_PLOT):
            # This one is for group/non group only
            new_all_data = []
            intermediate_data = []
            for i in range(len(all_data) - 1) :
                intermediate_data += all_data[i]

            new_all_data.append(intermediate_data)
            new_all_data.append(all_data[-1])

            new_label = ["group", "alone"]
            for i in range(2) :
                new_label[i] = new_label[i] + " / " + str(len(new_all_data[i]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            boxplot = ax.boxplot(new_all_data, labels = new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            ax.set_title(f"boxplot of mean max curvature, trip of {global_mean_mean_new_baseline_length} meters | {global_mean_mean_new_baseline_time} seconds | {global_mean_all_new_baseline_observation} points")

            plt.ylabel("Mean max curvature (mm)")
            plt.xlabel("Social binding / Number of pedestrians")
            plt.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_trajectories/2/{MAX_DISTANCE}/all_data/{MEDIUM_SAVE}/boxplot_group_curvatureness_for_new_baseline_with_{str_trajectory}_trip_of_{MAX_DISTANCE/1000}_meters.png")
            plt.close()

            new_plot_data = []
            intermediate_data = []
            for i in range(len(plot_data) - 1) :
                intermediate_data += plot_data[i]
            
            new_plot_data.append(intermediate_data)
            new_plot_data.append(plot_data[-1])

            new_label = ["group", "alone"]
            for i in range(2) :
                new_label[i] = new_label[i] + " / " + str(len(new_plot_data[i]))
            
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            boxplot = ax.boxplot(new_plot_data, labels = new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                                    , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                    boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            ax.set_title(f"boxplot of mean max curvature, trip of {global_mean_mean_new_baseline_length} meters | {global_mean_mean_new_baseline_time} seconds | {global_mean_all_new_baseline_observation} points")

            plt.ylabel("Mean max curvature (mm)")
            plt.xlabel("Social binding / Number of pedestrians")
            plt.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_trajectories/2/{MAX_DISTANCE}/mean_data/{MEDIUM_SAVE}/boxplot_group_curvatureness_for_new_baseline_with_{str_trajectory}_trip_of_{MAX_DISTANCE/1000}_meters.png")
            plt.close()

            if(ANOVA) :
                # Do the ANOVA thing
                name_of_the_file = f"../data/report_text/deflection/will/undisturbed_trajectories/set_2/{ANOVA_SAVE}ANOVA_for_mean_curvature_listness_new_baseline.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*new_all_data)
                    f.write("ANOVA for mean max curvature for Group/Alone in encounter situation for all data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")

                name_of_the_file = f"../data/report_text/deflection/will/undisturbed_trajectories/set_2/{ANOVA_SAVE}ANOVA_for_mean_curvature_listness_new_baseline_with_mean.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*new_plot_data)
                    f.write("ANOVA for mean max curvature for Group/Alone in encounter situation for mean data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")
