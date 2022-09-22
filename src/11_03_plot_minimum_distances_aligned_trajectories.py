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

        # NOT ALONE

        # without scaling
        bin_size = 4000 / N_BINS_RP
        pdf_edges = np.linspace(0, 4000, N_BINS_RP + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        for i, v in enumerate(soc_binding_values):
            (
                mean_observed_minimum_distance_per_bin,
                stds,
                stdes,
            ) = get_mean_std_ste_over_bins(
                straight_line_minimum_distances_with_interaction[v],
                observed_minimum_distances_with_interaction[v],
                pdf_edges[1:],
            )
            plt.plot(
                bin_centers,
                mean_observed_minimum_distance_per_bin,
                label=soc_binding_names[v],
                c=soc_binding_colors[v],
            )
        plt.ylim(0, 4000)
        plt.xlim(0, 4000)
        plt.title(f"{env_name_short}")
        plt.legend()
        # plt.show()
        plt.close()

        # with scaling
        bin_size = 4 / N_BINS_RP
        pdf_edges = np.linspace(0, 4, N_BINS_RP + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        data_bin = np.empty((len(bin_centers), len(soc_binding_values) * 2 + 1))
        data_bin[:, 0] = bin_centers.T
        fig, ax = plt.subplots()
        for i, v in enumerate(soc_binding_values):
            # if v != 1:
            # continue
            # plt.scatter(
            #     straight_line_minimum_distances_with_interaction[v]
            #     / np.nanmean(group_size_all[v]),
            #     observed_minimum_distances_with_interaction[v]
            #     / np.nanmean(group_size_all[v]),
            #     alpha=0.3,
            #     c=soc_binding_colors[v],
            #     label=soc_binding_names[v],
            # )
            (
                mean_observed_minimum_distance_per_bin,
                stds,
                stdes,
            ) = get_mean_std_ste_over_bins(
                straight_line_minimum_distances_with_interaction[v]
                / np.nanmean(group_size_all[v]),
                observed_minimum_distances_with_interaction[v]
                / np.nanmean(group_size_all[v]),
                pdf_edges[1:],
            )
            plt.plot(
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
            pd.DataFrame(data).to_csv(
                f"../data/plots/intrusion/{env_name_short}_{soc_binding_names[v]}_straight_line_vs_observed_scatter.csv",
                index=False,
                header=False,
            )

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
        ax.set_ylim(0, 4)
        ax.set_xlim(0, 4)
        ax.set_ylabel(r"$\bar{r_o}$")
        ax.set_xlabel(r"$\bar{r_p}$")
        # plt.title(f"{env_name_short}")
        ax.legend()
        ax.grid(color="lightgray", linestyle="--", linewidth=0.5)
        fig.savefig(
            f"../data/figures/intrusion/intrusion_{env_name_short}.png",
            dpi=300,
        )
        plt.show()

        # fig, ax = plt.subplots()
        # bin_size = (RP_MAX - RP_MIN) / N_BINS_RP
        # pdf_edges = np.linspace(RP_MIN, RP_MAX, N_BINS_RP + 1)
        # bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        # mean_observed_minimum_distance_per_bin = get_mean_over_bins(
        #     straight_line_minimum_distances_without_interaction,
        #     observed_minimum_distances_without_interaction,
        #     bin_centers,
        # )
        # ax.plot(bin_centers, mean_observed_minimum_distance_per_bin, label="baseline")

        # for i in soc_binding_values:
        #     mean_observed_minimum_distance_per_bin = get_mean_over_bins(
        #         straight_line_minimum_distances_with_interaction[i],
        #         observed_minimum_distances_with_interaction[i],
        #         bin_centers,
        #     )
        #     ax.plot(
        #         bin_centers,
        #         mean_observed_minimum_distance_per_bin,
        #         label=soc_binding_names[i],
        #         c=soc_binding_colors[i],
        #     )
        # ax.legend()
        # # plt.show()
        # plt.close()

        # plot scaled with group breadth
        # bin_size = 4 / N_BINS_RP
        # pdf_edges = np.linspace(0, 4, N_BINS_RP + 1)
        # bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        # fig, ax = plt.subplots()
        # data = np.empty((len(bin_centers), len(soc_binding_values) * 2 + 1))
        # data[:, 0] = bin_centers.T
        # for i, v in enumerate(soc_binding_values):
        #     print(soc_binding_names[v])
        #     (
        #         mean_observed_minimum_distance_per_bin,
        #         stds,
        #         stdes,
        #     ) = get_mean_std_ste_over_bins(
        #         straight_line_minimum_distances_with_interaction[v]
        #         / np.nanmean(group_breadths_with_interaction[v]),
        #         observed_minimum_distances_with_interaction[v]
        #         / np.nanmean(group_breadths_with_interaction[v]),
        #         bin_centers,
        #     )
        #     ax.plot(
        #         bin_centers,
        #         mean_observed_minimum_distance_per_bin,
        #         label=soc_binding_names[v],
        #         c=soc_binding_colors[v],
        #     )

        #     data[:, 1 + i * 2 : 1 + i * 2 + 2] = np.array(
        #         [mean_observed_minimum_distance_per_bin, stdes]
        #     ).T
        # pd.DataFrame(data).to_csv(
        #     f"../data/plots/intrusion/{env_name_short}_straight_line_vs_observed_bin_only.csv",
        #     index=False,
        #     header=False,
        # )
        # ax.legend()
        # ax.set_xlim([0, 4])
        # ax.set_ylim([0, 4])
        # fig.savefig(f"../data/figures/intrusion/intrusion_{env_name_short}_only.png")
        # # plt.show()
        # plt.close()

        # plot distribution of the minimum observed distance against baseline
        # bin_size = 1 / 16
        # pdf_edges = np.linspace(0, 1, 16 + 1)
        # bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])
        # fig, ax = plt.subplots()

        # hist_baseline = np.histogram(
        #     observed_minimum_distances_without_interaction
        #     / straight_line_minimum_distances_without_interaction,
        #     pdf_edges,
        # )[0]
        # pdf_baseline = hist_baseline / sum(hist_baseline) / bin_size
        # ax.plot(bin_centers, pdf_baseline, label="baseline")
        # for i in soc_binding_values:
        #     hist_soc = np.histogram(
        #         observed_minimum_distances_with_interaction[i]
        #         / straight_line_minimum_distances_with_interaction[i],
        #         pdf_edges,
        #     )[0]
        #     pdf_soc = hist_soc / sum(hist_soc) / bin_size
        #     ax.plot(
        #         bin_centers,
        #         pdf_soc,
        #         label=soc_binding_names[i],
        #         c=soc_binding_colors[i],
        #     )
        # ax.legend()
        # plt.show()
        # plt.close()

        # compute a 2D distribution, with one axis with ro and the other with rp

        # grids_count_with_interaction = np.zeros(
        #     (len(soc_binding_values), N_BINS_RP, N_BINS_RO)
        # )
        # xi = np.linspace(RP_MIN, RP_MAX, N_BINS_RP)
        # yi = np.linspace(RO_MIN, RO_MAX, N_BINS_RO)

        # grids_count_without_interaction = compute_grid_count(
        #     straight_line_minimum_distances_without_interaction,
        #     observed_minimum_distances_without_interaction,
        #     RP_MIN,
        #     RP_MAX,
        #     N_BINS_RP,
        #     RO_MIN,
        #     RO_MAX,
        #     N_BINS_RO,
        # )
        # plot_color_map(xi, yi, grids_count_without_interaction, "ro", "rp")

        # for i in soc_binding_values:
        #     grids_count_with_interaction = compute_grid_count(
        #         straight_line_minimum_distances_with_interaction[i],
        #         observed_minimum_distances_with_interaction[i],
        #         RP_MIN,
        #         RP_MAX,
        #         32,
        #         RO_MIN,
        #         RO_MAX,
        #         N_BINS_RO,
        #     )
        #     plot_color_map(
        #         xi,
        #         yi,
        #         grids_count_with_interaction / grids_count_without_interaction,
        #         "ro",
        #         "rp",
        #         vmin=0,
        #         vmax=3,
        #     )

        # plt.savefig(
        #     f"../data/figures/pair_distributions/{env_name_short}_{soc_binding_names[v]}_aligned_trajectories_2D_distribution.png"
        # )
        # plt.clf()
        # plt.cla()
