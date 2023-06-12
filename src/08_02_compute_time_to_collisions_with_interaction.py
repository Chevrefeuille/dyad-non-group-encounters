from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.trajectory_utils import *

from parameters import *
import matplotlib.pyplot as plt
from tqdm import tqdm

from utils import get_all_days, get_groups_thresholds, get_pedestrian_thresholds, get_social_values

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:
        # print(f"- {env_name}")
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )
        
        env_name_short = env_name.split(":")[0]

        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, soc_binding_color =  get_social_values(env_name)

        encounters = pickle_load(f"../data/pickle/opposite_encounters_{env_name_short}.pkl")
        pair_distribution_without_interaction = pickle_load(
            f"../data/pickle/pair_distribution_without_interaction_{env_name_short}.pkl"
        )

        bin_size_t = (
            PAIR_DISTRIBUTION_MAX_T_COLL - PAIR_DISTRIBUTION_MIN_T_COLL
        ) / N_BINS_PAIR_DISTRIBUTION_T_COLL
        pdf_edges_t = np.linspace(
            PAIR_DISTRIBUTION_MIN_T_COLL,
            PAIR_DISTRIBUTION_MAX_T_COLL,
            N_BINS_PAIR_DISTRIBUTION_T_COLL + 1,
        )
        bin_centers_t = 0.5 * (pdf_edges_t[0:-1] + pdf_edges_t[1:])
        pair_distribution_t = {}

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

            for group in tqdm(groups):
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()
                group_members_id = [m.get_id() for m in group.get_members()]

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding is None:
                    continue

                if soc_binding not in pair_distribution_t:
                    pair_distribution_t[soc_binding] = np.zeros(len(bin_centers_t))

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

                    times_to_collision = []
                    for i in range(len(traj_group)):
                        t_coll_A, pos_coll_A = compute_time_to_collision(
                            traj_A[i], traj_non_group[i]
                        )
                        # print(t_coll)
                        if t_coll_A > 0:
                            times_to_collision += [t_coll_A]

                            # delta_t = 0.5
                            # n_p = int(t_coll / delta_t)
                            # coll_pos_1 = [
                            #     traj_group[i, 1:3] + delta_t * k * traj_group[i, 5:7]
                            #     for k in range(n_p)
                            # ]
                            # coll_pos_2 = [
                            #     traj_non_group[i, 1:3] + delta_t * k * traj_non_group[i, 5:7]
                            #     for k in range(n_p)
                            # ]

                            # coll_traj_1, coll_traj_2 = np.zeros((len(coll_pos_1), 7)), np.zeros(
                            #     (len(coll_pos_2), 7)
                            # )
                            # coll_traj_1[:, 0] = np.arange(0, len(coll_pos_1) * delta_t, delta_t)
                            # coll_traj_2[:, 0] = np.arange(0, len(coll_pos_2) * delta_t, delta_t)
                            # coll_traj_1[:, 1:3] = coll_pos_1
                            # coll_traj_2[:, 1:3] = coll_pos_2

                            # coll_traj_3 = np.zeros((1, 7))
                            # coll_traj_3[:, 1:3] = pos_coll

                            # plot_animated_2D_trajectories([coll_traj_1, coll_traj_2, coll_traj_3], boundaries=env.boundaries)

                        t_coll_B, pos_coll_B = compute_time_to_collision(
                            traj_B[i], traj_non_group[i]
                        )
                        if t_coll_B > 0:
                            times_to_collision += [t_coll_B]

                    pair_distribution_t[soc_binding] += np.histogram(times_to_collision, pdf_edges_t)[0]




                 
        for i in soc_binding_values:
            pair_distribution_t[i] = (
                pair_distribution_t[i] / sum(pair_distribution_t[i]) / bin_size_t
            )
            # print(pair_distribution_without_interaction)

        pickle_save(
            f"../data/pickle/pair_distribution_times_to_collision_with_interaction_{env_name_short}.pkl",
            pair_distribution_t,
        )
     