from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
import matplotlib.pyplot as plt


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        env_name_short = env_name.split(":")[0]

        deflections_with_interaction = pickle_load(
            f"../data/pickle/deflection_with_interaction_{env_name_short}.pkl"
        )
        deflections_without_interaction = pickle_load(
            f"../data/pickle/deflection_without_interaction_{env_name_short}_random.pkl"
        )
        lengths_with_interaction = pickle_load(
            f"../data/pickle/length_trajectory_with_interaction_{env_name_short}.pkl"
        )
        lengths_without_interaction = pickle_load(
            f"../data/pickle/length_trajectory_without_interaction_{env_name_short}_random.pkl"
        )

        for measure in DEFLECTION_MEASURES:
            bin_size = (
                DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["max"]
                - DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["min"]
            ) / DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["n_bins"]
            pdf_edges = np.linspace(
                DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["min"],
                DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["max"],
                DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["n_bins"] + 1,
            )
            bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])
            fig, ax = plt.subplots()
            for group_non_group in ["non_group", "group_members"]:

                deflections = np.array(
                    deflections_without_interaction[group_non_group][measure]
                )
                hist = np.histogram(deflections, pdf_edges)[0]
                pdf = hist / np.sum(hist) / bin_size
                ax.plot(bin_centers, pdf, label=group_non_group)

            ax.legend()
            plt.show()

            # plot the baseline
            # ax.scatter(
            #     lengths_without_interaction[group_non_group],
            #     deflections_without_interaction[group_non_group][measure],
            #     label=f"baseline",
            #     marker=".",
            #     alpha=0.3,
            #     c="black",
            # )
            # bin plots
            # mean_deflection_per_bin_without_interaction = get_mean_over_bins(
            #     np.array(lengths_without_interaction[group_non_group]["gross"]),
            #     np.array(deflections_without_interaction[group_non_group][measure]),
            #     bin_centers,
            # )
            # ax.plot(
            #     bin_centers,
            #     mean_deflection_per_bin_without_interaction,
            #     label=f"baseline",
            #     lw=3,
            #     c="black",
            # )

            # plot the values with interaction
            # for i in soc_binding_values:
            #     # ax.scatter(
            #     #     lengths_with_interaction["opposite"][i][group_non_group],
            #     #     deflections_with_interaction["opposite"][i][measure][
            #     #         group_non_group
            #     #     ],
            #     #     label=soc_binding_names[i],
            #     #     c=soc_binding_colors[i],
            #     #     s=2,
            #     #     alpha=0.3,
            #     #     lw=3,
            #     # )

            #     # bin plots
            #     (
            #         mean_deflection_per_bin_without_interaction,
            #         std_deflection_per_bin_without_interaction,
            #     ) = get_mean_std_over_bins(
            #         np.array(
            #             lengths_with_interaction["opposite"][i][group_non_group][
            #                 "gross"
            #             ]
            #         ),
            #         np.array(
            #             deflections_with_interaction["opposite"][i][measure][
            #                 group_non_group
            #             ]
            #         ),
            #         bin_centers,
            #     )
            #     ax.plot(
            #         bin_centers,
            #         mean_deflection_per_bin_without_interaction,
            #         label=soc_binding_names[i],
            #         c=soc_binding_colors[i],
            #         lw=3,
            #     )

            # ax.set_title(f"{measure}-{group_non_group}-{env_name_short}")
            # ax.set_xlim([2000, 5000])
            # ax.set_ylim(LIMITS[measure])
            # ax.legend()
            # plt.show()
