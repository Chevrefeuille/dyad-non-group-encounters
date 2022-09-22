from lib2to3.pgen2.token import SLASHEQUAL
from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.trajectory_utils import *

from parameters import *
import matplotlib.pyplot as plt
from tqdm import tqdm

from utils import (
    get_all_days,
    get_groups_thresholds,
    get_pedestrian_thresholds,
    get_social_values,
)

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:
        print(f"- {env_name}")
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        encounters = pickle_load(
            f"../data/pickle/opposite_encounters_{env_name_short}.pkl"
        )

        thresholds_indiv = []
        # ONLY CORRIDOR
        if env_name == "atc:corridor":
            thresholds_indiv += [
                Threshold(
                    "x",
                    BOUNDARIES_ATC_CORRIDOR["xmin"],
                    BOUNDARIES_ATC_CORRIDOR["xmax"],
                )
            ]
            thresholds_indiv += [
                Threshold(
                    "y",
                    BOUNDARIES_ATC_CORRIDOR["ymin"],
                    BOUNDARIES_ATC_CORRIDOR["ymax"],
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

        non_groups = env.get_pedestrians(
            thresholds=thresholds_indiv, sampling_time=500, no_groups=True
        )

        groups = env.get_groups(
            size=2,
            ped_thresholds=thresholds_indiv,
            group_thresholds=[],
            with_social_binding=True,
            sampling_time=500,
        )

        print(len(non_groups), len(groups))

        thresholds_indiv += [Threshold("n", min=16)]

        non_groups = env.get_pedestrians(
            thresholds=thresholds_indiv, sampling_time=500, no_groups=True
        )

        groups = env.get_groups(
            size=2,
            ped_thresholds=thresholds_indiv,
            group_thresholds=[],
            with_social_binding=True,
            sampling_time=500,
        )

        print(len(non_groups), len(groups))

        thresholds_indiv += [
            Threshold("v", min=VEL_MIN, max=VEL_MAX)
        ]  # velocity in [0.5; 3]m/s

        non_groups = env.get_pedestrians(
            thresholds=thresholds_indiv, sampling_time=500, no_groups=True
        )

        groups = env.get_groups(
            size=2,
            ped_thresholds=thresholds_indiv,
            group_thresholds=[],
            with_social_binding=True,
            sampling_time=500,
        )

        print(len(non_groups), len(groups))

        group_thresholds = [
            Threshold("delta", min=GROUP_BREADTH_MIN, max=GROUP_BREADTH_MAX)
        ]

        groups = env.get_groups(
            size=2,
            ped_thresholds=thresholds_indiv,
            group_thresholds=group_thresholds,
            with_social_binding=True,
            sampling_time=500,
        )

        print(len(non_groups), len(groups))
