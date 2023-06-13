
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np
import cv2

from utils import *

"""The goal of this script is to find the walls of the environment.
We will use the occupancy grid to do so.
"""


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(':')[0]

        grid_count = pickle_load(f"../data/pickle/occupancy_{env_name_short}.pkl") 
        h, w = grid_count.shape

        env_map = cv2.normalize(
            grid_count, None, 0, 255, cv2.NORM_MINMAX, dtype = cv2.CV_8UC1
        )
        
        env_map = cv2.GaussianBlur(env_map, (3,3), 0)

        threshold = 20
        env_map[env_map > threshold] = 255
        env_map[env_map <= threshold] = 0

        # # sobel = cv2.Sobel(src=env_map, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=5)
        walls = cv2.Canny(env_map, 100, 200)
        pickle_save(f"../data/pickle/walls_{env_name_short}.pkl", walls)

        walls = np.flip(np.transpose(walls), 0)
        cv2.imwrite(f"../data/images/walls_{env_name_short}.png", walls)


        # cv2.imshow("map", env_map)
        # cv2.imshow("edge", edges)
        # # cv2.imwrite(f"../data/images/velocity_field_{env_name.split(':')[0]}.png", bgr)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    