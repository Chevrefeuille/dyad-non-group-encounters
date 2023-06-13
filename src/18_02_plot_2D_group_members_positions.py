from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np
from tqdm import tqdm

from utils import *


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        positions = pickle_load(
            f"../data/pickle/positions_group_members_{env_name_short}_with_interaction.pkl"
        )

        min_x, max_x = -1, 1
        min_y, max_y = -1, 1
        n_bin_x, n_bin_y = 64, 64

        threshold_d = 1

        for i, v in enumerate(soc_binding_values):

            grid, xi, yi, cell_size_x, cell_size_y = get_grid(
                min_x, max_x, n_bin_x, min_y, max_y, n_bin_y
            )

            indx_small = positions[v]["d"] / 1000 > 4

            xs = (
                np.concatenate(
                    (
                        positions[v]["pos_Ax"][indx_small],
                        positions[v]["pos_Bx"][indx_small],
                    )
                )
                / 1000
            )
            ys = (
                np.concatenate(
                    (
                        positions[v]["pos_Ay"][indx_small],
                        positions[v]["pos_By"][indx_small],
                    )
                )
                / 1000
            )

            p = np.vstack((xs, ys)).T

            update_grid(
                grid,
                p,
                min_x,
                n_bin_x,
                cell_size_x,
                min_y,
                n_bin_y,
                cell_size_y,
            )

            grid /= np.max(grid)

            # plot_color_map(
            #     xi,
            #     yi,
            #     grid,
            #     xlabel="x (m)",
            #     ylabel="y (m)",
            #     vmin=None,
            #     title=soc_binding_names[v],
            #     # vmax=None,
            #     # interpolation=None,
            #     # show=True,
            #     cmap="jet",
            #     # xlim=None,
            #     # ylim=None,
            #     save_path=f"../data/figures/group_structure/{soc_binding_names[v]}_bigger_4.pdf",
            # )

            # fig, ax = plt.subplots()
            # ax.scatter(xs, ys)
            # plt.show()
