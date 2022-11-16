from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np
from tqdm import tqdm

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

        observed_minimum_distances = []
        straight_line_minimum_distances = []
        velocities = []

        thresholds_ped = get_pedestrian_thresholds(env_name)

        for day in days:
            # print(day)
            non_groups = env.get_pedestrians(days=[day], thresholds=thresholds_ped)

            for non_group in tqdm(non_groups):
                non_group_id = non_group.get_id()

                encounters = non_group.get_encountered_pedestrians(
                    non_groups,
                    proximity_threshold=None,
                    alone=None,
                    skip=[non_group_id],
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

                    # plot_animated_2D_trajectories(
                    #     [
                    #         non_group.get_trajectory(),
                    #         other_non_group.get_trajectory(),
                    #     ],
                    #     boundaries=env.boundaries,
                    #     labels=["non-group", "other-non-group"],
                    # )

                    if len(traj_non_group) <= 1:
                        continue

                    traj_non_group_aligned, [
                        traj_other_non_group_aligned
                    ] = align_trajectories_at_origin(
                        traj_non_group, [traj_other_non_group]
                    )

                    # traj_other_non_group_vicinity = traj_other_non_group_aligned[
                    #     np.logical_and(
                    #         np.logical_and(
                    #             np.abs(traj_other_non_group_aligned[:, 1]) <= 4000,
                    #             np.abs(traj_other_non_group_aligned[:, 2]) <= 4000,
                    #         ),
                    #         traj_other_non_group_aligned[:, 1] >= 0,
                    #     )
                    # ]

                    traj_other_non_group_vicinity = traj_other_non_group_aligned[
                        np.logical_and(
                            np.abs(traj_other_non_group_aligned[:, 1]) <= 4000,
                            np.abs(traj_other_non_group_aligned[:, 2]) <= 4000,
                        )
                    ]

                    if len(traj_other_non_group_vicinity) <= 2:
                        continue

                    idx_first = np.argmin(
                        np.abs(traj_other_non_group_vicinity[:, 1] - 4000)
                    )
                    first_vel_in_vicinity = traj_other_non_group_vicinity[
                        idx_first, 5:7
                    ]

                    # plot_static_2D_trajectory(traj_other_non_group_aligned)

                    velocity_norm = np.linalg.norm(first_vel_in_vicinity)

                    rp = compute_straight_line_minimum_distance_from_vel(
                        traj_other_non_group_aligned
                    )
                    ro = compute_observed_minimum_distance(
                        traj_other_non_group_vicinity, interpolate=True
                    )

                    # if rp and ro > rp:
                    # if rp:

                    #     # print(d)
                    #     pos = traj_other_non_group_aligned[:, 1:3]
                    #     vel = traj_other_non_group_aligned[:, 5:7]
                    #     trajectory_in_vicinity = traj_other_non_group_aligned[
                    #         np.logical_and(
                    #             np.abs(pos[:, 0]) <= 4000, np.abs(pos[:, 1]) <= 4000
                    #         )
                    #     ]
                    #     trajectory_before_vicinity = traj_other_non_group_aligned[
                    #         np.logical_and(
                    #             np.abs(pos[:, 0]) >= 4000,
                    #             np.abs(pos[:, 0]) <= 4000 + 2000,
                    #         )
                    #     ]
                    #     pos_in_vicinity = trajectory_in_vicinity[:, 1:3]

                    #     if len(trajectory_in_vicinity) <= 2:
                    #         # do not get close enough
                    #         continue

                    #     plt.scatter(
                    #         pos[:, 0],
                    #         pos[:, 1],
                    #     )

                    #     # use velocities to interpolate the minimum distance:
                    #     # project the position vector NO (from non group to group, i.e origin)
                    #     # onto the line directed by
                    #     # the velocity vector to get the distance to the point P for which the distance
                    #     # between the line directed by the velocity and the origin
                    #     # is smallest
                    #     v_magn = np.linalg.norm(vel, axis=1)
                    #     lambdas = (
                    #         -np.matmul(vel, pos.T).diagonal() / v_magn
                    #     )  # the diagonal of the matrix contains the dot products
                    #     # compute the time to reach the point P
                    #     t_to_P = (lambdas / v_magn)[:-1]  # last point is not used
                    #     delta_ts = (
                    #         traj_non_group_aligned[1:, 0]
                    #         - traj_non_group_aligned[:-1, 0]
                    #     ) / 1000
                    #     interpolate_possible = np.logical_and(
                    #         t_to_P < delta_ts, t_to_P >= 0
                    #     )
                    #     Ps = (
                    #         pos[:-1, :][interpolate_possible]
                    #         + lambdas[:-1][interpolate_possible][:, None]
                    #         * vel[:-1, :][interpolate_possible]
                    #         / v_magn[:-1][interpolate_possible][:, None]
                    #     )

                    #     closest_ind = np.argmin(np.linalg.norm(pos_in_vicinity, axis=1))
                    #     d_closest = np.min(np.linalg.norm(pos_in_vicinity, axis=1))

                    #     if len(Ps):
                    #         closest_ind_interp = np.argmin(np.linalg.norm(Ps, axis=1))
                    #         d_closest_interp = np.min(np.linalg.norm(Ps, axis=1))
                    #     else:
                    #         d_closest_interp = d_closest

                    #     if d_closest <= d_closest_interp:
                    #         plt.scatter(
                    #             pos_in_vicinity[closest_ind, 0],
                    #             pos_in_vicinity[closest_ind, 1],
                    #             c="purple",
                    #         )
                    #         plt.plot(
                    #             [0, pos_in_vicinity[closest_ind, 0]],
                    #             [0, pos_in_vicinity[closest_ind, 1]],
                    #             c="purple",
                    #         )
                    #     else:
                    #         plt.scatter(
                    #             Ps[closest_ind_interp, 0],
                    #             Ps[closest_ind_interp, 1],
                    #             c="yellow",
                    #         )
                    #         plt.plot(
                    #             [0, Ps[closest_ind_interp, 0]],
                    #             [0, Ps[closest_ind_interp, 1]],
                    #             c="yellow",
                    #         )

                    #     # plt.scatter(Ps[:, 0], Ps[:, 1], c="yellow")

                    #     idx_first = np.argmin(np.abs(pos_in_vicinity[:, 0] - 4000))
                    #     first_pos_in_vicinity = pos_in_vicinity[idx_first, :]
                    #     first_vel_in_vicinity = trajectory_in_vicinity[idx_first, 5:7]
                    #     vel_before = np.nanmean(
                    #         trajectory_before_vicinity[:, 5:7], axis=0
                    #     )

                    #     plt.quiver(
                    #         trajectory_in_vicinity[idx_first, 1],
                    #         trajectory_in_vicinity[idx_first, 2],
                    #         vel_before[0],
                    #         vel_before[1],
                    #     )

                    #     distance_to_straight_line = np.abs(
                    #         np.cross(vel_before, first_pos_in_vicinity)
                    #     ) / np.linalg.norm(vel_before)

                    #     closest_straight_line = (
                    #         first_pos_in_vicinity
                    #         + np.dot(-first_pos_in_vicinity, vel_before)
                    #         * vel_before
                    #         / np.linalg.norm(vel_before) ** 2
                    #     )

                    #     plt.scatter(
                    #         pos_in_vicinity[idx_first, 0],
                    #         pos_in_vicinity[idx_first, 1],
                    #         c="red",
                    #     )

                    #     plt.plot(
                    #         [0, closest_straight_line[0]],
                    #         [0, closest_straight_line[1]],
                    #         c="orange",
                    #     )

                    #     plt.plot(
                    #         [-4000, 4000],
                    #         [
                    #             (-4000 - first_pos_in_vicinity[0])
                    #             * (vel_before[1] / vel_before[0])
                    #             + first_pos_in_vicinity[1],
                    #             (4000 - first_pos_in_vicinity[0])
                    #             * (vel_before[1] / vel_before[0])
                    #             + first_pos_in_vicinity[1],
                    #         ],
                    #         c="orange",
                    #     )

                    #     plt.scatter([0], [0], c="green")
                    #     plt.axis("scaled")
                    #     plt.xlim(-8000, 8000)
                    #     plt.ylim(-8000, 8000)
                    #     plt.show()

                    if rp:
                        observed_minimum_distances += [ro]
                        straight_line_minimum_distances += [rp]
                        velocities += [velocity_norm]

        pickle_save(
            f"../data/pickle/observed_minimum_distance_non_groups_{env_name_short}_with_interaction.pkl",
            np.array(observed_minimum_distances),
        )
        pickle_save(
            f"../data/pickle/straight_line_minimum_distance_non_groups_{env_name_short}_with_interaction.pkl",
            np.array(straight_line_minimum_distances),
        )
        pickle_save(
            f"../data/pickle/velocities_non_groups_{env_name_short}_with_interaction.pkl",
            np.array(velocities),
        )
