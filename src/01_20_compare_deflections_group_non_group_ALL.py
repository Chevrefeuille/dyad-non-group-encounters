from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
import matplotlib.pyplot as plt

import scipy.stats as stats


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        env_name_short = env_name.split(":")[0]

        deflections = pickle_load(
            f"../data/pickle/deflection_all_{env_name_short}_random.pkl"
        )

        lengths = pickle_load(
            f"../data/pickle/length_trajectory_all_{env_name_short}_random.pkl"
        )

        for measure in DEFLECTION_MEASURES:
            bin_size = (
                DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["max"]
                - DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["min"]
            ) / DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["n_bins"]
            pdf_edges = np.linspace(
                DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["min"],
                DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["max"],
                DEFLECTIONS_DISTRIBUTIONS_PARAMETERS[measure]["n_bins"] + 1,
            )
            bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])
            fig, ax = plt.subplots()
            for group_non_group in ["non_group", "group_members"]:
                hist = np.histogram(
                    np.array(deflections[group_non_group][measure]), pdf_edges
                )[0]
                pdf = hist / np.sum(hist) / bin_size
                ax.plot(bin_centers, pdf, label=group_non_group)

            # ax.set_title(measure)
            ax.set_xlabel(measure)
            ax.set_ylabel(f"p({measure})")
            ax.legend()
            fig.savefig(
                f"../data/figures/deflection/group_non_group/{env_name_short}_distribution_{measure}.png"
            )
            # plt.show()

        for measure in DEFLECTION_MEASURES:
            fig, ax = plt.subplots()
            plot_deflections = []
            for group_non_group in ["non_group", "group_members"]:
                plot_deflections += [np.array(deflections[group_non_group][measure])]

            ax.boxplot(plot_deflections, labels=["non_group", "group_members"], sym="")
            ax.set_title(f"{measure}-{env_name_short}")
            # ax.set_xlim([2000, 5000])
            # ax.set_ylim(LIMITS[measure])
            # plt.show()
            # fig.savefig(
            #     f"../data/figures/deflection/group_non_group/{env_name_short}_{measure}.png"
            # )
            plt.close()

            # compute ANOVAs

        print(f"#### {env_name_short.upper()}")
        # print("|  | Group | Non group | F | p | \n| -- | -- | --- | -- | -- |")
        print("|  | Group | Non group | \n| -- | -- | ---  |")

        for measure in DEFLECTION_MEASURES:
            plot_deflections = []
            for group_non_group in ["non_group", "group_members"]:
                lengths_g = np.array(lengths[group_non_group]["gross"])
                deflections_g = np.array(deflections[group_non_group][measure])
                deflections_g = deflections_g[
                    np.logical_and(lengths_g > TRAJ_SIZE_MIN, lengths_g < TRAJ_SIZE_MAX)
                ]
                plot_deflections += [deflections_g]

            F, p = stats.f_oneway(
                plot_deflections[0],
                plot_deflections[1],
            )

            F = round(F, 2)

            mean_non_group = round(np.nanmean(plot_deflections[0]), 3)
            std_non_group = round(np.nanstd(plot_deflections[0]), 3)
            mean_group = round(np.nanmean(plot_deflections[1]), 3)
            std_group = round(np.nanstd(plot_deflections[1]), 3)

            # line = f"| {measure} | {mean_group} (±{std_group})| {mean_non_group} (±{std_non_group}) | {F} | {p} |"
            line = f"| {measure} | {mean_group} (±{std_group})| {mean_non_group} (±{std_non_group}) |"
            print(line)
