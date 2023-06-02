from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
from parameters import *
from utils import *

import scienceplots

plt.style.use("science")


if __name__ == "__main__":
    limits = {"atc": [-0.3, 0.2], "diamor": [-0.5, 0.5]}

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

        # cropped_x_min, cropped_x_max = -4, 4
        # cropped_y_min, cropped_y_max = -4, 4
        # n_bins_x_cropped = math.ceil(
        #     n_bins_x_scaled_size
        #     * (cropped_x_max - cropped_x_min)
        #     / (max_x_scaled_size - min_x_scaled_size)
        # )
        # n_bins_y_cropped = math.ceil(
        #     n_bins_y_scaled_size
        #     * (cropped_y_max - cropped_y_min)
        #     / (max_y_scaled_size - min_y_scaled_size)
        # )
        # index_cropped_x_min = int(
        #     n_bins_x_scaled_size
        #     * (cropped_x_min - min_x_scaled_size)
        #     / (max_x_scaled_size - min_x_scaled_size)
        # )
        # index_cropped_x_max = index_cropped_x_min + n_bins_x_cropped

        # index_cropped_y_min = int(
        #     n_bins_y_scaled_size
        #     * (cropped_y_min - min_y_scaled_size)
        #     / (max_y_scaled_size - min_y_scaled_size)
        # )
        # index_cropped_y_max = index_cropped_y_min + n_bins_y_cropped

        # # print(index_cropped_x_min, index_cropped_x_max)
        # # print(index_cropped_y_min, index_cropped_y_max)

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

        # x_interp = np.linspace(min_x_scaled_size, max_x_scaled_size, 1000)
        # y_interp = np.linspace(min_y_scaled_size, max_y_scaled_size, 1000)

        # index_cropped_x_min_interp = int(
        #     index_cropped_x_min * len(x_interp) / n_bins_x_scaled_size
        # )
        # index_cropped_x_max_interp = int(
        #     index_cropped_x_max * len(x_interp) / n_bins_x_scaled_size
        # )
        # index_cropped_y_min_interp = int(
        #     index_cropped_y_min * len(y_interp) / n_bins_y_scaled_size
        # )
        # index_cropped_y_max_interp = int(
        #     index_cropped_y_max * len(y_interp) / n_bins_y_scaled_size
        # )

        # plot 2D pair distributions
        for i, v in enumerate(soc_binding_values):
            fig, ax = plt.subplots()

            grid_scaled_size = grids_count_scaled_size[i, ...] / np.max(
                grids_count_scaled_size[i, ...]
            )
            diff = grid_scaled_size - all_counts_scaled_size
            # print(diff.shape, xi_scaled_size.shape)
            # f_interp = interpolate.interp2d(
            #     (xi_scaled_size[1:] + xi_scaled_size[:-1]) / 2,
            #     (yi_scaled_size[1:] + yi_scaled_size[:-1]) / 2,
            #     diff,
            #     kind="cubic",
            # )
            # # print(f_interp)
            # diff_interp = f_interp(x_interp, y_interp)
            plot_color_map(
                xi_scaled_size,
                yi_scaled_size,
                # x_interp[index_cropped_x_min_interp:index_cropped_x_max_interp],
                # y_interp[index_cropped_y_min_interp:index_cropped_y_max_interp],
                # diff_interp[
                #     index_cropped_x_min_interp:index_cropped_x_max_interp,
                #     index_cropped_y_min_interp:index_cropped_y_max_interp,
                # ],
                diff,
                vmin=limits[env_name_short][0],
                vmax=limits[env_name_short][1],
                cmap="jet",
                ax=ax,
                fig=fig,
                show=False,
                interpolation="bicubic",
                xlim=(-4.5, 4.5),
                ylim=(-4.5, 4.5),
                xlabel="x",
                ylabel="y",
                aspect="equal",
                # save_path=f"../data/figures/pair_distributions/2D/scaling/{env_name_short}_{soc_binding_names[v]}_aligned_trajectories_2D_distribution_scaled_width.png",
            )
            # plt.suptitle(soc_binding_names[v])
            plt.savefig(
                f"../data/figures/2D_distributions/paper/2D_distributions_{env_name_short}_{soc_binding_names[v]}.pdf"
            )
            # plt.close()
            # plt.show()
