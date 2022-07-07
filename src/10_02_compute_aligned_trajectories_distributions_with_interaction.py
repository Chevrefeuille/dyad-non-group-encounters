from tkinter import N
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np

from utils import *


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        # for the angle theta
        bin_size_theta = (
            PAIR_DISTRIBUTION_MAX_THETA - PAIR_DISTRIBUTION_MIN_THETA
        ) / N_BINS_PAIR_DISTRIBUTION_THETA
        pdf_edges_theta = np.linspace(
            PAIR_DISTRIBUTION_MIN_THETA,
            PAIR_DISTRIBUTION_MAX_THETA,
            N_BINS_PAIR_DISTRIBUTION_THETA + 1,
        )
        pair_distribution_theta = {}

        encounters = pickle_load(
            f"../data/pickle/opposite_encounters_{env_name_short}.pkl"
        )
        walls = pickle_load(f"../data/pickle/walls_{env_name_short}.pkl")
        walls_cells = np.argwhere(walls)
        wall_img = f"../data/images/walls_{env_name_short}.png"

        grids_count = np.zeros((len(soc_binding_values), N_BINS_2D_RX, N_BINS_2D_RY))
        xi = np.linspace(0, (RX_MAX - RX_MIN) / 1000, N_BINS_2D_RX)
        yi = np.linspace(0, (RY_MAX - RY_MIN) / 1000, N_BINS_2D_RY)
        cell_size_x = int((RX_MAX - RX_MIN) / N_BINS_2D_RX)
        cell_size_y = int((RY_MAX - RY_MIN) / N_BINS_2D_RY)
        # grids_vel =np.zeros((len(soc_binding_values), n_bin_x, n_bin_y))

        for day in days:

            thresholds_ped = get_pedestrian_thresholds(env_name)
            thresholds_group = get_groups_thresholds()

            non_groups = env.get_pedestrians(days=[day], thresholds=thresholds_ped)

            groups = env.get_groups(
                size=2,
                days=[day],
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                with_social_binding=True,
            )

            for group in groups:
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()
                group_members_id = [m.get_id() for m in group.get_members()]

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding not in soc_binding_values:
                    continue

                if soc_binding not in pair_distribution_theta:
                    pair_distribution_theta[soc_binding] = np.zeros(
                        len(pdf_edges_theta) - 1
                    )

                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    non_groups, proximity_threshold=None, skip=group_members_id
                )

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

                    relative_direction = compute_relative_direction(
                        group_as_indiv.get_trajectory(), non_group.get_trajectory()
                    )

                    if relative_direction != "opposite":
                        continue

                    if len(traj_group) <= 1:
                        continue

                    traj_group_aligned, [
                        traj_non_group_aligned
                    ] = align_trajectories_at_origin(traj_group, [traj_non_group])

                    # plot_static_2D_trajectories(
                    #     [
                    #         traj_group,
                    #         traj_group_aligned,
                    #         traj_non_group_aligned,
                    #         traj_non_group,
                    #     ],
                    #     labels=["galigned", "ngaligned", "ng", "g"],
                    # )

                    pos_non_group_aligned = traj_non_group_aligned[:, 1:3]
                    # d_G_NG = compute_interpersonal_distance(traj_group_aligned, traj_non_group_aligned)
                    # pos_non_group_aligned = pos_non_group_aligned[d_G_NG < 5000]

                    cell_x = np.ceil(
                        (pos_non_group_aligned[:, 0] - RX_MIN) / cell_size_x
                    ).astype("int")
                    cell_y = np.ceil(
                        (pos_non_group_aligned[:, 1] - RY_MIN) / cell_size_y
                    ).astype("int")

                    # remove date outside the range of interest
                    in_roi = np.logical_and(
                        np.logical_and(cell_x >= 0, cell_x < N_BINS_2D_RX),
                        np.logical_and(cell_y >= 0, cell_y < N_BINS_2D_RY),
                    )
                    cell_x = cell_x[in_roi]
                    cell_y = cell_y[in_roi]

                    grids_count[
                        soc_binding_values.index(soc_binding), cell_x, cell_y
                    ] += 1

                    theta = np.arctan2(
                        pos_non_group_aligned[1:, 0], pos_non_group_aligned[1:, 1]
                    )
                    theta[theta > np.pi] -= 2 * np.pi
                    theta[theta < -np.pi] += 2 * np.pi
                    pair_distribution_theta[soc_binding] += np.histogram(
                        theta, pdf_edges_theta
                    )[0]

        for i, v in enumerate(soc_binding_values):
            max_value = np.max(grids_count[i, ...])
            grids_count[i, ...] /= max_value
            plt.figure()
            cmesh = plt.pcolormesh(
                xi, yi, grids_count[i, ...].T, cmap="inferno_r", shading="auto"
            )
            plt.xlabel("x (m)")
            plt.ylabel("y (m)")
            axes = plt.gca()
            # divider = make_axes_locatable(axes)
            # cax = divider.append_axes("right", size="5%", pad=0.3)
            plt.colorbar(cmesh)
            axes.set_aspect("equal")
            # plt.show()

            pair_distribution_theta[v] = (
                pair_distribution_theta[v]
                / sum(pair_distribution_theta[v])
                / bin_size_theta
            )

        pickle_save(
            f"../data/pickle/aligned_trajectories_2D_distribution_{env_name_short}_with_interaction.pkl",
            grids_count,
        )

        pickle_save(
            f"../data/pickle/aligned_trajectories_distribution_theta_with_interaction_{env_name_short}.pkl",
            pair_distribution_theta,
        )
