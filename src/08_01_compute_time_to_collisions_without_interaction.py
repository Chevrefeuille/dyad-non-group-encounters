from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *
from utils import *

import random as rnd
from tqdm import tqdm

from parameters import *

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

        bin_size_t = (
            PAIR_DISTRIBUTION_MAX_T_COLL - PAIR_DISTRIBUTION_MIN_T_COLL
        ) / N_BINS_PAIR_DISTRIBUTION_T_COLL
        pdf_edges_t = np.linspace(
            PAIR_DISTRIBUTION_MIN_T_COLL,
            PAIR_DISTRIBUTION_MAX_T_COLL,
            N_BINS_PAIR_DISTRIBUTION_T_COLL + 1,
        )
        bin_centers_t = 0.5 * (pdf_edges_t[0:-1] + pdf_edges_t[1:])
        hist_t = np.zeros(len(bin_centers_t))

        n_ped = 1000
        n_samples = 20

        for pedestrian_1 in tqdm(rnd.sample(pedestrians_by_day[day1], n_ped)):
            traj_1 = pedestrian_1.get_trajectory()
            for pedestrian_2 in rnd.sample(pedestrians_by_day[day2], n_ped):
                traj_2 = pedestrian_2.get_trajectory()

                n_rand = min(n_samples, len(traj_1), len(traj_2))
                random_id_1 = np.random.choice(len(traj_1), size=n_rand, replace=False)
                sample_1 = traj_1[random_id_1, :]
                random_id_2 = np.random.choice(len(traj_2), size=n_rand, replace=False)
                sample_2 = traj_2[random_id_2, :]

                # t = compute_times_to_collision(sample_1, sample_2)
                times_to_collision = []
                for i in range(n_rand):
                    t_coll, pos_coll = compute_time_to_collision(
                        sample_1[i], sample_2[i]
                    )
                    # print(t_coll)
                    if t_coll > 0:
                        times_to_collision += [t_coll]

                hist_t += np.histogram(times_to_collision, pdf_edges_t)[0]

                # if t_coll > 0:

                #     delta_t = 0.5
                #     n_p = 100
                #     coll_pos_1 = [
                #         sample_1[0, 1:3] + delta_t * k * sample_1[0, 5:7]
                #         for k in range(n_p)
                #     ]
                #     coll_pos_2 = [
                #         sample_2[0, 1:3] + delta_t * k * sample_2[0, 5:7]
                #         for k in range(n_p)
                #     ]

                #     coll_traj_1, coll_traj_2 = np.zeros((len(coll_pos_1), 7)), np.zeros(
                #         (len(coll_pos_2), 7)
                #     )
                #     coll_traj_1[:, 0] = np.arange(0, len(coll_pos_1) * delta_t, delta_t)
                #     coll_traj_2[:, 0] = np.arange(0, len(coll_pos_2) * delta_t, delta_t)
                #     coll_traj_1[:, 1:3] = coll_pos_1
                #     coll_traj_2[:, 1:3] = coll_pos_2

                #     coll_traj_3 = np.zeros((1, 7))
                #     coll_traj_3[:, 1:3] = pos_coll

        pdf_t = hist_t / sum(hist_t) / bin_size_t
        pair_distribution_t = np.stack((bin_centers_t, pdf_t))
        pickle_save(
            f"../data/pickle/pair_distribution_times_to_collision_without_interaction_{env_name_short}.pkl",
            pair_distribution_t,
        )

        # plt.plot(bin_centers_t, pdf_t)
        # plt.show()
