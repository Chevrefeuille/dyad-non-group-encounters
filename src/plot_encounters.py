import matplotlib.pyplot as plt
import numpy as np
from pedestrians_social_binding.utils import *



SOCIAL_BINDING = {"0": 0, "1": 1, "2": 2, "3": 3, "other": 4, "alone": 5}

PLOT_SOC_DEVIATION = True



if __name__ == "__main__":
    for env_name in ["diamor:corridor"]:
        env_name_short = env_name.split(":")[0]
        dict_deviation = pickle_load(f"../data/pickle/{env_name_short}_encounters_deviations.pkl")
        mean_deviation_soc = [[] for i in range(6)]
        new_label = ["0", "1", "2", "3", "other", "alone"]

        for group_id in dict_deviation["group"]:
            soc_binding = dict_deviation["group"][group_id]["social_binding"]
            max_dev_group = dict_deviation["group"][group_id]["group deviation"]
            print(max_dev_group)
            indice = SOCIAL_BINDING[str(soc_binding)]
            print(indice)
            print(type(indice))
            
            mean_deviation_soc[indice] += max_dev_group["max_lateral_deviation"]
        
        len_mean_deviation_soc = [len(mean_deviation_soc[i]) for i in range(6)] 
        mean_deviation_soc = [np.mean(mean_deviation_soc[i]) for i in range(6)]

        for i in range(6):
            new_label[i] = new_label[i] + " / " + str(len_mean_deviation_soc[i])

        if(PLOT_SOC_DEVIATION) :
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.set_title(f"Deviation in function of the social binding")
            ax.set_xlabel("Social binding / Number of encounters")
            ax.set_ylabel("Maximum lateral deviation (m)")
            ax.plot( new_label ,mean_deviation_soc,label="Maximum lateral deviation")
            ax.legend()
            plt.show()