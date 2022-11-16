from email import header
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import numpy as np
from parameters import *
from utils import *

import scipy.stats as stats
import pandas as pd

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
        MIN, MAX = 0, 4
        bin_size = (MAX- MIN) / N_BINS
        pdf_edges = np.linspace(MIN, MAX, N_BINS + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        fig, axes = plt.subplots(2, 2, constrained_layout=True, figsize=(16, 8))
        for n, p_lim in enumerate([0.25, 0.5, 0.75, 1]):
            print(f"------ {p_lim} -------")

            all_probabilities = []
            probabilities_array = np.zeros((len(soc_binding_values), N_BINS))
            errors_array = np.zeros((len(soc_binding_values), N_BINS))

            for i, v in enumerate(soc_binding_values):
                print(soc_binding_names[v])
                r0 = observed_minimum_distances_with_interaction[
                    v
                ] / np.nanmean(group_size_all[v])
                rb = straight_line_minimum_distances_with_interaction[
                    v
                ] / np.nanmean(group_size_all[v])

                # ind_bigger = r0 >= rb  # potential is supposed to never be attractive
                # rb = rb[ind_bigger]
                # r0 = r0[ind_bigger]

                probabilities = []
                errors = []
                for k in range(len(pdf_edges[1:])):
                    bin_ids = np.digitize(rb, pdf_edges[1:])
                    r0_for_bin = r0[bin_ids == k]
                    p = (
                        np.sum(r0_for_bin < p_lim) / len(r0_for_bin)
                        if len(r0_for_bin)
                        else np.nan
                    )
                    print(np.sum(r0_for_bin < p_lim), len(r0_for_bin))
                    probabilities += [p]
                    if len(r0_for_bin):
                        standard_error = (p * (1 - p) / len(r0_for_bin)) ** 0.5
                    else:
                        standard_error = np.nan
                    errors += [standard_error]
        
                # data_bin[:, 1 + i : 2 + i] = np.array(probabilities)[..., None]

                # pd.DataFrame(data_bin).to_csv(
                #     f"../data/plots/probabilities/{env_name_short}_probabilities.csv",
                #     index=False,
                #     header=False,
                # )

                probabilities_array[i, :] = np.array(probabilities)
                errors_array[i, :] = np.array(errors)

            row = n // 2
            col = n % 2

            sum_prob = np.sum(probabilities_array, axis=0)
            values_ok = np.where(sum_prob)
            data_bin = np.empty((len(values_ok[0]), 1 + 2 * len(soc_binding_values)))
            for i, v in enumerate(soc_binding_values):

                axes[row][col].errorbar(
                    bin_centers[values_ok],
                    probabilities_array[i, :][values_ok],
                    yerr=errors_array[i, :][values_ok],
                    fmt="o-",
                    capsize=4,
                    capthick=1,
                    label=soc_binding_names[v],
                    c=soc_binding_colors[v],
                )

                data_bin[:, 0] = bin_centers[values_ok].T
                data_bin[:, 1 + 2 * i] = np.array(probabilities_array[i, :][values_ok])
                data_bin[:, 2 + 2 * i] = np.array(errors_array[i, :][values_ok])

                pd.DataFrame(data_bin).to_csv(
                    f"../data/plots/probabilities/{env_name_short}_probabilities_{p_lim}.csv",
                    index=False,
                    header=False,
                )

            axes[row][col].set_ylim([-0.1, 1])
            axes[row][col].set_xlim([-0.1, 4])
            axes[row][col].legend()
            axes[row][col].set_ylabel(f"p(r_o < {p_lim})")
            axes[row][col].set_xlabel("r_p (scaled with group size)")
            axes[row][col].set_title(f"p(r_o < {p_lim})")
            axes[row][col].grid(color="lightgray", linestyle="--", linewidth=0.5)
            plt.suptitle(env_name_short)
            # plt.savefig(
            #     f"../data/figures/intrusion/probabilities/probabilities_{env_name_short}.png"
            # )
        plt.show()

    