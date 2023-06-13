from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *
from utils import *

from scipy.spatial import distance
from scipy import integrate
import random as rnd
from tqdm import tqdm

from parameters import *

"""The goal of this script is to compute the distribution of the aligned trajectories of two pedestrians without interaction.
The data is saved in a pickle file.
"""

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        thresholds_indiv = get_pedestrian_thresholds(env_name)

        pedestrians_by_day = env.get_pedestrians_grouped_by(
            "day", thresholds=thresholds_indiv, sampling_time=500
        )

        day1, day2 = ["0217", "0109"] if env_name_short == "atc" else ["06", "08"]

        grids_count = np.zeros((N_BINS_2D_RX, N_BINS_2D_RY))
        xi = np.linspace(0, (RX_MAX - RX_MIN) / 1000, N_BINS_2D_RX)
        yi = np.linspace(0, (RY_MAX - RY_MIN) / 1000, N_BINS_2D_RY)
        cell_size_x = int((RX_MAX - RX_MIN) / N_BINS_2D_RX)
        cell_size_y = int((RY_MAX - RY_MIN) / N_BINS_2D_RY)

        # for the angle theta
        bin_size_theta = (
            PAIR_DISTRIBUTION_MAX_THETA - PAIR_DISTRIBUTION_MIN_THETA
        ) / N_BINS_PAIR_DISTRIBUTION_THETA
        pdf_edges_theta = np.linspace(
            PAIR_DISTRIBUTION_MIN_THETA,
            PAIR_DISTRIBUTION_MAX_THETA,
            N_BINS_PAIR_DISTRIBUTION_THETA + 1,
        )
        bin_centers_theta = 0.5 * (pdf_edges_theta[0:-1] + pdf_edges_theta[1:])
        hist_theta = np.zeros(len(bin_centers_theta))

        n_ped = 2000
        n_samples = 200

        for pedestrian_1 in tqdm(rnd.sample(pedestrians_by_day[day1], n_ped)):
            traj_1 = pedestrian_1.get_trajectory()
            for pedestrian_2 in rnd.sample(pedestrians_by_day[day2], n_ped):
                traj_2 = pedestrian_2.get_trajectory()

                # plot_static_2D_trajectories(
                #     [traj_1, traj_2], labels=["1", "2"], boundaries=env.boundaries
                # )

                n_rand = min(n_samples, len(traj_1), len(traj_2))
                random_id_1 = np.random.choice(len(traj_1), size=n_rand, replace=False)
                sample_1 = traj_1[random_id_1, :]
                random_id_2 = np.random.choice(len(traj_2), size=n_rand, replace=False)
                sample_2 = traj_2[random_id_2, :]

                traj1_aligned, [traj2_aligned] = align_trajectories_at_origin(
                    sample_1, [sample_2]
                )

                # plot_static_2D_trajectories(
                #     [traj1_aligned, traj2_aligned],
                #     labels=["1", "2"],
                # )

                pos_1 = traj1_aligned[:, 1:3]
                pos_2 = traj2_aligned[:, 1:3]

                cell_x = np.ceil((pos_2[:, 0] - RX_MIN) / cell_size_x).astype("int")
                cell_y = np.ceil((pos_2[:, 1] - RY_MIN) / cell_size_y).astype("int")

                # remove date outside the range of interest
                in_roi = np.logical_and(
                    np.logical_and(cell_x >= 0, cell_x < N_BINS_2D_RX),
                    np.logical_and(cell_y >= 0, cell_y < N_BINS_2D_RY),
                )
                cell_x = cell_x[in_roi]
                cell_y = cell_y[in_roi]

                grids_count[cell_x, cell_y] += 1

                # for the angle
                vec_1_2 = pos_2 - pos_1
                theta = np.arctan2(vec_1_2[1:, 0], vec_1_2[1:, 1])
                theta[theta > np.pi] -= 2 * np.pi
                theta[theta < -np.pi] += 2 * np.pi
                hist_theta += np.histogram(theta, pdf_edges_theta)[0]

        max_value = np.max(grids_count)
        grids_count /= max_value

        pickle_save(
            f"../data/pickle/aligned_trajectories_2D_distribution_{env_name_short}_without_interaction.pkl",
            grids_count,
        )

        pdf_theta = hist_theta / sum(hist_theta) / bin_size_theta
        pair_distribution_theta = np.stack((bin_centers_theta, pdf_theta))
        pickle_save(
            f"../data/pickle/aligned_trajectories_distribution_theta_without_interaction_{env_name_short}.pkl",
            pair_distribution_theta,
        )

        # pdf_x = hist_x / sum(hist_x) / bin_size_x
        # pair_distribution_x = np.stack((bin_centers_x, pdf_x))
        # pickle_save(
        #     f"../data/pickle/pair_distribution_x_without_interaction_{env_name_short}.pkl",
        #     pair_distribution_x,
        # )

        # pdf_y = hist_y / sum(hist_y) / bin_size_y
        # pair_distribution_y = np.stack((bin_centers_y, pdf_y))
        # pickle_save(
        #     f"../data/pickle/pair_distribution_y_without_interaction_{env_name_short}.pkl",
        #     pair_distribution_y,
        # )

        # pdf_theta = hist_theta / sum(hist_theta) / bin_size_theta
        # pair_distribution_theta = np.stack((bin_centers_theta, pdf_theta))
        # pickle_save(
        #     f"../data/pickle/pair_distribution_theta_without_interaction_{env_name_short}.pkl",
        #     pair_distribution_theta,
        # )
