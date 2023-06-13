from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *

from tqdm import tqdm

"""The goal of this script is to get the encounters between pedestrians in the corridor environment. The data will be stored in a dictionary 
in the file data/encounters/encounters_{env_name}.pkl . The dictionary will have the following structure:
    - encounters[day][group_id] = [encounter_1, encounter_2, ...]"""

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

        encounters = {}

        for day in days:
            print(f"Day {day}:")
            encounters[day] = {}

            non_groups = env.get_pedestrians(
                days=[day], no_groups=True, thresholds=thresholds_indiv
            )
            print(f"  - Found {len(non_groups)} non groups.")

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_indiv,
                group_thresholds=thresholds_groups,
            )
            print(f"  - Found {len(groups)} groups.")

            n_encounters = 0
            for group in tqdm(groups):
                group_id = group.get_id()
                group_members_id = [m.get_id() for m in group.get_members()]
                group_as_indiv = group.get_as_individual()
                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    non_groups, proximity_threshold=VICINITY, skip=group_members_id
                )

                # group.plot_2D_trajectory()

                n_encounters += len(group_encounters)

                # if encounters:
                #     plot_animated_2D_trajectories(
                #         [group_as_indiv] + encounters,
                #         boundaries=env.boundaries,
                #         vicinity=vicinity,
                #         simultaneous=False,
                #         title=f"Encounters for {group_id}",
                #     )
                # else:
                #     print(f"{group} didn't meet any non group.")

                encounters[day][group_id] = [p.get_id() for p in group_encounters]
            print(f"  - Found {n_encounters} encounters.")

        pickle_save(f"../data/pickle/encounters_{env_name}.pkl", encounters)
