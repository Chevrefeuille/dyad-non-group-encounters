from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
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

        breadths_without_interaction = pickle_load(
            f"../data/pickle/group_breadth_without_interaction_diff_days_{env_name_short}.pkl"
        )
        distances_without_interaction = pickle_load(
            f"../data/pickle/group_non_group_distance_without_interaction_diff_days_{env_name_short}.pkl"
        )
        breadths_with_interaction = pickle_load(
            f"../data/pickle/group_breadth_with_interaction_{env_name_short}.pkl"
        )
        distances_with_interaction = pickle_load(
            f"../data/pickle/group_non_group_distance_with_interaction_{env_name_short}.pkl"
        )

        # scatter distance, breadth
        fig, ax = plt.subplots()
        for i in soc_binding_values:
            ax.scatter(
                distances_with_interaction[i],
                breadths_with_interaction[i],
                c=soc_binding_colors[i],
                label=soc_binding_names[i],
                alpha=0.3,
            )
        ax.legend()
        plt.savefig(
            f"../data/figures/breadth/{env_name}_scatter_breadth_vs_distance.png"
        )
        # plt.show()
        plt.close()

        # bin plot distance breadth
        n_bins = 16
        d_min, d_max = 0, 5000
        bin_size = (d_max - d_min) / n_bins
        pdf_edges = np.linspace(d_min, d_max, n_bins + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])
        fig, ax = plt.subplots()
        for i in soc_binding_values:
            means, stds = get_mean_std_over_bins(
                np.array(distances_with_interaction[i]),
                np.array(breadths_with_interaction[i]),
                bin_centers,
            )
            ax.plot(
                bin_centers, means, c=soc_binding_colors[i], label=soc_binding_names[i]
            )
        ax.legend()
        # plt.show()
        plt.savefig(f"../data/figures/breadth/{env_name}_bin_breadth_vs_distance.png")
        plt.close()

        # plot ratio distance / breadth
        # n_bins = 64
        # r_max, r_min = 80, 0
        # bin_size = (r_max - r_min) / n_bins
        # pdf_edges = np.linspace(r_min, r_max, n_bins + 1)
        # bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        # fig, ax = plt.subplots()
        # for i in soc_binding_values:
        #     delta_d_ratio_without_interaction = np.array(
        #         distances_without_interaction[i]
        #     ) / np.array(breadths_without_interaction[i])
        #     hist_without_interaction = np.histogram(
        #         delta_d_ratio_without_interaction, pdf_edges
        #     )[0]
        #     pdf_without_interaction = (
        #         hist_without_interaction / np.sum(hist_without_interaction) / bin_size
        #     )
        #     ax.plot(
        #         bin_centers,
        #         pdf_without_interaction,
        #         c=soc_binding_colors[i],
        #         label=soc_binding_names[i],
        #         ls="dashed",
        #     )

        #     delta_d_ratio_with_interaction = np.array(
        #         distances_with_interaction[i]
        #     ) / np.array(breadths_with_interaction[i])
        #     hist_with_interaction = np.histogram(
        #         delta_d_ratio_with_interaction, pdf_edges
        #     )[0]
        #     pdf_with_interaction = (
        #         hist_with_interaction / np.sum(hist_with_interaction) / bin_size
        #     )
        #     ax.plot(
        #         bin_centers,
        #         pdf_with_interaction,
        #         c=soc_binding_colors[i],
        #         label=soc_binding_names[i],
        #     )

        ax.legend()
        plt.show()
        plt.close()

        # # plot pair distributions with interaction scaled by pair distribution without interaction
        # for i in soc_binding_values:
        #     # print(pair_distribution_without_interaction)
        #     plt.plot(
        #         pair_distribution_t_without_interaction[0],
        #         pair_distribution_t_with_interaction[i]
        #         / pair_distribution_t_without_interaction[1],
        #         linewidth=3,
        #         label=soc_binding_names[i],
        #     )
        # plt.title(f"Pair distribution for time to collisions ({env_name})")
        # plt.legend()
        # # plt.show()
        # plt.savefig(
        #     f"../data/figures/pair_distributions/{env_name}_time_to_collision_pair_distribution.png"
        # )
        # plt.clf()
