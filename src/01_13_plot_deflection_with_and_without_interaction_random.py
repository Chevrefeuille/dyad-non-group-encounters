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

        if "atc" in env_name:
            soc_binding_values = [1, 2]

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

        # scatter plot
        for measure in DEFLECTION_MEASURES:
            for group_non_group in ["group", "non_group", "group_members"]:
                # plot the baseline without interactions

                plt.scatter(
                    lengths_without_interaction[group_non_group]["gross"],
                    deflections_without_interaction[group_non_group][measure],
                    s=2,
                    alpha=0.5,
                    label="baseline",
                )

                # plot the values with interaction
                for i in soc_binding_values:
                    plt.scatter(
                        lengths_with_interaction["opposite"][i][group_non_group][
                            "gross"
                        ],
                        deflections_with_interaction["opposite"][i][measure][
                            group_non_group
                        ],
                        label=soc_binding_names[i],
                        s=2,
                        alpha=0.5,
                    )

                # plt.ylim(LIMITS[measure])
                plt.title(f"{measure}-{group_non_group}-{env_name}")
                plt.legend()
                plt.show()
                # plt.cla()

        # bin plot
        bin_size_t = (RND_TRAJ_SIZE_MAX - RND_TRAJ_SIZE_MIN) / N_BINS_RND_TRAJ_SIZE
        pdf_edges_t = np.linspace(
            RND_TRAJ_SIZE_MIN,
            RND_TRAJ_SIZE_MAX,
            N_BINS_RND_TRAJ_SIZE + 1,
        )
        bin_centers_t = 0.5 * (pdf_edges_t[0:-1] + pdf_edges_t[1:])

        for measure in DEFLECTION_MEASURES:
            for group_non_group in ["group", "non_group"]:
                # plot the values without interaction
                mean_deflection_per_bin = get_mean_over_bins(
                    lengths_without_interaction[group_non_group]["net"],
                    np.array(deflections_without_interaction[group_non_group][measure]),
                    bin_centers_t,
                )
                plt.plot(bin_centers_t, mean_deflection_per_bin, label="baseline")

                # plot the values with interaction
                for i in soc_binding_values:
                    mean_deflection_per_bin = get_mean_over_bins(
                        lengths_with_interaction["opposite"][i][group_non_group][
                            "gross"
                        ],
                        np.array(
                            deflections_with_interaction["opposite"][i][measure][
                                group_non_group
                            ]
                        ),
                        bin_centers_t,
                    )

                    plt.plot(
                        bin_centers_t,
                        mean_deflection_per_bin,
                        label=soc_binding_names[i],
                    )

                plt.ylim(LIMITS[measure])
                plt.title(f"{group_non_group}-{measure}-{env_name}")
                plt.legend()
                # plt.show()
                plt.close()

        # for measure in DEFLECTION_MEASURES:
        #     for group_non_group in ["group", "non_group"]:
        #         # plot the baseline without interactions
        #         bin_ids = np.digitize(
        #             lengths_without_interaction[group_non_group][measure],
        #             bin_centers_t,
        #         )
        #         mean_deflection_per_bin_without_interaction = []
        #         deflections = np.array(
        #             deflections_without_interaction[group_non_group][measure]
        #         )
        #         for k in range(N_BINS_RND_TRAJ_SIZE):
        #             mean_for_bin = np.nanmean(deflections[bin_ids == k])
        #             mean_deflection_per_bin_without_interaction += [mean_for_bin]

        #         # plot the values with interaction
        #         for i in soc_binding_values:
        #             bin_ids = np.digitize(
        #                 lengths_with_interaction["opposite"][i][measure][
        #                     group_non_group
        #                 ],
        #                 bin_centers_t,
        #             )
        #             mean_deflection_per_bin = []
        #             deflections = np.array(
        #                 deflections_with_interaction["opposite"][i][measure][
        #                     group_non_group
        #                 ]
        #             )
        #             for k in range(N_BINS_RND_TRAJ_SIZE):
        #                 mean_for_bin = np.nanmean(deflections[bin_ids == k])
        #                 mean_deflection_per_bin += [mean_for_bin]
        #             plt.plot(
        #                 bin_centers_t,
        #                 np.array(mean_deflection_per_bin)
        #                 / np.array(mean_deflection_per_bin_without_interaction),
        #                 label=soc_binding_names[i],
        #             )

        #         plt.ylim([0, 2])
        #         plt.title(f"{group_non_group}-{measure}-{env_name}")
        #         plt.legend()
        #         plt.show()
        #         plt.cla()

        # for measure in DEFLECTION_MEASURES:
        #     for group_non_group in ["group", "non_group"]:
        #         # plot the baseline without interactions
        #         deflections_per_length = []
        #         for segment_length in SEGMENT_LENGTHS:
        #             deflections = deflections_without_interaction[group_non_group][
        #                 measure
        #             ][segment_length]
        #             deflections_per_length += [np.nanmean(deflections)]

        #         plt.plot(
        #             SEGMENT_LENGTHS,
        #             deflections_per_length,
        #             label=group_non_group,
        #         )

        #         # plot the values with interaction
        #         for i in soc_binding_values:
        #             plt.scatter(
        #                 lengths["opposite"][i][measure][group_non_group],
        #                 deflections_with_interaction["opposite"][i][measure][
        #                     group_non_group
        #                 ],
        #                 label=soc_binding_names[i],
        #                 s=2,
        #                 alpha=0.5,
        #             )

        #         plt.ylim(LIMITS[measure])
        #         plt.title(measure)
        #         plt.legend()

        # plot 2D maps of the segment length against the deflection
        # xi = np.linspace(RND_TRAJ_SIZE_MIN, RND_TRAJ_SIZE_MAX, 32)
        # yi = np.linspace(
        #     DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["min"],
        #     DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["max"],
        #     DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["n_bins"],
        # )
        # for measure in DEFLECTION_MEASURES:
        #     grid = compute_grid_count(
        #         np.array(lengths_without_interaction[group_non_group]["gross"]),
        #         np.array(deflections_without_interaction[group_non_group][measure]),
        #         RND_TRAJ_SIZE_MIN,
        #         RND_TRAJ_SIZE_MAX,
        #         32,
        #         DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["min"],
        #         DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["max"],
        #         DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["n_bins"],
        #     )
        #     plot_color_map(xi, yi, grid, "segment", measure, equal=False)
