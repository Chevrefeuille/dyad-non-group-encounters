from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.trajectory_utils import *

from parameters import *
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:
        # print(f"- {env_name}")
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = DAYS_ATC if env_name == "atc" else DAYS_DIAMOR
        soc_binding_type = "soc_rel" if env_name == "atc" else "interaction"
        soc_binding_values = (
            SOCIAL_RELATIONS_EN if env_name == "atc" else INTENSITIES_OF_INTERACTION_NUM
        )

        encounters = pickle_load(f"../data/pickle/opposite_encounters_{env_name}.pkl")

        valid_encounters = {}

        XMAX = VICINITY * 2
        XMIN = -VICINITY * 0.5
        YMIN = -VICINITY * 1
        YMAX = VICINITY * 1

        # define the grid for the density plot
        CELL_SIZE = 100
        n_bin_x = int(np.ceil((XMAX - XMIN) / CELL_SIZE) + 1)
        n_bin_y = int(np.ceil((YMAX - YMIN) / CELL_SIZE) + 1)
        grid_group = np.zeros((n_bin_x, n_bin_y))
        grid_non_group = np.zeros((n_bin_x, n_bin_y))

        distance_breadth_orientation = {}

        for day in days:
            # print(f"  - day {day}:")

            valid_encounters[day] = {}

            group_ids = list(encounters[day].keys())
            non_group_ids = list(
                set(
                    [
                        ped_id
                        for non_groups in encounters[day].values()
                        for ped_id in non_groups
                    ]
                )
            )
            threshold_v = Threshold("v", min=500, max=3000)  # velocity in [0.5; 3]m/s
            threshold_d = Threshold("d", min=5000)  # walk at least 5 m
            thresholds = [threshold_v, threshold_d]

            # threshold on the distance between the group members, max 4 m
            threshold_delta = Threshold("delta", max=2000)

            # corridor threshold for ATC
            if env_name == "atc":
                threshold_corridor_x = Threshold("x", 5000, 48000)
                threshold_corridor_y = Threshold("y", -27000, 8000)
                thresholds += [threshold_corridor_x, threshold_corridor_y]

            non_groups = env.get_pedestrians(
                days=[day], ids=non_group_ids, thresholds=thresholds
            )
            non_groups_dict = {p.get_id(): p for p in non_groups}

            groups = env.get_groups(
                size=2,
                days=[day],
                ids=group_ids,
                ped_thresholds=thresholds,
                group_thresholds=[threshold_delta],
            )

            for group in groups:
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding is None:
                    continue

                if soc_binding not in distance_breadth_orientation:
                    distance_breadth_orientation[soc_binding] = []

                group_encounters_id = encounters[day][group_id]
                group_encounters = [
                    non_groups_dict[ped_id]
                    for ped_id in group_encounters_id
                    if ped_id in non_groups_dict
                ]

                valid_encounters[day][group] = []

                if not group_encounters:
                    continue

                for non_group in group_encounters:

                    non_group_id = non_group.get_id()

                    trajectories = [
                        group_members[0].get_trajectory(),
                        group_members[1].get_trajectory(),
                        group_as_indiv.get_trajectory(),
                        non_group.get_trajectory(),
                    ]
                    [
                        traj_A,
                        traj_B,
                        traj_group,
                        traj_non_group,
                    ] = compute_simultaneous_observations(trajectories)

                    pos_A = traj_A[:, 1:3]
                    pos_B = traj_B[:, 1:3]
                    pos_group = traj_group[:, 1:3]
                    pos_non_group = traj_non_group[:, 1:3]

                    d_G_NG = np.linalg.norm(pos_group - pos_non_group, axis=1)

                    traj_A_encounter = traj_A[d_G_NG < VICINITY]
                    traj_B_encounter = traj_B[d_G_NG < VICINITY]
                    traj_group_encounter = traj_group[d_G_NG < VICINITY]
                    pos_A_encounter = pos_A[d_G_NG < VICINITY]
                    pos_B_encounter = pos_B[d_G_NG < VICINITY]
                    pos_group_encounter = pos_group[d_G_NG < VICINITY]
                    pos_non_group_encounter = pos_non_group[d_G_NG < VICINITY]

                    if len(pos_group_encounter) < 1:
                        continue

                    d_G_NG_encounter = np.linalg.norm(
                        pos_group_encounter - pos_non_group_encounter, axis=1
                    )

                    d_g_encounter = compute_interpersonal_distance(
                        pos_A_encounter, pos_B_encounter
                    )

                    rel_orientation_encounter = compute_relative_orientation(
                        traj_A_encounter, traj_B_encounter
                    )
                    # v_g_encounter = traj_group[:, 5:7]

                    # plt.plot(d_g_encounter)
                    # plt.scatter(d_G_NG_encounter, d_g_encounter)
                    # plt.ylim([0, 2000])
                    # plt.xlim([0, 22000])
                    # plt.show()

                    # get close and group breadth increase
                    # if (
                    #     len(d_g_encounter[d_G_NG_encounter < 1000])
                    #     and np.max(d_g_encounter[d_G_NG_encounter < 1000]) > 1500
                    # ):
                    #     plot_animated_2D_trajectories(
                    #         group_members + [non_group], boundaries=env.boundaries
                    #     )

                    distance_breadth_orientation[soc_binding] += list(
                        np.stack(
                            (
                                d_G_NG_encounter,
                                d_g_encounter,
                                rel_orientation_encounter,
                            ),
                            axis=1,
                        )
                    )

                    # line that define the direction of the meeting
                    # taken between a point in between the two trajectories
                    # at the start and at the end
                    line_start = (
                        pos_group_encounter[0] + pos_non_group_encounter[-1]
                    ) / 2
                    line_end = (
                        pos_group_encounter[-1] + pos_non_group_encounter[0]
                    ) / 2

                    # translate to have the group start around (0,0)
                    t_pos_A_encounter = translate_position(pos_A_encounter, -line_start)
                    t_pos_B_encounter = translate_position(pos_B_encounter, -line_start)
                    t_pos_group_encounter = translate_position(
                        pos_group_encounter, -line_start
                    )
                    t_pos_non_group_encounter = translate_position(
                        pos_non_group_encounter, -line_start
                    )

                    # rotate to align the trajectory of the group in the direction of the line
                    # along +x
                    line = np.array([line_start, line_end]) - line_start

                    # line /= np.linalg.norm(line)
                    angle = -np.arctan2(line[1, 1], line[1, 0])
                    # angle = np.pi / 2

                    line = rotate_position(line, angle)

                    r_pos_A_encounter = rotate_position(t_pos_A_encounter, angle)
                    r_pos_B_encounter = rotate_position(t_pos_B_encounter, angle)
                    r_pos_group_encounter = rotate_position(
                        t_pos_group_encounter, angle
                    )
                    r_pos_non_group_encounter = rotate_position(
                        t_pos_non_group_encounter, angle
                    )

                    group_cell_x = np.ceil(
                        (r_pos_A_encounter[:, 0] - XMIN) / CELL_SIZE
                    ).astype("int")
                    group_cell_y = np.ceil(
                        (r_pos_A_encounter[:, 1] - YMIN) / CELL_SIZE
                    ).astype("int")

                    # print(r_pos_A_encounter)
                    # grid_group[group_cell_x, group_cell_y] += 1

                    # print(max(d_g_encounter))
                    # if max(d_g_encounter) > 20000:
                    #     plt.scatter(
                    #         r_pos_A_encounter[:, 0] / 1000,
                    #         r_pos_A_encounter[:, 1] / 1000,
                    #         s=2,
                    #     )
                    #     plt.scatter(
                    #         r_pos_B_encounter[:, 0] / 1000,
                    #         r_pos_B_encounter[:, 1] / 1000,
                    #         s=2,
                    #     )
                    #     plt.axis("scaled")
                    #     plt.xlim(
                    #         [
                    #             env.boundaries["xmin"] / 1000,
                    #             env.boundaries["xmax"] / 1000,
                    #         ]
                    #     )
                    #     plt.ylim(
                    #         [
                    #             env.boundaries["ymin"] / 1000,
                    #             env.boundaries["ymax"] / 1000,
                    #         ]
                    #     )
                    #     plt.show()

                    # plt.plot(
                    #     line[:, 0] / 1000,
                    #     line[:, 1] / 1000,
                    #     c="red",
                    # )
                    # plt.axis("scaled")
                    # # plt.plot(
                    # #     [
                    # #         pos_group_encounter[0, 0] / 1000,
                    # #         pos_non_group_encounter[0, 0] / 1000,
                    # #     ],
                    # #     [
                    # #         pos_group_encounter[0, 1] / 1000,
                    # #         pos_non_group_encounter[0, 1] / 1000,
                    # #     ],
                    # #     c="red",
                    # # )
                    # # plt.plot(
                    # #     [
                    # #         pos_group_encounter[-1, 0] / 1000,
                    # #         pos_non_group_encounter[-1, 0] / 1000,
                    # #     ],
                    # #     [
                    # #         pos_group_encounter[-1, 1] / 1000,
                    # #         pos_non_group_encounter[-1, 1] / 1000,
                    # #     ],
                    # #     c="green",
                    # # )

        for i, soc_binding in enumerate(soc_binding_values):
            distance_breadth_orientation_soc_binding = np.array(
                distance_breadth_orientation[i]
            )
            CELL_SIZE = 100
            XMIN, XMAX = 0, 4000
            YMIN, YMAX = 0, 2000
            n_bin_x = int(np.ceil((XMAX - XMIN) / CELL_SIZE) + 1)

            # plot mean for each bin
            pdf_edges = np.linspace(XMIN, XMAX, n_bin_x)
            bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])
            distance = distance_breadth_orientation_soc_binding[:, 0]
            distance_bins = np.digitize(distance, pdf_edges)
            breadth = distance_breadth_orientation_soc_binding[:, 1]
            breadth_mean, breadth_error = [], []
            for bin_val in range(n_bin_x - 1):
                n_val = np.sum(distance_bins == bin_val)
                if n_val > 0:
                    mean = np.mean(breadth[distance_bins == bin_val])
                    std = np.std(breadth[distance_bins == bin_val])
                    error = std / (n_val**0.5)
                else:
                    mean, std, error = None, None, None
                breadth_mean += [mean]
                breadth_error += [error]
            bin_centers = [
                bin_centers[i] for i in range(n_bin_x - 1) if breadth_mean[i]
            ]
            breadth_error = [
                breadth_error[i] for i in range(n_bin_x - 1) if breadth_mean[i]
            ]
            breadth_mean = [
                breadth_mean[i] for i in range(n_bin_x - 1) if breadth_mean[i]
            ]

            plt.errorbar(
                bin_centers,
                breadth_mean,
                yerr=breadth_error,
                label=soc_binding,
            )
            # plt.ylim([0, 2000])
        plt.legend()
        plt.show()

        # print(distance_bin_indices)
