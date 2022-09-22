from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from parameters import *
from utils import *

import scipy.stats as stats


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        # if "atc" in env_name:
        #     soc_binding_values = [1, 2]

        observed_minimum_distances_with_interaction = pickle_load(
            f"../data/pickle/observed_minimum_distance_{env_name_short}_with_interaction.pkl"
        )
        straight_line_minimum_distances_with_interaction = pickle_load(
            f"../data/pickle/straight_line_minimum_distance_{env_name_short}_with_interaction.pkl"
        )

        observed_minimum_distances_without_interaction = pickle_load(
            f"../data/pickle/observed_minimum_distance_{env_name_short}_without_interaction.pkl"
        )
        straight_line_minimum_distances_without_interaction = pickle_load(
            f"../data/pickle/straight_line_minimum_distance_{env_name_short}_without_interaction.pkl"
        )

        group_size_all = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")
        group_breadth_all = pickle_load(
            f"../data/pickle/group_breadth_{env_name_short}.pkl"
        )

        values_per_bin = []

        bin_size = 4 / N_BINS_RP
        pdf_edges = np.linspace(0, 4, N_BINS_RP + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        fig, ax = plt.subplots()

        for k in range(N_BINS_RP):
            bin_values = []
            for i, v in enumerate(soc_binding_values):
                straight_line = straight_line_minimum_distances_with_interaction[
                    v
                ] / np.nanmean(group_size_all[v])
                observed = observed_minimum_distances_with_interaction[v] / np.nanmean(
                    group_size_all[v]
                )
                bin_ids = np.digitize(straight_line, pdf_edges[1:])

                bin_values += [observed[bin_ids == k]]
            values_per_bin += [bin_values]

        p_values = []

        for i in range(len(values_per_bin)):
            # for j in range(len(values_per_bin[i])):
            #     print(len(values_per_bin[i][j]))

            F, p = stats.f_oneway(*values_per_bin[i])
            # print(f"bin {i}: {round(p,3)}")
            p_values += [p]

        data = np.array([bin_centers, p_values]).T
        pd.DataFrame(data).to_csv(
            f"../data/plots/distance_anovas/{env_name_short}_pvalues.csv",
            index=False,
            header=False,
        )

        # plt.plot(p_values)
        # plt.show()
