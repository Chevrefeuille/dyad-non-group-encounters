from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.trajectory_utils import *

from parameters import *
import matplotlib.pyplot as plt
from tqdm import tqdm

if __name__ == "__main__":

    env = Environment("diamor", data_dir="../../atc-diamor-pedestrians/data/formatted")
    days = DAYS_DIAMOR

    for day in days[1:]:

        threshold_v = Threshold("v", min=500, max=3000)  # velocity in [0.5; 3]m/s
        threshold_d = Threshold("d", min=5000)  # walk at least 5 m
        thresholds = [threshold_v, threshold_d]

        # threshold on the distance between the group members, max 2 m
        threshold_delta = Threshold("delta", max=2000)

        groups = env.get_groups(
            size=2,
            days=[day],
            # ped_thresholds=thresholds,
            group_thresholds=[threshold_delta],
            with_social_binding=True,
        )

        print(len(groups))
        for group in groups:
            group.plot_2D_trajectory(animate=True)
