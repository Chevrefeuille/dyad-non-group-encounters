from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt

""" The goal of this script is to plot the pair distribution of the encounters between pedestrians in the corridor environment.
"""


if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:

        soc_binding_type = "soc_rel" if env_name == "atc" else "interaction"
        soc_binding_names = (
            SOCIAL_RELATIONS_EN if env_name == "atc" else INTENSITIES_OF_INTERACTION_NUM
        )
        soc_binding_values = [1, 2] if env_name == "atc" else [0, 1, 2, 3]

        pair_distribution_r_without_interaction = pickle_load(
            f"../data/pickle/pair_distribution_r_without_interaction_{env_name}.pkl"
        )
        pair_distribution_r_with_interaction = pickle_load(
            f"../data/pickle/pair_distribution_r_with_interaction_{env_name}.pkl"
        )
        pair_distribution_x_without_interaction = pickle_load(
            f"../data/pickle/pair_distribution_x_without_interaction_{env_name}.pkl"
        )
        pair_distribution_x_with_interaction = pickle_load(
            f"../data/pickle/pair_distribution_x_with_interaction_{env_name}.pkl"
        )
        pair_distribution_y_without_interaction = pickle_load(
            f"../data/pickle/pair_distribution_y_without_interaction_{env_name}.pkl"
        )
        pair_distribution_y_with_interaction = pickle_load(
            f"../data/pickle/pair_distribution_y_with_interaction_{env_name}.pkl"
        )
        pair_distribution_theta_without_interaction = pickle_load(
            f"../data/pickle/pair_distribution_theta_without_interaction_{env_name}.pkl"
        )
        pair_distribution_theta_with_interaction = pickle_load(
            f"../data/pickle/pair_distribution_theta_with_interaction_{env_name}.pkl"
        )

        distributions = {
            "r": [
                pair_distribution_r_without_interaction,
                pair_distribution_r_with_interaction,
            ],
            "x": [
                pair_distribution_x_without_interaction,
                pair_distribution_x_with_interaction,
            ],
            "y": [
                pair_distribution_y_without_interaction,
                pair_distribution_y_with_interaction,
            ],
            "theta": [
                pair_distribution_theta_without_interaction,
                pair_distribution_theta_with_interaction,
            ],
        }

        for v in distributions:
            (
                pair_distribution_without_interaction,
                pair_distribution_with_interaction,
            ) = distributions[v]
            # plot pair distributions without interaction

            plt.plot(
                pair_distribution_without_interaction[0],
                pair_distribution_without_interaction[1],
                linewidth=3,
                label="no interaction",
            )
            for i in soc_binding_values:
                plt.plot(
                    pair_distribution_without_interaction[0],
                    pair_distribution_with_interaction[i],
                    linewidth=3,
                    label=soc_binding_names[i],
                )
            plt.title(f"Distribution for {v} ({env_name})")
            plt.legend()
            # plt.show()
            plt.savefig(
                f"../data/figures/pair_distributions/{env_name}_{v}_distribution.png"
            )
            plt.clf()

            # plot pair distributions with interaction scaled by pair distribution without interaction
            for i in soc_binding_values:
                # print(pair_distribution_without_interaction)
                plt.plot(
                    pair_distribution_without_interaction[0],
                    pair_distribution_with_interaction[i]
                    / pair_distribution_without_interaction[1],
                    linewidth=3,
                    label=soc_binding_names[i],
                )
            plt.title(f"Pair distribution for {v} ({env_name})")
            plt.legend()
            # plt.show()
            plt.savefig(
                f"../data/figures/pair_distributions/{env_name}_{v}_pair_distribution.png"
            )
            plt.clf()
