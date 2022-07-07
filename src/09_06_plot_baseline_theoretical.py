from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
import matplotlib.pyplot as plt


if __name__ == "__main__":

    for env_name in ["atc:corridor"]:

        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        env_name_short = env_name.split(":")[0]

        deflections_without_interaction_random = pickle_load(
            f"../data/pickle/deflection_without_interaction_{env_name_short}_random.pkl"
        )
        lengths_without_interaction_random = pickle_load(
            f"../data/pickle/length_trajectory_without_interaction_{env_name_short}_random.pkl"
        )

        deflections_theoretical = pickle_load(
            f"../data/pickle/deflection_theoretical_{env_name_short}.pkl"
        )
        lengths_theoretical = pickle_load(
            f"../data/pickle/length_trajectory_theoretical_{env_name_short}.pkl"
        )

        colors = {"group": "red", "non_group": "green", "group_members": "blue"}

        # bin plot
        bin_size_t = (RND_TRAJ_SIZE_MAX - RND_TRAJ_SIZE_MIN) / N_BINS_RND_TRAJ_SIZE
        pdf_edges_t = np.linspace(
            RND_TRAJ_SIZE_MIN,
            RND_TRAJ_SIZE_MAX,
            N_BINS_RND_TRAJ_SIZE + 1,
        )
        bin_centers_t = 0.5 * (pdf_edges_t[0:-1] + pdf_edges_t[1:])

        for measure in DEFLECTION_MEASURES:
            for group_non_group in ["non_group", "group_members"]:
                fig, ax = plt.subplots()
                # scatter plots
                ax.scatter(
                    lengths_without_interaction_random[group_non_group]["gross"],
                    deflections_without_interaction_random[group_non_group][measure],
                    label=f"random-{group_non_group}",
                    marker=".",
                    alpha=0.3,
                )
                ax.scatter(
                    lengths_theoretical["gross"],
                    deflections_theoretical[measure],
                    label=f"theoretical-{group_non_group}",
                    marker=".",
                    alpha=0.3,
                )

                # bin plot
                mean_deflection_per_bin_without_interaction = get_mean_over_bins(
                    np.array(
                        lengths_without_interaction_random[group_non_group]["gross"]
                    ),
                    np.array(
                        deflections_without_interaction_random[group_non_group][measure]
                    ),
                    bin_centers_t,
                )
                ax.plot(
                    bin_centers_t,
                    mean_deflection_per_bin_without_interaction,
                    label=f"random-{group_non_group}",
                    c=colors[group_non_group],
                    ls="dashed",
                )
                # ax.set_ylim(LIMITS[measure])
                ax.set_title(f"{measure}-{group_non_group}-{env_name_short}")
                ax.set_xlim([1000, 6000])
                ax.legend()
                # fig.savefig(
                #     f"../data/figures/deflection/random_vs_segment/{env_name_short}_{group_non_group}_{measure}.png"
                # )
                plt.show()
                plt.close()

            # fig.savefig(
            #     f"../data/figures/deflection/random_vs_segment/{env_name_short}_{measure}.png"
            # )
            # plt.show()
            # plt.close()
