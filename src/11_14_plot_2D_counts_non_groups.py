from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
from parameters import *
from utils import *

from scipy.ndimage import gaussian_filter

if __name__ == "__main__":

    limits = {"atc": [-0.3, 0.2], "diamor": [-0.5, 0.5]}

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )
        grids_count_non_groups = pickle_load(
            f"../data/pickle/aligned_trajectories_2D_counts_non_groups_{env_name_short}.pkl"
        )
        grids_count_groups = pickle_load(
            f"../data/pickle/aligned_trajectories_2D_counts_{env_name_short}.pkl",
        )

        min_x, max_x = -4, 4
        min_y, max_y = -4, 4
        n_bins_x, n_bins_y = 20, 20
        (groups_all_counts, xi, yi, cell_size_x, cell_size_y,) = get_grid(
            min_x,
            max_x,
            n_bins_x,
            min_y,
            max_y,
            n_bins_y,
        )
        groups_all_counts = groups_all_counts[0]

        for i, v in enumerate(soc_binding_values):
            groups_all_counts += grids_count_groups[i, ...] / np.max(
                grids_count_groups[i, ...]
            )
        groups_all_counts /= len(soc_binding_values)

        # plot 2D pair distributions

        grids_count_non_groups = grids_count_non_groups / np.max(grids_count_non_groups)

        plot_color_map(
            xi,
            yi,
            grids_count_non_groups,
            # vmin=0,
            # vmax=1,
            cmap="jet",
            show=True,
            interpolation="bicubic"
            # save_path=f"../data/figures/pair_distributions/2D/scaling/{env_name_short}_{soc_binding_names[v]}_aligned_trajectories_2D_distribution_scaled_width.png",
        )

        plot_color_map(
            xi,
            yi,
            groups_all_counts,
            # vmin=0,
            # vmax=1,
            cmap="jet",
            show=True,
            interpolation="bicubic"
            # save_path=f"../data/figures/pair_distributions/2D/scaling/{env_name_short}_{soc_binding_names[v]}_aligned_trajectories_2D_distribution_scaled_width.png",
        )

        plot_color_map(
            xi,
            yi,
            groups_all_counts - grids_count_non_groups,
            # vmin=0,
            # vmax=1,
            cmap="jet",
            show=True,
            interpolation="bicubic"
            # save_path=f"../data/figures/pair_distributions/2D/scaling/{env_name_short}_{soc_binding_names[v]}_aligned_trajectories_2D_distribution_scaled_width.png",
        )
        # plt.suptitle(soc_binding_names[v])
        # plt.savefig(
        #     f"../data/figures/2D_distributions/paper/2D_distributions_{env_name_short}_{soc_binding_names[v]}.pdf"
        # )
        # plt.close()
        # plt.show()
