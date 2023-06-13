from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.environment import Environment

from parameters import *
from utils import *

""" The goal of this script is to plot the occupancy of the corridor (diamor & atc) environment. The occupancy is computed 
by counting the number of pedestrians in each cell of a grid."""


#plt.style.use("science")

from utils import (
    get_pedestrian_thresholds,
)

if __name__ == "__main__":
    for env_name in ["atc:corridor", "diamor:corridor"]:
        # print(f"- {env_name}")
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()

        thresholds_indiv = get_pedestrian_thresholds(env_name)

        pedestrians = env.get_pedestrians(thresholds=thresholds_indiv)

        GRID_SIZE = 100
        n_bin_x = int(np.ceil((XMAX - XMIN) / GRID_SIZE) + 1)
        n_bin_y = int(np.ceil((YMAX - YMIN) / GRID_SIZE) + 1)
        grid = np.zeros((n_bin_x, n_bin_y))

        for pedestrian in pedestrians:
            x = pedestrian.get_trajectory_column("x")
            y = pedestrian.get_trajectory_column("y")

            nx = np.ceil((x - XMIN) / GRID_SIZE).astype("int")
            ny = np.ceil((y - YMIN) / GRID_SIZE).astype("int")

            in_roi = np.logical_and(
                np.logical_and(nx >= 0, nx < n_bin_x),
                np.logical_and(ny >= 0, ny < n_bin_y),
            )
            nx = nx[in_roi]
            ny = ny[in_roi]

            grid[nx, ny] += 1

        max_val = np.max(grid)
        grid /= max_val

        xi = np.linspace(0, (XMAX - XMIN) / 1000, n_bin_x)
        yi = np.linspace(0, (YMAX - YMIN) / 1000, n_bin_y)

        fig, ax = plt.subplots(figsize=(3, 3))
        plot_color_map(
            xi,
            yi,
            grid,
            "x (m)",
            "y (m)",
            save_path=f"../data/figures/occupancy/occupancy_grid_{env_name_short}.pdf",
            # show=True,
            aspect="equal",
            cmap="inferno_r",
            fig=fig,
            ax=ax,
        )

    
