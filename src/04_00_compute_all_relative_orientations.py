from copy import deepcopy
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from parameters import *

from tqdm import tqdm

if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = DAYS_ATC if env_name == "atc" else DAYS_DIAMOR
        soc_binding_type = "soc_rel" if env_name == "atc" else "interaction"
        soc_binding_names = (
            SOCIAL_RELATIONS_EN if env_name == "atc" else INTENSITIES_OF_INTERACTION_NUM
        )
        soc_binding_values = [0, 1, 2, 3, 4] if env_name == "atc" else [0, 1, 2, 3]

        relative_orientation = {}

        for day in days:
            # print(f"Day {day}:")
            threshold_v = Threshold("v", min=500, max=3000)  # velocity in [0.5; 3]m/s
            threshold_d = Threshold("d", min=5000)  # walk at least 5 m
            thresholds_indiv = [threshold_v, threshold_d]

            # corridor threshold for ATC
            if env_name == "atc":
                threshold_corridor_x = Threshold("x", 5000, 48000)
                threshold_corridor_y = Threshold("y", -27000, 8000)
                thresholds_indiv += [threshold_corridor_x, threshold_corridor_y]

            # threshold on the distance between the group members, max 4 m
            threshold_delta = Threshold("delta", max=4000)

            non_groups = env.get_pedestrians(
                days=[day], no_groups=True, thresholds=thresholds_indiv
            )

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_indiv,
                group_thresholds=[threshold_delta],
                with_social_binding=True,
            )

            for group in groups:
                group_id = group.get_id()

                soc_binding = group.get_annotation(soc_binding_type)

                if soc_binding not in relative_orientation:
                    relative_orientation[soc_binding] = []

                rel_orientation = group.get_relative_orientation()
                relative_orientation[soc_binding] += list(rel_orientation)

        pickle_save(
            f"../data/pickle/group_relative_orientation_{env_name}.pkl",
            relative_orientation,
        )
