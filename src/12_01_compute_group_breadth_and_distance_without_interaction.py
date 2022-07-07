from copy import deepcopy
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from parameters import *
from utils import *

import random as rnd
from tqdm import tqdm

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )
        env_name_short = env_name.split(":")[0]

        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )
        days = get_all_days(env_name)

        thresholds_indiv = get_pedestrian_thresholds(env_name)
        thresholds_groups = get_groups_thresholds()

        times_undisturbed = pickle_load(
            f"../data/pickle/undisturbed_times_{env_name_short}.pkl"
        )

        breadths = {}
        distances = {}

        non_groups_by_day = env.get_pedestrians_grouped_by(
            "day", thresholds=thresholds_indiv, sampling_time=500, no_groups=True
        )

        groups_by_day = env.get_groups_grouped_by(
            "day",
            size=2,
            ped_thresholds=thresholds_indiv,
            group_thresholds=thresholds_groups,
            with_social_binding=True,
            sampling_time=500,
        )

        n_non_groups = 10
        n_samples = 100

        for day1 in tqdm(groups_by_day):
            groups = groups_by_day[day1]
            for group in groups:
                group_breadth = group.get_interpersonal_distance()
                group_as_indiv = group.get_as_individual()
                soc_binding = group.get_annotation(soc_binding_type)

                if soc_binding not in breadths:
                    breadths[soc_binding] = []
                    distances[soc_binding] = []

                group_traj = group_as_indiv.get_trajectory()
                for day2 in non_groups_by_day:
                    if day2 == day1:
                        continue

                    non_groups = non_groups_by_day[day2]

                    sample_non_groups = rnd.sample(non_groups, n_non_groups)

                    for non_group in sample_non_groups:
                        non_group_traj = non_group.get_trajectory()

                        n_rand = min(n_samples, len(group_traj), len(non_group_traj))
                        random_idx_group = np.random.choice(
                            len(group_traj), size=n_rand, replace=False
                        )
                        sample_traj_group = group_traj[random_idx_group, :]
                        sample_breadth_group = group_breadth[random_idx_group]

                        random_idx_non_group = np.random.choice(
                            len(non_group_traj), size=n_rand, replace=False
                        )
                        sample_traj_non_group = non_group_traj[random_idx_non_group, :]

                        d = compute_interpersonal_distance(
                            sample_traj_group[:, 1:3], sample_traj_non_group[:, 1:3]
                        )

                        # plot_static_2D_trajectories(
                        #     [sample_traj_group, sample_traj_non_group], boundaries=env.boundaries
                        # )

                        breadths[soc_binding] += list(sample_breadth_group)
                        distances[soc_binding] += list(d)

        pickle_save(
            f"../data/pickle/group_breadth_without_interaction_diff_days_{env_name_short}.pkl",
            breadths,
        )
        pickle_save(
            f"../data/pickle/group_non_group_distance_without_interaction_diff_days_{env_name_short}.pkl",
            distances,
        )
