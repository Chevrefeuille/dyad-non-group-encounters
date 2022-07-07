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

    for env_name in ["atc", "diamor"]:
        # print(f"- {env_name}")
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = DAYS_ATC if env_name == "atc" else DAYS_DIAMOR
        soc_binding_type = "soc_rel" if env_name == "atc" else "interaction"
        soc_binding_names = (
            SOCIAL_RELATIONS_EN if env_name == "atc" else INTENSITIES_OF_INTERACTION_NUM
        )
        soc_binding_values = [0, 1, 2, 3, 4] if env_name == "atc" else [0, 1, 2, 3]

        encounters = pickle_load(f"../data/pickle/opposite_encounters_{env_name}.pkl")
        pair_distribution_without_interaction = pickle_load(
            f"../data/pickle/pair_distribution_without_interaction_{env_name}.pkl"
        )

        bin_size = (
            PAIR_DISTRIBUTION_MAX - PAIR_DISTRIBUTION_MIN
        ) / N_BINS_PAIR_DISTRIBUTION
        pdf_edges = np.linspace(
            PAIR_DISTRIBUTION_MIN, PAIR_DISTRIBUTION_MAX, N_BINS_PAIR_DISTRIBUTION + 1
        )
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        relative_orientation = {}

        for day in days:

            threshold_v = Threshold("v", min=500, max=3000)  # velocity in [0.5; 3]m/s
            threshold_d = Threshold("d", min=5000)  # walk at least 5 m
            thresholds = [threshold_v, threshold_d]

            # threshold on the distance between the group members, max 2 m
            threshold_delta = Threshold("delta", max=2000)

            # corridor threshold for ATC
            if env_name == "atc":
                threshold_corridor_x = Threshold("x", 5000, 48000)
                threshold_corridor_y = Threshold("y", -27000, 8000)
                thresholds += [threshold_corridor_x, threshold_corridor_y]

            non_groups = env.get_pedestrians(days=[day], thresholds=thresholds)

            groups = env.get_groups(
                size=2,
                days=[day],
                ped_thresholds=thresholds,
                group_thresholds=[threshold_delta],
                with_social_binding=True,
            )

            for group in tqdm(groups):
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()
                group_members_id = [m.get_id() for m in group.get_members()]

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding is None:
                    continue

                if soc_binding not in relative_orientation:
                    relative_orientation[soc_binding] = []

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

                    rel_orientation = compute_relative_orientation(
                        traj_A, traj_B
                    )

                    relative_orientation[soc_binding] += list(rel_orientation)

        pickle_save(
            f"../data/pickle/group_relative_orientation_with_interaction_{env_name}.pkl",
            relative_orientation,
        )
