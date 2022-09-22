from operator import length_hint
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
import matplotlib.pyplot as plt


if __name__ == "__main__":

    fig, ax = plt.subplots()

    for env_name in ["atc:corridor", "diamor:corridor"]:

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        env_name_short = env_name.split(":")[0]

        lengths = pickle_load(
            f"../data/pickle/length_trajectory_without_interaction_{env_name_short}_random.pkl"
        )
        deflections = pickle_load(
            f"../data/pickle/deflection_without_interaction_{env_name_short}_random.pkl"
        )

        N_BINS_TRAJ_SIZE = 15
        TRAJ_SIZE_MIN, TRAJ_SIZE_MAX = 2000, 15000
        bin_size = (TRAJ_SIZE_MAX - TRAJ_SIZE_MIN) / N_BINS_TRAJ_SIZE
        pdf_edges = np.linspace(
            TRAJ_SIZE_MIN,
            TRAJ_SIZE_MAX,
            N_BINS_TRAJ_SIZE + 1,
        )
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])
        print(bin_centers)

        lengths_g = np.array(
            lengths["non_group"]["gross"] + lengths["group_members"]["gross"]
        )
        tortuosity = np.array(
            deflections["non_group"]["straightness_index"]
            + deflections["group_members"]["straightness_index"]
        )

        mean_tortuosity = get_mean_over_bins(lengths_g, tortuosity, bin_centers)
        print(mean_tortuosity)

        ax.plot(bin_centers, mean_tortuosity)

    plt.show()
