from copy import deepcopy
from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from parameters import *
from utils import *


from tqdm import tqdm

if __name__ == "__main__":

    for env_name in ["atc", "diamor"]:

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

        sizes = {}
        breadths = {}
        depths = {}

        groups = env.get_groups(
            size=2,
            ped_thresholds=thresholds_ped,
            group_thresholds=thresholds_group,
            with_social_binding=True,
        )

        for group in groups:
            group_id = group.get_id()

            soc_binding = group.get_annotation(soc_binding_type)

            if soc_binding not in sizes:
                sizes[soc_binding] = []
                breadths[soc_binding] = []
                depths[soc_binding] = []

            size = group.get_interpersonal_distance()
            depth, breadth = group.get_depth_and_breadth()

            sizes[soc_binding] += list(size)
            breadths[soc_binding] += list(breadth)
            depths[soc_binding] += list(depth)

            # group.plot_2D_trajectory()

        pickle_save(f"../data/pickle/group_breadth_{env_name}.pkl", breadths)
        pickle_save(f"../data/pickle/group_depth_{env_name}.pkl", depths)
        pickle_save(f"../data/pickle/group_size_{env_name}.pkl", sizes)

        # bin_size = (
        #     BREADTH_DISTRIBUTION_MAX - BREADTH_DISTRIBUTION_MIN
        # ) / N_BINS_BREADTH_DISTRIBUTION
        # pdf_edges = np.linspace(
        #     BREADTH_DISTRIBUTION_MIN,
        #     BREADTH_DISTRIBUTION_MAX,
        #     N_BINS_BREADTH_DISTRIBUTION + 1,
        # )
        # bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:]) / 1000

        # # plot pdf
        # for i in soc_binding_values:
        #     size_values = depths[i]
        #     hist = np.histogram(size_values, pdf_edges)[0]
        #     pdf = hist / sum(hist) / bin_size
        #     plt.plot(bin_centers, pdf, label=soc_binding_names[i])
        # plt.legend()
        # plt.show()

        # pickle_save(f"../data/pickle/group_breadth_{env_name}.pkl", breadth)
