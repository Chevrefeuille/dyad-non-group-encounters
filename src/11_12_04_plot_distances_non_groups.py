from calendar import c
from email import header
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import numpy as np
from parameters import *
from utils import *

from scipy.optimize import curve_fit
import pandas as pd


def fit(x, a, b):
    return (a / x) ** b


MARKERS = ["^", "o", "s", "D"]

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

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

        # with scaling
        N_BINS = 8
        MIN, MAX = 0, 4
        bin_size = (MAX - MIN) / N_BINS
        pdf_edges = np.linspace(MIN, MAX, N_BINS + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        f, ax = plt.subplots()
        for g in ["groups", "non_groups"]:
            mean, std, ste = get_mean_std_ste_over_bins(
                data[g]["straight_line"], data[g]["observed"], pdf_edges[1:]
            )
            ax.plot(
                bin_centers,
                mean,
                label=g,
            )
        ax.plot(
            [MIN, MAX],
            [MIN, MAX],
            label="y=x",
            c="black",
            linestyle="dashed",
            linewidth=0.5,
        )
        ax.set_aspect("equal")
        ax.legend()
        ax.set_ylabel(r"$\bar{r}_0$ (m)")
        ax.set_xlabel(r"$\bar{r}_b}$ (m)")
        ax.set_title(env_name_short)
        plt.show()
        # plt.savefig(
        #     f"../data/figures/intrusion/distances/{env_name_short}_distances_groups_vs_non_groups.pdf"
        # )
        # plt.close()
