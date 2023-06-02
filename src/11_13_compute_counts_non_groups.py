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

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        min_x, max_x = -4, 4
        min_y, max_y = -4, 4
        n_bins_x, n_bins_y = 20, 20
        (
            grids_count,
            xi,
            yi,
            cell_size_x,
            cell_size_y,
        ) = get_grid(min_x, max_x, n_bins_x, min_y, max_y, n_bins_y)

        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        thresholds_ped = get_pedestrian_thresholds(env_name)

        for day in days:
            # print(day)
            non_groups = env.get_pedestrians(
                days=[day], thresholds=thresholds_ped, no_groups=True, sampling_time=500
            )

            for non_group in tqdm(non_groups[:1000]):
                non_group_id = non_group.get_id()

                encounters = non_group.get_encountered_pedestrians(
                    non_groups, proximity_threshold=4000, skip=[non_group_id]
                )

                for other_non_group in encounters:

                    non_group_id = non_group.get_id()

                    trajectories = [
                        non_group.get_trajectory(),
                        other_non_group.get_trajectory(),
                    ]
                    relative_direction = compute_relative_direction(
                        non_group.get_trajectory(), other_non_group.get_trajectory()
                    )

                    if relative_direction != "opposite":
                        continue

                    [
                        traj_non_group,
                        traj_other_non_group,
                    ] = compute_simultaneous_observations(trajectories)

                    if len(traj_non_group) <= 1:
                        continue

                    traj_non_group_aligned, [
                        traj_other_non_group_aligned
                    ] = align_trajectories_at_origin(
                        traj_non_group, [traj_other_non_group]
                    )

                    # plot_static_2D_trajectory(
                    #     traj_other_non_group_aligned,
                    #     boundaries={
                    #         "xmin": -6000,
                    #         "xmax": 6000,
                    #         "ymin": -6000,
                    #         "ymax": 6000,
                    #     },
                    # )

                    pos_other_non_group_aligned = traj_other_non_group_aligned[:, 1:3]

                    pos_other_non_group_aligned = pos_other_non_group_aligned[
                        ~np.isnan(pos_other_non_group_aligned).any(axis=1), :
                    ]

                    grids_count = update_grid(
                        grids_count,
                        pos_other_non_group_aligned / 1000,
                        min_x,
                        n_bins_x,
                        cell_size_x,
                        min_y,
                        n_bins_y,
                        cell_size_y,
                    )

                    # plot_color_map(
                    #     xi,
                    #     yi,
                    #     grids_count,
                    #     cmap="jet",
                    # )

        pickle_save(
            f"../data/pickle/aligned_trajectories_2D_counts_non_groups_{env_name_short}.pkl",
            grids_count,
        )
