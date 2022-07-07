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

        deflections_with_interaction = pickle_load(
            f"../data/pickle/deflection_with_interaction_{env_name_short}.pkl"
        )
        deflections_without_interaction = pickle_load(
            f"../data/pickle/deflection_without_interaction_{env_name_short}_random.pkl"
        )
        lengths_with_interaction = pickle_load(
            f"../data/pickle/length_trajectory_with_interaction_{env_name_short}.pkl"
        )
        lengths_without_interaction = pickle_load(
            f"../data/pickle/length_trajectory_without_interaction_{env_name_short}_random.pkl"
        )

        print(f"#### {env_name_short.upper()}")

        print("|  | Group | Non group | F | p | \n| -- | -- | --- | -- | -- |")
        for measure in DEFLECTION_MEASURES:
            fig, ax = plt.subplots()
            plot_deflections = []
            for group_non_group in ["non_group", "group_members"]:
                # baseline_lengths = np.array(
                #     lengths_without_interaction[group_non_group]["net"]
                # )
                # baseline_deflection = np.array(
                #     deflections_without_interaction[group_non_group][measure]
                # )
                # baseline_deflection = baseline_deflection[
                #     np.logical_and(
                #         baseline_lengths > TRAJ_SIZE_MIN,
                #         baseline_lengths < TRAJ_SIZE_MAX,
                #     )
                # ]
                # all_deflections += [baseline_deflection]
                # labels += ["baseline"]
                all_deflections = []
                for i in soc_binding_values:
                    lengths = np.array(
                        lengths_with_interaction["opposite"][i][group_non_group]["net"]
                    )
                    deflections = np.array(
                        deflections_with_interaction["opposite"][i][measure][
                            group_non_group
                        ]
                    )
                    # deflections = deflections[
                    #     np.logical_and(lengths > TRAJ_SIZE_MIN, lengths < TRAJ_SIZE_MAX)
                    # ]
                    # deflections = deflections[~np.isnan(deflections)]
                    all_deflections += list(deflections)
                plot_deflections += [all_deflections]

            ax.boxplot(plot_deflections, labels=["non_group", "group_members"], sym="")
            ax.set_title(f"{measure}-{env_name_short}")
            # ax.set_xlim([2000, 5000])
            # ax.set_ylim(LIMITS[measure])
            # plt.show()
            fig.savefig(
                f"../data/figures/deflection/group_non_group/{env_name_short}_{measure}.png"
            )
            plt.close()

            # compute ANOVAs
            F, p = stats.f_oneway(
                plot_deflections[0],
                plot_deflections[1],
            )

            F = round(F, 2)

            mean_non_group = round(np.nanmean(plot_deflections[0]), 3)
            std_non_group = round(np.nanstd(plot_deflections[0]), 3)
            mean_group = round(np.nanmean(plot_deflections[1]), 3)
            std_group = round(np.nanstd(plot_deflections[1]), 3)

            line = f"| {measure} | {mean_group} (±{std_group})| {mean_non_group} (±{std_non_group}) | {F} | {p:.0e} |"
            print(line)
        #     print(f"    {measure} -> {anova}")
        # print()
