import numpy as np
import matplotlib.pyplot as plt

from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.constants import *
from parameters import *


def get_pedestrian_thresholds(env_name):
    thresholds_indiv = []
    thresholds_indiv += [
        Threshold("v", min=VEL_MIN, max=VEL_MAX)
    ]  # velocity in [0.5; 3]m/s
    thresholds_indiv += [Threshold("d", min=D_MIN)]  # walk at least 5 m

    # thresholds_indiv += [Threshold("theta", max=THETA_MAX)]  # no 90° turns

    # corridor threshold for ATC
    if env_name == "atc:corridor":
        thresholds_indiv += [
            Threshold(
                "x", BOUNDARIES_ATC_CORRIDOR["xmin"], BOUNDARIES_ATC_CORRIDOR["xmax"]
            )
        ]
        thresholds_indiv += [
            Threshold(
                "y", BOUNDARIES_ATC_CORRIDOR["ymin"], BOUNDARIES_ATC_CORRIDOR["ymax"]
            )
        ]
    elif env_name == "diamor:corridor":
        thresholds_indiv += [
            Threshold(
                "x",
                BOUNDARIES_DIAMOR_CORRIDOR["xmin"],
                BOUNDARIES_DIAMOR_CORRIDOR["xmax"],
            )
        ]
        thresholds_indiv += [
            Threshold(
                "y",
                BOUNDARIES_DIAMOR_CORRIDOR["ymin"],
                BOUNDARIES_DIAMOR_CORRIDOR["ymax"],
            )
        ]

    return thresholds_indiv


def get_groups_thresholds():
    # threshold on the distance between the group members, max 4 m
    group_thresholds = [
        Threshold("delta", min=GROUP_BREADTH_MIN, max=GROUP_BREADTH_MAX)
    ]
    return group_thresholds


def get_all_days(env_name):
    if "atc" in env_name:
        return DAYS_ATC
    elif "diamor" in env_name:
        return DAYS_DIAMOR
    else:
        raise ValueError(f"Unknown env {env_name}")


def get_social_values(env_name):
    if "atc" in env_name:
        return "soc_rel", SOCIAL_RELATIONS_EN, [1, 2, 3, 4], COLORS_SOC_REL
    elif "diamor" in env_name:
        return (
            "interaction",
            INTENSITIES_OF_INTERACTION_NUM,
            [0, 1, 2, 3],
            COLORS_INTERACTION,
        )
    else:
        raise ValueError(f"Unknown env {env_name}")


def get_mean_over_bins(x, y, bin_centers):
    mean_over_bins = []
    bin_ids = np.digitize(x, bin_centers)
    for k in range(len(bin_centers)):
        mean_for_bin = np.nanmean(y[bin_ids == k])
        mean_over_bins += [mean_for_bin]
    return mean_over_bins


def get_mean_std_over_bins(x, y, bin_centers):
    mean_over_bins = []
    std_over_bins = []
    bin_ids = np.digitize(x, bin_centers)
    for k in range(len(bin_centers)):
        mean_for_bin = np.nanmean(y[bin_ids == k])
        mean_over_bins += [mean_for_bin]
        std_for_bin = np.nanstd(y[bin_ids == k])
        std_over_bins += [std_for_bin]
    return mean_over_bins, std_over_bins


def plot_color_map(
    xi, yi, grid, xlabel, ylabel, title=None, vmin=None, vmax=None, save_path=None, equal=True
):
    if vmin is None:
        vmin = np.min(grid)
    if vmax is None:
        vmax = np.max(grid)
    fig, ax = plt.subplots()
    cmesh = ax.pcolormesh(
        xi, yi, grid.T, cmap="inferno_r", shading="auto", vmin=vmin, vmax=vmax
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # divider = make_axes_locatable(axes)
    # cax = divider.append_axes("right", size="5%", pad=0.3)
    plt.colorbar(cmesh)
    if equal:
        ax.set_aspect("equal")
    
    if title is not None:
        ax.set_title(title)

    if save_path is not None:
        fig.savefig(save_path)
        plt.close()
    else:
        plt.show()


def compute_grid_count(x, y, x_min, x_max, n_x, y_min, y_max, n_y):
    grid = np.zeros((n_x, n_y))
    cell_size_x = (x_max - x_min) / n_x
    cell_size_y = (y_max - y_min) / n_y

    cells_x = np.ceil((x - x_min) / cell_size_x).astype("int")
    cells_y = np.ceil((y - y_min) / cell_size_y).astype("int")

    # remove date outside the range of interest
    in_roi = np.logical_and(
        np.logical_and(
            cells_x >= 0,
            cells_x < n_x,
        ),
        np.logical_and(
            cells_y >= 0,
            cells_y < n_y,
        ),
    )
    cells_x = cells_x[in_roi]
    cells_y = cells_y[in_roi]

    for cell_x, cell_y in zip(cells_x, cells_y):
        grid[cell_x, cell_y] += 1
    grid /= np.max(grid)
    return grid


def get_bins(vmin, vmax, n_bins):
    bin_size = (vmax - vmin) / n_bins
    pdf_edges = np.linspace(vmin, vmax, n_bins + 1)
    bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])
    return bin_size, pdf_edges, bin_centers
