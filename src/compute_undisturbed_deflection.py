from copy import deepcopy
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.threshold import Threshold
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
from parameters import *

from tqdm import tqdm

"""The goal of this script is to compute the deflection of the pedestrians in the corridor environment. 
The deflection is the angle between the direction of the pedestrian and the direction of the group. The deflection for non_group_id is
the angle between the direction of the pedestrian and the direction of the same pedestrian at a next time step.
The data will be stored in a dictionary in the file data/deflection/deflection_{env_name}.pkl .
The dictionary will have the following structure:
    - deflection[day][group_id] = [deflection_1, deflection_2, ...]
    - deflection[day][group_members_id] = [deflection_1, deflection_2, ...]
    - deflection[day][non_group_id] = [deflection_1, deflection_2, ...]
    """

if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = DAYS_ATC if env_name_short == "atc" else DAYS_DIAMOR

        times_undisturbed = pickle_load(
            f"../data/pickle/undisturbed_times_{env_name_short}.pkl"
        )

        no_encounters_deviations = {"group": [],
                        "non_group": [],}

        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        for day in days:
            print(f"Day {day}:")

            non_groups = env.get_pedestrians(
                days=[day],
                no_groups=True,
                thresholds=thresholds_ped,
                sampling_time=500,
            )

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                sampling_time=500,
            )

            # compute deflection for the groups
            for group in tqdm(groups):
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()

                print("group_id", group_id)

             

                if group_id not in times_undisturbed[day]["group"]:
                    continue

                group_times_undisturbed = times_undisturbed[day]["group"][group_id]

                # print(group_times_undisturbed[0], group_times_undisturbed[-1])
                # print(group.get_center_of_mass_trajectory()[0,0],group.get_center_of_mass_trajectory()[-1,0])

                # print("group_center_of_the_mass_trajectori",  group.get_center_of_mass_trajectory().shape,  group.get_center_of_mass_trajectory())
                # print("group_times_undisturbed", group_times_undisturbed.shape, group_times_undisturbed)

                group_undisturbed_trajectory = get_trajectory_at_times(
                    group.get_center_of_mass_trajectory(), group_times_undisturbed
                )

                if (np.all(group_undisturbed_trajectory)):
                    print("group_detected", group_undisturbed_trajectory)
                    continue



                # plot_static_2D_trajectories(
                #     [
                #         group_as_indiv.get_trajectory(),
                #         group_undisturbed_trajectory,
                #     ],
                #     boundaries=env.boundaries,
                # )



                n_points_average = 4
                max_dev_g = compute_maximum_lateral_deviation_using_vel(
                    group_undisturbed_trajectory, n_points_average, interpolate=False)

                no_encounters_deviations["group"].append(max_dev_g)
                


            for non_group in tqdm(non_groups):
                non_group_id = non_group.get_id()

                if non_group_id not in times_undisturbed[day]["non_group"]:
                    continue

                non_group_times_undisturbed = times_undisturbed[day]["non_group"][
                    non_group_id
                ]

                non_group_undisturbed_trajectory = get_trajectory_at_times(
                    non_group.get_trajectory(),
                    non_group_times_undisturbed,
                )


                plot_static_2D_trajectories(
                    [
                        non_group.get_trajectory(),
                        non_group_undisturbed_trajectory,
                    ],
                    boundaries=env.boundaries,
                )

                if (np.all(non_group_undisturbed_trajectory)):
                    continue

                n_points_average = 4
                max_dev_ng = compute_maximum_lateral_deviation_using_vel(
                    non_group_undisturbed_trajectory, n_points_average, interpolate=False)
                
                no_encounters_deviations["non_group"].append(max_dev_ng)


    pickle_save(f"../data/pickle/{env_name_short}no_encounters_deviations.pkl", no_encounters_deviations)


            

               