from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import numpy as np
from parameters import *
from utils import *

from scipy.optimize import curve_fit


def fit(x, a, b, c):
    return a * np.exp(-b * x) + c


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

        observed_minimum_distances_with_interaction = pickle_load(
            f"../data/pickle/observed_minimum_distance_{env_name_short}_with_interaction_not_alone.pkl"
        )
        straight_line_minimum_distances_with_interaction = pickle_load(
            f"../data/pickle/straight_line_minimum_distance_{env_name_short}_with_interaction_not_alone.pkl"
        )
        velocities = pickle_load(
            f"../data/pickle/velocities_{env_name_short}_with_interaction_not_alone.pkl"
        )
        group_size_all = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")
        group_breadth_all = pickle_load(
            f"../data/pickle/group_breadth_{env_name_short}.pkl"
        )

        # with scaling

        fit_x = np.linspace(0, 4, 1000)

        f, axes = plt.subplots(1, 2, constrained_layout=True, figsize=(16, 8))
        left, bottom, width, height = [0.4, 0.3, 0.5, 0.5]
        inset_1 = axes[0].inset_axes([left, bottom, width, height])
        inset_2 = axes[1].inset_axes([left, bottom, width, height])
        inset_1.set_xlim(0.5, 4)
        inset_1.set_ylim(-0.5, 1)
        inset_2.set_xlim(0.5, 4)
        inset_2.set_ylim(-0.5, 1)

        for i, v in enumerate(soc_binding_values):
            observed_values = observed_minimum_distances_with_interaction[
                v
            ] / np.nanmean(group_size_all[v])
            straight_line_values = straight_line_minimum_distances_with_interaction[
                v
            ] / np.nanmean(group_size_all[v])
            vel = np.array(velocities[v]) / 1000

            potentials = (
                vel**2
                * (observed_values**2 - straight_line_values**2)
                / observed_values**2
            )

            # remove outliers
            observed_values = observed_values[potentials > -1]
            potentials = potentials[potentials > -1]

            exp_fit_params, _ = curve_fit(fit, observed_values, potentials, maxfev=5000)

            poly_fit_params = np.polyfit(observed_values, potentials, 3)
            poly_fit = np.poly1d(poly_fit_params)

            axes[0].plot(
                fit_x, fit(fit_x, *exp_fit_params), c=soc_binding_colors[v], ls="--"
            )
            axes[0].scatter(
                observed_values,
                potentials,
                edgecolors=soc_binding_colors[v],
                marker=MARKERS[i],
                facecolors="none",
                label=soc_binding_names[v],
            )

            inset_1.plot(
                fit_x, fit(fit_x, *exp_fit_params), c=soc_binding_colors[v], ls="--"
            )
            inset_1.scatter(
                observed_values,
                potentials,
                edgecolors=soc_binding_colors[v],
                marker=MARKERS[i],
                facecolors="none",
                label=soc_binding_names[v],
            )

            axes[1].plot(fit_x, poly_fit(fit_x), c=soc_binding_colors[v], ls="--")
            axes[1].scatter(
                observed_values,
                potentials,
                edgecolors=soc_binding_colors[v],
                marker=MARKERS[i],
                facecolors="none",
                label=soc_binding_names[v],
            )

            inset_2.plot(fit_x, poly_fit(fit_x), c=soc_binding_colors[v], ls="--")
            inset_2.scatter(
                observed_values,
                potentials,
                edgecolors=soc_binding_colors[v],
                marker=MARKERS[i],
                facecolors="none",
                label=soc_binding_names[v],
            )

        axes[0].legend()
        axes[0].set_ylabel("∝V")
        axes[0].set_xlabel("r_o (scaled with group size)")
        axes[1].legend()
        axes[1].set_ylabel("∝V")
        axes[1].set_xlabel("r_o (scaled with group size)")
        # axes[1].set_ylim(0, 1)
        plt.show()
        # plt.savefig(
        #     f"../data/figures/intrusion/potentials/{env_name_short}_potential_scaled_with_group_width.png"
        # )

        # # scaled with group breadth
        # bin_size = 4 / 8
        # pdf_edges = np.linspace(0, 4, 8 + 1)
        # bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        # fit_x = np.linspace(0, 4, 1000)

        # f, axes = plt.subplots(1, 2, constrained_layout=True, figsize=(16, 8))
        # left, bottom, width, height = [0.4, 0.3, 0.5, 0.5]
        # inset_1 = axes[0].inset_axes([left, bottom, width, height])
        # inset_2 = axes[1].inset_axes([left, bottom, width, height])
        # inset_1.set_xlim(0.5, 4)
        # inset_1.set_ylim(-0.5, 1)
        # inset_2.set_xlim(0.5, 4)
        # inset_2.set_ylim(-0.5, 1)

        # for i, v in enumerate(soc_binding_values):
        #     observed_values = observed_minimum_distances_with_interaction[
        #         v
        #     ] / np.nanmean(group_breadth_all[v])
        #     straight_line_values = straight_line_minimum_distances_with_interaction[
        #         v
        #     ] / np.nanmean(group_breadth_all[v])

        #     # potential = (
        #     #     observed_values**2 - straight_line_values**2
        #     # ) / observed_values**2
        #     # ax.scatter(observed_values, potential)

        #     ros, potentials = [], []
        #     for k in range(len(pdf_edges[1:])):
        #         bin_ids = np.digitize(straight_line_values, pdf_edges[1:])
        #         observed_for_bin = observed_values[bin_ids == k]
        #         mean_ro = np.nanmean(observed_for_bin)
        #         rp = bin_centers[k]
        #         ros += [mean_ro]
        #         potentials += [(mean_ro**2 - rp**2) / mean_ro**2]

        #     exp_fit_params, _ = curve_fit(fit, ros, potentials)

        #     poly_fit_params = np.polyfit(ros, potentials, 3)
        #     poly_fit = np.poly1d(poly_fit_params)

        #     axes[0].plot(
        #         fit_x, fit(fit_x, *exp_fit_params), c=soc_binding_colors[v], ls="--"
        #     )
        #     axes[0].scatter(
        #         ros,
        #         potentials,
        #         edgecolors=soc_binding_colors[v],
        #         marker=MARKERS[i],
        #         facecolors="none",
        #         label=soc_binding_names[v],
        #     )

        #     inset_1.plot(
        #         fit_x, fit(fit_x, *exp_fit_params), c=soc_binding_colors[v], ls="--"
        #     )
        #     inset_1.scatter(
        #         ros,
        #         potentials,
        #         edgecolors=soc_binding_colors[v],
        #         marker=MARKERS[i],
        #         facecolors="none",
        #         label=soc_binding_names[v],
        #     )

        #     axes[1].plot(fit_x, poly_fit(fit_x), c=soc_binding_colors[v], ls="--")
        #     axes[1].scatter(
        #         ros,
        #         potentials,
        #         edgecolors=soc_binding_colors[v],
        #         marker=MARKERS[i],
        #         facecolors="none",
        #         label=soc_binding_names[v],
        #     )

        #     inset_2.plot(fit_x, poly_fit(fit_x), c=soc_binding_colors[v], ls="--")
        #     inset_2.scatter(
        #         ros,
        #         potentials,
        #         edgecolors=soc_binding_colors[v],
        #         marker=MARKERS[i],
        #         facecolors="none",
        #         label=soc_binding_names[v],
        #     )

        # axes[0].legend()
        # axes[0].set_ylabel("∝V")
        # axes[0].set_xlabel("r_o (scaled with group breadth)")
        # axes[1].legend()
        # axes[1].set_ylabel("∝V")
        # axes[1].set_xlabel("r_o (scaled with group breadth)")
        # # plt.show()
        # plt.savefig(
        #     f"../data/figures/intrusion/potentials/{env_name_short}_potential_scaled_with_group_breadth.png"
        # )

        # # without scaling
        # bin_size = 4 / 8
        # pdf_edges = np.linspace(0, 4, 8 + 1)
        # bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        # fit_x = np.linspace(0, 4, 1000)

        # f, axes = plt.subplots(1, 2, constrained_layout=True, figsize=(16, 8))
        # left, bottom, width, height = [0.4, 0.3, 0.5, 0.5]
        # inset_1 = axes[0].inset_axes([left, bottom, width, height])
        # inset_2 = axes[1].inset_axes([left, bottom, width, height])
        # inset_1.set_xlim(0.5, 4)
        # inset_1.set_ylim(-0.5, 1)
        # inset_2.set_xlim(0.5, 4)
        # inset_2.set_ylim(-0.5, 1)

        # for i, v in enumerate(soc_binding_values):
        #     observed_values = observed_minimum_distances_with_interaction[v] / 1000
        #     straight_line_values = (
        #         straight_line_minimum_distances_with_interaction[v] / 1000
        #     )

        #     ros, potentials = [], []
        #     for k in range(len(pdf_edges[1:])):
        #         bin_ids = np.digitize(straight_line_values, pdf_edges[1:])
        #         observed_for_bin = observed_values[bin_ids == k]
        #         if len(observed_for_bin):
        #             mean_ro = np.nanmean(observed_for_bin)
        #             rp = bin_centers[k]
        #             ros += [mean_ro]
        #             potentials += [(mean_ro**2 - rp**2) / mean_ro**2]

        #     exp_fit_params, _ = curve_fit(fit, ros, potentials)

        #     poly_fit_params = np.polyfit(ros, potentials, 3)
        #     poly_fit = np.poly1d(poly_fit_params)

        #     axes[0].plot(
        #         fit_x, fit(fit_x, *exp_fit_params), c=soc_binding_colors[v], ls="--"
        #     )
        #     axes[0].scatter(
        #         ros,
        #         potentials,
        #         edgecolors=soc_binding_colors[v],
        #         marker=MARKERS[i],
        #         facecolors="none",
        #         label=soc_binding_names[v],
        #     )

        #     inset_1.plot(
        #         fit_x, fit(fit_x, *exp_fit_params), c=soc_binding_colors[v], ls="--"
        #     )
        #     inset_1.scatter(
        #         ros,
        #         potentials,
        #         edgecolors=soc_binding_colors[v],
        #         marker=MARKERS[i],
        #         facecolors="none",
        #         label=soc_binding_names[v],
        #     )

        #     axes[1].plot(fit_x, poly_fit(fit_x), c=soc_binding_colors[v], ls="--")
        #     axes[1].scatter(
        #         ros,
        #         potentials,
        #         edgecolors=soc_binding_colors[v],
        #         marker=MARKERS[i],
        #         facecolors="none",
        #         label=soc_binding_names[v],
        #     )

        #     inset_2.plot(fit_x, poly_fit(fit_x), c=soc_binding_colors[v], ls="--")
        #     inset_2.scatter(
        #         ros,
        #         potentials,
        #         edgecolors=soc_binding_colors[v],
        #         marker=MARKERS[i],
        #         facecolors="none",
        #         label=soc_binding_names[v],
        #     )

        # axes[0].legend()
        # axes[0].set_ylabel("∝V(r_o)")
        # axes[0].set_xlabel("r_o")
        # axes[1].legend()
        # axes[1].set_ylabel("∝V(r_o)")
        # axes[1].set_xlabel("r_o")
        # # plt.show()
        # plt.savefig(
        #     f"../data/figures/intrusion/potentials/{env_name_short}_potential_scaled.png"
        # )
