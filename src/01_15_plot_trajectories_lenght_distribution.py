from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *
import matplotlib.pyplot as plt

""" The goal of this script is to plot the distribution of the trajectory lengths with and without interaction for the random trajectories.
    """

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        env_name_short = env_name.split(":")[0]

        lengths_with_interaction = pickle_load(
            f"../data/pickle/length_trajectory_with_interaction_{env_name_short}.pkl"
        )

        lengths_without_interaction_random = pickle_load(
            f"../data/pickle/length_trajectory_without_interaction_{env_name_short}_random.pkl"
        )
        lengths_without_interaction_segment = pickle_load(
            f"../data/pickle/length_trajectory_without_interaction_{env_name_short}.pkl"
        )

        bin_size, pdf_edges, bin_centers = get_bins(
            TRAJ_SIZE_MIN, TRAJ_SIZE_MAX, N_BINS_TRAJ_SIZE
        )
        fig, ax = plt.subplots()

        for group_non_group in ["group", "non_group", "group_members"]:
            # plot the distribution without interaction random
            values = lengths_without_interaction_random[group_non_group]["gross"]
            hist = np.histogram(values, pdf_edges)[0]
            pdf = hist / np.sum(hist) / bin_size
            ax.plot(bin_centers, pdf, label=f"baseline (random)", color="black")

            # plot the distribution without interaction segment
            values = []
            for segment_length in SEGMENT_LENGTHS:
                print(
                    segment_length,
                    np.mean(
                        lengths_without_interaction_segment[group_non_group][
                            segment_length
                        ]["gross"]
                    ),
                )
                values += lengths_without_interaction_segment[group_non_group][
                    segment_length
                ]["gross"]
            hist = np.histogram(values, pdf_edges)[0]
            pdf = hist / np.sum(hist) / bin_size
            ax.plot(bin_centers, pdf, label=f"baseline (segments)", color="grey")

            # plot the distribution with interaction
            for i in soc_binding_values:
                values = lengths_with_interaction["opposite"][i][group_non_group][
                    "gross"
                ]

                hist = np.histogram(values, pdf_edges)[0]
                pdf = hist / np.sum(hist) / bin_size

                ax.plot(
                    bin_centers,
                    pdf,
                    label=f"{soc_binding_names[i]}-{group_non_group}",
                    c=soc_binding_colors[i],
                    ls=LINE_TYPES[group_non_group],
                )

        ax.set_title(f"Trajectory lengths - {env_name_short}")
        ax.legend()
        plt.show()
