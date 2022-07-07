from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.trajectory_utils import *

from parameters import *
from utils import *
import matplotlib.pyplot as plt
from tqdm import tqdm

if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:
        # print(f"- {env_name}")
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = DAYS_ATC if env_name == "atc" else DAYS_DIAMOR
        soc_binding_type = "soc_rel" if env_name == "atc" else "interaction"
        soc_binding_names = (
            SOCIAL_RELATIONS_EN if env_name == "atc" else INTENSITIES_OF_INTERACTION_NUM
        )
        soc_binding_values = [0, 1, 2, 3, 4] if env_name == "atc" else [0, 1, 2, 3]

        encounters = pickle_load(f"../data/pickle/opposite_encounters_{env_name}.pkl")
        pair_distribution_without_interaction = pickle_load(
            f"../data/pickle/pair_distribution_without_interaction_{env_name}.pkl"
        )

        # for the distance r
        bin_size_r = (
            PAIR_DISTRIBUTION_MAX_R - PAIR_DISTRIBUTION_MIN_R
        ) / N_BINS_PAIR_DISTRIBUTION_R
        pdf_edges_r = np.linspace(
            PAIR_DISTRIBUTION_MIN_R,
            PAIR_DISTRIBUTION_MAX_R,
            N_BINS_PAIR_DISTRIBUTION_R + 1,
        )
        pair_distribution_r = {}

        # for the distance along x
        bin_size_x = (
            PAIR_DISTRIBUTION_MAX_X - PAIR_DISTRIBUTION_MIN_X
        ) / N_BINS_PAIR_DISTRIBUTION_X
        pdf_edges_x = np.linspace(
            PAIR_DISTRIBUTION_MIN_X,
            PAIR_DISTRIBUTION_MAX_X,
            N_BINS_PAIR_DISTRIBUTION_X + 1,
        )
        pair_distribution_x = {}

        # for the distance along y
        bin_size_y = (
            PAIR_DISTRIBUTION_MAX_Y - PAIR_DISTRIBUTION_MIN_Y
        ) / N_BINS_PAIR_DISTRIBUTION_Y
        pdf_edges_y = np.linspace(
            PAIR_DISTRIBUTION_MIN_Y,
            PAIR_DISTRIBUTION_MAX_Y,
            N_BINS_PAIR_DISTRIBUTION_Y + 1,
        )
        pair_distribution_y = {}

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

        for day in days:

            thresholds_ped = get_pedestrian_thresholds(env_name)
            thresholds_groups = get_groups_thresholds()

            non_groups = env.get_pedestrians(days=[day], thresholds=thresholds_ped)

            groups = env.get_groups(
                size=2,
                days=[day],
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_groups,
                with_social_binding=True,
                sampling_time=500,
            )

            for group in tqdm(groups):
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()
                group_members_id = [m.get_id() for m in group.get_members()]

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding is None:
                    continue

                if soc_binding not in pair_distribution_r:
                    pair_distribution_r[soc_binding] = np.zeros(len(pdf_edges_r) - 1)
                if soc_binding not in pair_distribution_x:
                    pair_distribution_x[soc_binding] = np.zeros(len(pdf_edges_x) - 1)
                if soc_binding not in pair_distribution_y:
                    pair_distribution_y[soc_binding] = np.zeros(len(pdf_edges_y) - 1)
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

                    pos_A = traj_A[:, 1:3]
                    pos_B = traj_B[:, 1:3]
                    pos_group = traj_group[:, 1:3]
                    pos_non_group = traj_non_group[:, 1:3]

                    r_A_NG = np.linalg.norm(pos_A - pos_non_group, axis=1)
                    r_B_NG = np.linalg.norm(pos_B - pos_non_group, axis=1)
                    pair_distribution_r[soc_binding] += (
                        np.histogram(r_A_NG, pdf_edges_r)[0]
                        + np.histogram(r_B_NG, pdf_edges_r)[0]
                    )

                    x_A_NG = pos_non_group[:, 0] - pos_A[:, 0]
                    x_B_NG = pos_non_group[:, 0] - pos_B[:, 0]
                    pair_distribution_x[soc_binding] += (
                        np.histogram(x_A_NG, pdf_edges_x)[0]
                        + np.histogram(x_B_NG, pdf_edges_x)[0]
                    )

                    y_A_NG = pos_non_group[:, 1] - pos_A[:, 1]
                    y_B_NG = pos_non_group[:, 1] - pos_B[:, 1]
                    pair_distribution_y[soc_binding] += (
                        np.histogram(y_A_NG, pdf_edges_y)[0]
                        + np.histogram(y_B_NG, pdf_edges_y)[0]
                    )

                    vec_A_NG = pos_non_group - pos_A
                    theta_A_NG = np.arctan2(vec_A_NG[1:, 0], vec_A_NG[1:, 1])
                    theta_A_NG[theta_A_NG > np.pi] -= 2 * np.pi
                    theta_A_NG[theta_A_NG < -np.pi] += 2 * np.pi
                    vec_B_NG = pos_non_group - pos_B
                    theta_B_NG = np.arctan2(vec_B_NG[1:, 0], vec_B_NG[1:, 1])
                    theta_B_NG[theta_B_NG > np.pi] -= 2 * np.pi
                    theta_B_NG[theta_B_NG < -np.pi] += 2 * np.pi
                    pair_distribution_theta[soc_binding] += (
                        np.histogram(theta_A_NG, pdf_edges_theta)[0]
                        + np.histogram(theta_B_NG, pdf_edges_theta)[0]
                    )

        for i in soc_binding_values:
            pair_distribution_r[i] = (
                pair_distribution_r[i] / sum(pair_distribution_r[i]) / bin_size_r
            )
            pair_distribution_x[i] = (
                pair_distribution_x[i] / sum(pair_distribution_x[i]) / bin_size_x
            )
            pair_distribution_y[i] = (
                pair_distribution_y[i] / sum(pair_distribution_y[i]) / bin_size_y
            )
            pair_distribution_theta[i] = (
                pair_distribution_theta[i]
                / sum(pair_distribution_theta[i])
                / bin_size_theta
            )
            # print(pair_distribution_without_interaction)

        pickle_save(
            f"../data/pickle/pair_distribution_r_with_interaction_{env_name}.pkl",
            pair_distribution_r,
        )
        pickle_save(
            f"../data/pickle/pair_distribution_x_with_interaction_{env_name}.pkl",
            pair_distribution_x,
        )
        pickle_save(
            f"../data/pickle/pair_distribution_y_with_interaction_{env_name}.pkl",
            pair_distribution_y,
        )
        pickle_save(
            f"../data/pickle/pair_distribution_theta_with_interaction_{env_name}.pkl",
            pair_distribution_theta,
        )

        # plt.title(f"Pair distribution for {env_name}")
        # plt.legend()
        # plt.show()
