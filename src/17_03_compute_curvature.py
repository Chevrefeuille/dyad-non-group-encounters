from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import random as rnd
import numpy as np
import scipy.signal as signal
from scipy.fft import fft, fftfreq

from utils import *


cross = lambda x, y, axis=1: np.cross(x, y, axis=axis)


def compute_curvature(p):
    v = p[1:, :] - p[:-1, :]
    a = v[1:, :] - v[:-1, :]
    k = cross(v[1:, :], a, axis=1) / np.linalg.norm(v[1:, :], axis=1) ** 3
    return k


if __name__ == "__main__":

    # for env_name in ["atc:corridor", "diamor:corridor"]:
    for env_name in ["diamor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        observed_minimum_distances = {}
        straight_line_minimum_distances = {}
        group_sizes = {}
        velocities = {}

        thresholds_ped = get_pedestrian_thresholds(env_name)

        pedestrians = env.get_pedestrians(thresholds=thresholds_ped, no_groups=True)

        N = 3  # Filter order
        Wn = 0.1  # Cutoff frequency
        B, A = signal.butter(N, Wn, output="ba")

        for ped in rnd.sample(pedestrians, len(pedestrians)):
            # ped.plot_2D_trajectory()

            trajectory = ped.get_trajectory()

            x = trajectory[:, 1] / 1000
            y = trajectory[:, 2] / 1000
            t = trajectory[:, 0] / 1000 - trajectory[0, 0] / 1000
            N = len(t)

            x_f = fft(x)
            y_f = fft(y)

            t_f = fftfreq(N, d=0.1)[: N // 2]

            #print(t_f)

            smoothed_trajectory = np.vstack(
                (
                    signal.filtfilt(B, A, x),
                    signal.filtfilt(B, A, y),
                )
            ).T

            curvature = compute_curvature(smoothed_trajectory)

            # fig, axes = plt.subplots(5, 1)
            # # plot_static_2D_trajectory(trajectory, ax=axes[0], show=False,boundaries=env.boundaries)
            # axes[0].scatter(trajectory[:-1, 1] / 1000, trajectory[:-1, 2] / 1000, s=3)
            # # axes[0].scatter(
            # #     smoothed_trajectory[1:-1, 0],
            # #     smoothed_trajectory[1:-1, 1],
            # #     s=1,
            # #     c=np.abs(curvature),
            # #     vmin=0,
            # #     vmax=1,
            # # )



            # axes[0].set_aspect("equal")
            # axes[0].set_xlim(XMIN / 1000, XMAX / 1000)
            # axes[0].set_ylim(YMIN / 1000, YMAX / 1000)

            # axes[1].plot(np.abs(curvature))
            # axes[1].set_ylim(-3, 3)
            # axes[2].plot(
            #     t_f[1 : N // 2], 2.0 / N * np.abs(x_f[1 : N // 2]), "-b", label="x"
            # )
            # axes[2].plot(
            #     t_f[1 : N // 2], 2.0 / N * np.abs(y_f[1 : N // 2]), "-r", label="y"
            # )
            # axes[2].legend()
            # axes[2].grid()

            # axes[3].plot(t, x)
            # axes[4].plot(t, y)

            # #plt.show()
