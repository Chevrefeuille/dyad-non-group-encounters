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

        deflections = {"group": {}, "group_members": {}, "non_group": {}}
        lengths = {
            "group": {"net": [], "gross": []},
            "group_members": {"net": [], "gross": []},
            "non_group": {"net": [], "gross": []},
        }

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

                group_trajectory = group_as_indiv.get_trajectory()

                sub_trajectories = compute_continuous_sub_trajectories(group_trajectory)

                for sub_trajectory in sub_trajectories:

                    if len(sub_trajectory[:, 0]) < MIN_NUMBER_OBSERVATIONS:
                        continue

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

                    pieces_group = get_random_pieces(position, 20)
                    pieces_A = get_random_pieces(pos_A, 20)
                    pieces_B = get_random_pieces(pos_B, 20)

                    for piece_A, piece_B in zip(pieces_A, pieces_B):
                        trajectory1 = np.zeros((len(piece_A), 7))
                        trajectory2 = np.zeros((len(piece_B), 7))
                        trajectory1[:, 1:3] = piece_A
                        trajectory2[:, 1:3] = piece_B
                        plot_static_2D_trajectories(
                            [traj_A, trajectory1],
                            boundaries=env.boundaries,
                        )

                    lengths["group"]["net"] += [
                        compute_net_displacement(piece)
                        for piece in pieces_group
                        if len(piece) >= 4
                    ]
                    lengths["group_members"]["net"] += [
                        compute_net_displacement(piece)
                        for piece in pieces_A
                        if len(piece) >= 4
                    ] + [
                        compute_net_displacement(piece)
                        for piece in pieces_B
                        if len(piece) >= 4
                    ]

                    lengths["group"]["gross"] += [
                        compute_gross_displacement(piece)
                        for piece in pieces_group
                        if len(piece) >= 4
                    ]
                    lengths["group_members"]["gross"] += [
                        compute_gross_displacement(piece)
                        for piece in pieces_A
                        if len(piece) >= 4
                    ] + [
                        compute_gross_displacement(piece)
                        for piece in pieces_B
                        if len(piece) >= 4
                    ]

                    # print(pieces_group_sizes)

                    for measure in DEFLECTION_MEASURES:
                        if measure not in deflections["group"]:
                            deflections["group"][measure] = []
                            deflections["group_members"][measure] = []

                        group_deflections = [
                            compute_deflection(piece, measure=measure)
                            for piece in pieces_group
                            if len(piece) >= 4
                        ]

                        A_deflections = [
                            compute_deflection(piece, measure=measure)
                            for piece in pieces_A
                            if len(piece) >= 4
                        ]

                        B_deflections = [
                            compute_deflection(piece, measure=measure)
                            for piece in pieces_B
                            if len(piece) >= 4
                        ]

                        # if (
                        #     measure == "straightness_index"
                        #     and min(A_deflections) < 0.975
                        # ):
                        #     print(pieces_A_sizes)
                        #     print(A_deflections)
                        #     for piece_A, piece_B in zip(pieces_A, pieces_B):
                        #         trajectory1 = np.zeros((len(piece_A), 7))
                        #         trajectory2 = np.zeros((len(piece_B), 7))
                        #         trajectory1[:, 1:3] = piece_A
                        #         trajectory2[:, 1:3] = piece_B
                        #         plot_static_2D_trajectories(
                        #             [trajectory1],
                        #             boundaries=env.boundaries,
                        #         )

                        deflections["group"][measure] += group_deflections

                        deflections["group_members"][measure] += (
                            A_deflections + B_deflections
                        )

            # compute deflection for the non-groups
            for non_group in tqdm(non_groups):
                non_group_id = non_group.get_id()

                # non_group_undisturbed_trajectory = non_group.get_trajectory()

                non_group_trajectory = non_group.get_trajectory()

                # plot_static_2D_trajectories(
                #     [
                #         non_group.get_trajectory(),
                #         non_group_undisturbed_trajectory,
                #     ],
                #     boundaries=env.boundaries,
                # )

                # plot_static_2D_trajectories(
                #     [non_group_undisturbed_trajectory],
                #     boundaries=env.boundaries,
                # )

                sub_trajectories = compute_continuous_sub_trajectories(
                    non_group_trajectory
                )

                for sub_trajectory in sub_trajectories:

                    if len(sub_trajectory) < MIN_NUMBER_OBSERVATIONS:
                        continue

                    position = sub_trajectory[:, 1:3]

                    pieces = get_random_pieces(position, 20)

                    # for piece in pieces:
                    #     trajectory = np.zeros((len(piece), 7))
                    #     trajectory[:, 1:3] = piece
                    #     plot_static_2D_trajectories(
                    #         [sub_trajectory, trajectory],
                    #         boundaries=env.boundaries,
                    #     )

                    lengths["non_group"]["net"] += [
                        compute_net_displacement(piece)
                        for piece in pieces
                        if len(piece) >= 4
                    ]

                    lengths["non_group"]["gross"] += [
                        compute_gross_displacement(piece)
                        for piece in pieces
                        if len(piece) >= 4
                    ]

                    for measure in DEFLECTION_MEASURES:
                        if measure not in deflections["non_group"]:
                            deflections["non_group"][measure] = []

                        non_group_deflections = [
                            compute_deflection(piece, measure=measure)
                            for piece in pieces
                            if len(piece) >= 4
                        ]

                        # if measure == "straightness_index":
                        #     d = np.array(non_group_deflections)
                        #     too_small = np.where(d < 0.8)[0]
                        #     for i in too_small:
                        #         dxdy = np.linalg.norm(
                        #             np.abs(
                        #                 sub_trajectory[1:, 1:3]
                        #                 - sub_trajectory[:-1, 1:3]
                        #             )
                        #             / (sub_trajectory[1:, 0] - sub_trajectory[:-1, 0])[
                        #                 :, None
                        #             ],
                        #             axis=1,
                        #         )
                        #         # plt.plot(dxdy)
                        #         # plt.show()
                        #         turning_angles = compute_turning_angles(pieces[i])
                        #         print(turning_angles * 180 / np.pi)
                        #         trajectory1 = np.zeros((len(pieces[i]), 7))
                        #         trajectory1[:, 1:3] = pieces[i]
                        #         plot_static_2D_trajectories(
                        #             [sub_trajectory, trajectory1],
                        #             boundaries=env.boundaries,
                        #         )

                        deflections["non_group"][measure] += non_group_deflections

        pickle_save(
            f"../data/pickle/deflection_all_{env_name_short}_random.pkl",
            deflections,
        )
        pickle_save(
            f"../data/pickle/length_trajectory_all_{env_name_short}_random.pkl",
            lengths,
        )
