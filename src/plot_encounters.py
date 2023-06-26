import matplotlib.pyplot as plt
import numpy as np
from pedestrians_social_binding.utils import *
from sklearn.feature_selection import f_oneway
import os
from pedestrians_social_binding.constants import *

from tqdm import tqdm




SOCIAL_BINDING = {"0": 0, "1": 1, "2": 2, "3": 3, "other": 4, "alone": 5}

PLOT_SOC_DEVIATION = False

ANOVA = False

SPEED_INTERVAL = True

ALL_TRAJECTORY = True

RESULT_1 = True

RESULT_2 = True

RESULT_3 = True

if __name__ == "__main__":
    for env_name in ["diamor:corridor"]:
        env_name_short = env_name.split(":")[0]

        if (ALL_TRAJECTORY) :  
            dict_deviation = pickle_load(f"../data/pickle/{env_name_short}_encounters_deviations.pkl")
        else :
            pre_dict_deviation = pickle_load(f"../data/pickle/{env_name_short}_encounters_deviations_MAX_DISTANCE.pkl")
            pre_dict_deviation = pre_dict_deviation["MAX_DISTANCE"]

        ind = -1
        while (ind != len(MAX_DISTANCES_INTERVAL)-1) :
            deviation_soc = [[] for i in range(6)]
            deviation_soc_diff = [[] for i in range(5)]
            speed_soc = [[] for i in range(6)]
            length_soc = [[] for i in range(6)]
            mean_deviation_soc = [[] for i in range(6)]
            mean_length_soc = [[] for i in range(6)]
            new_label = ["0", "1", "2", "3", "other", "alone"]
            group_alone_label = ["group", "alone"]
            time_soc = [[] for i in range(6)]


            if (not ALL_TRAJECTORY) :
                ind += 1
                max_distance = MAX_DISTANCES_INTERVAL[ind]
                dict_deviation = pre_dict_deviation[max_distance]
            else :
                ind = len(MAX_DISTANCES_INTERVAL) -1

            for group_id in tqdm(dict_deviation["group"]):
                soc_binding = dict_deviation["group"][group_id]["social_binding"]
                max_dev_group = dict_deviation["group"][group_id]["group deviation"]
                max_dev_non_group = dict_deviation["group"][group_id]["encounters deviation"]

                indice = SOCIAL_BINDING[str(soc_binding)]

                for i in range(len(max_dev_group)):
                    deviation_soc[indice].append(max_dev_group[i]["max_lateral_deviation"])
                    deviation_soc[5].append(max_dev_non_group[i]["max_lateral_deviation"])
                    deviation_soc_diff[indice].append(max_dev_group[i]["max_lateral_deviation"] - max_dev_non_group[i]["max_lateral_deviation"])
                    speed_soc[indice].append(max_dev_group[i]["mean_velocity"])
                    speed_soc[5].append(max_dev_non_group[i]["mean_velocity"])
                    length_soc[indice].append(max_dev_group[i]["length_of_trajectory"])
                    length_soc[5].append(max_dev_non_group[i]["length_of_trajectory"])
                    time_soc[indice].append(max_dev_group[i]["time"])
                    time_soc[5].append(max_dev_non_group[i]["time"])


                
            non_group_average = [np.mean(deviation_soc[5])]
            flattened_list = [y for x in deviation_soc[:-1] for y in x]
            group_average = [np.mean(flattened_list)]

            len_deviation_soc = [len(deviation_soc[i]) for i in range(6)] 
            mean_deviation_soc = [np.mean(deviation_soc[i]) for i in range(6)]
            mean_speed_soc = [np.mean(speed_soc[i]) for i in range(6)]
            mean_length_soc = [np.mean(length_soc[i]) for i in range(6)]

            length_flattened_list = [y for x in length_soc for y in x]
            length_group_average = [np.mean(length_flattened_list)]

            for i in range(6):
                new_label[i] = new_label[i] + " / " + str(len_deviation_soc[i])

            group_alone_label[0] = group_alone_label[0] + " / " + str(len(flattened_list))
            group_alone_label[1] = group_alone_label[1] + " / " + str(len(deviation_soc[5]))
            

            if(PLOT_SOC_DEVIATION) :

                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                if (ALL_TRAJECTORY) :
                    ax.set_title(f"Deviation in function of the social binding")
                else :
                    ax.set_title(f"Deviation in function of the social binding for max distance : {length_group_average}")
                ax.set_xlabel("Social binding / Number of encounters")
                ax.set_ylabel("Maximum lateral deviation (m)")
                ax.boxplot(deviation_soc, labels=new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                            , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                if (ALL_TRAJECTORY) :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/{env_name_short}_deviation_soc.png")
                else :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/max_distance/{env_name_short}_deviation_soc_MAX_DISTANCE_{max_distance}.png")
                plt.close(fig)

                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                if (ALL_TRAJECTORY) :
                    ax.set_title(f"Mean deviation for group / alone encounters")
                else :
                    ax.set_title(f"Mean deviation for group / alone encounters for max distance : {length_group_average}")
                ax.set_xlabel("Social binding / Number of encounters")
                ax.set_ylabel("Mean maximum lateral deviation (m)")
                ax.boxplot([flattened_list, deviation_soc[5]], labels=group_alone_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                                , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                    boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                if (ALL_TRAJECTORY) :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/{env_name_short}_deviation_group_alone.png")
                else :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/max_distance/{env_name_short}_deviation_group_alone_MAX_DISTANCE_{max_distance}.png")
                plt.close(fig)

                if(ANOVA):
                    if(ALL_TRAJECTORY):
                        name_of_the_file = "../data/report_text/deflection/will/encounter/ANOVA_for_mean_max_deviation.txt"
                        if not os.path.exists(name_of_the_file):
                            with open(name_of_the_file, "a") as f :
                                f.write("-----------------------------------------------------------\n")
                                result = f_oneway(deviation_soc[0], deviation_soc[1], deviation_soc[2], deviation_soc[3], deviation_soc[4], deviation_soc[5])
                                f.write("ANOVA for mean max deviation in function of the social binding in encounter situation\n")
                                f.write("F-value : {0}\n".format(result[0]))
                                f.write("p-value : {0}\n".format(result[1]))
                                f.write("-----------------------------------------------------------\n")
                    else :
                        name_of_the_file = "../data/report_text/deflection/will/encounter/ANOVA_for_mean_max_deviation_MAX_DISTANCE_{0}.txt".format(max_distance)
                        if not os.path.exists(name_of_the_file):
                            with open(name_of_the_file, "a") as f :
                                f.write("-----------------------------------------------------------\n")
                                result = f_oneway(deviation_soc[0], deviation_soc[1], deviation_soc[2], deviation_soc[3], deviation_soc[4], deviation_soc[5])
                                f.write("ANOVA for mean max deviation in function of the social binding in encounter situation\n")
                                f.write("F-value : {0}\n".format(result[0]))
                                f.write("p-value : {0}\n".format(result[1]))
                                f.write("-----------------------------------------------------------\n")

                

                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                if (ALL_TRAJECTORY) :
                    ax.set_title(f"Deviation difference in function of the social binding")
                else :
                    ax.set_title(f"Deviation difference in function of the social binding for max distance {length_group_average}")
                ax.set_xlabel("Social binding / Number of encounters")
                ax.set_ylabel("Maximum lateral deviation (m)")
                ax.boxplot(deviation_soc_diff, labels=new_label[:-1], showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                                medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                if(ALL_TRAJECTORY):
                    fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/{env_name_short}_deviation_soc_diff.png")
                else :
                    fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/max_distance/{env_name_short}_deviation_soc_diff_MAX_DISTANCE_{max_distance}.png")
                plt.close(fig)

                if(ANOVA):
                    name_of_the_file = "../data/report_text/deflection/will/encounter/ANOVA_for_mean_max_deviation_diff.txt"
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
                                dict_speed_interval[speed_interval[k]][label].append([deviation_soc[i][j],time_soc[i][j]])
                                list_of_speed_interval[k].append([deviation_soc[i][j],time_soc[i][j]])
                                break

                if(RESULT_1) :
                    for interval in speed_interval :
                        for label in dict_speed_interval[interval].keys() :
                            X, Y = [], []
                            if(len(dict_speed_interval[interval][label]) > 0) :
                                for elt in dict_speed_interval[interval][label] :
                                    X.append(elt[1])
                                    Y.append(elt[0])

                            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                            ax.scatter(X, Y, label = f"speed interval = {interval} / label = {label} ")
                            ax.set_xlabel("Time (s)")
                            ax.set_ylabel("Maximum lateral deviation (m)")
                            if (ALL_TRAJECTORY) :
                                ax.set_title(f"Deviation in function of the time travelling")
                                fig.savefig(f"../data/figures/result/1/{label}/{env_name_short}_{label}_{interval}.png")
                            else :
                                ax.set_title(f"Deviation in function of the speed interval for a maximum distance of {length_group_average} m")
                                fig.savefig(f"../data/figures/result/1.1/{label}/{env_name_short}_{label}_{interval}_{max_distance}.png")
                            plt.close(fig)

                # time_interval = [(500,1000),(1000,1500),(1500,2000),(2000,2500),(2500,3000),(3000,3500),(3500,4000),(4000,10000)]
                time_interval = [(2500,2750),(2750,3000),(3000,3250),(3250,3500),(3500,3750),(3750,4000)]
                # time_interval = [(2750,2875),(2875,3000),(3000,3125),(3125,3250),(3250,3375),(3375,3500)]

                list_of_time_interval = [[] for i in range(len(time_interval))]
                dict_time_interval = {}
                for i in range(len(time_interval)) :
                    dict_time_interval[time_interval[i]] = {"0" : [], "1" : [], "2" : [], "3" : [], "other" : [], "alone" : []}

                i = -1
                for label in SOCIAL_BINDING.keys() :
                    i += 1
                    for j in range(len(time_soc[i])) :
                        for k in range(len(time_interval)) :
                            if(time_interval[k][0] <= time_soc[i][j] < time_interval[k][1]) :
                                dict_time_interval[time_interval[k]][label].append([deviation_soc[i][j],speed_soc[i][j]])
                                list_of_time_interval[k].append([deviation_soc[i][j],speed_soc[i][j]])
                                break
                            
                if(RESULT_2) :
                    for interval in time_interval :
                        for label in dict_time_interval[interval].keys() :
                            X, Y = [], []
                            if(len(dict_time_interval[interval][label]) > 0) :
                                for elt in dict_time_interval[interval][label] :
                                    X.append(elt[1])
                                    Y.append(elt[0])

                            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                            ax.scatter(X, Y, label = f"time interval = {interval} / label = {label} ")
                            ax.set_xlabel("Speed (m/s)")
                            ax.set_ylabel("Deviation (m)")
                            if (ALL_TRAJECTORY) :
                                ax.set_title(f"Deviation in function of the speed")
                                fig.savefig(f"../data/figures/result/2/{label}/{env_name_short}_{label}_{interval}.png")
                            else :
                                ax.set_title(f"Deviation in function of the speed interval for a maximum distance of {length_group_average} m")
                                fig.savefig(f"../data/figures/result/2.1/{label}/{env_name_short}_{label}_{interval}_{max_distance}.png")
                            plt.close(fig)

                else :
                    mean_deviation_for_speed_interval = [np.mean(list_of_speed_interval[i]) for i in range(len(list_of_speed_interval))]
                    str_speed_interval = []
                    for elt in speed_interval :
                        str_speed_interval.append(str(elt))

                    fig,ax = plt.subplots(1, 1, figsize=(10, 10))
                    if (ALL_TRAJECTORY) :
                        ax.set_title(f"Deviation in function of the speed interval")
                    else :
                        ax.set_title(f"Deviation in function of the speed interval for a maximum distance of {length_group_average} m")
                    ax.set_xlabel("Speed interval (m/s)")
                    ax.set_ylabel("Maximum lateral deviation (m)")
                    ax.plot(str_speed_interval, mean_deviation_for_speed_interval, marker = "o")
                    if (ALL_TRAJECTORY) :
                        fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/speed/{env_name_short}_deviation_speed_interval.png")
                    else :
                        fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/max_distance/speed/{env_name_short}_deviation_speed_interval_MAX_DISTANCE_{max_distance}.png")
                    plt.close(fig)

                    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                    if (ALL_TRAJECTORY) :
                        ax.set_title(f"Mean speed in function of the social binding")
                    else :
                        ax.set_title(f"Mean speed in function of the social binding for a maximum distance of {length_group_average} m")
                    ax.set_xlabel("Social binding / Number of encounters")
                    ax.set_ylabel("Mean speed (m/s)")
                    ax.boxplot(speed_soc, labels=new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                            medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                    if (ALL_TRAJECTORY) :
                        fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/speed/{env_name_short}_speed_for_soc_binding.png")
                    else :
                        fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/max_distance/speed/{env_name_short}_speed_for_soc_binding_MAX_DISTANCE_{max_distance}.png")
                    plt.close(fig)

                    for social_binding in SOCIAL_BINDING.keys() :
                        list_of_data = []
                        encounters_label = str_speed_interval.copy()
                        fig,ax = plt.subplots(1, 1, figsize=(15, 10))
                        if (ALL_TRAJECTORY) :
                            ax.set_title(f"Mean deviation in function of the speed interval for social binding : {length_group_average}")
                        else :
                            ax.set_title(f"Mean deviation in function of the speed interval for social binding : {social_binding} and max distance : {max_distance}")
                        ax.set_xlabel("Speed interval (m/s) / number of encounters")
                        ax.set_ylabel("Mean deviation (m)")
                        for i,speed in enumerate(speed_interval) :
                            list_of_data.append(dict_speed_interval[speed][social_binding])
                            encounters_label[i] += f" / {len(list_of_data[-1])}"
                        
                        ax.boxplot(list_of_data, labels=encounters_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                                    medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                    boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                        if (ALL_TRAJECTORY) :
                            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/speed/{env_name_short}_deviation_speed_interval_{social_binding}.png")
                        else :
                            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/max_distance/speed/{env_name_short}_deviation_speed_interval_{social_binding}_MAX_DISTANCE_{max_distance}.png")
                        plt.close(fig)


            


