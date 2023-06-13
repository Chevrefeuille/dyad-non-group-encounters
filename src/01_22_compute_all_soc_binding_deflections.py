from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
from parameters import *

from tqdm import tqdm

""" The goal of this script is to compute all the deflections for the encounters between pedestrians in the corridor environment.
The data is saved in a pickle file named "deflections_{env_name_short}.pkl" in the data/pickle folder. 
The dictionary is of the form:
    - deflections[soc_binding][measure] = [deflection_1, deflection_2, ...]
    - lengths[soc_binding][net/gross] = [length_1, length_2, ...]
    """

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        deflections = {}
        lengths = {}

        for day in days:
            print(f"Day {day}:")
            thresholds_ped = get_pedestrian_thresholds(env_name)
            thresholds_group = get_groups_thresholds()

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                sampling_time=500,
                with_social_binding=True,
            )

            # compute deflection for the groups
            for group in tqdm(groups):
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()

                members_trajectories = [m.get_trajectory() for m in group.get_members()]

                group_trajectory = group_as_indiv.get_trajectory()

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding is None:
                    continue

                if soc_binding not in deflections:
                    deflections[soc_binding] = {}
                    lengths[soc_binding] = {"net": [], "gross": []}

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

                    # for piece_A, piece_B in zip(pieces_A, pieces_B):
                    #     trajectory1 = np.zeros((len(piece_A), 7))
                    #     trajectory2 = np.zeros((len(piece_B), 7))
                    #     trajectory1[:, 1:3] = piece_A
                    #     trajectory2[:, 1:3] = piece_B
                    #     plot_static_2D_trajectories(
                    #         [traj_A, trajectory1],
                    #         boundaries=env.boundaries,
                    #     )

                    lengths[soc_binding]["net"] += [
                        compute_net_displacement(piece)
                        for piece in pieces_A
                        if len(piece) >= 4
                    ] + [
                        compute_net_displacement(piece)
                        for piece in pieces_B
                        if len(piece) >= 4
                    ]

                    lengths[soc_binding]["gross"] += [
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
                        if measure not in deflections[soc_binding]:
                            deflections[soc_binding][measure] = []

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

                        deflections[soc_binding][measure] += (
                            A_deflections + B_deflections
                        )

        pickle_save(
            f"../data/pickle/deflection_groups_wrt_soc_binding_{env_name_short}_random.pkl",
            deflections,
        )
        pickle_save(
            f"../data/pickle/length_trajectory_groups_wrt_soc_binding_{env_name_short}_random.pkl",
            lengths,
        )
