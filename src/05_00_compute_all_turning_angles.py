from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from scipy.spatial import distance
from scipy import integrate
import random as rnd
from tqdm import tqdm

from parameters import (
    N_BINS_TURNING_DISTRIBUTION,
    TURNING_DISTRIBUTION_MAX,
    TURNING_DISTRIBUTION_MIN,
)

if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        threshold_v = Threshold("v", min=500, max=3000)  # velocity in [0.5; 3]m/s
        threshold_d = Threshold("d", min=5000)  # walk at least 5 m
        thresholds_indiv = [threshold_v, threshold_d]

        # corridor threshold for ATC
        if env_name == "atc":
            threshold_corridor_x = Threshold("x", 5000, 48000)
            threshold_corridor_y = Threshold("y", -27000, 8000)
            thresholds_indiv += [threshold_corridor_x, threshold_corridor_y]

        pedestrians_by_day = env.get_pedestrians_grouped_by(
            "day", thresholds=thresholds_indiv
        )

        # start by constructing the probability of two pedestrians to be at distance d
        # for not interacting pedestrians
        # i.e. on different days (take two days with most and least people for atc)

        n_ped = 1000

        day1, day2 = ["0217", "0109"] if env_name == "atc" else ["06", "08"]

        bin_size = (
            TURNING_DISTRIBUTION_MAX - TURNING_DISTRIBUTION_MIN
        ) / N_BINS_TURNING_DISTRIBUTION
        pdf_edges = np.linspace(
            TURNING_DISTRIBUTION_MIN,
            TURNING_DISTRIBUTION_MAX,
            N_BINS_TURNING_DISTRIBUTION + 1,
        )
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        # check pairs
        hist = np.zeros(len(pdf_edges) - 1)
        for pedestrian in tqdm(rnd.sample(pedestrians_by_day[day1], n_ped)):
            pos = pedestrian.get_position()
            turning_angles = compute_turning_angles(pos)

            hist += np.histogram(turning_angles, pdf_edges)[0]

        # plot pair wise distance distribution
        # plot mean for each bin
        pdf = hist / sum(hist) / bin_size
        # print(integrate.trapezoid(pdf, bin_centers))

        pair_distribution = np.stack((bin_centers, pdf))

        pickle_save(
            f"../data/pickle/turning_angles_distribution_without_interaction_{env_name}.pkl",
            pair_distribution,
        )

        plt.plot(bin_centers, pdf, linewidth=3, label=env_name)
        plt.title(f"Baseline pair distribution - not interacting")
    plt.legend()
    plt.show()
