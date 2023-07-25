from parameters import *
import matplotlib.pyplot as plt
import numpy as np
from pedestrians_social_binding.utils import *
from sklearn.feature_selection import f_oneway
import os
from pedestrians_social_binding.constants import *

from tqdm import tqdm



# Current parameters
PLOT_SOC_DEVIATION = True
PLOT_NG = False
GROUP_PLOT = True

# Old parameters
ANOVA = True
SPEED_INTERVAL = False
SPEED_GLOBAL = False
SPEED_INTERVAL_2 = False
PLOT_SPEED = False
PLOT_TIME = False
PLOT_LENGTH = False

SOCIAL_BINDING = {"0" : 0, "1" : 1, "2" : 2, "3" : 3, "alone" : 4}
SOCIAL_BINDING_VALUES = [0, 1, 2, 3]
SOC_BINDING_NAMES = ["0", "1", "2", "3", "alone"]
LIST_OF_SOCIAL_BINDING = ["0", "1", "2", "3", "alone"]

MEDIUM_SAVE = f"curvature/v2/"
ANOVA_SAVE = f"curvature/v2/"



if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env_name_short = env_name.split(":")[0] 
        dict_curvature = pickle_load(f"../data/pickle/{env_name_short}_encounters_curvature_v2.pkl")

        group_alone_label = ["group", "alone"]

        # These lists are used to compute metrics (various value for each group or pedestrian)
        curv_encounter_soc = [[] for i in range(5)]
        curv_max_encounter_soc = [[] for i in range(5)]
        curv_encounter_soc_diff = [[] for i in range(5)]
        speed_encounter_soc = [[] for i in range(5)]
        length_encounter_soc = [[] for i in range(5)]
        time_encounter_soc = [[] for i in range(5)]
        observation_encounter_soc = [[] for i in range(5)]

        # These lists are used to compute metrics (1 values for each group or pedestrian)
        mean_curv_encounter_soc = [[] for i in range(5)]
        mean_length_encounter_soc = [[] for i in range(5)]
        mean_speed_encounter_soc = [[] for i in range(5)]
        mean_time_encounter_soc = [[] for i in range(5)]
        mean_curv_encounter_soc_diff = [[] for i in range(4)]

        # Same idea but for alone people in function of the social binding they encounter
        n_g_mean_curv_encounter_soc = [[] for i in range(4)]
        n_g_mean_length_encounter_soc = [[] for i in range(4)]
        n_g_mean_speed_encounter_soc = [[] for i in range(4)]
        n_g_mean_time_encounter_soc = [[] for i in range(4)]
        n_g_observation_encounter_soc = [[] for i in range(4)]

        n_g_curv_encounter_soc = [[] for i in range(4)]
        n_g_speed_encounter_soc = [[] for i in range(4)]
        n_g_length_encounter_soc = [[] for i in range(4)]


        for group_id in dict_curvature["group"]:

            soc_binding = dict_curvature["group"][group_id]["social_binding"]
            if soc_binding not in SOCIAL_BINDING_VALUES:
                print(soc_binding, type(soc_binding))
                continue

            max_curv_group = dict_curvature["group"][group_id]["group curvature"]
            max_curv_non_group = dict_curvature["group"][group_id]["encounters curvature"]

            indice = soc_binding

            intermediate_curvature = []
            intermediate_max_curvature = []
            intermediate_length = []
            intermediate_speed = []
            intermediate_time = []

            n_g_intermediate_curvature = []
            n_g_intermediate_length = []
            n_g_intermediate_speed = []
            n_g_intermediate_time = []

            if len(max_curv_group) == 0:
                continue

            for i,curvature in enumerate(max_curv_group):
                intermediate_curvature.append(max_curv_group[i]["curvature_mean"])
                intermediate_max_curvature.append(max_curv_group[i]["curvature_max"])
                intermediate_length.append(max_curv_group[i]["length_of_trajectory"])
                intermediate_speed.append(max_curv_group[i]["mean_velocity"])
                intermediate_time.append(max_curv_group[i]["time"])

                curv_encounter_soc[indice].append(max_curv_group[i]["curvature_mean"])
                curv_max_encounter_soc[indice].append(max_curv_group[i]["curvature_max"])
                curv_encounter_soc_diff[indice].append(max_curv_group[i]["curvature_mean"] - max_curv_non_group[i]["curvature_mean"])
                speed_encounter_soc[indice].append(max_curv_group[i]["mean_velocity"])
                length_encounter_soc[indice].append(max_curv_group[i]["length_of_trajectory"])
                time_encounter_soc[indice].append(max_curv_group[i]["time"])
                observation_encounter_soc[indice].append(max_curv_group[i]["number_of_observations"])

            mean_curv_encounter_soc[indice].append(np.mean(intermediate_curvature))
            mean_length_encounter_soc[indice].append(np.mean(intermediate_length))
            mean_speed_encounter_soc[indice].append(np.mean(intermediate_speed))
            mean_time_encounter_soc[indice].append(np.mean(intermediate_time))


            intermediate_curvature = []
            intermediate_max_curvature = []
            intermediate_length = []
            intermediate_speed = []
            intermediate_time = []

            n_g_intermediate_curvature = []
            n_g_intermediate_length = []
            n_g_intermediate_speed = []
            n_g_intermediate_time = []

            if len(max_curv_non_group) == 0:
                continue

            for i,curvature in enumerate(max_curv_non_group):

                intermediate_curvature.append(max_curv_non_group[i]["curvature_mean"])
                intermediate_max_curvature.append(max_curv_non_group[i]["curvature_max"])
                intermediate_length.append(max_curv_non_group[i]["length_of_trajectory"])
                intermediate_speed.append(max_curv_non_group[i]["mean_velocity"])
                intermediate_time.append(max_curv_non_group[i]["time"])

                curv_encounter_soc[-1].append(max_curv_non_group[i]["curvature_mean"])
                curv_max_encounter_soc[-1].append(max_curv_non_group[i]["curvature_max"])
                speed_encounter_soc[-1].append(max_curv_non_group[i]["mean_velocity"])
                length_encounter_soc[-1].append(max_curv_non_group[i]["length_of_trajectory"])
                time_encounter_soc[-1].append(max_curv_non_group[i]["time"])
                observation_encounter_soc[-1].append(max_curv_non_group[i]["number_of_observations"])

                n_g_curv_encounter_soc[indice].append(max_curv_non_group[i]["curvature_mean"])
                n_g_speed_encounter_soc[indice].append(max_curv_non_group[i]["mean_velocity"])
                n_g_length_encounter_soc[indice].append(max_curv_non_group[i]["length_of_trajectory"])


            mean_curv_encounter_soc[-1].append(np.mean(intermediate_curvature))
            mean_length_encounter_soc[-1].append(np.mean(intermediate_length))
            mean_speed_encounter_soc[-1].append(np.mean(intermediate_speed))
            mean_time_encounter_soc[-1].append(np.mean(intermediate_time))



        global_mean_mean_encounter_length = np.around(np.nanmean([np.nanmean(mean_length_encounter_soc[i]) for i in range(5)]), 2) /1000
        global_mean_mean_encounter_speed = np.around(np.nanmean([np.nanmean(mean_speed_encounter_soc[i]) for i in range(5)]), 2)
        global_mean_mean_encounter_curv = np.around(np.nanmean([np.nanmean(mean_curv_encounter_soc[i]) for i in range(5)]), 2)
        global_mean_mean_encounter_time = np.around(np.nanmean([np.nanmean(mean_time_encounter_soc[i]) for i in range(5)]), 2) /1000

        flattened_encounter_length = [item for sublist in length_encounter_soc for item in sublist]
        global_mean_all_encounter_length = np.around(np.nanmean(flattened_encounter_length), 2) /1000

        flattened_encounter_speed = [item for sublist in speed_encounter_soc for item in sublist]
        global_mean_all_encounter_speed = np.around(np.nanmean(flattened_encounter_speed), 2)

        flattened_encounter_curv = [item for sublist in curv_encounter_soc for item in sublist]
        global_mean_all_encounter_curv = np.around(np.nanmean(flattened_encounter_curv), 2)

        flattened_encounter_time = [item for sublist in time_encounter_soc for item in sublist]
        global_mean_all_encounter_time = np.around(np.nanmean(flattened_encounter_time), 2) /1000

        flattened_encounter_observation = [item for sublist in observation_encounter_soc for item in sublist]
        global_mean_all_encounter_observation = np.around(np.nanmean(flattened_encounter_observation), 2)


        if(PLOT_SOC_DEVIATION) :
            # Here we plot the curvature in function of the social binding
            plot_data = curv_encounter_soc.copy()
            plot_label = LIST_OF_SOCIAL_BINDING.copy()
            for i in range(5) :
                plot_label[i] = plot_label[i] + " / " + str(len(plot_data[i]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the social binding in encounter situation : {global_mean_all_encounter_length} meters  |  {global_mean_all_encounter_time} s | {global_mean_all_encounter_observation} observations")
            ax.set_xlabel("Social binding / data")
            ax.set_ylabel("Maximum lateral curvature (m)")

            ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
   
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{MEDIUM_SAVE}{env_name_short}all_mean_curvature.png")
            plt.close()

            plot_data = curv_max_encounter_soc.copy()
            plot_label = LIST_OF_SOCIAL_BINDING.copy()
            for i in range(5) :
                plot_label[i] = plot_label[i] + " / " + str(len(plot_data[i]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the social binding in encounter situation : {global_mean_all_encounter_length} meters  |  {global_mean_all_encounter_time} s")
            ax.set_xlabel("Social binding / data")
            ax.set_ylabel("Maximum lateral curvature (m)")

            ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{MEDIUM_SAVE}{env_name_short}_max_curvature.png")
            plt.close()

            if ANOVA :
                # Do the ANOVA thing
                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_1/{ANOVA_SAVE}ANOVA_for_mean_max_curvature_new_baseline.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data)
                    f.write("ANOVA for mean max curvature for 0/1/2/3/alone in encounter situation for all data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")

                # Do the ANOVA thing
                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_3/{ANOVA_SAVE}ANOVA_for_mean_max_curvature_new_baseline.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data[:-1])
                    f.write("ANOVA for mean max curvature for 0/1/2/3 in encounter situation for all data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")


            plot_data =mean_curv_encounter_soc.copy()
            plot_label = LIST_OF_SOCIAL_BINDING.copy()
            for i in range(5) :
                plot_label[i] = plot_label[i] + " / " + str(len(plot_data[i]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the social binding in encounter situation : {global_mean_mean_encounter_length} meters  |  {global_mean_mean_encounter_time} s | {global_mean_all_encounter_observation} observations")

            ax.set_xlabel("Social binding / Group")
            ax.set_ylabel("Maximum lateral curvature (m)")

            ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)

            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/mean_data/{MEDIUM_SAVE}{env_name_short}mean_mean_curvature.png")
            plt.close()

            if ANOVA :
                # Do the ANOVA thing
                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_1/{ANOVA_SAVE}ANOVA_for_mean_max_curvature_new_baseline_with_mean.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data)
                    f.write("ANOVA for mean max curvature for 0/1/2/3/alone in encounter situation for mean data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")

                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_3/{ANOVA_SAVE}ANOVA_for_mean_max_curvature_new_baseline_with_mean.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data[:-1])
                    f.write("ANOVA for mean max curvature for 0/1/2/3 in encounter situation for mean data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")

        if GROUP_PLOT :
            # This one is for group/non group only

            group_data = []
            for i in range (len(curv_encounter_soc) - 1):
                group_data += curv_encounter_soc[i]

            plot_data = [group_data, curv_encounter_soc[-1]]
            plot_label = ["Group", "Non group"]
            plot_label[0] = plot_label[0] + " / " + str(len(plot_data[0]))
            plot_label[1] = plot_label[1] + " / " + str(len(plot_data[1]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the group apartenance in encounter situation : {global_mean_all_encounter_length} meters  |  {global_mean_all_encounter_time} s | {global_mean_all_encounter_observation} observations")
            ax.set_xlabel("Group apartenance / data")
            ax.set_ylabel("Maximum lateral curvature (m)")
            boxplot = ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            
            plt.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{MEDIUM_SAVE}{env_name_short}_group_alone.png")
            plt.close()

            if ANOVA:
                # Do the ANOVA thing
                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_2/{ANOVA_SAVE}ANOVA_for_mean_max_curvature_new_baseline.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data)
                    f.write("ANOVA for mean max curvature for Group/Alone in encounter situation for all data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")


            group_data = []
            for i in range (len(mean_curv_encounter_soc) - 1):
                group_data += mean_curv_encounter_soc[i]

            plot_data = [group_data, mean_curv_encounter_soc[-1]]
            plot_label = ["Group", "Non group"]
            plot_label[0] = plot_label[0] + " / " + str(len(plot_data[0]))
            plot_label[1] = plot_label[1] + " / " + str(len(plot_data[1]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the group apartenance in encounter situation : {global_mean_mean_encounter_length} meters  |  {global_mean_mean_encounter_time} s | {global_mean_all_encounter_observation} observations")
            ax.set_xlabel("Group apartenance / Group")
            ax.set_ylabel("Maximum lateral curvature (m)")
            boxplot = ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            
            plt.savefig(f"../data/figures/deflection/will/boxplot/encounter/mean_data/{MEDIUM_SAVE}{env_name_short}_group_alone.png")
            plt.close()

            if ANOVA :
                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_2/{ANOVA_SAVE}ANOVA_for_mean_max_curvature_new_baseline_with_mean.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data)
                    f.write("ANOVA for mean max curvature for Group/Alone in encounter situation for mean data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")




        if(PLOT_NG) :
            # Here we plot the curvature in function of the social binding
            plot_data = n_g_curv_encounter_soc.copy()
            plot_label = LIST_OF_SOCIAL_BINDING.copy()[:-1]

            for i in range(4) :
                plot_label[i] = plot_label[i] + " / " + str(len(plot_data[i]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
            
            ax.set_title(f"Deviation for alone people in function of the social binding of their encounter / {global_mean_all_encounter_length} meters | {global_mean_all_encounter_observation} observations")
            ax.set_xlabel("Social binding / Group / data")
            ax.set_ylabel("Maximum lateral curvature (m)")
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{MEDIUM_SAVE}{env_name_short}_curvature_alone.png")
            plt.close(fig)


            plot_data = n_g_mean_curv_encounter_soc.copy()
            plot_label = LIST_OF_SOCIAL_BINDING.copy()[:-1]

            for i in range(4) :
                plot_label[i] = plot_label[i] + " / " + str(len(plot_data[i]))

            fig,ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.boxplot(n_g_mean_curv_encounter_soc, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
            
            ax.set_title(f"Deviation for alone people in function of the social binding of their encounter / {global_mean_mean_encounter_length} meters | {global_mean_all_encounter_observation} observations")
            ax.set_xlabel("Social binding / Group / data")
            ax.set_ylabel("Maximum lateral curvature (m)")
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/mean_data/{MEDIUM_SAVE}{env_name_short}_curvature_alone.png")
            plt.close(fig)

            if(ANOVA):
                name_of_the_file = f"../data/report_text/deflection/will/encounter/all_data/{ANOVA_SAVE}ANOVA_for_mean_max_curvature_MAX_DISTANCE_{0}.txt".format(global_mean_mean_encounter_length)
                if not os.path.exists(name_of_the_file):
                    with open(name_of_the_file, "a") as f :
                        f.write("-----------------------------------------------------------\n")
                        result = f_oneway(curv_encounter_soc[0], curv_encounter_soc[1], curv_encounter_soc[2], curv_encounter_soc[3], curv_encounter_soc[4], curv_encounter_soc[5])
                        f.write("ANOVA for mean max curvature in function of the social binding in encounter situation\n")
                        f.write("F-value : {0}\n".format(result[0]))
                        f.write("p-value : {0}\n".format(result[1]))
                        f.write("-----------------------------------------------------------\n")