from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from parameters import *
from utils import *


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

        group_size_all = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")
        group_breadth_all = pickle_load(
            f"../data/pickle/group_breadth_{env_name_short}.pkl"
        )

        N_BINS = 8

        # NOT ALONE

        # without scaling
        bin_size = 4 / N_BINS
        pdf_edges = np.linspace(0, 4, N_BINS + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        fig, ax = plt.subplots()

        for i, v in enumerate(soc_binding_values):
            (
                mean_observed_minimum_distance_per_bin,
                stds,
                stdes,
            ) = get_mean_std_ste_over_bins(
                straight_line_minimum_distances_with_interaction[v] / 1000,
                observed_minimum_distances_with_interaction[v] / 1000,
                pdf_edges[1:],
            )
            ax.plot(
                bin_centers,
                mean_observed_minimum_distance_per_bin,
                label=soc_binding_names[v],
                c=soc_binding_colors[v],
            )

        ax.plot(bin_centers, bin_centers, ls="dashed", c="black")
        ax.set_ylim(0, 4)
        ax.set_xlim(0, 4)
        ax.set_ylabel(r"$r_0$")
        ax.set_xlabel(r"$r_b$")
        ax.set_aspect("equal")
        # plt.title(f"{env_name_short}")
        ax.legend()
        ax.grid(color="lightgray", linestyle="--", linewidth=0.5)
        # fig.savefig(
        #     f"../data/figures/intrusion/scattering_{env_name_short}.png",
        #     dpi=300,
        # )
        plt.show()

        # with scaling
        bin_size = 4 / N_BINS
        pdf_edges = np.linspace(0, 4, N_BINS + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        data_bin = np.empty((len(bin_centers), len(soc_binding_values) * 2 + 1))
        data_bin[:, 0] = bin_centers.T
        fig, ax = plt.subplots()
        for i, v in enumerate(soc_binding_values):
            rb = straight_line_minimum_distances_with_interaction[v] / np.nanmean(
                group_size_all[v]
            )
            r0 = observed_minimum_distances_with_interaction[v] / np.nanmean(
                group_size_all[v]
            )

            # indx = r0 >= rb
            # rb = rb[indx]
            # r0 = r0[indx]

            (
                mean_observed_minimum_distance_per_bin,
                stds,
                stdes,
            ) = get_mean_std_ste_over_bins(rb, r0, pdf_edges[1:])
            ax.plot(
                bin_centers,
                mean_observed_minimum_distance_per_bin,
                label=soc_binding_names[v],
                c=soc_binding_colors[v],
            )
            data = np.array(
                [
                    straight_line_minimum_distances_with_interaction[v]
                    / np.nanmean(group_size_all[v]),
                    observed_minimum_distances_with_interaction[v]
                    / np.nanmean(group_size_all[v]),
                ]
            ).T
            # pd.DataFrame(data).to_csv(
            #     f"../data/plots/intrusion/{env_name_short}_{soc_binding_names[v]}_straight_line_vs_observed_scatter.csv",
            #     index=False,
            #     header=False,
            # )

            data_bin[:, 1 + i * 2 : 1 + i * 2 + 2] = np.array(
                [mean_observed_minimum_distance_per_bin, stdes]
            ).T
        pd.DataFrame(data_bin).to_csv(
            f"../data/plots/intrusion/{env_name_short}_straight_line_vs_observed_bin.csv",
            index=False,
            header=False,
        )
        # for p in pdf_edges:
        #     plt.axvline(p, color="b")
        ax.plot(bin_centers, bin_centers, ls="dashed", c="black")
        ax.set_ylim(0, 4)
        ax.set_xlim(0, 4)
        ax.set_ylabel(r"$\bar{r_0}$")
        ax.set_xlabel(r"$\bar{r_b}$")
        ax.set_aspect("equal")
        # plt.title(f"{env_name_short}")
        ax.legend()
        ax.grid(color="lightgray", linestyle="--", linewidth=0.5)
        # fig.savefig(
        #     f"../data/figures/intrusion/scattering_{env_name_short}.png",
        #     dpi=300,
        # )
        plt.show()
