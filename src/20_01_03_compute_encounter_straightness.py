from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *

from tqdm import tqdm




PLOT_VERIF = False



if __name__ == "__main__":
    for env_name in ["diamor:corridor"]:
        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )
        env_name_short = env_name.split(":")[0]

        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )
        days = get_all_days(env_name)
        days = [days[0]]


        dict_straightness = {
            "group": {},
        }


        thresholds_indiv = get_pedestrian_thresholds(env_name)
        thresholds_groups = get_groups_thresholds()

        for day in days:
            print(f"Day {day}:")

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_indiv,
                group_thresholds=thresholds_groups,
                sampling_time=500
            )

            all_pedestrians = env.get_pedestrians(
                days=[day], no_groups=False, thresholds=thresholds_indiv, sampling_time=500
            )

            for group in tqdm(groups):
                group_id = group.get_id()
                group_members_id = [m.get_id() for m in group.get_members()]
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()
                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding not in soc_binding_values:
                    soc_binding = "other"
                
                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    all_pedestrians, proximity_threshold=VICINITY, skip=group_members_id
                )

                if not group_encounters:
                    continue

                dict_straightness["group"][group_id] = {
                    "group straightness": [],
                    "social_binding": soc_binding,
                    "encounters straightness": [],
                }

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

                    in_vicinity = np.logical_and(
                        np.abs(traj_group[:, 1] - traj_non_group[:, 1]) <= 4000,
                        np.abs(traj_group[:, 2] - traj_non_group[:, 2]) <= 4000,
                    )

                    traj_A_vicinity = traj_A[in_vicinity]
                    traj_B_vicinity = traj_B[in_vicinity]
                    traj_group_vicinity = traj_group[in_vicinity]
                    traj_non_group_vicinity = traj_non_group[in_vicinity]

                    if (len(traj_group_vicinity) < 6 or len(traj_non_group_vicinity) < 6):
                        continue

                    mean_group_speed = np.nanmean(traj_group_vicinity[:,4])/1000 
                    if (mean_group_speed < 0.5):
                        continue
                    elif (mean_group_speed > 2.5):
                        continue    

                    encounter_speed = np.nanmean(traj_non_group_vicinity[:,4])/1000
                    if (encounter_speed < 0.5):
                        continue
                    elif (encounter_speed > 2.5):
                        continue

                    time_of_group_traj = traj_group_vicinity[-1, 0] - traj_group_vicinity[0, 0]
                    time_of_non_group_traj = traj_non_group_vicinity[-1, 0] - traj_non_group_vicinity[0, 0]
                        
                    ng_straightness = {"straightness": float, "mean_velocity": np.ndarray, "length_of_trajectory": float, "time": float}

                    length_non_group = compute_length(traj_non_group_vicinity)
                    ng_straightness["straightness"] = compute_straightness_index(traj_non_group_vicinity)

                    group_straightness = {"straightness": float, "mean_velocity": np.ndarray, "length_of_trajectory": float, "time": float}

                    length_group = compute_length(traj_group_vicinity)
                    group_straightness["straightness"] = compute_straightness_index(traj_group_vicinity)

                    if(PLOT_VERIF) :
                        fig, ax = plot_baseline(trajectory = traj_group_vicinity , max_dev = group_straightness,soc_binding = soc_binding,group = True, id = group_id, boundaries = env.boundaries, colors = colors,ax = None,
                                            n_average = N_POINTS_AVERAGE, show = False)
                        plot_baseline(trajectory = traj_non_group_vicinity , max_dev = ng_straightness,soc_binding = soc_binding,group = False, id = non_group_id, boundaries = env.boundaries, colors = colors, ax = ax, fig = fig,
                                    show = True
                        )
                        plt.close()

                    group_straightness["mean_velocity"] = mean_group_speed
                    ng_straightness["mean_velocity"] = encounter_speed

                    group_straightness["time"] = time_of_group_traj
                    ng_straightness["time"] = time_of_non_group_traj

                    group_straightness["length_of_trajectory"] = length_group
                    ng_straightness["length_of_trajectory"] = length_non_group

                    dict_straightness["group"][group_id]["group straightness"].append(group_straightness)
                    dict_straightness["group"][group_id]["encounters straightness"].append(ng_straightness)


    pickle_save(f"../data/pickle/{env_name_short}_encounters_straightness.pkl", dict_straightness)