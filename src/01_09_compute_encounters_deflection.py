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

""" The goal of this script is to compute the deflection angle between two pedestrians in a group and a third pedestrian.
    The deflection angle is the angle between the direction of the group and the direction of the third pedestrian.
    The deflection angle is computed at the time of the closest encounter between the group and the third pedestrian.
    
    """

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:
        # print(f"- {env_name}")
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

        deflections = {}
        lengths = {}

        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        for day in days:

            non_groups = env.get_pedestrians(
                days=[day], thresholds=thresholds_ped, sampling_time=500
            )

            groups = env.get_groups(
                size=2,
                days=[day],
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
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

                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    non_groups,
                    proximity_threshold=4000,
                    skip=group_members_id,
                    alone=None,
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

                    if relative_direction not in deflections:
                        deflections[relative_direction] = {}
                        lengths[relative_direction] = {}

                    if soc_binding not in deflections[relative_direction]:
                        deflections[relative_direction][soc_binding] = {}
                        lengths[relative_direction][soc_binding] = {
                            "group": {"net": [], "gross": []},
                            "non_group": {"net": [], "gross": []},
                            "group_members": {"net": [], "gross": []},
                        }

                    pos_A = traj_A[:, 1:3]
                    pos_B = traj_B[:, 1:3]
                    pos_group = traj_group[:, 1:3]
                    pos_non_group = traj_non_group[:, 1:3]

                    d_G_NG = compute_interpersonal_distance(pos_group, pos_non_group)

                    traj_A_encounter = traj_A[d_G_NG < VICINITY]
                    traj_B_encounter = traj_B[d_G_NG < VICINITY]
                    traj_group_encounter = traj_group[d_G_NG < VICINITY]
                    traj_non_group_encounter = traj_non_group[d_G_NG < VICINITY]
                    pos_A_encounter = pos_A[d_G_NG < VICINITY]
                    pos_B_encounter = pos_B[d_G_NG < VICINITY]
                    pos_group_encounter = pos_group[d_G_NG < VICINITY]
                    pos_non_group_encounter = pos_non_group[d_G_NG < VICINITY]

                    if len(pos_group_encounter) <= N_POINTS_MIN_VICINITY:
                        continue

                    # plot_animated_2D_trajectories(
                    #     [traj_A_encounter, traj_B_encounter, traj_non_group_encounter],
                    #     boundaries=env.boundaries,
                    # )

                    lengths[relative_direction][soc_binding]["group"]["net"] += [
                        compute_net_displacement(pos_group_encounter)
                    ]
                    lengths[relative_direction][soc_binding]["group_members"][
                        "net"
                    ] += [compute_net_displacement(pos_A_encounter)] + [
                        compute_net_displacement(pos_B_encounter)
                    ]
                    lengths[relative_direction][soc_binding]["non_group"]["net"] += [
                        compute_net_displacement(pos_non_group_encounter)
                    ]

                    lengths[relative_direction][soc_binding]["group"]["gross"] += [
                        compute_gross_displacement(pos_group_encounter)
                    ]
                    lengths[relative_direction][soc_binding]["group_members"][
                        "gross"
                    ] += [compute_gross_displacement(pos_A_encounter)] + [
                        compute_gross_displacement(pos_B_encounter)
                    ]
                    lengths[relative_direction][soc_binding]["non_group"]["gross"] += [
                        compute_gross_displacement(pos_non_group_encounter)
                    ]

                    for measure in DEFLECTION_MEASURES:
                        if measure not in deflections[relative_direction][soc_binding]:
                            deflections[relative_direction][soc_binding][measure] = {
                                "group": [],
                                "non_group": [],
                                "group_members": [],
                            }

                        deflections[relative_direction][soc_binding][measure][
                            "group"
                        ] += [compute_deflection(pos_group_encounter, measure=measure)]
                        deflections[relative_direction][soc_binding][measure][
                            "group_members"
                        ] += [compute_deflection(pos_A_encounter, measure=measure)] + [
                            compute_deflection(pos_B_encounter, measure=measure)
                        ]
                        deflections[relative_direction][soc_binding][measure][
                            "non_group"
                        ] += [
                            compute_deflection(pos_non_group_encounter, measure=measure)
                        ]

        pickle_save(
            f"../data/pickle/deflection_with_interaction_{env_name_short}_all.pkl",
            deflections,
        )
        pickle_save(
            f"../data/pickle/length_trajectory_with_interaction_{env_name_short}_all.pkl",
            lengths,
        )
