from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from parameters import *
from utils import *

from tqdm import tqdm

""" The goal of this script is to get the undisturbed trajectories of the pedestrians in the corridor environment. Undisturbed trajectories 
are trajectories where the pedestrian is not in a group and is not close to another pedestrian.
The data will be stored in a dictionary in the file data/undisturbed_trajectories/undisturbed_trajectories_{env_name}.pkl .
The dictionary will have the following structure:
    - undisturbed_trajectories[day][group_id] = [undisturbed_trajectory_1, undisturbed_trajectory_2, ...]"""

if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = DAYS_ATC if env_name == "atc" else DAYS_DIAMOR

        times_undisturbed = {}

        for day in days:
            print(f"Day {day}:")

            thresholds_ped = get_pedestrian_thresholds(env_name)
            thresholds_group = get_groups_thresholds()

            non_groups = env.get_pedestrians(
                days=[day],
                no_groups=True,
                thresholds=thresholds_ped,
            )

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
            )

            times_undisturbed[day] = {"group": {}, "non_group": {}}

            all_pedestrians = env.get_pedestrians(
                days=[day]
            )

            print(f"  - Found {len(non_groups)} non groups.")
            print(f"  - Found {len(groups)} groups.")

            # find groups undisturbed trajectories
            for group in tqdm(groups):
                group_id = group.get_id()
                group_members_id = [m.get_id() for m in group.get_members()]
                group_as_indiv = group.get_as_individual()
                undisturbed_trajectory = group.get_undisturbed_trajectory(
                    UNDISTURBED_VICINITY, all_pedestrians, skip=group_members_id
                )

                if not len(undisturbed_trajectory):
                    continue

                # plot_animated_2D_trajectories(
                #     [undisturbed_trajectory],
                #     boundaries=env.boundaries,
                #     vicinity=UNDISTURBED_VICINITY,
                #     simultaneous=False,
                #     title=f"Encounters for {group_id}",
                # )

                times_undisturbed[day]["group"][group_id] = undisturbed_trajectory[:, 0]

            for non_group in tqdm(non_groups):
                non_group_id = non_group.get_id()
                undisturbed_trajectory = non_group.get_undisturbed_trajectory(
                    UNDISTURBED_VICINITY, all_pedestrians
                )
                if not len(undisturbed_trajectory):
                    continue

                # encounters = non_group.get_encountered_pedestrians(
                #     UNDISTURBED_VICINITY, non_groups
                # )

                # non_group.set_trajectory(undisturbed_trajectory)

                # if encounters:
                # plot_animated_2D_trajectories(
                #     [undisturbed_trajectory],
                #     boundaries=env.boundaries,
                #     vicinity=UNDISTURBED_VICINITY,
                #     simultaneous=False,
                #     title=f"Encounters for {non_group_id}",
                # )

                times_undisturbed[day]["non_group"][
                    non_group_id
                ] = undisturbed_trajectory[:, 0]

        pickle_save(
            f"../data/pickle/undisturbed_times_{env_name}.pkl", times_undisturbed
        )
