from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np
from tqdm import tqdm

from utils import *


if __name__ == "__main__":

    net_min, net_max = 1, 30
    n_bins = 64
    bin_size, pdf_edges, bin_centers = get_bins(net_min, net_max, n_bins)

    fig, axes = plt.subplots(3, 1)

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        days = get_all_days(env_name)

        displacements = pickle_load(f"../data/pickle/net_gross_{env_name_short}.pkl")

        # ax.scatter(displacements["net"], displacements["gross"])
        net = displacements["net"] / 1000
        gross = displacements["gross"] / 1000

        indices = np.logical_and(net >= net_min, net <= net_max)
        net = net[indices]
        gross = gross[indices]

        tortuosity = net / gross
        mean_gross, std_gross, ste_gross, _ = get_mean_std_ste_n_over_bins(
            net, gross, pdf_edges[1:]
        )
        mean_tor, std_tor, ste_tor, _ = get_mean_std_ste_n_over_bins(
            net, tortuosity, pdf_edges[1:]
        )

        diff = gross - net
        mean_diff, std_diff, ste_diff, _ = get_mean_std_ste_n_over_bins(
            net, diff, pdf_edges[1:]
        )

        axes[0].errorbar(
            bin_centers,
            mean_gross,
            ste_gross,
            label=env_name_short,
            capsize=2,
        )

        axes[1].errorbar(
            bin_centers,
            mean_tor,
            ste_tor,
            label=env_name_short,
            capsize=2,
        )

        axes[2].errorbar(
            bin_centers,
            mean_diff,
            ste_diff,
            label=env_name_short,
            capsize=2,
        )

    axes[0].plot([net_min, net_max], [net_min, net_max], c="red")
    axes[0].set_aspect("equal")
    axes[0].grid(color="lightgray", linestyle="--", linewidth=0.5)
    axes[0].legend()

    axes[1].grid(color="lightgray", linestyle="--", linewidth=0.5)
    axes[1].legend()

    axes[2].grid(color="lightgray", linestyle="--", linewidth=0.5)
    axes[2].legend()

    plt.show()
