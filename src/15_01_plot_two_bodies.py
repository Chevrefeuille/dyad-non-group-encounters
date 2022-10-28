from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.pedestrian import *
from pedestrians_social_binding.environment import *

import numpy as np

from utils import *


if __name__ == "__main__":

    data = pickle_load("data.pkl")

    pedestrians: list[Pedestrian] = []

    for i, traj_data in enumerate(data):
        trajectory = np.zeros((len(traj_data), 7))
        trajectory[:, 0] = traj_data[:, 0]
        trajectory[:, 1:3] = traj_data[:, 1:3]
        trajectory[:, 5:7] = traj_data[:, 3:5]
        ped = Pedestrian(i, None, None, trajectory, [])

        pedestrians += [ped]

    p1, p2 = pedestrians

    # plot_animated_2D_trajectories([p1.get_trajectory(), p2.get_trajectory()])

    traj_1_aligned, [traj_2_aligned] = align_trajectories_at_origin(
        p1.get_trajectory(), [p2.get_trajectory()]
    )
    plot_animated_2D_trajectories(
        [traj_1_aligned, traj_2_aligned]
    )
