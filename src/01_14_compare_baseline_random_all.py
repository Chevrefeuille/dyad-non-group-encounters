from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
import matplotlib.pyplot as plt
import pandas as pd


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        env_name_short = env_name.split(":")[0]

        deflections_without_interaction_segments = pickle_load(
            f"../data/pickle/deflection_without_interaction_{env_name_short}.pkl"
        )
        deflections_without_interaction_random = pickle_load(
            f"../data/pickle/deflection_without_interaction_{env_name_short}_random.pkl"
        )
        lengths_without_interaction_random = pickle_load(
            f"../data/pickle/length_trajectory_without_interaction_{env_name_short}_random.pkl"
        )
        lengths_without_interaction_segment = pickle_load(
            f"../data/pickle/length_trajectory_without_interaction_{env_name_short}.pkl"
        )

        colors = {"group": "red", "non_group": "green", "group_members": "blue"}

        # bin plot
        bin_size_t = (1000 - 10000) / 12
        pdf_edges_t = np.linspace(
            1000,
            10000,
            12 + 1,
        )
        bin_centers = 0.5 * (pdf_edges_t[0:-1] + pdf_edges_t[1:])

        for measure in DEFLECTION_MEASURES:
            fig, ax = plt.subplots()
            for group_non_group in ["non_group", "group_members"]:
                # scatter plots
                # ax.scatter(
                #     lengths_without_interaction_random[group_non_group]["gross"],
                #     deflections_without_interaction_random[group_non_group][measure],
                #     label=f"random-{group_non_group}",
                #     marker=".",
                #     alpha=0.3,
                # )
                # deflections_segments = []
                # length_segments = []
                # for segment_length in SEGMENT_LENGTHS:
                #     deflections_segments += deflections_without_interaction_segments[
                #         group_non_group
                #     ][measure][segment_length]
                #     length_segments += lengths_without_interaction_segment[
                #         group_non_group
                #     ][segment_length]["gross"]
                # ax.scatter(
                #     length_segments,
                #     deflections_segments,
                #     label=f"random-{group_non_group}",
                #     marker="+",
                #     alpha=0.3,
                # )

                # bin plot
                (
                    mean_deflection_per_bin_without_interaction,
                    std,
                    ste,
                ) = get_mean_std_ste_over_bins(
                    np.array(
                        lengths_without_interaction_random[group_non_group]["gross"]
                    ),
                    np.array(
                        deflections_without_interaction_random[group_non_group][measure]
                    ),
                    bin_centers,
                )
                ax.plot(
                    bin_centers,
                    mean_deflection_per_bin_without_interaction,
                    label=f"random-{group_non_group}",
                    c=colors[group_non_group],
                )

                data = np.array(
                    [
                        bin_centers / 1000,
                        mean_deflection_per_bin_without_interaction,
                        ste,
                    ]
                ).T
                pd.DataFrame(data).to_csv(
                    f"../data/plots/deflections/baseline/{env_name_short}_{measure}_{group_non_group}.csv",
                    index=False,
                    header=False,
                )

                # plot the baseline without interactions with random lengths
                # deflections_per_segment = []
                # for segment_length in SEGMENT_LENGTHS:
                #     deflections = deflections_without_interaction_segments[
                #         group_non_group
                #     ][measure][segment_length]
                #     deflections_per_segment += [np.nanmean(deflections)]
                # ax.plot(
                #     SEGMENT_LENGTHS,
                #     deflections_per_segment,
                #     label=f"segments-{group_non_group}",
                #     c=colors[group_non_group],
                # )

            ax.set_ylim(LIMITS[measure])
            ax.set_title(f"{measure}-{group_non_group}-{env_name_short}")
            ax.set_xlim([1000, 10000])
            ax.legend()
            fig.savefig(
                f"../data/figures/deflection/random/{env_name_short}_{group_non_group}_{measure}.png"
            )
            # plt.show()
            plt.close()

            # fig.savefig(
            #     f"../data/figures/deflection/random_vs_segment/{env_name_short}_{measure}.png"
            # )
            # plt.show()
            # plt.close()
