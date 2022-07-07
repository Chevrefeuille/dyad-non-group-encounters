from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.trajectory_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


from utils import *

if __name__ == "__main__":

    env = Environment(
        "atc:corridor", data_dir="../../atc-diamor-pedestrians/data/formatted"
    )

    day = "0109"

    peds = env.get_pedestrians(
        days=["0109"],
        ids=[12390000, 12390800, 12391300, 12391301, 12390900, 12382300, 12390801],
    )

    trajectories = [ped.get_trajectory() for ped in peds]

    plot_animated_2D_trajectories(trajectories, boundaries=env.boundaries)
