from email import header
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
import matplotlib.pyplot as plt

import scipy.stats as stats

""" The goal of this script is to print a table with the mean and standard deviation of the deflection angle for each social value.
    The deflection angle is the angle between the direction of the group and the direction of the third pedestrian.
    The deflection angle is computed at the time of the closest encounter between the group and the third pedestrian.
    """

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        env_name_short = env_name.split(":")[0]

        deflections_with_interaction = pickle_load(
            f"../data/pickle/deflection_with_interaction_{env_name_short}_all.pkl"
        )
        deflections_without_interaction_segment = pickle_load(
            f"../data/pickle/deflection_without_interaction_{env_name_short}.pkl"
        )
        deflections_without_interaction_random = pickle_load(
            f"../data/pickle/deflection_without_interaction_{env_name_short}_random.pkl"
        )
        lengths_without_interaction_random = pickle_load(
            f"../data/pickle/length_trajectory_without_interaction_{env_name_short}_random.pkl"
        )
        lengths_with_interaction = pickle_load(
            f"../data/pickle/length_trajectory_with_interaction_{env_name_short}_all.pkl"
        )

        header = (
            "|  | $I$ | $S$ | $\\bar{\epsilon}$ |\n| -- | --- | --- | ------------- |"
        )

        print(f"#### {env_name_short.upper()}")
        for group_non_group in ["group_members", "non_group"]:
            print(f"- {group_non_group.replace('_', ' ')}")
            print(header)
            line_segment = "| Baseline (segment)"
            line_random = "| Baseline (random)"
            for measure in DEFLECTION_MEASURES:
                deflections_baseline_segment = (
                    deflections_without_interaction_segment[group_non_group][measure][
                        3000
                    ]
                    + deflections_without_interaction_segment[group_non_group][measure][
                        4000
                    ]
                )
                mean_deflection = round(np.nanmean(deflections_baseline_segment), 3)
                std_deflection = round(np.nanstd(deflections_baseline_segment), 3)
                line_segment += f"| {mean_deflection} ({std_deflection}) "

                # print(deflections_without_interaction_random[group_non_group][measure])
                lengths = np.array(
                    lengths_without_interaction_random[group_non_group]["gross"]
                )
                deflections = np.array(
                    deflections_without_interaction_random[group_non_group][measure]
                )
                deflections = deflections[
                    np.logical_and(lengths > TRAJ_SIZE_MIN, lengths < TRAJ_SIZE_MAX)
                ]
                mean_deflection_random = round(np.nanmean(deflections), 3)
                std_deflection_random = round(np.nanstd(deflections), 3)
                line_random += f"| {mean_deflection_random} ({std_deflection_random}) "

            line_segment += " |"
            line_random += " |"
            # print(line_segment)
            # print(line_random)

            for i in soc_binding_values:
                line = f"| {soc_binding_names[i]} "
                for measure in DEFLECTION_MEASURES:
                    deflections = np.array(
                        deflections_with_interaction["opposite"][i][measure][
                            group_non_group
                        ]
                    )
                    lengths = np.array(
                        lengths_with_interaction["opposite"][i][group_non_group][
                            "gross"
                        ]
                    )
                    deflections = deflections[
                        np.logical_and(lengths > TRAJ_SIZE_MIN, lengths < TRAJ_SIZE_MAX)
                    ]
                    mean_deflection = round(np.nanmean(deflections), 3)
                    std_deflection = round(np.nanstd(deflections), 3)
                    line += f"| {mean_deflection} ({std_deflection}) "
                line += " |"
                print(line)
        print()

        print("ANOVA")
        print("----- ALL ------")
        for measure in DEFLECTION_MEASURES:
            print(f"-> {measure}")
            for group_non_group in ["group_members", "non_group"]:

                all_deflections = []
                for i in soc_binding_values:
                    all_deflections += [
                        deflections_with_interaction["opposite"][i][measure][
                            group_non_group
                        ]
                    ]
                F, p = stats.f_oneway(*all_deflections)
                print(f"  - {group_non_group.replace('_', ' ')}: {F}, {p}")
        print("----- Pairwise ------")
        header = (
            "| | "
            + " | ".join([soc_binding_names[i] for i in soc_binding_values])
            + " |"
        )
        for measure in DEFLECTION_MEASURES:
            print(measure)
            for group_non_group in ["group_members", "non_group"]:
                print(f"- {group_non_group.replace('_', ' ')}")
                print(header)
                for i in soc_binding_values:
                    line = f"| {soc_binding_names[i]} |"
                    deflections_i = np.array(
                        deflections_with_interaction["opposite"][i][measure][
                            group_non_group
                        ]
                    )
                    deflections_i = deflections_i[~np.isnan(deflections_i)]
                    for j in soc_binding_values:
                        if i >= j:
                            line += " - |"
                            continue

                        deflections_j = np.array(
                            deflections_with_interaction["opposite"][j][measure][
                                group_non_group
                            ]
                        )
                        deflections_j = deflections_j[~np.isnan(deflections_j)]

                        t, p = stats.ttest_ind(
                            deflections_i,
                            deflections_j,
                        )
                        line += f" {round(p,3)} |"
                    print(line)

                # print(soc_binding_names[i], soc_binding_names[j], round(p, 3))
