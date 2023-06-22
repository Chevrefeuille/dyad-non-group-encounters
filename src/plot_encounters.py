import matplotlib.pyplot as plt
import numpy as np
from pedestrians_social_binding.utils import *
from sklearn.feature_selection import f_oneway
import os



SOCIAL_BINDING = {"0": 0, "1": 1, "2": 2, "3": 3, "other": 4, "alone": 5}

PLOT_SOC_DEVIATION = True

ANOVA = True

SPEED_INTERVAL = True



if __name__ == "__main__":
    for env_name in ["diamor:corridor"]:
        env_name_short = env_name.split(":")[0]
        dict_deviation = pickle_load(f"../data/pickle/{env_name_short}_encounters_deviations.pkl")
        deviation_soc = [[] for i in range(6)]
        deviation_soc_diff = [[] for i in range(5)]
        speed_soc = [[] for i in range(6)]
        mean_deviation_soc = [[] for i in range(6)]
        new_label = ["0", "1", "2", "3", "other", "alone"]
        group_alone_label = ["group", "alone"]

        for group_id in dict_deviation["group"]:
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

            
        non_group_average = [np.mean(deviation_soc[5])]
        flattened_list = [y for x in deviation_soc[:-1] for y in x]
        group_average = [np.mean(flattened_list)]

        len_deviation_soc = [len(deviation_soc[i]) for i in range(6)] 
        mean_deviation_soc = [np.mean(deviation_soc[i]) for i in range(6)]
        mean_speed_soc = [np.mean(speed_soc[i]) for i in range(6)]

        for i in range(6):
            new_label[i] = new_label[i] + " / " + str(len_deviation_soc[i])

        group_alone_label[0] = group_alone_label[0] + " / " + str(len(flattened_list))
        group_alone_label[1] = group_alone_label[1] + " / " + str(len(deviation_soc[5]))
        

        if(PLOT_SOC_DEVIATION) :

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the social binding")
            ax.set_xlabel("Social binding / Number of encounters")
            ax.set_ylabel("Maximum lateral deviation (m)")
            ax.boxplot(deviation_soc, labels=new_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                          , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/{env_name_short}_deviation_soc.png")
            plt.close(fig)

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Mean deviation for group / alone encounters")
            ax.set_xlabel("Social binding / Number of encounters")
            ax.set_ylabel("Mean maximum lateral deviation (m)")
            ax.boxplot([flattened_list, deviation_soc[5]], labels=group_alone_label, showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black')
                            , medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                                boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/{env_name_short}_deviation_group_alone.png")
            plt.close(fig)

            if(ANOVA):
                name_of_the_file = "../data/report_text/deflection/will/encounter/ANOVA_for_mean_max_deviation.txt"
                if not os.path.exists(name_of_the_file):
                    with open(name_of_the_file, "a") as f :
                        f.write("-----------------------------------------------------------\n")
                        result = f_oneway(deviation_soc[0], deviation_soc[1], deviation_soc[2], deviation_soc[3], deviation_soc[4], deviation_soc[5])
                        f.write("ANOVA for mean max deviation in function of the social binding in encounter situation\n")
                        f.write("F-value : {0}\n".format(result[0]))
                        f.write("p-value : {0}\n".format(result[1]))
                        f.write("-----------------------------------------------------------\n")

            

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation difference in function of the social binding")
            ax.set_xlabel("Social binding / Number of encounters")
            ax.set_ylabel("Maximum lateral deviation (m)")
            ax.boxplot(deviation_soc_diff, labels=new_label[:-1], showmeans = True, meanline = True, showfliers = False, meanprops = dict(marker='o', markeredgecolor='black', markerfacecolor='black'),
                            medianprops = dict(color = "black"), whiskerprops = dict(color = "black"), capprops = dict(color = "black"),
                            boxprops = dict(color = "black"), patch_artist = True, showbox = True, showcaps = True)
            fig.savefig(f"../data/figures/deflection/will/boxplot/encounter/{env_name_short}_deviation_soc_diff.png")
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
                        print(speed_interval[k][0], speed_soc[i][j], speed_interval[k][1])
                        if(speed_interval[k][0] <= speed_soc[i][j] < speed_interval[k][1]) :
                            dict_speed_interval[speed_interval[k]][label].append(deviation_soc[i][j])
                            list_of_speed_interval[k].append(deviation_soc[i][j])
                            break


            mean_deviation_for_speed_interval = [np.mean(list_of_speed_interval[i]) for i in range(len(list_of_speed_interval))]
            str_speed_interval = []
            for elt in speed_interval :
                str_speed_interval.append(str(elt))

            fig,ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the speed interval")
            ax.set_xlabel("Speed interval (m/s)")
            ax.set_ylabel("Maximum lateral deviation (m)")
            ax.plot(str_speed_interval, mean_deviation_for_speed_interval, marker = "o")
            
            plt.show()