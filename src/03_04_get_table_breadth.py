from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from parameters import *

import numpy as np
import matplotlib.pyplot as plt

""" The goal of this script is to print the table of the breadth distributions of the groups in the corridor environment considering groups without
 interaction."""

if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:

        print(env_name)
        days = DAYS_ATC if env_name == "atc" else DAYS_DIAMOR
        soc_binding_type = "soc_rel" if env_name == "atc" else "interaction"
        soc_binding_names = (
            SOCIAL_RELATIONS_EN if env_name == "atc" else INTENSITIES_OF_INTERACTION_NUM
        )
        soc_binding_values = [2, 1, 3, 4] if env_name == "atc" else [0, 1, 2, 3]

        breadth = pickle_load(
            f"../data/pickle/group_breadth_with_interaction_{env_name}.pkl"
        )

        # plot pdf without interaction
        for i in soc_binding_values:
            breadth_values_without_interaction = np.array(breadth[i]) / 1000
            print(
                f"{soc_binding_names[i]} & ${round(np.nanmean(breadth_values_without_interaction),2)} \pm {round(np.nanstd(breadth_values_without_interaction),2)}$"
            )
