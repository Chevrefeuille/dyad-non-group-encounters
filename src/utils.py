import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.constants import *
from parameters import *


def get_pedestrian_thresholds(env_name):
    thresholds_indiv = []
    thresholds_indiv += [
        Threshold("v", min=VEL_MIN, max=VEL_MAX)
    ]  # velocity in [0.5; 3]m/s
    # thresholds_indiv += [Threshold("d", min=D_MIN)]  # walk at least 5 m
    thresholds_indiv += [Threshold("n", min=16)]
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
        return "soc_rel", SOCIAL_RELATIONS_EN, [2, 1, 3, 4], COLORS_SOC_REL
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
        print(len(y[bin_ids == k]))
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


def get_mean_std_ste_over_bins(x, y, bin_centers):
    mean_over_bins = []
    std_over_bins = []
    ste_over_bins = []
    bin_ids = np.digitize(x, bin_centers)
    for k in range(len(bin_centers)):
        mean_for_bin = np.nanmean(y[bin_ids == k]) if len(y[bin_ids == k]) else np.nan
        # print(k, y[bin_ids == k])
        mean_over_bins += [mean_for_bin]
        std_for_bin = np.nanstd(y[bin_ids == k]) if len(y[bin_ids == k]) else np.nan
        std_over_bins += [std_for_bin]
        ste_over_bins += [
            std_for_bin / len(y[bin_ids == k]) ** 0.5
            if len(y[bin_ids == k])
            else np.nan
        ]
    return mean_over_bins, std_over_bins, ste_over_bins


def get_mean_std_ste_n_over_bins(x, y, bin_centers):
    mean_over_bins = []
    std_over_bins = []
    ste_over_bins = []
    n_over_bins = []
    bin_ids = np.digitize(x, bin_centers)
    for k in range(len(bin_centers)):
        mean_for_bin = np.nanmean(y[bin_ids == k]) if len(y[bin_ids == k]) else np.nan
        # print(k, y[bin_ids == k])
        mean_over_bins += [mean_for_bin]
        std_for_bin = np.nanstd(y[bin_ids == k]) if len(y[bin_ids == k]) else np.nan
        std_over_bins += [std_for_bin]
        ste_over_bins += [
            std_for_bin / len(y[bin_ids == k]) ** 0.5
            if len(y[bin_ids == k])
            else np.nan
        ]
        n_over_bins += [len(y[bin_ids == k])]
    return mean_over_bins, std_over_bins, ste_over_bins, n_over_bins


def plot_color_map(
    xi,
    yi,
    grid,
    xlabel=None,
    ylabel=None,
    title=None,
    vmin=None,
    vmax=None,
    save_path=None,
    aspect="auto",
    cmap="inferno",
    interpolation=None,
    ax=None,
    fig=None,
    show=True,
):
    if vmin is None:
        vmin = np.min(grid)
    if vmax is None:
        vmax = np.max(grid)
    if ax is None:
        fig, ax = plt.subplots()
    extent = np.min(xi), np.max(xi), np.min(yi), np.max(yi)

    cmesh = ax.imshow(
        np.flip(grid.T),
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        interpolation=interpolation,
        extent=extent,
        aspect=aspect,
    )
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    divider = make_axes_locatable(ax)
    if ax is not None and fig is not None:
        fig.colorbar(cmesh, ax=ax, location="right")
    else:
        cax = divider.append_axes("right", size="5%", pad=0.1)
        plt.colorbar(cmesh, cax=cax)
    # if equal:
    #     ax.set_aspect("equal")

    if title is not None:
        ax.set_title(title)

    if save_path is not None:
        fig.savefig(save_path)
        plt.close()
    if show:
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


def get_grid(min_x, max_x, n_bin_x, min_y, max_y, n_bin_y, n_channels=1):
    grid = np.zeros((n_channels, n_bin_x, n_bin_y))
    xi = np.linspace(min_x, max_x, n_bin_x)
    yi = np.linspace(min_y, max_y, n_bin_y)
    cell_size_x = (max_x - min_x) / n_bin_x
    cell_size_y = (max_y - min_y) / n_bin_y
    return grid, xi, yi, cell_size_x, cell_size_y


def update_grid(
    grid,
    data,
    min_x,
    n_bin_x,
    cell_size_x,
    min_y,
    n_bin_y,
    cell_size_y,
    channel=0,
):
    cell_x_index = np.ceil((data[:, 0] - min_x) / cell_size_x).astype("int")
    cell_y_index = np.ceil((data[:, 1] - min_y) / cell_size_y).astype("int")

    # remove date outside the range of interest
    in_roi = np.logical_and(
        np.logical_and(cell_x_index >= 0, cell_x_index < n_bin_x),
        np.logical_and(cell_y_index >= 0, cell_y_index < n_bin_y),
    )
    cell_x_index = cell_x_index[in_roi]
    cell_y_index = cell_y_index[in_roi]

    grid[channel, cell_x_index, cell_y_index] += 1

    return grid
