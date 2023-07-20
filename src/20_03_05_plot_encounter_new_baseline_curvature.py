import os
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
from parameters import *
from scipy.stats import f_oneway

ANOVA = True
SOCIAL_BINDING = {"0" : 0, "1" : 1, "2" : 2, "3" : 3, "alone" : 4}
SOCIAL_BINDING_VALUES = [0, 1, 2, 3]
SOC_BINDING_NAMES = ["0", "1", "2", "3", "alone"]
ANOVA_SAVE = f"curvature/"


if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env_name_short = env_name.split(":")[0]
        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )

        no_encounters_curvature = pickle_load("../data/pickle/undisturbed_curvature_MAX_DISTANCE_2.pkl")
        dict_curvature = pickle_load(f"../data/pickle/{env_name_short}_encounters_curvature.pkl")

        MAX_DISTANCE = MAX_DISTANCE_INTERVAL[0]
        print("MAX_DISTANCE", MAX_DISTANCE)

        # Organize value of encounter situation in list in order to plot
        curv_encounter_soc = [[] for _ in range(5)]
        curv_max_encounter_soc = [[] for _ in range(5)]
        length_encounter_soc = [[] for _ in range(5)]
        
        mean_curv_encounter_soc = [[] for _ in range(5)]
        mean_length_encounter_soc = [[] for _ in range(5)]

        for group_id in dict_curvature["group"]:

            soc_binding = dict_curvature["group"][group_id]["social_binding"]
            if soc_binding not in SOCIAL_BINDING_VALUES:
                print(soc_binding, type(soc_binding))
                continue

            max_curv_group = dict_curvature["group"][group_id]["group curvature"]
            max_curv_non_group = dict_curvature["group"][group_id]["encounters curvature"]
            indice = soc_binding

            intermediate = []
            itermediate_max = []
            intermediate_length = []

            if len(max_curv_group) == 0:
                continue

            for i,curvature in enumerate(max_curv_group):
                intermediate.append(max_curv_group[i]["curvature_mean"])
                itermediate_max.append(max_curv_group[i]["curvature_max"])
                intermediate_length.append(max_curv_group[i]["length_of_trajectory"])

                curv_encounter_soc[indice].append(max_curv_group[i]["curvature_mean"])
                curv_max_encounter_soc[indice].append(max_curv_group[i]["curvature_max"])
                length_encounter_soc[indice].append(max_curv_group[i]["length_of_trajectory"])

            mean_curv_encounter_soc[indice].append(np.nanmean(intermediate))
            mean_length_encounter_soc[indice].append(np.nanmean(intermediate_length))
            
            intermediate = []
            itermediate_max = []
            intermediate_length = []

            if len(max_curv_non_group) == 0:
                continue

            for i,curvature in enumerate(max_curv_non_group):

                intermediate.append(max_curv_non_group[i]["curvature_mean"])
                itermediate_max.append(max_curv_non_group[i]["curvature_max"])
                intermediate_length.append(max_curv_non_group[i]["length_of_trajectory"])

                curv_encounter_soc[-1].append(max_curv_non_group[i]["curvature_mean"])
                curv_max_encounter_soc[-1].append(max_curv_non_group[i]["curvature_max"])
                length_encounter_soc[-1].append(max_curv_non_group[i]["length_of_trajectory"])

            mean_curv_encounter_soc[-1].append(np.nanmean(intermediate))
            mean_length_encounter_soc[-1].append(np.nanmean(intermediate_length))

        # Organize value of undisturbed situation in list in order to plot
        curv_new_baseline_soc = [[] for _ in range(5)]
        curv_max_new_baseline_soc = [[] for _ in range(5)]
        length_new_baseline_soc = [[] for _ in range(5)]
        mean_curv_new_baseline_soc = [[] for _ in range(5)]
        mean_length_new_baseline_soc = [[] for _ in range(5)]

        for group_id in no_encounters_curvature["group"]:

            social_binding = no_encounters_curvature["group"][group_id]["social_binding"]
            if social_binding not in SOCIAL_BINDING_VALUES:
                print(social_binding, type(social_binding))
                continue

            max_curv = no_encounters_curvature["group"][group_id]["curvature_list"]
            if len(max_curv) == 0:
                continue
            indice = social_binding

            intermediate = []
            intermediate_max = []
            intermediate_length = []
            for i,curvature in enumerate(max_curv):
                
                intermediate.append(max_curv[i]["curvature_mean"])
                intermediate_length.append(max_curv[i]["length_of_trajectory"])
                itermediate_max.append(max_curv[i]["curvature_max"])

                curv_new_baseline_soc[indice].append(max_curv[i]["curvature_mean"])
                curv_max_new_baseline_soc[indice].append(max_curv[i]["curvature_max"])
                length_new_baseline_soc[indice].append(max_curv[i]["length_of_trajectory"])

            mean_curv_new_baseline_soc[indice].append(np.nanmean(intermediate))
            mean_length_new_baseline_soc[indice].append(np.nanmean(intermediate_length))

        for non_group_id in no_encounters_curvature["non_group"]:
            
            max_curv = no_encounters_curvature["non_group"][non_group_id]["curvature_list"]
            if len(max_curv) == 0:
                continue

            intermediate = []
            intermediate_max = []
            intermediate_length = []
            for i,curvature in enumerate(max_curv):

                intermediate.append(max_curv[i]["curvature_mean"])
                intermediate_length.append(max_curv[i]["length_of_trajectory"])
                itermediate_max.append(max_curv[i]["curvature_max"])

                curv_new_baseline_soc[-1].append(max_curv[i]["curvature_mean"])
                curv_max_new_baseline_soc[-1].append(max_curv[i]["curvature_max"])
                length_new_baseline_soc[-1].append(max_curv[i]["length_of_trajectory"])

            mean_curv_new_baseline_soc[-1].append(np.nanmean(intermediate))
            mean_length_new_baseline_soc[-1].append(np.nanmean(intermediate_length))

        PLOT_LABEL = ["Encounter situation ", "new baseline situation "]

        # Get some relevant mean
        global_mean_mean_encounter_length = np.around(np.nanmean([np.nanmean(mean_length_encounter_soc[i]) for i in range(5)]), 2)
        global_mean_mean_new_baseline_length = np.around(np.nanmean([np.nanmean(mean_length_new_baseline_soc[i]) for i in range(5)]), 2)

        flattened_encounter_length = [item for sublist in length_encounter_soc for item in sublist]
        global_mean_all_encounter_length = np.around(np.nanmean(flattened_encounter_length), 2)

        flattened_new_baseline_length = [item for sublist in length_new_baseline_soc for item in sublist]
        global_mean_all_new_baseline_length = np.around(np.nanmean(flattened_new_baseline_length), 2)


        # Plot
        for i in range(5):
            plot_label = PLOT_LABEL.copy()
            plot_label[0] += f"{len(curv_encounter_soc[i])} / {global_mean_all_encounter_length} m"
            plot_label[1] += f"{len(curv_new_baseline_soc[i])} / {global_mean_all_new_baseline_length} m"

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Encounter situation vs. new baseline situation")
            ax.set_xlabel("Social binding / value / length of trajectory")
            ax.set_ylabel("Lateral curvature (m)")
            all_data = [curv_encounter_soc[i], curv_new_baseline_soc[i]]

            ax.boxplot(all_data, labels = plot_label ,showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            
            plt.savefig(f"../data/figures/deflection/will/boxplot/versus/all/curvature/mean_curv_encounter_new_baseline_{env_name_short}_{SOC_BINDING_NAMES[i]}.png")
            plt.close()

            plot_label = PLOT_LABEL.copy()
            plot_label[0] += f"{len(curv_max_encounter_soc[i])} / {global_mean_mean_encounter_length} m"
            plot_label[1] += f"{len(curv_max_new_baseline_soc[i])} / {global_mean_mean_new_baseline_length} m"

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Encounter situation vs. new baseline situation")
            ax.set_xlabel("Social binding / value / length of trajectory")
            ax.set_ylabel("Lateral maximum curvature (m)")
            all_data = [curv_max_encounter_soc[i], curv_max_new_baseline_soc[i]]

            ax.boxplot(all_data, labels = plot_label ,showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            
            plt.savefig(f"../data/figures/deflection/will/boxplot/versus/all/curvature/max_curv_encounter_new_baseline_{env_name_short}_{SOC_BINDING_NAMES[i]}.png")


            plot_label = PLOT_LABEL.copy()
            plot_label[0] += f"{len(mean_curv_encounter_soc[i])} / {global_mean_mean_encounter_length} m"
            plot_label[1] += f"{len(mean_curv_new_baseline_soc[i])} / {global_mean_mean_new_baseline_length} m"

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Encounter situation vs. new baseline situation")
            ax.set_xlabel("Social binding / value")
            ax.set_ylabel("Lateral curvature (m)")
            mean_data = [mean_curv_encounter_soc[i], mean_curv_new_baseline_soc[i]]

            ax.boxplot(mean_data, labels = plot_label ,showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)

            plt.savefig(f"../data/figures/deflection/will/boxplot/versus/mean/curvature/encounter_new_baseline_mean_{env_name_short}_{SOC_BINDING_NAMES[i]}.png")
            plt.close()

            # ANOVA
            if ANOVA:
                name_of_the_file = f"../data/report_text/deflection/will/versus/all_data/{ANOVA_SAVE}ANOVA_{SOC_BINDING_NAMES[i]}.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*all_data)
                    f.write(f"ANOVA for mean max curvature for social binding {SOC_BINDING_NAMES[i]}\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")

                name_of_the_file = f"../data/report_text/deflection/will/versus/mean_data/{ANOVA_SAVE}ANOVA_{SOC_BINDING_NAMES[i]}.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*mean_data)
                    f.write("ANOVA for mean max curvature for social binding {SOC_BINDING_NAMES[i]}\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")



