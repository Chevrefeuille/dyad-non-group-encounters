from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.trajectory_utils import *

from parameters import *
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

""" The goal of this script is to find intrusions of non-group pedestrians into the groups in the corridor environment.
    The intrusions are defined as the non-group pedestrians that are closer than 4 m to the group members.
    """


if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:
        # print(f"- {env_name}")
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = DAYS_ATC if env_name == "atc" else DAYS_DIAMOR
        soc_binding_type = "soc_rel" if env_name == "atc" else "interaction"
        soc_binding_values = (
            SOCIAL_RELATIONS_EN if env_name == "atc" else INTENSITIES_OF_INTERACTION_NUM
        )

        encounters = pickle_load(f"../data/pickle/opposite_encounters_{env_name}.pkl")

        for day in days:
            # print(f"  - day {day}:")

            group_ids = list(encounters[day].keys())
            non_group_ids = list(
                set(
                    [
                        ped_id
                        for non_groups in encounters[day].values()
                        for ped_id in non_groups
                    ]
                )
            )
            threshold_v = Threshold("v", min=500, max=3000)  # velocity in [0.5; 3]m/s
            threshold_d = Threshold("d", min=5000)  # walk at least 5 m
            thresholds = [threshold_v, threshold_d]

            # threshold on the distance between the group members, max 4 m
            threshold_delta = Threshold("delta", max=4000)

            # corridor threshold for ATC
            if env_name == "atc":
                threshold_corridor_x = Threshold("x", 5000, 48000)
                threshold_corridor_y = Threshold("y", -27000, 8000)
                thresholds += [threshold_corridor_x, threshold_corridor_y]

            non_groups = env.get_pedestrians(
                days=[day], ids=non_group_ids, thresholds=thresholds
            )
            non_groups_dict = {p.get_id(): p for p in non_groups}

            groups = env.get_groups(
                size=2,
                days=[day],
                ids=group_ids,
                ped_thresholds=thresholds,
                group_thresholds=[threshold_delta],
            )

            for group in groups:
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding is None:
                    continue

                group_encounters_id = encounters[day][group_id]
                group_encounters = [
                    non_groups_dict[ped_id]
                    for ped_id in group_encounters_id
                    if ped_id in non_groups_dict
                ]

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

                    pos_A = traj_A[:, 1:3]
                    pos_B = traj_B[:, 1:3]
                    pos_group = traj_group[:, 1:3]
                    pos_non_group = traj_non_group[:, 1:3]

                    d_G_NG = np.linalg.norm(pos_group - pos_non_group, axis=1)

                    traj_A_encounter = traj_A[d_G_NG < VICINITY]
                    traj_B_encounter = traj_B[d_G_NG < VICINITY]
                    traj_group_encounter = traj_group[d_G_NG < VICINITY]
                    traj_non_group_encounter = traj_non_group[d_G_NG < VICINITY]
                    pos_A_encounter = pos_A[d_G_NG < VICINITY]
                    pos_B_encounter = pos_B[d_G_NG < VICINITY]
                    pos_group_encounter = pos_group[d_G_NG < VICINITY]
                    pos_non_group_encounter = pos_non_group[d_G_NG < VICINITY]

                    if len(pos_group_encounter) < 1:
                        continue

                    d_G_NG_encounter = compute_interpersonal_distance(
                        pos_group_encounter, pos_non_group_encounter
                    )

                    breadth_encounter = compute_interpersonal_distance(
                        pos_A_encounter, pos_B_encounter
                    )

                    d_AN = compute_interpersonal_distance(
                        pos_A_encounter, pos_non_group_encounter
                    )

                    d_BN = compute_interpersonal_distance(
                        pos_B_encounter, pos_non_group_encounter
                    )

                    diff = np.abs(d_AN + d_BN - breadth_encounter)

                    if np.min(diff) <= 400:
                        plot_animated_2D_trajectories(
                            [
                                traj_A,
                                traj_B,
                                traj_non_group,
                            ]
                        )

                    # plt.plot(diff)
                    # plt.show()
