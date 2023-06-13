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

""" The goal of this script is to compute the pair distribution function for the pedestrians in the corridor environment.
the pair distribution is the probability of finding two pedestrians at a distance d.
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

        # start by constructing the probability of two pedestrians to be at distance d
        # for not interacting pedestrians
        # i.e. on different days (take two days with most and least people for atc)

        day1, day2 = ["0217", "0109"] if env_name_short == "atc" else ["06", "08"]

        # for the distance r
        bin_size_r = (
            PAIR_DISTRIBUTION_MAX_R - PAIR_DISTRIBUTION_MIN_R
        ) / N_BINS_PAIR_DISTRIBUTION_R
        pdf_edges_r = np.linspace(
            PAIR_DISTRIBUTION_MIN_R,
            PAIR_DISTRIBUTION_MAX_R,
            N_BINS_PAIR_DISTRIBUTION_R + 1,
        )
        bin_centers_r = 0.5 * (pdf_edges_r[0:-1] + pdf_edges_r[1:])
        hist_r = np.zeros(len(bin_centers_r))

        # for the distance along x
        bin_size_x = (
            PAIR_DISTRIBUTION_MAX_X - PAIR_DISTRIBUTION_MIN_X
        ) / N_BINS_PAIR_DISTRIBUTION_X
        pdf_edges_x = np.linspace(
            PAIR_DISTRIBUTION_MIN_X,
            PAIR_DISTRIBUTION_MAX_X,
            N_BINS_PAIR_DISTRIBUTION_X + 1,
        )
        bin_centers_x = 0.5 * (pdf_edges_x[0:-1] + pdf_edges_x[1:])
        hist_x = np.zeros(len(bin_centers_x))

        # for the distance along y
        bin_size_y = (
            PAIR_DISTRIBUTION_MAX_Y - PAIR_DISTRIBUTION_MIN_Y
        ) / N_BINS_PAIR_DISTRIBUTION_Y
        pdf_edges_y = np.linspace(
            PAIR_DISTRIBUTION_MIN_Y,
            PAIR_DISTRIBUTION_MAX_Y,
            N_BINS_PAIR_DISTRIBUTION_Y + 1,
        )
        bin_centers_y = 0.5 * (pdf_edges_y[0:-1] + pdf_edges_y[1:])
        hist_y = np.zeros(len(bin_centers_y))

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
            pos_1 = pedestrian_1.get_position()
            for pedestrian_2 in rnd.sample(pedestrians_by_day[day2], n_ped):
                pos_2 = pedestrian_2.get_position()

                n_rand = min(n_samples, len(pos_1), len(pos_2))
                random_id_1 = np.random.choice(len(pos_1), size=n_rand, replace=False)
                sample_1 = pos_1[random_id_1, :]
                random_id_2 = np.random.choice(len(pos_2), size=n_rand, replace=False)
                sample_2 = pos_2[random_id_2, :]

                r = compute_interpersonal_distance(sample_1, sample_2)
                hist_r += np.histogram(r, pdf_edges_r)[0]

                x = sample_1[:, 0] - sample_2[:, 0]
                hist_x += np.histogram(x, pdf_edges_x)[0]

                y = sample_1[:, 1] - sample_2[:, 1]
                hist_y += np.histogram(y, pdf_edges_y)[0]

                vec_1_2 = sample_2 - sample_1
                theta = np.arctan2(vec_1_2[1:, 0], vec_1_2[1:, 1])
                theta[theta > np.pi] -= 2 * np.pi
                theta[theta < -np.pi] += 2 * np.pi
                hist_theta += np.histogram(theta, pdf_edges_theta)[0]

        pdf_r = hist_r / sum(hist_r) / bin_size_r
        pair_distribution_r = np.stack((bin_centers_r, pdf_r))
        pickle_save(
            f"../data/pickle/pair_distribution_r_without_interaction_{env_name_short}.pkl",
            pair_distribution_r,
        )

        pdf_x = hist_x / sum(hist_x) / bin_size_x
        pair_distribution_x = np.stack((bin_centers_x, pdf_x))
        pickle_save(
            f"../data/pickle/pair_distribution_x_without_interaction_{env_name_short}.pkl",
            pair_distribution_x,
        )

        pdf_y = hist_y / sum(hist_y) / bin_size_y
        pair_distribution_y = np.stack((bin_centers_y, pdf_y))
        pickle_save(
            f"../data/pickle/pair_distribution_y_without_interaction_{env_name_short}.pkl",
            pair_distribution_y,
        )

        pdf_theta = hist_theta / sum(hist_theta) / bin_size_theta
        pair_distribution_theta = np.stack((bin_centers_theta, pdf_theta))
        pickle_save(
            f"../data/pickle/pair_distribution_theta_without_interaction_{env_name_short}.pkl",
            pair_distribution_theta,
        )
