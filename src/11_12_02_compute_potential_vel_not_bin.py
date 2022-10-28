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
        fit_x = np.linspace(MIN + bin_size / 4, MAX, n_interp)

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

            r0s, potentials, vs = [], [], []
            for k in range(len(pdf_edges[1:])):
                bin_ids = np.digitize(r0, pdf_edges[1:])
                rb_for_bin = rb[bin_ids == k]
                velocities_for_bin = vel[bin_ids == k]
                if len(rb_for_bin):
                    mean_rb = np.nanmean(rb_for_bin)
                    mean_v = np.nanmean(velocities_for_bin)
                    vs += [mean_v]
                    bin_r0 = bin_centers[k]
                    r0s += [bin_r0]
                    potentials += [(bin_r0**2 - mean_rb**2) / bin_r0**2]

            potentials = np.array(potentials)
            vs = np.array(vs)
            # potentials *= vs**2

            # fit_params, _ = curve_fit(fit, r0s, potentials)

            # ax.plot(
            #     fit_x,
            #     fit(fit_x, *fit_params),
            #     ls="--",
            #     label=soc_binding_names[v],
            #     c=soc_binding_colors[v],
            # )
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

        r0s, potentials, vs = [], [], []
        for k in range(len(pdf_edges[1:])):
            bin_ids = np.digitize(r0, pdf_edges[1:])
            rb_for_bin = rb[bin_ids == k]
            velocities_for_bin = vel[bin_ids == k]
            if len(rb_for_bin):
                mean_rb = np.nanmean(rb_for_bin)
                mean_v = np.nanmean(velocities_for_bin)
                vs += [mean_v]
                bin_r0 = bin_centers[k]
                r0s += [bin_r0]
                potentials += [(bin_r0**2 - mean_rb**2) / bin_r0**2]

        potentials = np.array(potentials)
        vs = np.array(vs)
        # potentials *= vs**2

        # fit_params, _ = curve_fit(fit, r0s, potentials)

        # ax.plot(
        #     fit_x,
        #     fit(fit_x, *fit_params),
        #     ls="--",
        #     label="non group",
        #     c="purple",
        # )
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
