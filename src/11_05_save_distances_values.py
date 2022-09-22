from email import header
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pyparsing import col
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

        group_size_all = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")
        group_breadth_all = pickle_load(
            f"../data/pickle/group_breadth_{env_name_short}.pkl"
        )

        for alone in ["alone", "not_alone"]:

            observed_minimum_distances_with_interaction = pickle_load(
                f"../data/pickle/observed_minimum_distance_{env_name_short}_with_interaction_{alone}.pkl"
            )
            straight_line_minimum_distances_with_interaction = pickle_load(
                f"../data/pickle/straight_line_minimum_distance_{env_name_short}_with_interaction_{alone}.pkl"
            )

            # RAW
            for i, v in enumerate(soc_binding_values):
                straight_line_values = straight_line_minimum_distances_with_interaction[
                    v
                ]
                observed_values = observed_minimum_distances_with_interaction[v]
                data = np.array([observed_values, straight_line_values]).T
                pd.DataFrame(data, columns=["ro", "rp"]).to_csv(
                    f"../data/csv/intrusion/{env_name_short}/{alone}/{env_name_short}_{soc_binding_names[v]}_straight_line_vs_observed_{alone}.csv",
                    index=False,
                )
                data_scaled_size = np.array(
                    [
                        observed_values / np.nanmean(group_size_all[v]),
                        straight_line_values / np.nanmean(group_size_all[v]),
                    ]
                ).T
                pd.DataFrame(data_scaled_size, columns=["ro", "rp"]).to_csv(
                    f"../data/csv/intrusion/{env_name_short}/{alone}/{env_name_short}_{soc_binding_names[v]}_straight_line_vs_observed_scaled_with_group_size_{alone}.csv",
                    index=False,
                )
                data_scaled_breadth = np.array(
                    [
                        observed_values / np.nanmean(group_breadth_all[v]),
                        straight_line_values / np.nanmean(group_breadth_all[v]),
                    ]
                ).T
                pd.DataFrame(data_scaled_breadth, columns=["ro", "rp"]).to_csv(
                    f"../data/csv/intrusion/{env_name_short}/{alone}/{env_name_short}_{soc_binding_names[v]}_straight_line_vs_observed_scaled_with_group_breadth_{alone}.csv",
                    index=False,
                )

            # BIN
            # without scaling
            bin_size = 4000 / N_BINS_RP
            pdf_edges = np.linspace(0, 4000, N_BINS_RP + 1)
            bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

            for i, v in enumerate(soc_binding_values):
                (
                    mean_observed_minimum_distance_per_bin,
                    stds,
                    stdes,
                    n,
                ) = get_mean_std_ste_n_over_bins(
                    straight_line_minimum_distances_with_interaction[v],
                    observed_minimum_distances_with_interaction[v],
                    pdf_edges[1:],
                )
                data = np.array(
                    [
                        bin_centers,
                        mean_observed_minimum_distance_per_bin,
                        stds,
                        stdes,
                        n,
                    ]
                ).T
                pd.DataFrame(
                    data, columns=["ro_bin", "mean_rp", "std_rp", "ste_rp", "n_values"]
                ).to_csv(
                    f"../data/csv/intrusion/{env_name_short}/{alone}/{env_name_short}_{soc_binding_names[v]}_straight_line_vs_observed_bin_{alone}.csv",
                    index=False,
                )

            # with scaling
            bin_size = 4 / N_BINS_RP
            pdf_edges = np.linspace(0, 4, N_BINS_RP + 1)
            bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

            # plot 2D pair distributions with interaction
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
                    mean_observed_minimum_distance_per_bin_scaled_size,
                    stds_scaled_size,
                    stdes_scaled_size,
                    n_scaled_size,
                ) = get_mean_std_ste_n_over_bins(
                    straight_line_minimum_distances_with_interaction[v]
                    / np.nanmean(group_size_all[v]),
                    observed_minimum_distances_with_interaction[v]
                    / np.nanmean(group_size_all[v]),
                    pdf_edges[1:],
                )
                data_scaled_size = np.array(
                    [
                        bin_centers,
                        mean_observed_minimum_distance_per_bin_scaled_size,
                        stds_scaled_size,
                        stdes_scaled_size,
                        n_scaled_size,
                    ]
                ).T
                pd.DataFrame(
                    data_scaled_size,
                    columns=["ro_bin", "mean_rp", "std_rp", "ste_rp", "n_values"],
                ).to_csv(
                    f"../data/csv/intrusion/{env_name_short}/{alone}/{env_name_short}_{soc_binding_names[v]}_straight_line_vs_observed_scaled_with_group_size_bin_{alone}.csv",
                    index=False,
                )

                (
                    mean_observed_minimum_distance_per_bin_scaled_breadth,
                    stds_scaled_breadth,
                    stdes_scaled_breadth,
                    n_scaled_breadth,
                ) = get_mean_std_ste_n_over_bins(
                    straight_line_minimum_distances_with_interaction[v]
                    / np.nanmean(group_breadth_all[v]),
                    observed_minimum_distances_with_interaction[v]
                    / np.nanmean(group_breadth_all[v]),
                    pdf_edges[1:],
                )
                data_scaled_breadth = np.array(
                    [
                        bin_centers,
                        mean_observed_minimum_distance_per_bin_scaled_breadth,
                        stds_scaled_breadth,
                        stdes_scaled_breadth,
                        n_scaled_breadth,
                    ]
                ).T
                pd.DataFrame(
                    data_scaled_breadth,
                    columns=["ro_bin", "mean_rp", "std_rp", "ste_rp", "n_values"],
                ).to_csv(
                    f"../data/csv/intrusion/{env_name_short}/{alone}/{env_name_short}_{soc_binding_names[v]}_straight_line_vs_observed_scaled_with_group_breadth_bin_{alone}.csv",
                    index=False,
                )
