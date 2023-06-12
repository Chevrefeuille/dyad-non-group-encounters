
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np
import cv2

from utils import *


def compute_instantaneous_direction(phase):
    if phase >= np.pi / 4 and phase < 3 * np.pi / 4:
        direction = "up"
    elif phase >= 3 * np.pi / 4 or phase < -3 * np.pi / 4:
        direction = "left"
    elif phase < np.pi / 4 and phase >= -np.pi / 4:
        direction = "right"
    elif phase < -np.pi / 4 and phase >= -3 * np.pi / 4:
        direction = "bottom"
    return direction


def compute_direction(pos):
    displacement = pos[1:] - pos[:-1]
    phase = np.arctan2(displacement[:, 1], displacement[:, 0])
    phase[phase > np.pi] -= 2 * np.pi
    phase[phase < -np.pi] += 2 * np.pi

    inst_direction = np.array([compute_instantaneous_direction(p) for p in phase])
    n_left = np.sum(inst_direction == "left")
    n_right = np.sum(inst_direction == "right")
    n_up = np.sum(inst_direction == "up")
    n_bottom = np.sum(inst_direction == "bottom")
    n = len(inst_direction)

    if n_left > 0.7 * n:
        return "left"
    elif n_right > 0.7 * n:
        return "right"
    elif n_up > 0.7 * n:
        return "up"
    elif n_bottom > 0.7 * n:
        return "bottom"
    else:
        return None


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = DAYS_ATC if "atc" in env_name else DAYS_DIAMOR

        xmin, xmax, ymin, ymax = env.get_boundaries()

        n_bin_x = int(np.ceil((xmax - xmin) / VEL_FIELD_CELL_SIZE) + 1)
        n_bin_y = int(np.ceil((ymax - ymin) / VEL_FIELD_CELL_SIZE) + 1)
        grid_vel = np.zeros((n_bin_x, n_bin_y, 2))
        grid_count = np.zeros((n_bin_x, n_bin_y))

        for day in days:
            print(f"Day {day}:")

            thresholds_ped = get_pedestrian_thresholds(env_name)

            pedestrians = env.get_pedestrians(days=[day], thresholds=thresholds_ped)
            print(f"  - Found {len(pedestrians)} pedestrians.")

            for pedestrian in pedestrians:

                traj = pedestrian.get_trajectory()
                pos = traj[:, 1:3]
                vel = traj[:, 5:7]

                cell_x = np.ceil((pos[:, 0] - xmin) / VEL_FIELD_CELL_SIZE).astype("int")
                cell_y = np.ceil((pos[:, 1] - ymin) / VEL_FIELD_CELL_SIZE).astype("int")

                grid_vel[cell_x, cell_y] += vel
                grid_count[cell_x, cell_y] += 1

                # direction = compute_direction(pos)

                # if direction == "right":
                #     # plt.plot(phase)
                #     # plt.ylim([-np.pi, np.pi])
                #     # plt.show()
                #pedestrian.plot_2D_trajectory(animate=True)


        grid_vel[grid_count > 0, :] /= grid_count[grid_count > 0, None] # averaging

        pickle_save(f"../data/pickle/velocity_field_{env_name.split(':')[0]}.pkl", grid_vel) 
        pickle_save(f"../data/pickle/occupancy_{env_name.split(':')[0]}.pkl", grid_count) 

        # to draw HSV image
        mag, ang = cv2.cartToPolar(grid_vel[..., 0], grid_vel[..., 1])

        hsv = np.zeros((n_bin_x, n_bin_y, 3)).astype(np.uint8)
        hsv[grid_count > 0, 1] = 255  # constant value

        hsv[..., 0] = ang * 180 / np.pi / 2  # hue
        hsv[..., 2] = 255 - cv2.normalize(
            mag, None, 0, 255, cv2.NORM_MINMAX
        )  # saturation

        # print(hsv[int(n_bin_x / 2), ...])
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        bgr = np.flip(np.transpose(bgr, (1, 0, 2)), 0)
        # cv2.imshow("vel", bgr)
        cv2.imwrite(f"../data/images/velocity_field_{env_name.split(':')[0]}.png", bgr)
        # cv2.waitKey(0)
        cv2.destroyAllWindows()

    