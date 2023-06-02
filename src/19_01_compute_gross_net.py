from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *


import numpy as np
from tqdm import tqdm

from utils import *


if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()

        net, gross = [], []

        thresholds_ped = get_pedestrian_thresholds(env_name)

        pedestrians = env.get_pedestrians(thresholds=thresholds_ped)

        for ped in tqdm(pedestrians):
            # ped.plot_2D_trajectory()

            trajectory = ped.get_trajectory()
            pos = trajectory[:, 1:3]

            n_points = len(pos)

            if n_points < 10:
                continue

            pieces = get_random_pieces(pos, 10)

            for piece in pieces:
                net_piece = compute_net_displacement(piece)
                gross_piece = compute_gross_displacement(piece)

                # if gross_piece < net_piece:
                #     print(len(piece))
                #     plt.scatter(
                #         piece[:, 0], piece[:, 1], alpha=np.linspace(0.1, 1, len(pos))
                #     )
                #     plt.axis("equal")
                #     plt.show()

                net += [net_piece]
                gross += [gross_piece]

        displacements = {"net": np.array(net), "gross": np.array(gross)}

        pickle_save(
            f"../data/pickle/net_gross_{env_name_short}.pkl",
            displacements,
        )
