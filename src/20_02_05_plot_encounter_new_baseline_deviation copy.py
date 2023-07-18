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
ANOVA_SAVE = f"{N_POINTS_AVERAGE}/"


if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env_name_short = env_name.split(":")[0]
        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )

        no_encounters_sinuositys = pickle_load("../data/pickle/undisturbed_deflection_MAX_DISTANCE_2.pkl")
        dict_sinuosity = pickle_load(f"../data/pickle/{env_name_short}_encounters_sinuositys.pkl")

        MAX_DISTANCE = MAX_DISTANCE_INTERVAL[0]
        print("MAX_DISTANCE", MAX_DISTANCE)

        # Organize value of encounter situation in list in order to plot
        sinu_encounter_soc = [[] for _ in range(5)]
        length_encounter_soc = [[] for _ in range(5)]
        
        mean_sinu_encounter_soc = [[] for _ in range(5)]
        mean_length_encounter_soc = [[] for _ in range(5)]

        for group_id in dict_sinuosity["group"]:

            soc_binding = dict_sinuosity["group"][group_id]["social_binding"]
            if soc_binding not in SOCIAL_BINDING_VALUES:
                print(soc_binding, type(soc_binding))
                continue

            max_sinu_group = dict_sinuosity["group"][group_id]["group sinuosity"]
            max_sinu_non_group = dict_sinuosity["group"][group_id]["encounters sinuosity"]
            indice = soc_binding

            intermediate = []
            intermediate_length = []

            if len(max_sinu_group) == 0:
                continue

            for i,sinuosity in enumerate(max_sinu_group):
                intermediate.append(max_sinu_group[i]["max_lateral_sinuosity"])
                intermediate_length.append(max_sinu_group[i]["length_of_trajectory"])
                sinu_encounter_soc[indice].append(max_sinu_group[i]["max_lateral_sinuosity"])
                length_encounter_soc[indice].append(max_sinu_group[i]["length_of_trajectory"])

            mean_sinu_encounter_soc[indice].append(np.nanmean(intermediate))
            mean_length_encounter_soc[indice].append(np.nanmean(intermediate_length))
            
            intermediate = []
            intermediate_length = []

            if len(max_sinu_non_group) == 0:
                continue

            for i,sinuosity in enumerate(max_sinu_non_group):

                intermediate.append(max_sinu_non_group[i]["max_lateral_sinuosity"])
                intermediate_length.append(max_sinu_non_group[i]["length_of_trajectory"])
                sinu_encounter_soc[-1].append(max_sinu_non_group[i]["max_lateral_sinuosity"])
                length_encounter_soc[-1].append(max_sinu_non_group[i]["length_of_trajectory"])

            mean_sinu_encounter_soc[-1].append(np.nanmean(intermediate))
            mean_length_encounter_soc[-1].append(np.nanmean(intermediate_length))

        # Organize value of undisturbed situation in list in order to plot
        sinu_new_baseline_soc = [[] for _ in range(5)]
        length_new_baseline_soc = [[] for _ in range(5)]
        mean_sinu_new_baseline_soc = [[] for _ in range(5)]
        mean_length_new_baseline_soc = [[] for _ in range(5)]

        for group_id in no_encounters_sinuositys["group"]:

            social_binding = no_encounters_sinuositys["group"][group_id]["social_binding"]
            if social_binding not in SOCIAL_BINDING_VALUES:
                print(social_binding, type(social_binding))
                continue

            max_sinu = no_encounters_sinuositys["group"][group_id]["max_sinu"]
            if len(max_sinu) == 0:
                continue
            indice = social_binding

            intermediate = []
            intermediate_length = []
            for i,sinuosity in enumerate(max_sinu):
                
                intermediate.append(max_sinu[i]["max_lateral_sinuosity"])
                intermediate_length.append(max_sinu[i]["length_of_trajectory"])
                sinu_new_baseline_soc[indice].append(max_sinu[i]["max_lateral_sinuosity"])
                length_new_baseline_soc[indice].append(max_sinu[i]["length_of_trajectory"])

            mean_sinu_new_baseline_soc[indice].append(np.nanmean(intermediate))
            mean_length_new_baseline_soc[indice].append(np.nanmean(intermediate_length))

        for non_group_id in no_encounters_sinuositys["non_group"]:
            
            max_sinu = no_encounters_sinuositys["non_group"][non_group_id]["max_sinu"]
            if len(max_sinu) == 0:
                continue

            intermediate = []
            intermediate_length = []
            for i,sinuosity in enumerate(max_sinu):

                intermediate.append(max_sinu[i]["max_lateral_sinuosity"])
                intermediate_length.append(max_sinu[i]["length_of_trajectory"])
                sinu_new_baseline_soc[-1].append(max_sinu[i]["max_lateral_sinuosity"])
                length_new_baseline_soc[-1].append(max_sinu[i]["length_of_trajectory"])

            mean_sinu_new_baseline_soc[-1].append(np.nanmean(intermediate))
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
            plot_label[0] += f"{len(sinu_encounter_soc[i])} / {global_mean_all_encounter_length} m"
            plot_label[1] += f"{len(sinu_new_baseline_soc[i])} / {global_mean_all_new_baseline_length} m"

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Encounter situation vs. new baseline situation")
            ax.set_xlabel("Social binding / value / length of trajectory")
            ax.set_ylabel("Lateral sinuosity (m)")
            all_data = [sinu_encounter_soc[i], sinu_new_baseline_soc[i]]

            ax.boxplot(all_data, labels = plot_label ,showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            
            plt.savefig(f"../data/figures/deflection/will/boxplot/versus/all/encounter_new_baseline_{env_name_short}_{SOC_BINDING_NAMES[i]}.png")
            plt.close()



            plot_label = PLOT_LABEL.copy()
            plot_label[0] += f"{len(mean_sinu_encounter_soc[i])} / {global_mean_mean_encounter_length} m"
            plot_label[1] += f"{len(mean_sinu_new_baseline_soc[i])} / {global_mean_mean_new_baseline_length} m"

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Encounter situation vs. new baseline situation")
            ax.set_xlabel("Social binding / value")
            ax.set_ylabel("Lateral sinuosity (m)")
            mean_data = [mean_sinu_encounter_soc[i], mean_sinu_new_baseline_soc[i]]

            ax.boxplot(mean_data, labels = plot_label ,showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)

            plt.savefig(f"../data/figures/deflection/will/boxplot/versus/mean/encounter_new_baseline_mean_{env_name_short}_{SOC_BINDING_NAMES[i]}.png")
            plt.close()

            # ANOVA
            if ANOVA:
                name_of_the_file = f"../data/report_text/deflection/will/versus/all_data/{ANOVA_SAVE}ANOVA_{SOC_BINDING_NAMES[i]}.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*all_data)
                    f.write(f"ANOVA for mean max sinuosity for social binding {SOC_BINDING_NAMES[i]}\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")

                name_of_the_file = f"../data/report_text/deflection/will/versus/mean_data/{ANOVA_SAVE}ANOVA_{SOC_BINDING_NAMES[i]}.txt"
                if os.path.exists(name_of_the_file):
                    os.remove(name_of_the_file)
                with open(name_of_the_file, "a") as f :
                    f.write("-----------------------------------------------------------\n")
                    result = f_oneway(*mean_data)
                    f.write("ANOVA for mean max sinuosity for social binding {SOC_BINDING_NAMES[i]}\n")
                    f.write("F-value : {0}\n".format(result[0]))
                    f.write("p-value : {0}\n".format(result[1]))
                    f.write("-----------------------------------------------------------\n")



