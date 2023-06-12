from copy import deepcopy
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
from parameters import *

from tqdm import tqdm

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = DAYS_ATC if env_name_short == "atc" else DAYS_DIAMOR

        times_undisturbed = pickle_load(
            f"../data/pickle/undisturbed_times_{env_name_short}.pkl"
        )

        deflections = {"group": {}, "group_members": {}, "non_group": {}}
        lengths = {"group": {}, "group_members": {}, "non_group": {}}

        for day in days:
            print(f"Day {day}:")
            thresholds_ped = get_pedestrian_thresholds(env_name)
            thresholds_group = get_groups_thresholds()

            non_groups = env.get_pedestrians(
                days=[day],
                no_groups=True,
                thresholds=thresholds_ped,
                sampling_time=500,
            )

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                sampling_time=500,
            )

            # compute deflection for the groups
            for group in tqdm(groups):
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()

                members_trajectories = [m.get_trajectory() for m in group.get_members()]

                if group_id not in times_undisturbed[day]["group"]:
                    continue

                group_times_undisturbed = times_undisturbed[day]["group"][group_id]

                group_undisturbed_trajectory = get_trajectory_at_times(
                    group_as_indiv.get_trajectory(), group_times_undisturbed
                )

                # plot_static_2D_trajectories(
                #     [
                #         group_as_indiv.get_trajectory(),
                #         group_undisturbed_trajectory,
                #     ],
                #     boundaries=env.boundaries,
                # )

                sub_trajectories = compute_continuous_sub_trajectories(
                    group_undisturbed_trajectory
                )

                for sub_trajectory in sub_trajectories:

                    if len(sub_trajectory[:, 0]) < MIN_NUMBER_OBSERVATIONS:
                        continue

                    # plot_static_2D_trajectory(sub_trajectory, boundaries=env.boundaries)

                    position = sub_trajectory[:, 1:3]
                    traj_A, _ = compute_simultaneous_observations(
                        [members_trajectories[0], sub_trajectory]
                    )
                    pos_A = traj_A[:, 1:3]
                    traj_B, _ = compute_simultaneous_observations(
                        [members_trajectories[1], sub_trajectory]
                    )
                    pos_B = traj_B[:, 1:3]

                    if len(pos_A) < MIN_NUMBER_OBSERVATIONS:
                        continue

                    for segment_length in SEGMENT_LENGTHS:
                        pieces_group = get_pieces(
                            position,
                            piece_size=segment_length,
                            overlap=True,
                            delta=100,
                        )
                        pieces_A = get_pieces(
                            pos_A,
                            piece_size=segment_length,
                            overlap=True,
                            delta=100,
                        )
                        pieces_B = get_pieces(
                            pos_B,
                            piece_size=segment_length,
                            overlap=True,
                            delta=100,
                        )

                        # for piece_A, piece_B in zip(pieces_A, pieces_B):
                        #     trajectory1 = np.zeros((len(piece_A), 7))
                        #     trajectory2 = np.zeros((len(piece_B), 7))
                        #     trajectory1[:, 1:3] = piece_A
                        #     trajectory2[:, 1:3] = piece_B
                        #     plot_static_2D_trajectories(
                        #         [traj_A, trajectory1],
                        #         boundaries=env.boundaries,
                        #     )

                        if segment_length not in lengths["group"]:
                            lengths["group"][segment_length] = {"gross": [], "net": []}
                            lengths["group_members"][segment_length] = {
                                "gross": [],
                                "net": [],
                            }

                        lengths["group"][segment_length]["net"] += [
                            compute_net_displacement(piece)
                            for piece in pieces_group
                            if len(piece) >= 3
                        ]
                        lengths["group_members"][segment_length]["net"] += [
                            compute_net_displacement(piece)
                            for piece in pieces_A
                            if len(piece) >= 3
                        ] + [
                            compute_net_displacement(piece)
                            for piece in pieces_B
                            if len(piece) >= 3
                        ]

                        lengths["group"][segment_length]["gross"] += [
                            compute_gross_displacement(piece)
                            for piece in pieces_group
                            if len(piece) >= 3
                        ]
                        lengths["group_members"][segment_length]["gross"] += [
                            compute_gross_displacement(piece)
                            for piece in pieces_A
                            if len(piece) >= 3
                        ] + [
                            compute_net_displacement(piece)
                            for piece in pieces_B
                            if len(piece) >= 3
                        ]

                        for measure in DEFLECTION_MEASURES:

                            if measure not in deflections["group"]:
                                deflections["group"][measure] = {}
                                deflections["group_members"][measure] = {}

                            if segment_length not in deflections["group"][measure]:
                                deflections["group"][measure][segment_length] = []
                                deflections["group_members"][measure][
                                    segment_length
                                ] = []

                            deflections["group"][measure][segment_length] += [
                                compute_deflection(piece, measure=measure)
                                for piece in pieces_group
                                if len(piece) >= 3
                            ]

                            deflections["group_members"][measure][segment_length] += [
                                compute_deflection(piece, measure=measure)
                                for piece in pieces_A
                                if len(piece) >= 3
                            ] + [
                                compute_deflection(piece, measure=measure)
                                for piece in pieces_B
                                if len(piece) >= 3
                            ]

            # compute deflection for the non-groups
            for non_group in tqdm(non_groups):
                non_group_id = non_group.get_id()

                if non_group_id not in times_undisturbed[day]["non_group"]:
                    continue

                non_group_times_undisturbed = times_undisturbed[day]["non_group"][
                    non_group_id
                ]

                non_group_undisturbed_trajectory = get_trajectory_at_times(
                    non_group.get_trajectory(),
                    non_group_times_undisturbed,
                )

                # plot_static_2D_trajectories(
                #     [
                #         non_group.get_trajectory(),
                #         non_group_undisturbed_trajectory,
                #     ],
                #     boundaries=env.boundaries,
                # )

                sub_trajectories = compute_continuous_sub_trajectories(
                    non_group_undisturbed_trajectory
                )

                for sub_trajectory in sub_trajectories:

                    if len(sub_trajectory[:, 0]) < MIN_NUMBER_OBSERVATIONS:
                        continue

                    # plot_static_2D_trajectory(sub_trajectory, boundaries=env.boundaries)

                    position = sub_trajectory[:, 1:3]
                    # if env_name_short == "diamor" and measure == "sinuosity":
                    # position = position[1::5]  # to sample every 500ms

                    # plt.scatter(position[:, 0], position[:, 1])
                    # plt.show()

                    # for piece in pieces:
                    #     trajectory = np.zeros((len(piece), 7))
                    #     trajectory[:, 1:3] = piece
                    #     plot_static_2D_trajectories(
                    #         [trajectory],
                    #         boundaries=env.boundaries,
                    #     )
                    for segment_length in SEGMENT_LENGTHS:
                        pieces = get_pieces(
                            position,
                            piece_size=segment_length,
                            overlap=True,
                            delta=100,
                        )

                        if segment_length not in lengths["non_group"]:
                            lengths["non_group"][segment_length] = {
                                "net": [],
                                "gross": [],
                            }

                        lengths["non_group"][segment_length]["net"] += [
                            compute_net_displacement(piece)
                            for piece in pieces
                            if len(piece) >= 3
                        ]

                        lengths["non_group"][segment_length]["gross"] += [
                            compute_gross_displacement(piece)
                            for piece in pieces
                            if len(piece) >= 3
                        ]

                        for measure in DEFLECTION_MEASURES:
                            if measure not in deflections["non_group"]:
                                deflections["non_group"][measure] = {}
                            if segment_length not in deflections["non_group"][measure]:
                                deflections["non_group"][measure][segment_length] = []

                            deflections["non_group"][measure][segment_length] += [compute_deflection(piece, measure=measure) for piece in pieces if len(piece) >= 3]

        pickle_save(
            f"../data/pickle/deflection_without_interaction_{env_name_short}.pkl",
            deflections,
        )

        pickle_save(
            f"../data/pickle/length_trajectory_without_interaction_{env_name_short}.pkl",
            lengths,
        )

        # print(deflections)

        # for piece in pieces:
        #     plt.scatter(piece[:, 0], piece[:, 1])
        # plt.show()
        # deflection = compute_deflection(position)

        # if deflection < 0.7:
        #     group_as_indiv.set_trajectory(sub_trajectory)
        #     group_as_indiv.plot_2D_trajectory()
