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
PLOT_NG = True

# Old parameters
ANOVA = False
SPEED_INTERVAL = False
SPEED_GLOBAL = False
SPEED_INTERVAL_2 = False
PLOT_SPEED = False
PLOT_TIME = False
PLOT_LENGTH = False


SOCIAL_BINDING = {"0": 0, "1": 1, "2": 2, "3": 3, "other": 4, "alone": 5}
LIST_OF_SOCIAL_BINDING = ["0", "1", "2", "3", "other", "alone"]




if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env_name_short = env_name.split(":")[0] 
        dict_deviation = pickle_load(f"../data/pickle/{env_name_short}_encounters_deviations.pkl")

        group_alone_label = ["group", "alone"]

        # These lists are used to compute metrics (various value for each group or pedestrian)
        deviation_soc = [[] for i in range(6)]
        deviation_soc_diff = [[] for i in range(5)]
        speed_soc = [[] for i in range(6)]
        length_soc = [[] for i in range(6)]
        time_soc = [[] for i in range(6)]

        # These lists are used to compute metrics (1 values for each group or pedestrian)
        total_soc_dev = [[] for i in range(6)]
        total_soc_length = [[] for i in range(6)]
        total_soc_speed = [[] for i in range(6)]
        total_soc_time = [[] for i in range(6)]
        total_soc_dev_diff = [[] for i in range(5)]

        # Same idea but for alone people in function of the social binding they encounter
        n_g_total_soc_dev = [[] for i in range(5)]
        n_g_total_soc_length = [[] for i in range(5)]
        n_g_total_soc_speed = [[] for i in range(5)]
        n_g_total_soc_time = [[] for i in range(5)]

        n_g_deviation_soc = [[] for i in range(5)]
        n_g_speed_soc = [[] for i in range(5)]
        n_g_length_soc = [[] for i in range(5)]



        for group_id in dict_deviation["group"]:
            soc_binding = dict_deviation["group"][group_id]["social_binding"]
            max_dev_group = dict_deviation["group"][group_id]["group deviation"]
            max_dev_non_group = dict_deviation["group"][group_id]["encounters deviation"]

            indice = SOCIAL_BINDING[str(soc_binding)]
            intermediate_deviation = []
            intermediate_length = []
            intermediate_speed = []
            intermediate_time = []

            n_g_intermediate_deviation = []
            n_g_intermediate_length = []
            n_g_intermediate_speed = []
            n_g_intermediate_time = []

            for i,deviation in enumerate(max_dev_group):

                intermediate_deviation.append(max_dev_group[i]["max_lateral_deviation"])
                intermediate_length.append(max_dev_group[i]["length_of_trajectory"])
                intermediate_speed.append(max_dev_group[i]["mean_velocity"])
                intermediate_time.append(max_dev_group[i]["time"])

                deviation_soc[indice].append(max_dev_group[i]["max_lateral_deviation"])
                deviation_soc_diff[indice].append(max_dev_group[i]["max_lateral_deviation"] - max_dev_non_group[i]["max_lateral_deviation"])
                speed_soc[indice].append(max_dev_group[i]["mean_velocity"])
                length_soc[indice].append(max_dev_group[i]["length_of_trajectory"])
                time_soc[indice].append(max_dev_group[i]["time"])

            for i,deviation in enumerate(max_dev_non_group):

                deviation_soc[5].append(max_dev_non_group[i]["max_lateral_deviation"])
                speed_soc[5].append(max_dev_non_group[i]["mean_velocity"])
                length_soc[5].append(max_dev_non_group[i]["length_of_trajectory"])
                time_soc[5].append(max_dev_non_group[i]["time"])

                n_g_deviation_soc[indice].append(max_dev_non_group[i]["max_lateral_deviation"])
                n_g_speed_soc[indice].append(max_dev_non_group[i]["mean_velocity"])
                n_g_length_soc[indice].append(max_dev_non_group[i]["length_of_trajectory"])

                n_g_intermediate_deviation.append(max_dev_non_group[i]["max_lateral_deviation"])
                n_g_intermediate_length.append(max_dev_non_group[i]["length_of_trajectory"])
                n_g_intermediate_speed.append(max_dev_non_group[i]["mean_velocity"])
                n_g_intermediate_time.append(max_dev_non_group[i]["time"])

            if (len(intermediate_deviation) != 0) :
                total_soc_dev[indice].append(np.nanmean(intermediate_deviation))
            if (len(n_g_intermediate_deviation) != 0) :
                total_soc_dev[5].append(np.nanmean(n_g_intermediate_deviation))
                n_g_total_soc_dev[indice].append(np.nanmean(n_g_intermediate_deviation))
            if (len(intermediate_deviation) != 0 and len(n_g_intermediate_deviation) != 0) :
                total_soc_dev_diff[indice].append(np.nanmean(intermediate_deviation) - np.nanmean(n_g_intermediate_deviation))
            if (len(intermediate_speed) != 0) :
                total_soc_speed[indice].append(np.nanmean(intermediate_speed))
            if (len(n_g_intermediate_speed) != 0) :
                total_soc_speed[5].append(np.nanmean(n_g_intermediate_speed))
            if (len(intermediate_length) != 0) :
                total_soc_length[indice].append(np.nanmean(intermediate_length))
            if (len(n_g_intermediate_length) != 0) :
                total_soc_length[5].append(np.nanmean(n_g_intermediate_length))
            if (len(intermediate_time) != 0) :
                total_soc_time[indice].append(np.nanmean(intermediate_time))
            if (len(n_g_intermediate_time) != 0) :
                total_soc_time[5].append(np.nanmean(n_g_intermediate_time))

            

        # Here we compute the average of the deviation for each group
        non_group_average = [np.mean(deviation_soc[5])]
        flattened_list = [y for x in deviation_soc[:-1] for y in x]
        group_average = [np.mean(flattened_list)]

        len_deviation_soc = [len(deviation_soc[i]) for i in range(6)]
        mean_deviation_soc = [np.mean(deviation_soc[i]) for i in range(6)]
        mean_speed_soc = [np.mean(speed_soc[i]) for i in range(6)]
        mean_length_soc = [np.mean(length_soc[i]) for i in range(6)]

        length_flattened_list = [y for x in length_soc for y in x]
        length_group_average = np.around(np.mean(length_flattened_list)/1000, decimals=4)

        time_flattened_list = [y for x in time_soc for y in x]
        time_group_average = np.around(np.mean(time_flattened_list)/1000, decimals=3)

        new_label = LIST_OF_SOCIAL_BINDING.copy()
        for i in range(6):
            new_label[i] = new_label[i] + " / " + str(len(total_soc_dev[i])) + " / " + str(len_deviation_soc[i])

        n_g_new_label = LIST_OF_SOCIAL_BINDING.copy()[:-1]

        len_n_g_deviation_soc = [len(n_g_deviation_soc[i]) for i in range(5)]

        for i in range(5) :
            n_g_new_label[i] = n_g_new_label[i] + " / " + str(len(n_g_total_soc_dev[i])) + " / " + str(len_n_g_deviation_soc[i])
        del(n_g_new_label[4])
        del(n_g_deviation_soc[4])

        group_alone_label[0] = group_alone_label[0] + " / " + str(len(flattened_list))
        group_alone_label[1] = group_alone_label[1] + " / " + str(len(deviation_soc[5]))

        if(PLOT_SOC_DEVIATION) :

            plot_data = deviation_soc.copy()
            plot_label = LIST_OF_SOCIAL_BINDING.copy()
            for i in range(6) :
                plot_label[i] = plot_label[i] + " / " + str(len(plot_data[i]))
            
            del(plot_data[4])
            del(plot_label[4])

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the social binding in encounter situation : {length_group_average} meters  |  {time_group_average} s")
            ax.set_xlabel("Social binding / data")
            ax.set_ylabel("Maximum lateral deviation (m)")

            ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            # ax.boxplot(total_soc_dev, labels=new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
            #         , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
            #     
            #         boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{env_name_short}_deviation.png")
            plt.close()

            plot_data =total_soc_dev.copy()
            plot_label = LIST_OF_SOCIAL_BINDING.copy()
            for i in range(6) :
                plot_label[i] = plot_label[i] + " / " + str(len(plot_data[i]))

            del(plot_data[4])
            del(plot_label[4])

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the social binding in encounter situation : {np.around(np.mean(mean_length_soc))} meters  |  {time_group_average} s")

            ax.set_xlabel("Social binding / Group")
            ax.set_ylabel("Maximum lateral deviation (m)")

            ax.boxplot(plot_data, labels=plot_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            # ax.boxplot(total_soc_dev, labels=new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
            #         , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
            #     
            #         boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/mean_data/{env_name_short}_deviation.png")
            plt.close()



        if(PLOT_NG) :
            
            del(n_g_total_soc_dev[4])

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.boxplot(n_g_deviation_soc, labels=n_g_new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
            ax.set_title(f"Deviation for alone people in function of the social binding of their encounter / {length_group_average} meters")
            ax.set_xlabel("Social binding / Group / data")
            ax.set_ylabel("Maximum lateral deviation (m)")
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{env_name_short}_deviation_alone.png")
            plt.close(fig)

            fig,ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.boxplot(n_g_total_soc_dev, labels=n_g_new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
            ax.set_title(f"Deviation for alone people in function of the social binding of their encounter / {np.around(np.mean(mean_length_soc))} meters")
            ax.set_xlabel("Social binding / Group / data")
            ax.set_ylabel("Maximum lateral deviation (m)")
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/mean_data/{env_name_short}_deviation_alone.png")
            plt.close(fig)

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Mean deviation for group / alone encounters")
            ax.set_xlabel("Social binding / Number of encounters")
            ax.set_ylabel("Mean maximum lateral deviation (m)")
            ax.boxplot([flattened_list, deviation_soc[5]], labels=group_alone_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                            , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{env_name_short}_deviation_group_alone.png")
            plt.close(fig)

            if(ANOVA):
                name_of_the_file = "../data/report_text/deflection/will/encounter/all_data/ANOVA_for_mean_max_deviation_MAX_DISTANCE_{0}.txt".format(max_distance)
                if not os.path.exists(name_of_the_file):
                    with open(name_of_the_file, "a") as f :
                        f.write("-----------------------------------------------------------\n")
                        result = f_oneway(deviation_soc[0], deviation_soc[1], deviation_soc[2], deviation_soc[3], deviation_soc[4], deviation_soc[5])
                        f.write("ANOVA for mean max deviation in function of the social binding in encounter situation\n")
                        f.write("F-value : {0}\n".format(result[0]))
                        f.write("p-value : {0}\n".format(result[1]))
                        f.write("-----------------------------------------------------------\n")
            
        if(PLOT_LENGTH) :
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Length of the trajectory in function of the social binding / {length_group_average} meters  |  {time_group_average} s")
            ax.set_xlabel("Social binding / Group / data")
            ax.set_ylabel("Length of the trajectory (m)")
            ax.boxplot(length_soc, labels=new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{env_name_short}_length.png")
            plt.close()

        if(PLOT_SPEED) :
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Speed in function of the social binding / {length_group_average} meters  |  {time_group_average} s")
            ax.set_xlabel("Social binding / Group / data")
            ax.set_ylabel("Speed (m/s)")
            ax.boxplot(speed_soc, labels=new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{env_name_short}_speed.png")
            plt.close()

        if(PLOT_TIME) :
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Time in function of the social binding / {length_group_average} meters  |  {time_group_average} s")
            ax.set_xlabel("Social binding / Group / data")
            ax.set_ylabel("Time (s)")
            ax.boxplot(time_soc, labels=new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                        , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist=True, showbox = True, showcaps = True)
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{env_name_short}_time.png")
            plt.close()


            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation difference in function of the social binding / {length_group_average}")
            ax.set_xlabel("Social binding / Number of encounters")
            ax.set_ylabel("Maximum lateral deviation (m)")
            ax.boxplot(deviation_soc_diff, labels=new_label[:-1], showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                            medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/{env_name_short}_deviation_soc_diff.png")
            plt.close(fig)

            if(ANOVA):
                name_of_the_file = "../data/report_text/deflection/will/encounter/all_data/ANOVA_for_mean_max_deviation_diff.txt"
                if not os.path.exists(name_of_the_file):
                    with open(name_of_the_file, "a") as f :
                        f.write("-----------------------------------------------------------\n")
                        result = f_oneway(deviation_soc_diff[0], deviation_soc_diff[1], deviation_soc_diff[2], deviation_soc_diff[3], deviation_soc_diff[4])
                        f.write("ANOVA for mean max deviation difference in function of the social binding in encounter situation\n")
                        f.write("F-value : {0}\n".format(result[0]))
                        f.write("p-value : {0}\n".format(result[1]))
                        f.write("-----------------------------------------------------------\n")

        if(SPEED_INTERVAL) :
            # Create a dictionnary with the speed interval as key and the mean max deviation for each social binding
            speed_interval = [(0,0.5),(0.5,0.75),(0.75,1),(1,1.25),(1.25,1.5),(1.5,2),(2,2.5),(2,5,10)]
            list_of_speed_interval = [[] for i in range(len(speed_interval))]
            dict_speed_interval = {}
            for i in range(len(speed_interval)) :
                dict_speed_interval[speed_interval[i]] = {"0" : [], "1" : [], "2" : [], "3" : [], "other" : [], "alone" : []}

            i = -1
            for label in SOCIAL_BINDING.keys() :
                i += 1
                for j in range(len(speed_soc[i])) :
                    for k in range(len(speed_interval)) :
                        if(speed_interval[k][0] <= speed_soc[i][j] < speed_interval[k][1]) :
                            dict_speed_interval[speed_interval[k]][label].append(deviation_soc[i][j])
                            list_of_speed_interval[k].append(deviation_soc[i][j])
                            break

            # Create a boxplot for each speed interval
            for i,interval in enumerate(speed_interval) :
                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                ax.set_title(f"Deviation in function of the social binding for speed interval {interval}")
                ax.set_xlabel("Social binding / Number of encounters")
                ax.set_ylabel("Maximum lateral deviation (m)")
                label = LIST_OF_SOCIAL_BINDING.copy()
                for j,name in enumerate(LIST_OF_SOCIAL_BINDING) :
                    label[j] = label[j] + " / " + str(len(dict_speed_interval[interval][name]))

                ax.boxplot([dict_speed_interval[interval][name] for name in LIST_OF_SOCIAL_BINDING], labels=label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                                medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/speed_interval/{env_name_short}_deviation_speed_interval_{interval}.png")
                plt.close(fig)

            if (SPEED_GLOBAL) :
                mean_deviation_for_speed_interval = [np.mean(list_of_speed_interval[i]) for i in range(len(list_of_speed_interval))]
                str_speed_interval = []
                for elt in speed_interval :
                    str_speed_interval.append(str(elt))

                fig,ax = plt.subplots(1, 1, figsize=(10, 10))
                ax.set_title(f"Deviation in function of the speed interval")
                ax.set_xlabel("Speed interval (m/s)")
                ax.set_ylabel("Maximum lateral deviation (m)")
                ax.plot(str_speed_interval, mean_deviation_for_speed_interval, marker = "o")
                fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/speed/{env_name_short}_deviation_speed_interval.png")
                plt.close(fig)

                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                ax.set_title(f"Mean speed in function of the social binding")
                ax.set_xlabel("Social binding / Number of encounters")
                ax.set_ylabel("Mean speed (m/s)")
                ax.boxplot(speed_soc, labels=new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                        medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/speed/{env_name_short}_speed_for_soc_binding.png")
                plt.close(fig)

                for social_binding in SOCIAL_BINDING.keys() :
                    list_of_data = []
                    encounters_label = str_speed_interval.copy()
                    fig,ax = plt.subplots(1, 1, figsize=(15, 10))
                    ax.set_title(f"Mean deviation in function of the speed interval for social binding : {length_group_average}")
                    ax.set_xlabel("Speed interval (m/s) / number of encounters")
                    ax.set_ylabel("Mean deviation (m)")
                    for i,speed in enumerate(speed_interval) :
                        list_of_data.append(dict_speed_interval[speed][social_binding])
                        encounters_label[i] += f" / {len(list_of_data[-1])}"
                    
                    ax.boxplot(list_of_data, labels=encounters_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                                medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                    fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/all_data/speed/{env_name_short}_deviation_speed_interval_{social_binding}.png")
                    plt.close(fig)
