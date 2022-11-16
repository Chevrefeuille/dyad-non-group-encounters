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

        N_BINS = 8
        bin_size = 4 / N_BINS
        pdf_edges = np.linspace(0, 4, N_BINS + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        for k in range(N_BINS):
            bin_values = []
            for i, v in enumerate(soc_binding_values):
                rb = straight_line_minimum_distances_with_interaction[v] / np.nanmean(
                    group_size_all[v]
                )
                r0 = observed_minimum_distances_with_interaction[v] / np.nanmean(
                    group_size_all[v]
                )
                bin_ids = np.digitize(rb, pdf_edges[1:])

                bin_values += [r0[bin_ids == k]]
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
        fig, ax = plt.subplots()
        ax.plot(bin_centers, p_values)
        ax.set_ylim([0.0001, 1])
        ax.plot([0, 4], [0.05, 0.05], c="red")
        ax.set_yscale("log")
        ax.grid(color="lightgray", linestyle="--", linewidth=0.5)
        ax.set_ylabel(f"p-value")
        ax.set_xlabel("r_b (scaled with group size)")
        ax.set_title(f"p-value")
        fig.savefig(
            f"../data/figures/intrusion/scattering_p_values_{env_name_short}.png",
            dpi=300,
        )
        plt.show()
