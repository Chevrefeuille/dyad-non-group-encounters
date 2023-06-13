from operator import length_hint
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
import matplotlib.pyplot as plt
import pandas as pd

""" The goal of this script is to plot the tortuosity of trajectories with respect to their length.
"""

if __name__ == "__main__":

    fig, ax = plt.subplots()
    N_BINS_TRAJ_SIZE = 30
    TRAJ_SIZE_MIN, TRAJ_SIZE_MAX = 1000, 50000
    bin_size = (TRAJ_SIZE_MAX - TRAJ_SIZE_MIN) / N_BINS_TRAJ_SIZE
    pdf_edges = np.linspace(
        TRAJ_SIZE_MIN,
        TRAJ_SIZE_MAX,
        N_BINS_TRAJ_SIZE + 1,
    )
    bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])
    # print(bin_centers)

    data = np.empty((len(bin_centers), 3))
    data[:, 0] = bin_centers

    for i, env_name in enumerate(["atc:corridor", "diamor:corridor"]):

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        env_name_short = env_name.split(":")[0]

        lengths = pickle_load(
            f"../data/pickle/length_trajectory_all_{env_name_short}_random.pkl"
        )
        deflections = pickle_load(
            f"../data/pickle/deflection_all_{env_name_short}_random.pkl"
        )

        lengths_g = np.array(lengths["non_group"]["gross"])
        lengths_n = np.array(lengths["non_group"]["net"])

        # tortuosity = np.array(
        #     deflections["non_group"]["straightness_index"]
        #     + deflections["group_members"]["straightness_index"]
        # )

        mean_g = get_mean_over_bins(lengths_n, lengths_g, pdf_edges[1:])
        # plt.scatter(lengths_n, lengths_g, marker=".", alpha=0.3)
        # print(mean_tortuosity)

        ax.plot(bin_centers, mean_g)

        # data[:, i + 1] = mean_tortuosity

    ax.plot(bin_centers, bin_centers, c="red")
    # plt.axis("scaled")

    plt.show()
    pd.DataFrame(data).to_csv(
        f"../data/plots/tortuosity/tortuosity.csv",
        index=False,
        header=False,
    )
