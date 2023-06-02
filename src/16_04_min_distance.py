from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *
from pedestrians_social_binding.trajectory_utils import *


import numpy as np
from tqdm import tqdm
from scipy.spatial import distance

from utils import *

cross = lambda x, y, axis=1: np.cross(x, y, axis=axis)

if __name__ == "__main__":

    for env_name in ["diamor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        N = 16

        thresholds_ped = get_pedestrian_thresholds(env_name)

        all_areas = []
        all_min_distances = []

        for day in days:
            all_peds = env.get_pedestrians(days=[day])
            non_groups = env.get_pedestrians(
                days=[day], thresholds=thresholds_ped, no_groups=True
            )

            for ng in tqdm(non_groups):
                ng_id = ng.get_id()
                encounters = ng.get_encountered_pedestrians(
                    all_peds,
                    proximity_threshold=None,
                    alone=None,
                    skip=[ng_id],
                )

                times = ng.get_time()

                trajectories = get_trajectories_at_times(
                    [ped.get_trajectory() for ped in encounters], times
                )

                traj = ng.get_trajectory()
                n_points = len(traj)
                min_distances = np.zeros(n_points)
                for i in range(n_points):
                    p_ng = traj[i, 1:3].reshape(1, 2) / 1000
                    if np.any(np.isnan(p_ng)):
                        min_distances[i] = np.nan
                        continue
                    p_ped = (
                        np.array(
                            [trajectories[j][i, 1:3] for j in range(len(encounters))]
                        )
                        / 1000
                    )
                    if len(p_ped):
                        dist = distance.cdist(p_ng, p_ped)
                        min_distances[i] += np.nanmin(dist)

                    else:
                        min_distances[i] = np.nan

                min_distances = np.array(min_distances)
                all_min_distances += min_distances[int(N / 2) : -int(N / 2)].tolist()

                areas = []
                for i in range(int(N / 2), n_points - int(N / 2)):
                    sub_traj = traj[i - int(N / 2) : i + int(N / 2)]
                    # plt.scatter(sub_traj[:, 1], sub_traj[:, 2])
                    # plt.axis("equal")
                    # plt.show()
                    area = compute_area_under_the_curve(sub_traj[:, 1:3]) / 1000**2
                    # print(area)
                    areas += [area]

                areas = np.abs(np.array(areas))
                all_areas += areas.tolist()

        pickle_save(f"../data/pickle/areas_{N}_non_groups.pkl", all_areas)
        pickle_save(
            f"../data/pickle/min_distances_{N}_non_groups.pkl", all_min_distances
        )

        # plt.scatter(all_min_distances, all_areas)
        # plt.show()

        # fig, axes = plt.subplots(1, 2)
        # sc = axes[0].scatter(
        #     traj[:, 1] / 1000,
        #     traj[:, 2] / 1000,
        #     c=min_distances,
        #     s=3,
        #     vmin=0,
        #     vmax=10,
        # )
        # axes[0].set_xlim(
        #     env.boundaries["xmin"] / 1000, env.boundaries["xmax"] / 1000
        # )
        # axes[0].set_ylim(
        #     env.boundaries["ymin"] / 1000, env.boundaries["ymax"] / 1000
        # )
        # axes[0].set_aspect("equal")
        # plt.colorbar(sc, ax=axes[0])

        # sc = axes[1].scatter(
        #     traj[int(N / 2) : -int(N / 2), 1] / 1000,
        #     traj[int(N / 2) : -int(N / 2), 2] / 1000,
        #     c=areas,
        #     s=3,
        #     vmin=0,
        #     vmax=1,
        # )
        # axes[1].set_xlim(
        #     env.boundaries["xmin"] / 1000, env.boundaries["xmax"] / 1000
        # )
        # axes[1].set_ylim(
        #     env.boundaries["ymin"] / 1000, env.boundaries["ymax"] / 1000
        # )
        # axes[1].set_aspect("equal")
        # plt.colorbar(sc, ax=axes[1])
        # plt.show()

        # plot_static_2D_trajectories(
        #     [ng.get_trajectory()] + trajectories,
        #     boundaries=env.boundaries,
        #     colors=["blue"] + len(encounters) * ["orange"],
        # )
