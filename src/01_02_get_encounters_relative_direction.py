from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.trajectory_utils import *


if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        relative_directions = {}

        days = DAYS_ATC if env_name == "atc" else DAYS_DIAMOR
        encounters = pickle_load(f"../data/pickle/encounters_{env_name}.pkl")

        for day in days:
            # print(f"Day {day}:")

            relative_directions[day] = {}

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
                days=[day], ids=group_ids, ped_thresholds=thresholds
            )

            for group in groups:
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()

                relative_directions[day][group_id] = {}

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
                    relative_direction = compute_relative_direction(
                        group_as_indiv.get_trajectory(), non_group.get_trajectory()
                    )
                    # print(relative_direction)
                    relative_directions[day][group_id][
                        non_group_id
                    ] = relative_direction

                    # if relative_direction == "opposite":
                    #     colors = 2 * ["cornflowerblue"] + ["coral"]
                    #     plot_animated_2D_trajectories(
                    #         group_members + [non_group],
                    #         boundaries=env.boundaries,
                    #         vel=True,
                    #         colors=colors,
                    #         simultaneous=True,
                    #     )

        pickle_save(
            f"../data/pickle/relative_directions_{env_name}.pkl", relative_directions
        )
