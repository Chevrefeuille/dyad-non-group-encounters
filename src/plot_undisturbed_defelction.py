from parameters import *
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

SPEED_GLOBAL = False

RESULT_1 = False

RESULT_2 = False

RESULT_3 = True

if __name__ == "__main__":
    for env_name in ["diamor:corridor"]:
        env_name_short = env_name.split(":")[0] 

        pre_dict_deviation = pickle_load(f"../data/pickle/undisturbed_deflection_MAX_DISTANCE.plk")

        for max_distance in MAX_DISTANCE_INTERVAL:
            print("MAX_DISTANCE : ", max_distance)
            deviation_soc = [[] for i in range(6)]
            speed_soc = [[] for i in range(6)]
            length_soc = [[] for i in range(6)]
            mean_deviation_soc = [[] for i in range(6)]
            mean_length_soc = [[] for i in range(6)]
            new_label = ["0", "1", "2", "3", "other", "alone"]
            group_alone_label = ["group", "alone"]
            time_soc = [[] for i in range(6)]

            dict_deviation = pre_dict_deviation["MAX_DISTANCE"][max_distance]

            for group_id in dict_deviation["group"]:
                soc_binding = dict_deviation["group"][group_id]["social_binding"]
                max_dev_group = dict_deviation["group"][group_id]["max_dev"]
                indice = SOCIAL_BINDING[str(soc_binding)]

                for i in range(len(max_dev_group)):
                    deviation_soc[indice].append(max_dev_group[i]["max_lateral_deviation"])
                    speed_soc[indice].append(max_dev_group[i]["mean_velocity"])
                    length_soc[indice].append(max_dev_group[i]["length_of_trajectory"])
                    time_soc[indice].append(max_dev_group[i]["time"])

            for non_group_id in dict_deviation["non_group"]:
                max_dev_non_group = dict_deviation["non_group"][non_group_id]["max_dev"]

                for i in range(len(max_dev_non_group)):
                    deviation_soc[5].append(max_dev_non_group[i]["max_lateral_deviation"])
                    speed_soc[5].append(max_dev_non_group[i]["mean_velocity"])
                    length_soc[5].append(max_dev_non_group[i]["length_of_trajectory"])
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
                ax.set_title(f"Deviation in function of the social binding for max distance : {length_group_average}")
                ax.set_xlabel("Social binding / Number of encounters")
                ax.set_ylabel("Maximum lateral deviation (m)")
                ax.boxplot(deviation_soc, labels=new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                            , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)

                fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_2/max_distance/{env_name_short}_deviation_soc_MAX_DISTANCE_{max_distance}.png")
                plt.close(fig)

                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                ax.set_title(f"Mean deviation for group / alone encounters for max distance : {length_group_average}")
                ax.set_xlabel("Social binding / Number of encounters")
                ax.set_ylabel("Mean maximum lateral deviation (m)")
                ax.boxplot([flattened_list, deviation_soc[5]], labels=group_alone_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                                , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                    boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_2/max_distance/{env_name_short}_deviation_group_alone_MAX_DISTANCE_{max_distance}.png")
                plt.close(fig)

                if(ANOVA):
                    name_of_the_file = "../data/report_text/deflection/will/undisturbed_2/ANOVA_for_mean_max_deviation_MAX_DISTANCE_{0}.txt".format(max_distance)
                    if not os.path.exists(name_of_the_file):
                        with open(name_of_the_file, "a") as f :
                            f.write("-----------------------------------------------------------\n")
                            result = f_oneway(deviation_soc[0], deviation_soc[1], deviation_soc[2], deviation_soc[3], deviation_soc[4], deviation_soc[5])
                            f.write("ANOVA for mean max deviation in function of the social binding in encounter situation\n")
                            f.write("F-value : {0}\n".format(result[0]))
                            f.write("p-value : {0}\n".format(result[1]))
                            f.write("-----------------------------------------------------------\n")

                

                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                ax.set_title(f"Deviation difference in function of the social binding for max distance {length_group_average}")
                ax.set_xlabel("Social binding / Number of encounters")
                ax.set_ylabel("Maximum lateral deviation (m)")
                ax.boxplot(deviation_soc_diff, labels=new_label[:-1], showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                                medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)

                fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_2/max_distance/{env_name_short}_deviation_soc_diff_MAX_DISTANCE_{max_distance}.png")
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
                    print("1")
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

                            ax.set_title(f"Deviation in function of the speed interval for a maximum distance of {length_group_average} m")
                            fig.savefig(f"../data/figures/result/undisturbed_2/1.1/{label}/{env_name_short}_{label}_{interval}_{max_distance}.png")
                            plt.close(fig)

                time_interval = [(500,1000),(1000,1500),(1500,2000),(2000,2500),(2500,2750),(2750,3000),(3000,3250),(3250,3500),(3500,3750),(3750,4000),(4000,10000)]
                #time_interval = [(2500,2750),(2750,3000),(3000,3250),(3250,3500),(3500,3750),(3750,4000)]
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
                    print("2")
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
                            ax.set_title(f"Deviation in function of the speed interval for a maximum distance of {length_group_average} m")
                            fig.savefig(f"../data/figures/result/undisturbed_2/2.1/{label}/{env_name_short}_{label}_{interval}_{max_distance}.png")
                            plt.close(fig)

                dict_label = {}
                for i in range(len(time_interval)) :
                    for j in range(len(speed_interval)) :
                        dict_label[(time_interval[i],speed_interval[j])] = {"0" : [], "1" : [], "2" : [], "3" : [], "other" : [], "alone" : []}

                

                if(RESULT_3) :
                    print("3")
                    for group_id in dict_deviation["group"]:
                        soc_binding = dict_deviation["group"][group_id]["social_binding"]
                        max_dev_group = dict_deviation["group"][group_id]["max_dev"]
                        indice = SOCIAL_BINDING[str(soc_binding)]

                        for i in range(len(max_dev_group)):
                            counter_break = False
                            for j in range(len(time_interval)) :
                                for k in range(len(speed_interval)) :
                                    if(time_interval[j][0] <= max_dev_group[i]["time"] < time_interval[j][1] and speed_interval[k][0] <= max_dev_group[i]["mean_velocity"] < speed_interval[k][1]) :
                                        dict_label[(time_interval[j],speed_interval[k])][str(soc_binding)].append(max_dev_group[i]["max_lateral_deviation"])
                                        counter_break = True
                                        break
                                if(counter_break) :
                                    break
                    
                    for non_group_id in dict_deviation["non_group"]:
                        max_dev_non_group = dict_deviation["non_group"][non_group_id]["max_dev"]
                        for i in range(len(max_dev_non_group)) :
                            counter_break = False
                            for j in range(len(time_interval)) :
                                for k in range(len(speed_interval)) :
                                    if(time_interval[j][0] <= max_dev_non_group[i]["time"] < time_interval[j][1] and speed_interval[k][0] <= max_dev_non_group[i]["mean_velocity"] < speed_interval[k][1]) :
                                        dict_label[(time_interval[j],speed_interval[k])]["alone"].append(max_dev_non_group[i]["max_lateral_deviation"])
                                        counter_break = True
                                        break
                                if(counter_break) :
                                    break

                    for speed in speed_interval :
                        for interval in time_interval :
                            Y = [[] for i in range(len(SOCIAL_BINDING.keys()))]
                            Y_group = [[],[]]
                            for label in dict_label[(interval,speed)].keys() :
                                indice = SOCIAL_BINDING[label]
                                if(len(dict_label[(interval,speed)][label]) > 0) :
                                    for elt in dict_label[(interval,speed)][label] :
                                        Y[indice].append(elt)
                                        if indice == "alone" :
                                            Y_group[1].append(elt)
                                        else :
                                            Y_group[0].append(elt)

                                fig, ax = plt.subplots(1, 1, figsize=(10, 10))

                                label = ["0", "1", "2", "3", "other", "alone"]
                                for l,name in enumerate(label) : 
                                    label[l] += f" / {len(Y[SOCIAL_BINDING[name]])})"
                                
                                ax.boxplot(Y, labels=label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                                medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                                ax.set_xlabel("Social binding / Number of pedestrians")
                                ax.set_ylabel("Maximum lateral deviation (m)")

                                ax.set_title(f"Deviation in function of the social binding for a maximum distance of {length_group_average} m")
                                name_of_the_file = f"../data/figures/result/undisturbed_2/3.1/{speed}"
                                final_name = name_of_the_file + f"/{env_name_short}_{interval}_{speed}_{max_distance}.png"
                                if (os .path.exists(name_of_the_file)) :
                                    fig.savefig(final_name)
                                else :
                                    os.mkdir(f"../data/figures/result/undisturbed_2/3.1/{speed}")
                                    fig.savefig(final_name)

                                plt.close(fig)


                                fig, ax = plt.subplots(1, 1, figsize=(10, 10))

                                label = ["group", "alone"]
                                for l in range (len(label)) : 
                                    label[l] += f" / {len(Y_group[l])})"

                                ax.boxplot(Y_group, labels=label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                                medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                                ax.set_xlabel("Social binding / Number of pedestrians")
                                ax.set_ylabel("Maximum lateral deviation (m)")

                                ax.set_title(f"Deviation in function of the social binding for a maximum distance of {length_group_average} m")
                                name_of_the_file = f"../data/figures/result/undisturbed_2/3.1/{speed}"
                                final_name = name_of_the_file + f"/{env_name_short}_{interval}_{speed}_{max_distance}.png"
                                if (os .path.exists(name_of_the_file)) :
                                    fig.savefig(final_name)
                                else :
                                    os.mkdir(f"../data/figures/result/undisturbed_2/3.1/{speed}")
                                    fig.savefig(final_name)

                                plt.close(fig)

                if (SPEED_GLOBAL) :
                    mean_deviation_for_speed_interval = [np.mean(list_of_speed_interval[i]) for i in range(len(list_of_speed_interval))]
                    str_speed_interval = []
                    for elt in speed_interval :
                        str_speed_interval.append(str(elt))

                    fig,ax = plt.subplots(1, 1, figsize=(10, 10))
                    ax.set_title(f"Deviation in function of the speed interval for a maximum distance of {length_group_average} m")
                    ax.set_xlabel("Speed interval (m/s)")
                    ax.set_ylabel("Maximum lateral deviation (m)")
                    ax.plot(str_speed_interval, mean_deviation_for_speed_interval, marker = "o")

                    fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_2/max_distance/speed/{env_name_short}_deviation_speed_interval_MAX_DISTANCE_{max_distance}.png")
                    plt.close(fig)

                    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                    ax.set_title(f"Mean speed in function of the social binding for a maximum distance of {length_group_average} m")
                    ax.set_xlabel("Social binding / Number of encounters")
                    ax.set_ylabel("Mean speed (m/s)")
                    ax.boxplot(speed_soc, labels=new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                            medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
 
                    fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_2/max_distance/speed/{env_name_short}_speed_for_soc_binding_MAX_DISTANCE_{max_distance}.png")
                    plt.close(fig)

                    for social_binding in SOCIAL_BINDING.keys() :
                        list_of_data = []
                        encounters_label = str_speed_interval.copy()
                        fig,ax = plt.subplots(1, 1, figsize=(15, 10))

                        ax.set_title(f"Mean deviation in function of the speed interval for social binding : {social_binding} and max distance : {max_distance}")
                        ax.set_xlabel("Speed interval (m/s) / number of encounters")
                        ax.set_ylabel("Mean deviation (m)")
                        for i,speed in enumerate(speed_interval) :
                            list_of_data.append(dict_speed_interval[speed][social_binding])
                            encounters_label[i] += f" / {len(list_of_data[-1])}"
                        
                        ax.boxplot(list_of_data, labels=encounters_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                                    medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                    boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
                        fig.savefig(f"../data/figures/deflection/will/boxplot/undisturbed_2/max_distance/speed/{env_name_short}_deviation_speed_interval_{social_binding}_MAX_DISTANCE_{max_distance}.png")
                        plt.close(fig)


            

