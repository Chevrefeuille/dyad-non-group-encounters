from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from parameters import *

import numpy as np
import matplotlib.pyplot as plt

""" The goal of this script is to plot the relative orientation distributions of the groups in the corridor
 environment considering groups with and without interaction."""

if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:
        days = DAYS_ATC if env_name == "atc" else DAYS_DIAMOR
        soc_binding_type = "soc_rel" if env_name == "atc" else "interaction"
        soc_binding_names = (
            SOCIAL_RELATIONS_EN if env_name == "atc" else INTENSITIES_OF_INTERACTION_NUM
        )
        soc_binding_values = [1, 2] if env_name == "atc" else [0, 1, 2, 3]

        relative_orientation_with_interaction = pickle_load(
            f"../data/pickle/group_relative_orientation_with_interaction_{env_name}.pkl"
        )
        relative_orientation_without_interaction = pickle_load(
            f"../data/pickle/group_relative_orientation_without_interaction_{env_name}.pkl"
        )
        relative_orientation = pickle_load(
            f"../data/pickle/group_relative_orientation_{env_name}.pkl"
        )

        bin_size = (
            ORIENTATION_DISTRIBUTION_MAX - ORIENTATION_DISTRIBUTION_MIN
        ) / N_BINS_ORIENTATION_DISTRIBUTION
        pdf_edges = np.linspace(
            ORIENTATION_DISTRIBUTION_MIN,
            ORIENTATION_DISTRIBUTION_MAX,
            N_BINS_ORIENTATION_DISTRIBUTION + 1,
        )
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        # plot pdf
        for i in soc_binding_values:
            relative_orientation_values = relative_orientation[i]
            hist = np.histogram(relative_orientation_values, pdf_edges)[0]
            pdf = hist / sum(hist) / bin_size
            plt.plot(bin_centers, pdf, label=soc_binding_names[i])
        plt.legend()
        plt.show()

        # plot pdf without interaction
        for i in soc_binding_values:
            relative_orientation_values_without_interaction = (
                relative_orientation_without_interaction[i]
            )
            hist_without_interaction = np.histogram(
                relative_orientation_values_without_interaction, pdf_edges
            )[0]
            pdf_without_interaction = (
                hist_without_interaction / sum(hist_without_interaction) / bin_size
            )
            plt.plot(bin_centers, pdf_without_interaction, label=soc_binding_names[i])
        plt.legend()
        plt.show()

        # plot pdf with interaction
        for i in soc_binding_values:
            relative_orientation_values_with_interaction = (
                relative_orientation_with_interaction[i]
            )
            hist_with_interaction = np.histogram(
                relative_orientation_values_with_interaction, pdf_edges
            )[0]
            pdf_with_interaction = (
                hist_with_interaction / sum(hist_with_interaction) / bin_size
            )
            plt.plot(bin_centers, pdf_with_interaction, label=soc_binding_names[i])
        plt.legend()
        plt.show()

        # plot pdf with interaction scaled by pdf without
        for i in soc_binding_values:
            relative_orientation_values_with_interaction = (
                relative_orientation_with_interaction[i]
            )
            relative_orientation_values_without_interaction = (
                relative_orientation_without_interaction[i]
            )
            hist_with_interaction = np.histogram(
                relative_orientation_values_with_interaction, pdf_edges
            )[0]
            hist_without_interaction = np.histogram(
                relative_orientation_values_without_interaction, pdf_edges
            )[0]
            pdf_with_interaction = (
                hist_with_interaction / sum(hist_with_interaction) / bin_size
            )
            pdf_without_interaction = (
                hist_without_interaction / sum(hist_without_interaction) / bin_size
            )
            plt.plot(
                bin_centers,
                pdf_with_interaction / pdf_without_interaction,
                label=soc_binding_names[i],
            )
        plt.legend()
        plt.show()
