from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.trajectory_utils import *

from parameters import *
from utils import *
import matplotlib.pyplot as plt
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

        encounters = pickle_load(
            f"../data/pickle/opposite_encounters_{env_name_short}.pkl"
        )

        breadths = {}
        distances = {}

        for day in days:

            non_groups = env.get_pedestrians(
                days=[day], thresholds=thresholds_indiv, sampling_time=500
            )

            groups = env.get_groups(
                size=2,
                days=[day],
                ped_thresholds=thresholds_indiv,
                group_thresholds=thresholds_groups,
                with_social_binding=True,
                sampling_time=500,
            )

            for group in tqdm(groups):
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()
                group_members_id = [m.get_id() for m in group.get_members()]

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding is None:
                    continue

                if soc_binding not in breadths:
                    breadths[soc_binding] = []
                    distances[soc_binding] = []

                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    non_groups, proximity_threshold=None, skip=group_members_id
                )

                if not group_encounters:
                    continue

                for non_group in group_encounters:

                    non_group_id = non_group.get_id()

                    trajectories = [
                        group_members[0].get_trajectory(),
                        group_members[1].get_trajectory(),
                        group_as_indiv.get_trajectory(),
                        non_group.get_trajectory(),
                    ]
                    [
                        traj_A,
                        traj_B,
                        traj_group,
                        traj_non_group,
                    ] = compute_simultaneous_observations(trajectories)

                    relative_direction = compute_relative_direction(
                        group_as_indiv.get_trajectory(), non_group.get_trajectory()
                    )

                    if relative_direction != "opposite":
                        continue

                    delta = compute_interpersonal_distance(
                        traj_A[:, 1:3], traj_B[:, 1:3]
                    )

                    d_G_NG = compute_interpersonal_distance(traj_group, traj_non_group)

                    # print(np.min(d_G_NG / delta))
                    # if np.min(d_G_NG / delta) < 1:
                    #     plot_animated_2D_trajectories(
                    #         [traj_A, traj_B, traj_non_group],
                    #         title=soc_binding_names[soc_binding],
                    #         boundaries=env.boundaries,
                    #     )

                    breadths[soc_binding] += list(delta)
                    distances[soc_binding] += list(d_G_NG)

        pickle_save(
            f"../data/pickle/group_breadth_with_interaction_{env_name_short}.pkl",
            breadths,
        )
        pickle_save(
            f"../data/pickle/group_non_group_distance_with_interaction_{env_name_short}.pkl",
            distances,
        )
