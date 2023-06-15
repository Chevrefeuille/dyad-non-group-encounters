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


def plot_baseline(trajectory, max_dev, soc_binding):
    point_of_max_deviation = max_dev["position of max lateral deviation"]
    start_vel = max_dev["start_vel"]
    x_start_plot = trajectory[0,1]
    y_start_plot = trajectory[0,2]
    x_end_plot = start_vel[0] * 1000 + x_start_plot
    y_end_plot = start_vel[1] * 1000 + y_start_plot

    vel_perpandicular = np.array([start_vel[1], -start_vel[0]])
    x_start_perp_plot = point_of_max_deviation[1]
    y_start_perp_plot = point_of_max_deviation[2]
    x_end_perp_plot = vel_perpandicular[0] * 1000 + x_start_perp_plot
    y_end_perp_plot = vel_perpandicular[1] * 1000 + y_start_perp_plot
    x_second_end_perp_plot = -vel_perpandicular[0] * 1000 + x_start_perp_plot
    y_second_end_perp_plot = -vel_perpandicular[1] * 1000 + y_start_perp_plot



    ## plot the trajectory
    color = colors[soc_binding]
    boundaries = env.boundaries
    fig = plt.figure(figsize=(15, 10))
    plt.xlim([boundaries["xmin"] / 1000, boundaries["xmax"] / 1000])
    plt.ylim([boundaries["ymin"] / 1000, boundaries["ymax"] / 1000])
    plt.scatter(trajectory[:,1] / 1000,trajectory[:,2] / 1000, s=10, c=color)
    plt.scatter(point_of_max_deviation[1] / 1000, point_of_max_deviation[2] / 1000, s=10, c="black")
    plt.plot([x_start_plot / 1000, x_end_plot / 1000], [y_start_plot / 1000, y_end_plot / 1000], c="purple", label="velocity")
    plt.xlabel('X Coord', fontsize=12, fontweight='bold')
    plt.ylabel('Y Coord', fontsize=12, fontweight='bold')
    plt.title('Plot of the baseline for undisturbed group')
    plt.plot([x_end_perp_plot / 1000, x_second_end_perp_plot / 1000], [y_end_perp_plot / 1000, y_second_end_perp_plot/1000]
                , c="green", label="perpendicular of the vector of velocity")
    plt.legend()
    plt.show()


  

if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = DAYS_ATC if env_name_short == "atc" else DAYS_DIAMOR
        plot_verif = True

        times_undisturbed = pickle_load(
            f"../data/pickle/undisturbed_times_{env_name_short}.pkl"
        )

        no_encounters_deviations = {
            "group": {},
            "non_group": {},
        }

        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )

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

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding not in soc_binding_values:
                    continue

                if group_id not in times_undisturbed[day]["group"]:
                    continue

                group_times_undisturbed = times_undisturbed[day]["group"][group_id]

                trajectory = group.get_center_of_mass_trajectory()

                group_undisturbed_trajectory = get_trajectory_at_times(
                    trajectory, group_times_undisturbed
                )


                print("group_undisturbed_trajectory",group_undisturbed_trajectory)

                masque = np.isin(group_times_undisturbed,trajectory[:,0])
                filter_group_times_undisturbed = group_times_undisturbed[masque]

                if(filter_group_times_undisturbed.shape[0] <= 10):
                    continue

                group_undisturbed_trajectory = get_trajectory_at_times(
                    trajectory, filter_group_times_undisturbed
                )

                ## Gérer quand il y a des nan dans la trajectoire -> séparer en deux parties et prendre en compte les deux trajectoires par la suite

                #print("group_undisturbed_trajectory", np.diff(group_undisturbed_trajectory[:,0]))
                if(np.any(np.isnan(group_undisturbed_trajectory))):
                    print("YOUHOU")
                    list_of_sub_trajectories = compute_continuous_sub_trajectories(group_undisturbed_trajectory)
                    i = 0
                    for sub_trajectory in list_of_sub_trajectories:
                        i+=1
                        if(sub_trajectory.shape[0] <= 10):
                            continue

                        sub_group_id = group_id + "_" + i
                        n_points_average = 4
                        max_dev_sub = compute_maximum_lateral_deviation_using_vel_2(
                        sub_trajectory, n_points_average, interpolate=False)

                        if(np.all(np.isnan(max_dev_sub["max_lateral_deviation"])) ):
                            continue

                        no_encounters_deviations["group"][str(sub_group_id)] = {
                                "social_binding": soc_binding,
                                "max_dev": max_dev_sub
                            }
                        if (plot_verif):
                            plot_baseline(sub_trajectory, max_dev_sub, soc_binding)
                else :
                    if(group_undisturbed_trajectory.shape[0] <= 10):
                        continue

                    if (np.all(group_undisturbed_trajectory)):
                        continue

                    n_points_average = 4
                    max_dev_g = compute_maximum_lateral_deviation_using_vel_2(
                        group_undisturbed_trajectory, n_points_average, interpolate=False)
                    
                    if(np.all(np.isnan(max_dev_g["max_lateral_deviation"])) ):
                        continue

                    no_encounters_deviations["group"][str(group_id)] = {
                            "social_binding": soc_binding,
                            "max_dev": max_dev_g
                        }
                    if (plot_verif):
                        plot_baseline(group_undisturbed_trajectory, max_dev_g, soc_binding)

                
            for non_group in tqdm(non_groups):
                non_group_id = non_group.get_id()

                if non_group_id not in times_undisturbed[day]["non_group"]:
                    continue

                non_group_times_undisturbed = times_undisturbed[day]["non_group"][
                    non_group_id
                ]

                trajectory = non_group.get_trajectory()

                masque = np.isin(non_group_times_undisturbed,trajectory[:,0])
                filter_non_group_times_undisturbed = non_group_times_undisturbed[masque]

                if(filter_non_group_times_undisturbed.shape[0] <= 10):
                    continue

                non_group_undisturbed_trajectory = get_trajectory_at_times(
                    trajectory,
                    filter_non_group_times_undisturbed,
                )

                ## Gérer quand il y a des nan dans la trajectoire -> séparer en deux parties et prendre en compte les deux trajectoires par la suite

                if(np.all(np.isnan(non_group_undisturbed_trajectory))):
                    list_of_sub_trajectories = compute_continuous_sub_trajectories(non_group_undisturbed_trajectory)
                    i = 0
                    for sub_trajectory in list_of_sub_trajectories:
                        i+=1
                        if(sub_trajectory.shape[0] <= 10):
                            continue

                        sub_non_group_id = non_group_id + "_" + i
                        n_points_average = 4
                        max_dev_ng = compute_maximum_lateral_deviation_using_vel_2(
                        sub_trajectory, n_points_average, interpolate=False)

                        if(np.all(np.isnan(max_dev_ng["max_lateral_deviation"])) ):
                            continue

                        no_encounters_deviations["non_group"][str(sub_non_group_id)] = {
                                "max_dev": max_dev_ng,
                            }

                if (np.all(non_group_undisturbed_trajectory)):
                    continue

                n_points_average = 4

                # des fois revois None, à voir dans quel cas
                max_dev_ng = compute_maximum_lateral_deviation_using_vel_2(
                    non_group_undisturbed_trajectory, n_points_average, interpolate=False)
                
                if(np.all(np.isnan(max_dev_ng["max_lateral_deviation"])) ):
                    continue

                no_encounters_deviations["non_group"][str(non_group_id)] = {
                        "max_dev": max_dev_ng,
                    }

    print(no_encounters_deviations)

    