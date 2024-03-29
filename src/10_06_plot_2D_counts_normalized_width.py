from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
from parameters import *
from utils import *

from scipy.ndimage import gaussian_filter

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        grids_count_scaled_size = pickle_load(
            f"../data/pickle/aligned_trajectories_2D_counts_{env_name_short}_scaled_size.pkl"
        )

        min_x_scaled_size, max_x_scaled_size = -6, 6
        min_y_scaled_size, max_y_scaled_size = -6, 6
        n_bins_x_scaled_size, n_bins_y_scaled_size = 20, 20
        (
            all_counts_scaled_size,
            xi_scaled_size,
            yi_scaled_size,
            cell_size_x_scaled_size,
            cell_size_y_scaled_size,
        ) = get_grid(
            min_x_scaled_size,
            max_x_scaled_size,
            n_bins_x_scaled_size,
            min_y_scaled_size,
            max_y_scaled_size,
            n_bins_y_scaled_size,
        )
        all_counts_scaled_size = all_counts_scaled_size[0]

        for i, v in enumerate(soc_binding_values):

            all_counts_scaled_size += grids_count_scaled_size[i, ...] / np.max(
                grids_count_scaled_size[i, ...]
            )
        all_counts_scaled_size /= len(soc_binding_values)

        # plot 2D pair distributions
        for i, v in enumerate(soc_binding_values):
            fig, axes = plt.subplots(3, 3, figsize=(10, 8))

            grid_scaled_size = grids_count_scaled_size[i, ...] / np.max(
                grids_count_scaled_size[i, ...]
            )
            plot_color_map(
                xi_scaled_size,
                yi_scaled_size,
                all_counts_scaled_size,
                title="Scaling with group width",
                vmin=0,
                vmax=1,
                cmap="jet",
                ax=axes[0, 2],
                fig=fig,
                show=False,
                interpolation="bicubic"
                # save_path=f"../data/figures/pair_distributions/2D/scaling/{env_name_short}_{soc_binding_names[v]}_aligned_trajectories_2D_distribution_scaled_width.png",
            )
            plot_color_map(
                xi_scaled_size,
                yi_scaled_size,
                grid_scaled_size,
                vmin=0,
                vmax=1,
                cmap="jet",
                ax=axes[1, 2],
                fig=fig,
                show=False,
                interpolation="bicubic"
                # save_path=f"../data/figures/pair_distributions/2D/scaling/{env_name_short}_{soc_binding_names[v]}_aligned_trajectories_2D_distribution_scaled_width.png",
            )
            plot_color_map(
                xi_scaled_size,
                yi_scaled_size,
                grid_scaled_size - all_counts_scaled_size,
                vmin=-0.5,
                vmax=0.5,
                cmap="jet",
                ax=axes[2, 2],
                fig=fig,
                show=False,
                interpolation="bicubic"
                # save_path=f"../data/figures/pair_distributions/2D/scaling/{env_name_short}_{soc_binding_names[v]}_aligned_trajectories_2D_distribution_scaled_width.png",
            )
            plt.suptitle(soc_binding_names[v])
            plt.savefig(
                f"../data/figures/2D_distributions/2D_distributions_{env_name_short}_{soc_binding_names[v]}.png"
            )
            plt.close()
            # plt.show()
