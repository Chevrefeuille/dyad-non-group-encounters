from calendar import c
from email import header
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import numpy as np
from parameters import *
from utils import *

from scipy.optimize import curve_fit
import pandas as pd


MARKERS = ["^", "o", "s", "D"]

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        observed_minimum_distances_non_groups = pickle_load(
            f"../data/pickle/observed_minimum_distance_non_groups_{env_name_short}_with_interaction.pkl"
        )
        straight_line_minimum_distances_non_groups = pickle_load(
            f"../data/pickle/straight_line_minimum_distance_non_groups_{env_name_short}_with_interaction.pkl"
        )
        velocities_non_groups = pickle_load(
            f"../data/pickle/velocities_non_groups_{env_name_short}_with_interaction.pkl"
        )

        observed_minimum_distances_groups = pickle_load(
            f"../data/pickle/observed_minimum_distance_{env_name_short}_with_interaction.pkl"
        )
        straight_line_minimum_distances_groups = pickle_load(
            f"../data/pickle/straight_line_minimum_distance_{env_name_short}_with_interaction.pkl"
        )
        velocities_groups = pickle_load(
            f"../data/pickle/velocities_{env_name_short}_with_interaction.pkl"
        )

        group_size = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")

        N_BINS = 8
        MIN, MAX = 0, 4
        bin_size = (MAX - MIN) / N_BINS
        pdf_edges = np.linspace(MIN, MAX, N_BINS + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        n_interp = 1000
        fit_x = np.linspace(MIN + bin_size * 3 / 2, MAX, n_interp)

        if env_name_short == "atc":
            a, b = 0.823, 0  # obtained from 11_12_05
        else:
            a, b = 1, 0

        for i, v in enumerate(soc_binding_values):

            r0 = observed_minimum_distances_groups[v] / np.nanmean(group_size[v])
            rb = straight_line_minimum_distances_groups[v] / np.nanmean(group_size[v])
            vel = velocities_groups[v] / np.nanmean(group_size[v])

            # r0 = observed_minimum_distances_groups[v] / 1000
            # rb = straight_line_minimum_distances_groups[v] / 1000
            # vel = velocities_groups[v] / 1000

            rb *= a

            p = (r0**2 - rb**2) / r0**2

            fig = plt.figure()
            ax = plt.axes(projection="3d")
            ax.scatter3D(r0, rb, p, c=p)
            ax.set_zlim([-4, 1])
            ax.set_xlabel("r0")
            ax.set_ylabel("rb")
            ax.set_zlabel("U")
            plt.show()
