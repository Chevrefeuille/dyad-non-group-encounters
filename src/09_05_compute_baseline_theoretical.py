from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.trajectory_utils import *
from pedestrians_social_binding.plot_utils import *

from utils import *


import numpy as np
from tqdm import tqdm
from scipy.spatial.distance import cdist

""" The goal of this script is to compute the theoretical trajectory of a group.
The theoretical trajectory is the trajectory of the group if the group members were not interacting with each other.
"""

if __name__ == "__main__":

    for env_name in ["atc:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        boundaries = env.get_boundaries()

        env_name_short = env_name.split(":")[0]

        xmin, xmax, ymin, ymax = env.get_boundaries()
        days = get_all_days(env_name)
        soc_binding_type, soc_binding_names, soc_binding_values, _ = get_social_values(
            env_name
        )

        splines = pickle_load(f"../data/pickle/splines_{env_name_short}.pkl")
        n_splines, _, n_points_interp = splines.shape
        points = np.transpose(splines, axes=(0, 2, 1)).reshape(
            len(splines) * len(splines[0, 0]), 2
        )

        deflections = {}
        lengths = {"net": [], "gross": []}

        n_trajectory = 1000

        for _ in range(n_trajectory):
            random_spline_indx = np.random.randint(n_splines)
            random_spline = splines[random_spline_indx]

            random_start_idx = np.random.randint(n_points_interp)
            random_start = random_spline[:, random_start_idx].T
            random_end_idx = np.random.randint(
                max(random_start_idx - 150, 0),
                min(random_start_idx + 150, n_points_interp),
            )
            random_end = random_spline[:, random_end_idx].T

            random_vel = int(np.random.normal(1500, 300))

            min_idx = min(random_start_idx, random_end_idx)
            max_idx = max(random_start_idx, random_end_idx)
            spline_pos = random_spline[:, min_idx:max_idx].T
            distance = compute_gross_displacement(spline_pos)

            delta_t = 0.5  # 0.5 s
            t = distance / random_vel

            if t > delta_t:
                n_points = int(t / delta_t)
                k = len(spline_pos) // n_points
                spline_pos = spline_pos[::k]

                if len(spline_pos) < 3:
                    continue

                trajectory = np.zeros((len(spline_pos), 7))
                trajectory[:, 1:3] = spline_pos

                net_displacement = compute_net_displacement(spline_pos)

                lengths["net"] += [net_displacement]
                lengths["gross"] += [distance]

                # plot_static_2D_trajectory(trajectory, boundaries=env.boundaries)

                for measure in DEFLECTION_MEASURES:
                    if measure not in deflections:
                        deflections[measure] = []

                    deflections[measure] += [compute_deflection(spline_pos, measure)]
                    print(deflections[measure][-1])

        pickle_save(
            f"../data/pickle/deflection_theoretical_{env_name_short}.pkl",
            deflections,
        )
        pickle_save(
            f"../data/pickle/length_trajectory_theoretical_{env_name_short}.pkl",
            lengths,
        )
