from email import header
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import pandas as pd

from parameters import *
from utils import *


def proportions_ztest2(p1, n1, p2, n2):
    if n1 == 0 or n2 == 0:
        return np.nan, np.nan
    z = (p1 / n1 - p2 / n2) / (
        ((p1 + p2) / (n1 + n2)) * (1 - (p1 + p2) / (n1 + n2)) * (1 / n1 + 1 / n2)
    ) ** 0.5
    return z, stats.norm.sf(abs(z)) * 2


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

        print(f"# {env_name_short}")

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        observed_minimum_distances_with_interaction = pickle_load(
            f"../data/pickle/observed_minimum_distance_{env_name_short}_with_interaction.pkl"
        )
        straight_line_minimum_distances_with_interaction = pickle_load(
            f"../data/pickle/straight_line_minimum_distance_{env_name_short}_with_interaction.pkl"
        )
        group_size_all = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")
        group_breadth_all = pickle_load(
            f"../data/pickle/group_breadth_{env_name_short}.pkl"
        )

        N_BINS = 8

        bin_size = 4 / N_BINS
        pdf_edges = np.linspace(0, 4, N_BINS + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        fig, axes = plt.subplots(2, 2, constrained_layout=True, figsize=(16, 8))
        for index, p_lim in enumerate([0.25, 0.5, 0.75, 1]):
            row = index // 2
            col = index % 2
            p_chi_square = []
            # with scaling
            for k in range(len(pdf_edges[1:])):
                statistics = {}
                contingency_table = np.zeros((3, len(soc_binding_values)))
                for i, v in enumerate(soc_binding_values):
                    observed_values = observed_minimum_distances_with_interaction[
                        v
                    ] / np.nanmean(group_size_all[v])
                    straight_line_values = (
                        straight_line_minimum_distances_with_interaction[v]
                        / np.nanmean(group_size_all[v])
                    )

                    bin_ids = np.digitize(straight_line_values, pdf_edges[1:])
                    observed_for_bin = observed_values[bin_ids == k]
                    n_smaller = np.sum(observed_for_bin < p_lim)
                    n = len(observed_for_bin)
                    n_bigger = n - n_smaller
                    p = n_smaller / n if n else np.nan
                    contingency_table[0, i] = n_smaller
                    contingency_table[1, i] = n_bigger
                    contingency_table[2, i] = round(p, 2)
                    statistics[v] = {
                        "n": len(observed_for_bin),
                        "np": np.sum(observed_for_bin < p_lim),
                    }

                contingency_table = contingency_table[:2, :]
                col_without_zeros = np.sum(contingency_table > 0, axis=0) == 2
                contingency_table_no_zeros = contingency_table[:, col_without_zeros]

                if len(contingency_table_no_zeros[0]):
                    chi_stat, p, dof, expected = stats.chi2_contingency(
                        contingency_table
                    )
                    p_chi_square += [p]
                else:
                    p_chi_square += [np.nan]

            axes[row][col].plot(bin_centers, p_chi_square, "o-")
            axes[row][col].plot([0, 4], [0.05, 0.05], c="red")

            axes[row][col].set_yscale("log")
            axes[row][col].set_ylim([0.0001, 1])
            axes[row][col].set_xlim([-0.1, 4])
            # axes[row][col].legend()
            axes[row][col].set_ylabel(f"p-value p(r_o < {p_lim})")
            axes[row][col].set_xlabel("r_p (scaled with group size)")
            axes[row][col].set_title(f"p-value")
            axes[row][col].grid(color="lightgray", linestyle="--", linewidth=0.5)

            data = np.stack((bin_centers, np.array(p_chi_square))).T
            # pd.DataFrame(data).to_csv(
            #     f"../data/plots/probabilities_pvalues/{env_name_short}_probabilities_pvalues_{p_lim}.csv",
            #     index=False,
            #     header=False,
            # )
        plt.suptitle(env_name_short)
        plt.savefig(
            f"../data/figures/intrusion/probabilities/probabilities_p-values_{env_name_short}.png"
        )
        plt.show()
