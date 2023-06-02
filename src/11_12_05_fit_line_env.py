from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import numpy as np
from parameters import *
from utils import *

import pandas as pd


def fit(x, a, b):
    return a * x + b


MARKERS = ["^", "o", "s", "D"]

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env_name_short = env_name.split(":")[0]
        print(env_name_short)

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        observed_minimum_distances_non_groups = pickle_load(
            f"../data/pickle/observed_minimum_distance_non_groups_{env_name_short}_with_interaction.pkl"
        )
        straight_line_minimum_distances_non_groups = pickle_load(
            f"../data/pickle/straight_line_minimum_distance_non_groups_{env_name_short}_with_interaction.pkl"
        )
        velocities_non_groups = pickle_load(
            f"../data/pickle/velocities_non_groups_{env_name_short}_with_interaction.pkl"
        )

        observed_minimum_distances_groups = pickle_load(
            f"../data/pickle/observed_minimum_distance_{env_name_short}_with_interaction.pkl"
        )
        straight_line_minimum_distances_groups = pickle_load(
            f"../data/pickle/straight_line_minimum_distance_{env_name_short}_with_interaction.pkl"
        )
        velocities_groups = pickle_load(
            f"../data/pickle/velocities_{env_name_short}_with_interaction.pkl"
        )

        group_size = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")

        all_observed_groups = []
        all_straight_line_groups = []
        all_velocities_groups = []
        for i, v in enumerate(soc_binding_values):
            all_observed_groups += observed_minimum_distances_groups[v].tolist()
            all_straight_line_groups += straight_line_minimum_distances_groups[
                v
            ].tolist()
            all_velocities_groups += velocities_groups[v].tolist()

        data = {
            "groups": {
                "observed": np.array(all_observed_groups) / 1000,
                "straight_line": np.array(all_straight_line_groups) / 1000,
                "velocities": np.array(all_velocities_groups) / 1000,
                "marker": "s",
                "color": "red",
            },
            "non_groups": {
                "observed": np.array(observed_minimum_distances_non_groups) / 1000,
                "straight_line": np.array(straight_line_minimum_distances_non_groups)
                / 1000,
                "velocities": np.array(velocities_non_groups) / 1000,
                "marker": "o",
                "color": "blue",
            },
        }

        N_BINS = 8
        MIN, MAX = 0, 4
        bin_size = (MAX - MIN) / N_BINS
        pdf_edges = np.linspace(MIN, MAX, N_BINS + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        all_r0 = np.concatenate(
            (data["non_groups"]["observed"], data["groups"]["observed"])
        )
        all_rb = np.concatenate(
            (data["non_groups"]["straight_line"], data["groups"]["straight_line"])
        )

        c = np.nanmean(all_r0[all_rb > 3.5] / 3.75)
        print(f"weighted: {c}")

        last_bin_idx_groups = np.logical_and(
            data["groups"]["straight_line"] > 3.5, data["groups"]["straight_line"] <= 4
        )
        last_bin_idx_non_groups = np.logical_and(
            data["non_groups"]["straight_line"] > 3.5,
            data["non_groups"]["straight_line"] <= 4,
        )
        # print(pdf_edges)
        c2 = (
            (
                np.nanmean(data["groups"]["observed"][last_bin_idx_groups])
                + np.nanmean(data["non_groups"]["observed"][last_bin_idx_non_groups])
            )
            / 2
        ) / 3.75
        print(f"non weighted: {c2}")

        f, ax = plt.subplots()

        fit_x = np.linspace(MIN, MAX, 5)
        data_bin = np.zeros(
            (len(bin_centers), 1 + 2 + 2 + len(soc_binding_type) * 2)
        )  # 1 for x, 2 ng, 2g, 2 * 4 each bonding
        data_bin[:, 0] = bin_centers.T
        data_fit = np.zeros((len(fit_x), 2))
        data_fit[:, 0] = fit_x.T

        for i, g in enumerate(["groups", "non_groups"]):
            mean, std, ste = get_mean_std_ste_over_bins(
                data[g]["straight_line"], data[g]["observed"], pdf_edges[1:]
            )
            # print(g, mean)
            ax.plot(
                bin_centers,
                mean,
                label=g,
            )
            data_bin[:, 2 * i + 1 : 2 * i + 2] = np.array(mean)[..., None]
            data_bin[:, 2 * i + 2 : 2 * i + 3] = np.array(ste)[..., None]

        for i, v in enumerate(soc_binding_values):
            observed = observed_minimum_distances_groups[v] / 1000
            straight_line = straight_line_minimum_distances_groups[v] / 1000
            mean, std, ste = get_mean_std_ste_over_bins(
                straight_line, observed, pdf_edges[1:]
            )
            data_bin[:, 2 * i + 5 : 2 * i + 6] = np.array(mean)[..., None]
            data_bin[:, 2 * i + 6 : 2 * i + 7] = np.array(ste)[..., None]

        pd.DataFrame(data_bin).to_csv(
            f"../data/plots/correction/{env_name_short}_straight_line_vs_observed_bin.csv",
            index=False,
            header=False,
        )

        ax.plot(fit_x, c2 * fit_x, ls="dashed", c="green", label=f"y={round(c2,3)}x")

        data_fit[:, 1] = (fit_x * c2).T

        pd.DataFrame(data_fit).to_csv(
            f"../data/plots/correction/{env_name_short}_straight_line_vs_observed_fit.csv",
            index=False,
            header=False,
        )

        ax.set_aspect("equal")
        ax.legend()
        ax.set_ylabel(r"$r_0$ (m)")
        ax.set_xlabel(r"$r_b$ (m)")
        ax.set_title(env_name_short)
        # plt.show()
        # plt.savefig(
        #     f"../data/figures/intrusion/fit/coefficient_without_scaling_{env_name_short}.png"
        # )
        # plt.close()

        # ================================================================================
        # ================================================================================
        # ================================================================================
        # ================================================================================

        all_observed_groups = []
        all_straight_line_groups = []
        all_velocities_groups = []
        for i, v in enumerate(soc_binding_values):
            all_observed_groups += (
                observed_minimum_distances_groups[v] / np.nanmean(group_size[v])
            ).tolist()
            all_straight_line_groups += (
                straight_line_minimum_distances_groups[v] / np.nanmean(group_size[v])
            ).tolist()

        all_straight_line_groups = np.array(all_straight_line_groups)
        all_observed_groups = np.array(all_observed_groups)

        N_BINS = 8
        MIN, MAX = 0, 4
        bin_size = (MAX - MIN) / N_BINS
        pdf_edges = np.linspace(MIN, MAX, N_BINS + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        last_bin_idx = np.logical_and(
            all_straight_line_groups > 3.5,
            all_straight_line_groups <= 4,
        )
        c = np.nanmean(
            all_observed_groups[last_bin_idx] / all_straight_line_groups[last_bin_idx]
        )
        print(f"scaled: {c}")

        fit_x = np.linspace(MIN, MAX, 5)
        data_bin = np.empty((len(bin_centers), 2 * len(soc_binding_values) + 1))
        data_bin[:, 0] = bin_centers.T
        data_fit = np.empty((len(fit_x), 2))
        data_fit[:, 0] = fit_x.T

        f, ax = plt.subplots()
        for i, v in enumerate(soc_binding_values):

            # print(soc_binding_names[v])
            r0 = observed_minimum_distances_groups[v] / np.nanmean(group_size[v])
            rb = straight_line_minimum_distances_groups[v] / np.nanmean(group_size[v])

            mean, std, ste = get_mean_std_ste_over_bins(rb, r0, pdf_edges[1:])
            ax.plot(
                bin_centers, mean, label=soc_binding_names[v], c=soc_binding_colors[v]
            )

            data_bin[:, 2 * i + 1 : 2 * i + 2] = np.array(mean)[..., None]
            data_bin[:, 2 * i + 2 : 2 * i + 3] = np.array(ste)[..., None]

        pd.DataFrame(data_bin).to_csv(
            f"../data/plots/correction/{env_name_short}_straight_line_vs_observed_scaled_bin.csv",
            index=False,
            header=False,
        )

        fit_x = np.linspace(MIN, MAX, 5)

        ax.plot(fit_x, c * fit_x, ls="dashed", c="blue", label=f"y={round(c,3)}x")

        data_fit[:, 1] = (fit_x * c).T

        pd.DataFrame(data_fit).to_csv(
            f"../data/plots/correction/{env_name_short}_straight_line_vs_observed_fit_scaled.csv",
            index=False,
            header=False,
        )

        ax.set_aspect("equal")
        ax.legend()
        ax.set_ylabel(r"$\bar{r}_0$ (m)")
        ax.set_xlabel(r"$\bar{r}_b$ (m)")
        ax.set_title(env_name_short)
        # plt.show()
        plt.savefig(
            f"../data/figures/intrusion/fit/coefficient_with_scaling_{env_name_short}.png"
        )
        # plt.close()
