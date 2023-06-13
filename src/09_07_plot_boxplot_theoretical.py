from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
import matplotlib.pyplot as plt

""" The goal of this script is to plot the distribution of time to collisions for different social bindings.
    The distribution is computed for each social binding and then plotted on the same graph.
    """

if __name__ == "__main__":

    for env_name in ["atc:corridor"]:

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
        deflections_theoretical = pickle_load(
            f"../data/pickle/deflection_theoretical_{env_name_short}.pkl"
        )
        lengths_theoretical = pickle_load(
            f"../data/pickle/length_trajectory_theoretical_{env_name_short}.pkl"
        )

        for measure in DEFLECTION_MEASURES:
            for group_non_group in ["non_group", "group_members"]:
                fig, ax = plt.subplots()
                all_deflections = []
                labels = []

                # for the theoretical baseline
                theoretical_lengths = np.array(lengths_theoretical["net"])
                theoretical_deflection = np.array(deflections_theoretical[measure])
                theoretical_deflection = theoretical_deflection[
                    np.logical_and(
                        theoretical_lengths > TRAJ_SIZE_MIN,
                        theoretical_lengths < TRAJ_SIZE_MAX,
                    )
                ]
                all_deflections += [theoretical_deflection]
                labels += ["theoretical"]

                # for the baseline
                baseline_lengths = np.array(
                    lengths_without_interaction[group_non_group]["net"]
                )
                baseline_deflection = np.array(
                    deflections_without_interaction[group_non_group][measure]
                )
                baseline_deflection = baseline_deflection[
                    np.logical_and(
                        baseline_lengths > TRAJ_SIZE_MIN,
                        baseline_lengths < TRAJ_SIZE_MAX,
                    )
                ]
                all_deflections += [baseline_deflection]
                labels += ["baseline"]

                # for interactions
                for i in soc_binding_values:
                    lengths = np.array(
                        lengths_with_interaction["opposite"][i][group_non_group]["net"]
                    )
                    deflections = np.array(
                        deflections_with_interaction["opposite"][i][measure][
                            group_non_group
                        ]
                    )
                    deflections = deflections[
                        np.logical_and(lengths > TRAJ_SIZE_MIN, lengths < TRAJ_SIZE_MAX)
                    ]
                    deflections = deflections[~np.isnan(deflections)]
                    all_deflections += [deflections]
                    labels += [soc_binding_names[i]]

                ax.boxplot(all_deflections, labels=labels, sym="")

                ax.set_title(f"{measure}-{group_non_group}-{env_name_short}")
                # ax.set_xlim([2000, 5000])
                # ax.set_ylim(LIMITS[measure])
                # plt.show()
                fig.savefig(
                    f"../data/figures/deflection/theoretical/{env_name_short}_{group_non_group}_{measure}.png"
                )
                plt.close()
