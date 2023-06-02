from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import numpy as np
from parameters import *
from utils import *

from scipy.optimize import curve_fit
import pandas as pd

import scipy.stats as stats

# def fit(x, a, b):
#     return a * np.exp(-b*x)


def fit(x, a, b):
    return (a / x) ** b


MARKERS = ["^", "o", "s", "D"]


def compute_binned_potential(r0, rb, pdf_edges, a, correct=True, cap=False):
    r0s, potentials = [], []

    for k in range(len(pdf_edges[1:])):
        bin_ids = np.digitize(rb, pdf_edges[1:])
        observed_for_bin = r0[bin_ids == k]
        if len(observed_for_bin):
            mean_r0 = np.nanmean(observed_for_bin)
            bin_rb = bin_centers[k]
            if correct:
                bin_rb *= a
            # bin_rb = (bin_rb - b) / a  # correction
            p = (mean_r0**2 - bin_rb**2) / mean_r0**2
            if cap:
                p = max(p, 0)
            potentials += [p]
            r0s += [mean_r0]
    return np.array(r0s), np.array(potentials)


if __name__ == "__main__":
    N_BINS = 8
    MIN, MAX = 0, 4
    bin_size = (MAX - MIN) / N_BINS
    pdf_edges = np.linspace(MIN, MAX, N_BINS + 1)
    bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])
    n_interp = 1000

    fit_x = np.linspace(0, 5, n_interp)

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

        observed_minimum_distances_groups = pickle_load(
            f"../data/pickle/observed_minimum_distance_{env_name_short}_with_interaction.pkl"
        )
        straight_line_minimum_distances_groups = pickle_load(
            f"../data/pickle/straight_line_minimum_distance_{env_name_short}_with_interaction.pkl"
        )

        group_size = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")

        all_observed_groups = []
        all_straight_line_groups = []
        for i, v in enumerate(soc_binding_values):
            all_observed_groups += observed_minimum_distances_groups[v].tolist()
            all_straight_line_groups += straight_line_minimum_distances_groups[
                v
            ].tolist()

        data = {
            "groups": {
                "observed": np.array(all_observed_groups) / 1000,
                "straight_line": np.array(all_straight_line_groups) / 1000,
                "marker": "s",
                "color": "red",
            },
            "non_groups": {
                "observed": np.array(observed_minimum_distances_non_groups) / 1000,
                "straight_line": np.array(straight_line_minimum_distances_non_groups)
                / 1000,
                "marker": "o",
                "color": "blue",
            },
        }

        fitting_bounds = ([0.8, 2], [10, 8])

        if env_name_short == "atc":
            a, b = 0.755, 0  # obtained from 11_12_05
        else:
            a, b = 1, 0

        f, ax = plt.subplots()

        data_bin = np.empty((len(bin_centers), 2 * len(soc_binding_values)))

        # data_fit = np.empty((len(fit_x), 1 + len(soc_binding_values)))
        # data_fit[:, 0] = fit_x

        for g in ["groups", "non_groups"]:
            rb = data[g]["straight_line"]
            r0 = data[g]["observed"]

            r0s, potentials = compute_binned_potential(r0, rb, pdf_edges, a)

            fit_params, _ = curve_fit(fit, r0s, potentials, bounds=([0.8, 2], [10, 8]))
            print(fit_params)
            [alpha, beta] = fit_params
            ax.plot(
                fit_x,
                fit(fit_x, *fit_params),
                ls="--",
                label=rf"$(\frac{{{round(alpha,2)}}}{{x}})^{{{round(beta,2)}}}$",
                c=data[g]["color"],
            )
            y = potentials
            y_fit = fit(r0s, *fit_params)
            # residual sum of squares
            ss_res = np.sum((y - y_fit) ** 2)
            # total sum of squares
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            # r-squared
            r2 = 1 - (ss_res / ss_tot)
            # print(r2)

            # compute AIC
            mse = np.mean((y - y_fit) ** 2)
            aic = len(y) * np.log(mse) + 2 * len(fit_params)
            print(f"{soc_binding_names[v]}: {aic:.2f}")

            # compute Kstest
            ks = stats.ks_2samp(y, y_fit)
            print(f"{soc_binding_names[v]}: {ks}")

            ax.scatter(
                r0s,
                potentials,
                label=g,
                facecolors="none",
                marker=data[g]["marker"],
                edgecolors=data[g]["color"],
            )

        ax.legend()
        ax.set_ylabel("∝V")
        ax.set_xlabel(r"$r_0$ (m)")
        ax.set_ylim([-0.5, 3])
        ax.set_xlim([0, 4])
        ax.grid(color="lightgray", linestyle="--", linewidth=0.5)
        ax.set_title(env_name_short)

        # plt.savefig(
        #     f"../data/figures/intrusion/potentials/corrected/potential_group_non_group_{env_name_short}.png"
        # )
        plt.show()
