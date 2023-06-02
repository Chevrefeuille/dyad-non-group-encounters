
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np
import scipy.signal as signal

from utils import *


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

        for ped in pedestrians:
            # ped.plot_2D_trajectory()

            trajectory = ped.get_trajectory()

            delta = trajectory[1:,1:3] - trajectory[:-1,1:3]
            main_direction = np.mean(delta, axis=0)
            main_angle = np.arctan2(main_direction[1], main_direction[0])

            if main_angle > np.pi / 2 or main_angle < -np.pi/2:
                delta[:,0]*=-1
                # trajectory[:,5] *= -1
            
            angles = np.arctan2(delta[:,1], delta[:,0])
            angles *= 180 / np.pi

            n_smoothing = 5 # odd size kernel
            moving_avg_angles = np.convolve(angles, np.ones(n_smoothing)/n_smoothing, mode='valid')

            N  = 3    # Filter order
            Wn = 0.1 # Cutoff frequency
            B, A = signal.butter(N, Wn, output='ba')
            butter_angles = signal.filtfilt(B,A, angles)

            der_butter_angles = butter_angles[1:]-butter_angles[:-1]

            # n_bins = int(360 / 20)
            # bin_size, bin_edges, bin_centers = get_bins(-180, 180, n_bins)
            # bin_ids = np.digitize(angles, bin_edges)
            # quantized_angles = bin_centers[bin_ids - 1]

            fig, axes = plt.subplots(3, 1)
            # plot_static_2D_trajectory(trajectory, ax=axes[0], show=False,boundaries=env.boundaries)
            axes[0].scatter(trajectory[:-1,1]/1000,trajectory[:-1,2]/1000, c=butter_angles, vmin=-180, vmax=180, s=3)
            axes[0].set_aspect("equal")
            axes[0].set_xlim(XMIN / 1000, XMAX / 1000)
            axes[0].set_ylim(YMIN/1000, YMAX/1000)

            t = np.arange(len(angles))
            axes[1].plot(angles, label="raw")
            # axes[1].plot(quantized_angles, label="raw")
            axes[1].plot(butter_angles, label="butter filter")
            axes[1].plot(moving_avg_angles, label="moving average")
            axes[1].set_ylim(-180, 180)
            axes[1].legend()

            axes[2].plot(der_butter_angles)
            axes[2].set_ylim(-20, 20)

            
            plt.show()



           