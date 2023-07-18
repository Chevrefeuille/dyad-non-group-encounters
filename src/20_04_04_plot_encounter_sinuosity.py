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

MEDIUM_SAVE = f"sinuosity/"
ANOVA_SAVE = f"sinuosity/"



if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env_name_short = env_name.split(":")[0] 
        dict_sinuosity = pickle_load(f"../data/pickle/{env_name_short}_encounters_sinuosity.pkl")

        group_alone_label = ["group", "alone"]

        # These lists are used to compute metrics (various value for each group or pedestrian)
        sinu_encounter_soc = [[] for i in range(5)]
        sinu_encounter_soc_diff = [[] for i in range(5)]
        speed_encounter_soc = [[] for i in range(5)]
        length_encounter_soc = [[] for i in range(5)]
        time_encounter_soc = [[] for i in range(5)]

        # These lists are used to compute metrics (1 values for each group or pedestrian)
        mean_sinu_encounter_soc = [[] for i in range(5)]
        mean_length_encounter_soc = [[] for i in range(5)]
        mean_speed_encounter_soc = [[] for i in range(5)]
        mean_time_encounter_soc = [[] for i in range(5)]
        mean_sinu_encounter_soc_diff = [[] for i in range(4)]

        # Same idea but for alone people in function of the social binding they encounter
        n_g_mean_sinu_encounter_soc = [[] for i in range(4)]
        n_g_mean_length_encounter_soc = [[] for i in range(4)]
        n_g_mean_speed_encounter_soc = [[] for i in range(4)]
        n_g_mean_time_encounter_soc = [[] for i in range(4)]

        n_g_sinu_encounter_soc = [[] for i in range(4)]
        n_g_speed_encounter_soc = [[] for i in range(4)]
        n_g_length_encounter_soc = [[] for i in range(4)]


        for group_id in dict_sinuosity["group"]:

            soc_binding = dict_sinuosity["group"][group_id]["social_binding"]
            if soc_binding not in SOCIAL_BINDING_VALUES:
                print(soc_binding, type(soc_binding))
                continue

            max_sinu_group = dict_sinuosity["group"][group_id]["group sinuosity"]
            max_sinu_non_group = dict_sinuosity["group"][group_id]["encounters sinuosity"]

            indice = soc_binding

            intermediate_sinuosity = []
            intermediate_length = []
            intermediate_speed = []
            intermediate_time = []

            n_g_intermediate_sinuosity = []
            n_g_intermediate_length = []
            n_g_intermediate_speed = []
            n_g_intermediate_time = []

            if len(max_sinu_group) == 0:
                continue

            for i,sinuosity in enumerate(max_sinu_group):
                intermediate_sinuosity.append(max_sinu_group[i]["sinuosity"])
                intermediate_length.append(max_sinu_group[i]["length_of_trajectory"])
                intermediate_speed.append(max_sinu_group[i]["mean_velocity"])
                intermediate_time.append(max_sinu_group[i]["time"])

                sinu_encounter_soc[indice].append(max_sinu_group[i]["sinuosity"])
                sinu_encounter_soc_diff[indice].append(max_sinu_group[i]["sinuosity"] - max_sinu_non_group[i]["sinuosity"])
                speed_encounter_soc[indice].append(max_sinu_group[i]["mean_velocity"])
                length_encounter_soc[indice].append(max_sinu_group[i]["length_of_trajectory"])
                time_encounter_soc[indice].append(max_sinu_group[i]["time"])

            mean_sinu_encounter_soc[indice].append(np.mean(intermediate_sinuosity))
            mean_length_encounter_soc[indice].append(np.mean(intermediate_length))
            mean_speed_encounter_soc[indice].append(np.mean(intermediate_speed))
            mean_time_encounter_soc[indice].append(np.mean(intermediate_time))


            intermediate_sinuosity = []
            intermediate_length = []
            intermediate_speed = []
            intermediate_time = []

            n_g_intermediate_sinuosity = []
            n_g_intermediate_length = []
            n_g_intermediate_speed = []
            n_g_intermediate_time = []

            if len(max_sinu_non_group) == 0:
                continue

            for i,sinuosity in enumerate(max_sinu_non_group):

                intermediate_sinuosity.append(max_sinu_non_group[i]["sinuosity"])
                intermediate_length.append(max_sinu_non_group[i]["length_of_trajectory"])
                intermediate_speed.append(max_sinu_non_group[i]["mean_velocity"])
                intermediate_time.append(max_sinu_non_group[i]["time"])

                sinu_encounter_soc[-1].append(max_sinu_non_group[i]["sinuosity"])
                speed_encounter_soc[-1].append(max_sinu_non_group[i]["mean_velocity"])
                length_encounter_soc[-1].append(max_sinu_non_group[i]["length_of_trajectory"])
                time_encounter_soc[-1].append(max_sinu_non_group[i]["time"])

                n_g_sinu_encounter_soc[indice].append(max_sinu_non_group[i]["sinuosity"])
                n_g_speed_encounter_soc[indice].append(max_sinu_non_group[i]["mean_velocity"])
                n_g_length_encounter_soc[indice].append(max_sinu_non_group[i]["length_of_trajectory"])


            mean_sinu_encounter_soc[-1].append(np.mean(intermediate_sinuosity))
            mean_length_encounter_soc[-1].append(np.mean(intermediate_length))
            mean_speed_encounter_soc[-1].append(np.mean(intermediate_speed))
            mean_time_encounter_soc[-1].append(np.mean(intermediate_time))



        global_mean_mean_encounter_length = np.around(np.nanmean([np.nanmean(mean_length_encounter_soc[i]) for i in range(5)]), 2) /1000
        global_mean_mean_encounter_speed = np.around(np.nanmean([np.nanmean(mean_speed_encounter_soc[i]) for i in range(5)]), 2)
        global_mean_mean_encounter_sinu = np.around(np.nanmean([np.nanmean(mean_sinu_encounter_soc[i]) for i in range(5)]), 2)
        global_mean_mean_encounter_time = np.around(np.nanmean([np.nanmean(mean_time_encounter_soc[i]) for i in range(5)]), 2) /1000

        flattened_encounter_length = [item for sublist in length_encounter_soc for item in sublist]
        global_mean_all_encounter_length = np.around(np.nanmean(flattened_encounter_length), 2) /1000

        flattened_encounter_speed = [item for sublist in speed_encounter_soc for item in sublist]
        global_mean_all_encounter_speed = np.around(np.nanmean(flattened_encounter_speed), 2)

        flattened_encounter_sinu = [item for sublist in sinu_encounter_soc for item in sublist]
        global_mean_all_encounter_sinu = np.around(np.nanmean(flattened_encounter_sinu), 2)

        flattened_encounter_time = [item for sublist in time_encounter_soc for item in sublist]
        global_mean_all_encounter_time = np.around(np.nanmean(flattened_encounter_time), 2) /1000


        if(PLOT_SOC_DEVIATION) :
            # Here we plot the sinuosity in function of the social binding
            plot_data = sinu_encounter_soc.copy()
            plot_label = LIST_OF_SOCIAL_BINDING.copy()
            for i in range(5) :
                plot_label[i] = plot_label[i] + " / " + str(len(plot_data[i]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the social binding in encounter situation : {global_mean_all_encounter_length} meters  |  {global_mean_all_encounter_time} s")
            ax.set_xlabel("Social binding / data")
            ax.set_ylabel("Maximum lateral sinuosity (m)")

            ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
   
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{MEDIUM_SAVE}{env_name_short}_sinuosity.png")
            plt.close()

            if ANOVA :
                # Do the ANOVA thing
                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_1/{ANOVA_SAVE}ANOVA_for_mean_max_sinuosity_new_baseline.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data)
                    f.write("ANOVA for mean max sinuosity for 0/1/2/3/alone in encounter situation for all data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")

                # Do the ANOVA thing
                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_3/{ANOVA_SAVE}ANOVA_for_mean_max_sinuosity_new_baseline.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data[:-1])
                    f.write("ANOVA for mean max sinuosity for 0/1/2/3 in encounter situation for all data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")


            plot_data =mean_sinu_encounter_soc.copy()
            plot_label = LIST_OF_SOCIAL_BINDING.copy()
            for i in range(5) :
                plot_label[i] = plot_label[i] + " / " + str(len(plot_data[i]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the social binding in encounter situation : {global_mean_mean_encounter_length} meters  |  {global_mean_mean_encounter_time} s")

            ax.set_xlabel("Social binding / Group")
            ax.set_ylabel("Maximum lateral sinuosity (m)")

            ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)

            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/mean_data/{MEDIUM_SAVE}{env_name_short}_sinuosity.png")
            plt.close()

            if ANOVA :
                # Do the ANOVA thing
                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_1/{ANOVA_SAVE}ANOVA_for_mean_max_sinuosity_new_baseline_with_mean.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data)
                    f.write("ANOVA for mean max sinuosity for 0/1/2/3/alone in encounter situation for mean data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")

                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_3/{ANOVA_SAVE}ANOVA_for_mean_max_sinuosity_new_baseline_with_mean.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data[:-1])
                    f.write("ANOVA for mean max sinuosity for 0/1/2/3 in encounter situation for mean data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")

        if GROUP_PLOT :
            # This one is for group/non group only

            group_data = []
            for i in range (len(sinu_encounter_soc) - 1):
                group_data += sinu_encounter_soc[i]

            plot_data = [group_data, sinu_encounter_soc[-1]]
            plot_label = ["Group", "Non group"]
            plot_label[0] = plot_label[0] + " / " + str(len(plot_data[0]))
            plot_label[1] = plot_label[1] + " / " + str(len(plot_data[1]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the group apartenance in encounter situation : {global_mean_all_encounter_length} meters  |  {global_mean_all_encounter_time} s")
            ax.set_xlabel("Group apartenance / data")
            ax.set_ylabel("Maximum lateral sinuosity (m)")
            boxplot = ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            
            plt.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{MEDIUM_SAVE}{env_name_short}_group_alone.png")
            plt.close()

            if ANOVA:
                # Do the ANOVA thing
                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_2/{ANOVA_SAVE}ANOVA_for_mean_max_sinuosity_new_baseline.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data)
                    f.write("ANOVA for mean max sinuosity for Group/Alone in encounter situation for all data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")


            group_data = []
            for i in range (len(mean_sinu_encounter_soc) - 1):
                group_data += mean_sinu_encounter_soc[i]

            plot_data = [group_data, mean_sinu_encounter_soc[-1]]
            plot_label = ["Group", "Non group"]
            plot_label[0] = plot_label[0] + " / " + str(len(plot_data[0]))
            plot_label[1] = plot_label[1] + " / " + str(len(plot_data[1]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the group apartenance in encounter situation : {global_mean_mean_encounter_length} meters  |  {global_mean_mean_encounter_time} s")
            ax.set_xlabel("Group apartenance / Group")
            ax.set_ylabel("Maximum lateral sinuosity (m)")
            boxplot = ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            
            plt.savefig(f"../data/figures/deflection/will/boxplot/encounter/mean_data/{MEDIUM_SAVE}{env_name_short}_group_alone.png")
            plt.close()

            if ANOVA :
                name_of_the_file = f"../data/report_text/deflection/will/encounter/set_2/{ANOVA_SAVE}ANOVA_for_mean_max_sinuosity_new_baseline_with_mean.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*plot_data)
                    f.write("ANOVA for mean max sinuosity for Group/Alone in encounter situation for mean data\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")




        if(PLOT_NG) :
            # Here we plot the sinuosity in function of the social binding
            plot_data = n_g_sinu_encounter_soc.copy()
            plot_label = LIST_OF_SOCIAL_BINDING.copy()[:-1]

            for i in range(4) :
                plot_label[i] = plot_label[i] + " / " + str(len(plot_data[i]))

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
            
            ax.set_title(f"Deviation for alone people in function of the social binding of their encounter / {global_mean_all_encounter_length} meters")
            ax.set_xlabel("Social binding / Group / data")
            ax.set_ylabel("Maximum lateral sinuosity (m)")
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{MEDIUM_SAVE}{env_name_short}_sinuosity_alone.png")
            plt.close(fig)


            plot_data = n_g_mean_sinu_encounter_soc.copy()
            plot_label = LIST_OF_SOCIAL_BINDING.copy()[:-1]

            for i in range(4) :
                plot_label[i] = plot_label[i] + " / " + str(len(plot_data[i]))

            fig,ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.boxplot(n_g_mean_sinu_encounter_soc, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
            
            ax.set_title(f"Deviation for alone people in function of the social binding of their encounter / {global_mean_mean_encounter_length} meters")
            ax.set_xlabel("Social binding / Group / data")
            ax.set_ylabel("Maximum lateral sinuosity (m)")
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/mean_data/{MEDIUM_SAVE}{env_name_short}_sinuosity_alone.png")
            plt.close(fig)

            if(ANOVA):
                name_of_the_file = f"../data/report_text/deflection/will/encounter/all_data/{ANOVA_SAVE}ANOVA_for_mean_max_sinuosity_MAX_DISTANCE_{0}.txt".format(global_mean_mean_encounter_length)
                if not os.path.exists(name_of_the_file):
                    with open(name_of_the_file, "a") as f :
                        f.write("-----------------------------------------------------------\n")
                        result = f_oneway(sinu_encounter_soc[0], sinu_encounter_soc[1], sinu_encounter_soc[2], sinu_encounter_soc[3], sinu_encounter_soc[4], sinu_encounter_soc[5])
                        f.write("ANOVA for mean max sinuosity in function of the social binding in encounter situation\n")
                        f.write("F-value : {0}\n".format(result[0]))
                        f.write("p-value : {0}\n".format(result[1]))
                        f.write("-----------------------------------------------------------\n")