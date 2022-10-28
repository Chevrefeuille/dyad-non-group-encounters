from tkinter import N
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np

from utils import *
from tqdm import tqdm

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        group_breadth_all = pickle_load(
            f"../data/pickle/group_breadth_{env_name_short}.pkl"
        )
        group_depth_all = pickle_load(
            f"../data/pickle/group_depth_{env_name_short}.pkl"
        )
        group_size_all = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        # for i, v in enumerate(soc_binding_values):
        #     print(soc_binding_names[v])
        #     print(f" - depth: {5000/np.nanmean(group_depth_all[v])}")
        #     print(f" - breadth: {5000/np.nanmean(group_breadth_all[v])}")
        #     print(f" - size: {5000/np.nanmean(group_size_all[v])}")

        min_x_no_scaling, max_x_no_scaling = -4, 4
        min_y_no_scaling, max_y_no_scaling = -4, 4
        n_bins_x_no_scaling, n_bins_y_no_scaling = 20, 20
        (
            grids_count_no_scaling,
            xi_no_scaling,
            yi_no_scaling,
            cell_size_x_no_scaling,
            cell_size_y_no_scaling,
        ) = get_grid(
            min_x_no_scaling,
            max_x_no_scaling,
            n_bins_x_no_scaling,
            min_y_no_scaling,
            max_y_no_scaling,
            n_bins_y_no_scaling,
            n_channels=len(soc_binding_values),
        )

        min_x_scaled_breadth, max_x_scaled_breadth = -20, 20
        min_y_scaled_breadth, max_y_scaled_breadth = -8, 8
        n_bins_x_scaled_breadth, n_bins_y_scaled_breadth = 20, 20
        (
            grids_count_scaled_breadth,
            xi_scaled_breadth,
            yi_scaled_breadth,
            cell_size_x_scaled_breadth,
            cell_size_y_scaled_breadth,
        ) = get_grid(
            min_x_scaled_breadth,
            max_x_scaled_breadth,
            n_bins_x_scaled_breadth,
            min_y_scaled_breadth,
            max_y_scaled_breadth,
            n_bins_y_scaled_breadth,
            n_channels=len(soc_binding_values),
        )

        min_x_scaled_size, max_x_scaled_size = -6, 6
        min_y_scaled_size, max_y_scaled_size = -6, 6
        n_bins_x_scaled_size, n_bins_y_scaled_size = 20, 20
        (
            grids_count_scaled_size,
            xi_scaled_size,
            yi_scaled_size,
            cell_size_x_scaled_size,
            cell_size_y_scaled_size,
        ) = get_grid(
            min_x_scaled_size,
            max_x_scaled_size,
            n_bins_x_scaled_size,
            min_y_scaled_size,
            max_y_scaled_size,
            n_bins_y_scaled_size,
            n_channels=len(soc_binding_values),
        )

        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        for day in tqdm(days):

            non_groups = env.get_pedestrians(
                days=[day], thresholds=thresholds_ped, no_groups=True
            )

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

                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    non_groups,
                    proximity_threshold=4000,
                    skip=group_members_id,
                    # alone=True,
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

                    grids_count_no_scaling = update_grid(
                        grids_count_no_scaling,
                        pos_non_group_aligned / 1000,
                        min_x_no_scaling,
                        n_bins_x_no_scaling,
                        cell_size_x_no_scaling,
                        min_y_no_scaling,
                        n_bins_y_no_scaling,
                        cell_size_y_no_scaling,
                        channel=soc_binding_values.index(soc_binding),
                    )

                    pos_non_group_aligned_scaled_size = pos_non_group_aligned.copy()
                    pos_non_group_aligned_scaled_size /= np.nanmean(
                        group_size_all[soc_binding]
                    )

                    grids_count_scaled_size = update_grid(
                        grids_count_scaled_size,
                        pos_non_group_aligned_scaled_size,
                        min_x_scaled_size,
                        n_bins_x_scaled_size,
                        cell_size_x_scaled_size,
                        min_y_scaled_size,
                        n_bins_y_scaled_size,
                        cell_size_y_scaled_size,
                        channel=soc_binding_values.index(soc_binding),
                    )

                    pos_non_group_aligned_scaled_breadth = pos_non_group_aligned.copy()
                    pos_non_group_aligned_scaled_breadth[:, 0] /= np.nanmean(
                        group_depth_all[soc_binding]
                    )
                    pos_non_group_aligned_scaled_breadth[:, 1] /= np.nanmean(
                        group_breadth_all[soc_binding]
                    )
                    grids_count_scaled_breadth = update_grid(
                        grids_count_scaled_breadth,
                        pos_non_group_aligned_scaled_breadth,
                        min_x_scaled_breadth,
                        n_bins_x_scaled_breadth,
                        cell_size_x_scaled_breadth,
                        min_y_scaled_breadth,
                        n_bins_y_scaled_breadth,
                        cell_size_y_scaled_breadth,
                        channel=soc_binding_values.index(soc_binding),
                    )

        pickle_save(
            f"../data/pickle/aligned_trajectories_2D_counts_{env_name_short}.pkl",
            grids_count_no_scaling,
        )
        pickle_save(
            f"../data/pickle/aligned_trajectories_2D_counts_{env_name_short}_scaled_size.pkl",
            grids_count_scaled_size,
        )
        pickle_save(
            f"../data/pickle/aligned_trajectories_2D_counts_{env_name_short}_scaled_breadth.pkl",
            grids_count_scaled_breadth,
        )
