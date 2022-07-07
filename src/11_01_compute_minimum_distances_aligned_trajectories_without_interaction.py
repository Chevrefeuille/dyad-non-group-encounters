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

        day1, day2 = ["0109", "0217"] if env_name_short == "atc" else ["06", "08"]

        observed_minimum_distances = []
        straight_line_minimum_distances = []

        n_ped = 2000

        for pedestrian_1 in tqdm(rnd.sample(pedestrians_by_day[day1], n_ped)):
            traj_1 = pedestrian_1.get_trajectory()
            for pedestrian_2 in rnd.sample(pedestrians_by_day[day2], n_ped):
                traj_2 = pedestrian_2.get_trajectory()

                # plot_static_2D_trajectories([traj_1, traj_2], labels=["1", "2"])

                # find random subset with the same numbers of observations
                n_1 = len(traj_1)
                n_2 = len(traj_2)

                if n_1 <= 1 or n_2 <= 1:
                    continue

                rnd_len = np.random.randint(1, min(n_1, n_2))
                start_1 = np.random.randint(0, len(traj_1) - rnd_len)
                start_2 = np.random.randint(0, len(traj_2) - rnd_len)
                sub_traj_1 = traj_1[start_1 : start_1 + rnd_len]
                sub_traj_2 = traj_2[start_2 : start_2 + rnd_len]

                traj1_aligned, [traj2_aligned] = align_trajectories_at_origin(
                    sub_traj_1, [sub_traj_2]
                )

                # pos_1 = traj1_aligned[:, 1:3]
                # pos_2 = traj2_aligned[:, 1:3]

                # r0 = compute_observed_minimum_distance(traj1_aligned, traj2_aligned)
                sub_traj_1 = traj_1[start_1 : start_1 + rnd_len]
                sub_traj_2 = traj_2[start_2 : start_2 + rnd_len]

                rp = compute_straight_line_minimum_distance(traj2_aligned)
                ro = compute_observed_minimum_distance(traj2_aligned, interpolate=True)

                if rp:
                    observed_minimum_distances += [ro]
                    straight_line_minimum_distances += [rp]

        pickle_save(
            f"../data/pickle/observed_minimum_distance_{env_name_short}_without_interaction.pkl",
            np.array(observed_minimum_distances),
        )
        pickle_save(
            f"../data/pickle/straight_line_minimum_distance_{env_name_short}_without_interaction.pkl",
            np.array(straight_line_minimum_distances),
        )

        # max_value = np.max(grids_count)
        # grids_count /= max_value
        # plt.figure()
        # cmesh = plt.pcolormesh(xi, yi, grids_count.T, cmap="inferno_r", shading="auto")
        # plt.xlabel("x (m)")
        # plt.ylabel("y (m)")
        # axes = plt.gca()
        # # divider = make_axes_locatable(axes)
        # # cax = divider.append_axes("right", size="5%", pad=0.3)
        # plt.colorbar(cmesh)
        # axes.set_aspect("equal")
        # # plt.show()

        # pickle_save(
        #     f"../data/pickle/aligned_trajectories_2D_distribution_{env_name_short}_without_interaction.pkl",
        #     grids_count,
        # )

        # pdf_theta = hist_theta / sum(hist_theta) / bin_size_theta
        # pair_distribution_theta = np.stack((bin_centers_theta, pdf_theta))
        # pickle_save(
        #     f"../data/pickle/aligned_trajectories_distribution_theta_without_interaction_{env_name_short}.pkl",
        #     pair_distribution_theta,
        # )

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
