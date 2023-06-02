from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *
from pedestrians_social_binding.trajectory_utils import *


import numpy as np
from tqdm import tqdm

from utils import *

cross = lambda x, y, axis=None: np.cross(x, y, axis=axis)

if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        cos_thetas = {
            "cos_g": {},
            "d": {},
            "v_g": {},
            "a_g": {},
            "cos_n": {},
            "v_n": {},
            "a_n": {},
        }

        for day in tqdm(days):

            non_groups = env.get_pedestrians(
                days=[day], thresholds=thresholds_ped, no_groups=True
            )

            groups = env.get_groups(
                size=2,
                days=[day],
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                with_social_binding=True,
            )

            for group in groups:
                group_id = group.get_id()
                group_as_indiv = group.get_as_individual()
                group_members = group.get_members()
                group_members_id = [m.get_id() for m in group.get_members()]

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding not in soc_binding_values:
                    continue

                if soc_binding not in cos_thetas["d"]:
                    cos_thetas["d"][soc_binding] = []
                    cos_thetas["cos_g"][soc_binding] = []
                    cos_thetas["a_g"][soc_binding] = []
                    cos_thetas["v_g"][soc_binding] = []
                    cos_thetas["cos_n"][soc_binding] = []
                    cos_thetas["v_n"][soc_binding] = []
                    cos_thetas["a_n"][soc_binding] = []

                group_encounters = group_as_indiv.get_encountered_pedestrians(
                    non_groups,
                    proximity_threshold=None,
                    alone=None,
                    skip=group_members_id,
                )

                for non_group in group_encounters:

                    non_group_id = non_group.get_id()

                    trajectories = [
                        group_members[0].get_trajectory(),
                        group_members[1].get_trajectory(),
                        group_as_indiv.get_trajectory(),
                        non_group.get_trajectory(),
                    ]
                    relative_direction = compute_relative_direction(
                        group_as_indiv.get_trajectory(), non_group.get_trajectory()
                    )

                    if relative_direction != "opposite":
                        continue

                    [
                        traj_A,
                        traj_B,
                        traj_group,
                        traj_non_group,
                    ] = compute_simultaneous_observations(trajectories)

                    in_vicinity = np.logical_and(
                        np.abs(traj_group[:, 1] - traj_non_group[:, 1]) <= 4000,
                        np.abs(traj_group[:, 2] - traj_non_group[:, 2]) <= 2000,
                    )

                    traj_A_vicinity = traj_A[in_vicinity]
                    traj_B_vicinity = traj_B[in_vicinity]
                    traj_group_vicinity = traj_group[in_vicinity]
                    traj_non_group_vicinity = traj_non_group[in_vicinity]

                    if len(traj_group_vicinity) <= 2:
                        continue

                    NG = traj_group_vicinity[:, 1:3] - traj_non_group_vicinity[:, 1:3]
                    r = np.linalg.norm(NG, axis=1)

                    cos_thetas["d"][soc_binding] += r.tolist()

                    v_N = traj_non_group_vicinity[:, 5:7]
                    v_N_mag = np.linalg.norm(v_N, axis=1)
                    a_N = (v_N[1:, :] - v_N[:-1, :]) / (
                        traj_non_group_vicinity[1:, 0] - traj_non_group_vicinity[:-1, 0]
                    )[:, None]
                    a_N_mag = np.linalg.norm(a_N, axis=1)
                    a_N_mag = np.append(a_N_mag, np.NaN)
                    a_N = np.append(a_N, np.NaN)
                    cos_theta_N = (NG * v_N).sum(1) / (r * v_N_mag)

                    cos_thetas["cos_n"][soc_binding] += cos_theta_N.tolist()
                    cos_thetas["v_n"][soc_binding] += v_N_mag.tolist()
                    cos_thetas["a_n"][soc_binding] += a_N_mag.tolist()

                    v_G = traj_group_vicinity[:, 5:7]
                    v_G_mag = np.linalg.norm(v_G, axis=1)
                    cos_theta_G = (-NG * v_G).sum(1) / (r * v_G_mag)
                    a_G = (v_G[1:, :] - v_G[:-1, :]) / (
                        traj_group_vicinity[1:, 0] - traj_group_vicinity[:-1, 0]
                    )[:, None]
                    a_G_mag = np.linalg.norm(a_G, axis=1)
                    a_G_mag = np.append(a_G_mag, np.NaN)

                    cos_thetas["cos_g"][soc_binding] += cos_theta_G.tolist()
                    cos_thetas["v_g"][soc_binding] += v_G_mag.tolist()
                    cos_thetas["a_g"][soc_binding] += a_G_mag.tolist()

                    # plt.plot(cos_theta)
                    # plt.ylim(-1, 1)
                    # plt.show()

                    # plot_static_2D_trajectories(
                    #     [
                    #         traj_A_vicinity,
                    #         traj_B_vicinity,
                    #         traj_group_vicinity,
                    #         traj_non_group_vicinity,
                    #     ],
                    #     boundaries=env.boundaries,
                    #     colors=[
                    #         "cornflowerblue",
                    #         "cornflowerblue",
                    #         "lightsteelblue",
                    #         "orange",
                    #     ],
                    # )

        pickle_save(
            f"../data/pickle/{env_name_short}_observables_encounters.pkl", cos_thetas
        )

        # plt.scatter(
        #     traj_non_group_vicinity[:, 1], traj_non_group_vicinity[:, 2]
        # )
        # plt.quiver(
        #     traj_non_group_vicinity[0, 1],
        #     traj_non_group_vicinity[0, 2],
        #     vel_non_group[0],
        #     vel_non_group[1],
        # )
        # plt.axis("equal")
        # plt.show()
