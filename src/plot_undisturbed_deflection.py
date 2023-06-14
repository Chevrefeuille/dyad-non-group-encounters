from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from parameters import *
from utils import *
import numpy as np

""" The goal of this script is to plot the deflection of pedestrians in the corridor environment
    """

LIMITS = {
    "straightness_index": [0.975, 1],
    "sinuosity": [0, 0.0062],
    "maximum_scaled_lateral_deviation": [0.02, 0.06],
}

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:
        env_name_short = env_name.split(":")[0]

        days = get_all_days(env_name)
        deflections = pickle_load(
            f"../data/pickle/deflection_without_interaction_{env_name_short}.pkl"
        )

        for measure in DEFLECTION_MEASURES:
            deflections_per_length_group = []
            deflections_per_length_group_members = []
            deflections_per_length_non_group = []
            for segment_length in SEGMENT_LENGTHS:
                all_deflections_group = deflections["group"][measure][segment_length]
                all_deflections_group_members = deflections["group_members"][measure][
                    segment_length
                ]
                all_deflections_non_group = deflections["non_group"][measure][
                    segment_length
                ]
                deflections_per_length_group += [np.nanmean(all_deflections_group)]
                deflections_per_length_group_members += [
                    np.nanmean(all_deflections_group_members)
                ]
                deflections_per_length_non_group += [
                    np.nanmean(all_deflections_non_group)
                ]
            plt.plot(SEGMENT_LENGTHS, deflections_per_length_group, label="group")
            plt.plot(
                SEGMENT_LENGTHS,
                deflections_per_length_group_members,
                label="group_members",
            )
            plt.plot(
                SEGMENT_LENGTHS, deflections_per_length_non_group, label="non group"
            )
            plt.ylim(LIMITS[measure])
            plt.title(measure)
            plt.legend()
            # plt.show()

            plt.savefig(
                f"../data/figures/deflection/{env_name_short}_{measure}_no_interaction.png"
            )
            plt.clf()
