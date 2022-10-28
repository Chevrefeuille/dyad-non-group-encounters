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

        group_size = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")

        N_BINS = 8
        MIN, MAX = 0, 4
        bin_size = (MAX - MIN) / N_BINS
        pdf_edges = np.linspace(MIN, MAX, N_BINS + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        n_interp = 1000
        fit_x = np.linspace(MIN + bin_size * 3 / 2, MAX, n_interp)

        f, ax = plt.subplots()

        data_bin = np.empty((len(bin_centers), 2 * len(soc_binding_values)))

        # data_fit = np.empty((len(fit_x), 1 + len(soc_binding_values)))
        # data_fit[:, 0] = fit_x

        for i, v in enumerate(soc_binding_values):

            # r0 = observed_minimum_distances_groups[v] / np.nanmean(group_size[v])
            # rb = straight_line_minimum_distances_groups[v] / np.nanmean(group_size[v])
            # vel = velocities_groups[v] / np.nanmean(group_size[v])

            r0 = observed_minimum_distances_groups[v] / 1000
            rb = straight_line_minimum_distances_groups[v] / 1000
            vel = velocities_groups[v] / 1000

            ind_bigger = r0 >= rb  # potential is supposed to never be attractive
            rb = rb[ind_bigger]
            r0 = r0[ind_bigger]
            vel = vel[ind_bigger]

            p = (r0**2 - rb**2) / r0**2

            r0s, potentials = [], []
            for k in range(len(pdf_edges[1:])):
                bin_ids = np.digitize(rb, pdf_edges[1:])
                r0_for_bin = r0[bin_ids == k]
                p_for_bin = p[bin_ids == k]
                if len(r0_for_bin):
                    mean_r0 = np.nanmean(r0_for_bin)
                    mean_p = np.nanmean(p_for_bin)
                    r0s += [mean_r0]
                    potentials += [mean_p]

            # potentials = np.array(potentials)
            # vs = np.array(vs)
            # potentials *= vs**2

            fit_params, _ = curve_fit(fit, r0s, potentials)

            ax.plot(
                fit_x,
                fit(fit_x, *fit_params),
                ls="--",
                label=soc_binding_names[v],
                c=soc_binding_colors[v],
            )
            ax.scatter(
                r0s,
                potentials,
                label=soc_binding_names[v],
                facecolors="none",
                marker=MARKERS[i],
                edgecolors=soc_binding_colors[v],
            )

        r0 = np.array(observed_minimum_distances_non_groups) / 1000
        rb = np.array(straight_line_minimum_distances_non_groups) / 1000
        vel = np.array(velocities_non_groups) / 1000

        ind_bigger = r0 > rb  # potential is supposed to never be attractive
        rb = rb[ind_bigger]
        r0 = r0[ind_bigger]
        vel = vel[ind_bigger]

        p = (r0**2 - rb**2) / r0**2

        r0s, potentials = [], []
        for k in range(len(pdf_edges[1:])):
            bin_ids = np.digitize(rb, pdf_edges[1:])
            r0_for_bin = r0[bin_ids == k]
            p_for_bin = p[bin_ids == k]
            if len(r0_for_bin):
                mean_r0 = np.nanmean(r0_for_bin)
                mean_p = np.nanmean(p_for_bin)
                r0s += [mean_r0]
                potentials += [mean_p]

        # potentials = np.array(potentials)
        # vs = np.array(vs)
        # potentials *= vs**2

        fit_params, _ = curve_fit(fit, r0s, potentials)

        ax.plot(
            fit_x,
            fit(fit_x, *fit_params),
            ls="--",
            label="non group",
            c="purple",
        )
        ax.scatter(
            r0s,
            potentials,
            label="non group",
            marker="x",
            c="purple",
        )

        ax.legend()
        ax.set_ylabel("∝V")
        ax.set_xlabel(r"$\bar{r}_0$ (m)")
        ax.set_title(env_name_short)
        plt.show()

        # plt.savefig(
        #     f"../data/figures/intrusion/potentials/non_groups/{env_name_short}_potential_groups_vs_non_groups_bond.pdf"
        # )
        plt.close()

        #
        # ========================================
        # ========================================
        #

        f, ax = plt.subplots()
        for i, v in enumerate(soc_binding_values):
            observed_values = observed_minimum_distances_groups[v] / 1000
            straight_line_values = straight_line_minimum_distances_groups[v] / 1000

            mean, std, ste = get_mean_std_ste_over_bins(
                straight_line_values, observed_values, pdf_edges[1:]
            )
            ax.plot(
                bin_centers,
                mean,
                label=soc_binding_names[v],
                c=soc_binding_colors[v],
            )

        observed_values = np.array(observed_minimum_distances_non_groups) / 1000
        straight_line_values = (
            np.array(straight_line_minimum_distances_non_groups) / 1000
        )

        mean, std, ste = get_mean_std_ste_over_bins(
            straight_line_values, observed_values, pdf_edges[1:]
        )
        ax.plot(bin_centers, mean, label="non group", c="purple")
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
        # plt.savefig(
        #     f"../data/figures/intrusion/distances/{env_name_short}_distances_groups_vs_non_groups_bond.pdf"
        # )
        plt.show()
        plt.close()
