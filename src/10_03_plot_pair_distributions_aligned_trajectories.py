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

        # if "atc" in env_name:
        #     soc_binding_values = [1, 2]

        aligned_trajectories_2D_distributions_without_interaction = pickle_load(
            f"../data/pickle/aligned_trajectories_2D_distribution_{env_name_short}_without_interaction.pkl"
        )
        aligned_trajectories_2D_distributions_with_interaction = pickle_load(
            f"../data/pickle/aligned_trajectories_2D_distribution_{env_name_short}_with_interaction.pkl"
        )

        pair_distribution_theta_without_interaction = pickle_load(
            f"../data/pickle/aligned_trajectories_distribution_theta_without_interaction_{env_name_short}.pkl"
        )

        pair_distribution_theta_with_interaction = pickle_load(
            f"../data/pickle/aligned_trajectories_distribution_theta_with_interaction_{env_name_short}.pkl"
        )

        xi = np.linspace(RX_MIN, RX_MAX, N_BINS_2D_RX) / 1000
        yi = np.linspace(RY_MIN, RY_MAX, N_BINS_2D_RY) / 1000

        # plot 2D pair distributions without interaction
        for i, v in enumerate(soc_binding_values):
            save_path = f"../data/figures/pair_distributions/2D/{env_name_short}_baseline_aligned_trajectories_2D_distribution.png"
            plot_color_map(
                xi,
                yi,
                aligned_trajectories_2D_distributions_without_interaction,
                "x (m)",
                "y (m)",
                vmin=0,
                vmax=1,
                save_path=save_path,
            )

        # plot 2D pair distributions with interaction
        for i, v in enumerate(soc_binding_values):
            grid = aligned_trajectories_2D_distributions_with_interaction[i, ...]
            save_path = f"../data/figures/pair_distributions/2D/{env_name_short}_{soc_binding_names[v]}_aligned_trajectories_2D_distribution.png"
            plot_color_map(
                xi, yi, grid, "x (m)", "y (m)", vmin=0, vmax=1, save_path=save_path
            )

        # plot differences
        for i, v1 in enumerate(soc_binding_values):
            grid1 = aligned_trajectories_2D_distributions_with_interaction[i, ...]
            smoothed_grid1 = gaussian_filter(grid1, sigma=2)
            for j, v2 in enumerate(soc_binding_values):
                if j <= i:
                    continue
                grid2 = aligned_trajectories_2D_distributions_with_interaction[j, ...]
                smoothed_grid2 = gaussian_filter(grid2, sigma=2)
                diff = smoothed_grid1 - smoothed_grid2
                save_path = f"../data/figures/pair_distributions/2D/{env_name_short}_diff_{soc_binding_names[v1]}_{soc_binding_names[v2]}_aligned_trajectories_2D_distribution.png"
                plot_color_map(
                    xi,
                    yi,
                    diff,
                    "x (m)",
                    "y (m)",
                    title=f"{soc_binding_names[v1]}-{soc_binding_names[v2]}",
                    vmin=-0.5,
                    vmax=0.5,
                    save_path=save_path,
                )

        # plot smoothed 2D pair distributions with interaction
        for i, v in enumerate(soc_binding_values):
            grid = aligned_trajectories_2D_distributions_with_interaction[i, ...]
            smoothed_grid = gaussian_filter(grid, sigma=2)
            save_path = f"../data/figures/pair_distributions/2D/{env_name_short}_smoothed_{soc_binding_names[v]}_aligned_trajectories_2D_distribution.png"
            plot_color_map(
                xi,
                yi,
                smoothed_grid,
                "x (m)",
                "y (m)",
                title=soc_binding_names[v],
                vmin=0,
                vmax=1,
                save_path=save_path,
            )

        # plot 2D pair distributions with interaction scaled by pair distribution without interaction
        for i, v in enumerate(soc_binding_values):
            grid = (
                aligned_trajectories_2D_distributions_with_interaction[i, ...]
                / aligned_trajectories_2D_distributions_without_interaction
            )
            save_path = f"../data/figures/pair_distributions/2D/{env_name_short}_pair_{soc_binding_names[v]}_aligned_trajectories_2D.png"
            plot_color_map(
                xi, yi, grid, "x (m)", "y (m)", vmin=0, vmax=2, save_path=save_path
            )

        # plot integrated distribution (over x)
        fig, ax = plt.subplots()
        grid = aligned_trajectories_2D_distributions_without_interaction
        x_integration = np.sum(grid, axis=1)
        x_integration /= np.sum(x_integration)
        ax.plot(xi, x_integration, linewidth=3, label="no interaction")

        for i, v in enumerate(soc_binding_values):
            grid = aligned_trajectories_2D_distributions_with_interaction[i, ...]
            x_integration = np.sum(grid, axis=1)
            x_integration /= np.sum(x_integration)
            ax.plot(
                xi,
                x_integration,
                label=soc_binding_names[v],
                linewidth=3,
            )
        ax.legend()
        ax.grid()
        ax.set_title(f"Distribution for x ({env_name_short})")
        fig.savefig(
            f"../data/figures/pair_distributions/{env_name_short}_aligned_trajectories_x_distribution.png"
        )
        plt.close()
        # plt.show()

        # plot integrated distribution (over y)
        fig, ax = plt.subplots()
        grid = aligned_trajectories_2D_distributions_without_interaction
        y_integration = np.sum(grid, axis=0)
        y_integration /= np.sum(y_integration)
        ax.plot(yi, y_integration, linewidth=3, label="no interaction")

        for i, v in enumerate(soc_binding_values):
            grid = aligned_trajectories_2D_distributions_with_interaction[i, ...]
            y_integration = np.sum(grid, axis=0)
            y_integration /= np.sum(y_integration)
            ax.plot(
                yi,
                y_integration,
                label=soc_binding_names[v],
                linewidth=3,
            )
        ax.legend()
        ax.set_title(f"Pair distribution for y ({env_name_short})")
        ax.grid()
        fig.savefig(
            f"../data/figures/pair_distributions/{env_name_short}_aligned_trajectories_y_distribution.png"
        )
        plt.close()

        # plot pair integrated distribution (over x)
        fig, ax = plt.subplots()
        for i, v in enumerate(soc_binding_values):
            x_integration_with_interaction = np.sum(
                aligned_trajectories_2D_distributions_with_interaction[i, ...], axis=1
            )
            x_integration_with_interaction /= np.sum(x_integration_with_interaction)
            x_integration_without_interaction = np.sum(
                aligned_trajectories_2D_distributions_without_interaction, axis=1
            )
            x_integration_without_interaction /= np.sum(
                x_integration_without_interaction
            )
            ax.plot(
                xi,
                x_integration_with_interaction / x_integration_without_interaction,
                label=soc_binding_names[v],
                linewidth=3,
            )
        ax.legend()
        ax.grid()
        ax.set_title(f"Pair distribution for x ({env_name_short})")
        fig.savefig(
            f"../data/figures/pair_distributions/{env_name_short}_aligned_trajectories_x_pair_distribution.png"
        )
        plt.close()
        # plt.show()

        # plot pair integrated distribution (over y)
        fig, ax = plt.subplots()
        for i, v in enumerate(soc_binding_values):
            y_integration_with_interaction = np.sum(
                aligned_trajectories_2D_distributions_with_interaction[i, ...], axis=0
            )
            y_integration_with_interaction /= np.sum(y_integration_with_interaction)
            y_integration_without_interaction = np.sum(
                aligned_trajectories_2D_distributions_without_interaction, axis=0
            )
            y_integration_without_interaction /= np.sum(
                y_integration_without_interaction
            )
            ax.plot(
                yi,
                y_integration_with_interaction / y_integration_without_interaction,
                label=soc_binding_names[v],
                linewidth=3,
            )
        ax.legend()
        ax.grid()
        ax.set_title(f"Pair distribution for y ({env_name_short})")
        fig.savefig(
            f"../data/figures/pair_distributions/{env_name_short}_aligned_trajectories_y_pair_distribution.png"
        )
        plt.close()

        # plot theta pair distribution
        # fig, ax = plt.subplots()
        # for i in soc_binding_values:
        #     ax.plot(
        #         pair_distribution_theta_without_interaction[0],
        #         pair_distribution_theta_with_interaction[i]
        #         / pair_distribution_theta_without_interaction[1],
        #         linewidth=3,
        #         label=soc_binding_names[i],
        #     )
        # ax.set_title(f"Pair distribution for theta ({env_name_short})")
        # ax.legend()
        # # plt.show()
        # fig.savefig(
        #     f"../data/figures/pair_distributions/{env_name_short}_aligned_trajectories_theta_pair_distribution.png"
        # )
        # plt.close()
