from tkinter import N
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np
import cv2
import matplotlib.pyplot as plt
import random as rnd

from utils import *


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        grid_vel = pickle_load(
            f"../data/pickle/velocity_field_{env_name_short.split(':')[0]}.pkl"
        )

        days = DAYS_ATC if "atc" in env_name_short else DAYS_DIAMOR

        xmin, xmax, ymin, ymax = env.get_boundaries()

        for i in range(20):

            # find a random seed point with non null velocity
            non_null_v = np.argwhere(grid_vel[:, :, 0] > 0)
            random_val = non_null_v[np.random.choice(non_null_v.shape[0], 1)][0]
            # print(random_val, grid_vel[random_val[0], random_val[1]])
            p = [
                [
                    random_val[0] * VEL_FIELD_CELL_SIZE + xmin,
                    random_val[1] * VEL_FIELD_CELL_SIZE + ymin,
                ]
            ]
            # p = [[rnd.randint(xmin, xmax), rnd.randint(ymin, ymax)]]
            # p = [[int((xmax - xmin) / 2), int((ymax - ymin) / 2)]]

            v = []
            n_step = 200
            delta_t = 0.5  # s

            for k in range(n_step):
                position = p[-1]
                cell_x = int(np.ceil((position[0] - xmin) / VEL_FIELD_CELL_SIZE))
                cell_y = int(np.ceil((position[1] - ymin) / VEL_FIELD_CELL_SIZE))

                cell_v = grid_vel[cell_x, cell_y]

                v += [list(cell_v)]

                new_position = [
                    position[0] + cell_v[0] * delta_t,
                    position[1] + cell_v[1] * delta_t,
                ]

                p += [new_position]

                if (
                    new_position[0] < xmin
                    or new_position[0] > xmax
                    or new_position[1] < ymin
                    or new_position[1] > ymax
                ):
                    break
            # print(p)

            trajectory = np.zeros((len(p), 7))
            trajectory[:, 1] = [pos[0] for pos in p]
            trajectory[:, 2] = [pos[1] for pos in p]
            trajectory[:-1, 5] = [vel[0] for vel in v]
            trajectory[:-1, 6] = [vel[1] for vel in v]

            background_path = f"../data/images/velocity_field_{env_name_short}.png"
            plot_animated_2D_trajectory(
                trajectory,
                boundaries=env.boundaries,
                colors=len(trajectory) * ["black"],
                vel=True,
                background=background_path,
            )
        # middle_cell_x = current_cell_x * VEL_FIELD_CELL_SIZE + VEL_FIELD_CELL_SIZE / 2
        # middle_cell_y = current_cell_x * VEL_FIELD_CELL_SIZE + VEL_FIELD_CELL_SIZE / 2
