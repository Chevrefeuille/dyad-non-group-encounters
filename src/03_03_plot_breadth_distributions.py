from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from parameters import *

import numpy as np
import matplotlib.pyplot as plt

""" The goal of this script is to plot the breadth distributions of the groups in the corridor environment considering groups with interaction.
"""

if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:
        days = DAYS_ATC if env_name == "atc" else DAYS_DIAMOR
        soc_binding_type = "soc_rel" if env_name == "atc" else "interaction"
        soc_binding_names = (
            SOCIAL_RELATIONS_EN if env_name == "atc" else INTENSITIES_OF_INTERACTION_NUM
        )
        soc_binding_values = [1, 2] if env_name == "atc" else [0, 1, 2, 3]

        breadth_with_interaction = pickle_load(
            f"../data/pickle/group_breadth_with_interaction_{env_name}.pkl"
        )
        breadth_without_interaction = pickle_load(
            f"../data/pickle/group_breadth_without_interaction_{env_name}.pkl"
        )
        breadth = pickle_load(f"../data/pickle/group_breadth_{env_name}.pkl")

        bin_size = (
            BREADTH_DISTRIBUTION_MAX - BREADTH_DISTRIBUTION_MIN
        ) / N_BINS_BREADTH_DISTRIBUTION
        pdf_edges = np.linspace(
            BREADTH_DISTRIBUTION_MIN,
            BREADTH_DISTRIBUTION_MAX,
            N_BINS_BREADTH_DISTRIBUTION + 1,
        )
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:]) / 1000

        # plot pdf
        for i in soc_binding_values:
            breadth_values = breadth[i]
            hist = np.histogram(breadth_values, pdf_edges)[0]
            pdf = hist / sum(hist) / bin_size
            plt.plot(bin_centers, pdf, label=soc_binding_names[i])
        plt.legend()
        plt.show()

        # plot pdf without interaction
        for i in soc_binding_values:
            breadth_values_without_interaction = breadth_without_interaction[i]
            hist_without_interaction = np.histogram(
                breadth_values_without_interaction, pdf_edges
            )[0]
            pdf_without_interaction = (
                hist_without_interaction / sum(hist_without_interaction) / bin_size
            )
            plt.plot(bin_centers, pdf_without_interaction, label=soc_binding_names[i])
        plt.legend()
        plt.show()

        # plot pdf with interaction
        for i in soc_binding_values:
            breadth_values_with_interaction = breadth_with_interaction[i]
            hist_with_interaction = np.histogram(
                breadth_values_with_interaction, pdf_edges
            )[0]
            pdf_with_interaction = (
                hist_with_interaction / sum(hist_with_interaction) / bin_size
            )
            plt.plot(bin_centers, pdf_with_interaction, label=soc_binding_names[i])
        plt.legend()
        plt.show()

        # plot pdf with interaction scaled by pdf without
        for i in soc_binding_values:
            breadth_values_with_interaction = breadth_with_interaction[i]
            breadth_values_without_interaction = breadth_without_interaction[i]
            hist_with_interaction = np.histogram(
                breadth_values_with_interaction, pdf_edges
            )[0]
            hist_without_interaction = np.histogram(
                breadth_values_without_interaction, pdf_edges
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
