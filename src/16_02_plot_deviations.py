from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *
from pedestrians_social_binding.trajectory_utils import *


import numpy as np

from utils import *

cross = lambda x, y, axis=None: np.cross(x, y, axis=axis)

if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        env_name_short = env_name.split(":")[0]

        XMIN, XMAX, YMIN, YMAX = env.get_boundaries()
        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        deviations = pickle_load(f"../data/pickle/{env_name_short}_deviations.pkl")
        bin_size, pdf_edges, bin_centers = get_bins(0, 1.6, 16)

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        for i, v in enumerate(soc_binding_values):
            values = np.array(deviations[i]["ext"] + deviations[i]["int"]) / 1000
            hist = np.histogram(values, pdf_edges)[0]
            pdf = hist / np.sum(hist) / bin_size
            axes[0][0].plot(
                bin_centers,
                pdf,
                label=f"{soc_binding_names[v]}-group",
                color=soc_binding_colors[v],
            )
            values = np.array(deviations[i]["non_group"]) / 1000
            hist = np.histogram(values, pdf_edges)[0]
            pdf = hist / np.sum(hist) / bin_size
            axes[1][0].plot(
                bin_centers,
                pdf,
                label=f"{soc_binding_names[v]}-non_group",
                color=soc_binding_colors[v],
            )
        axes[0][0].legend()
        axes[0][0].grid(color="lightgray", linestyle="--", linewidth=0.5)

        axes[1][0].legend()
        axes[1][0].grid(color="lightgray", linestyle="--", linewidth=0.5)

        # group vs non groups
        all_dev_non_groups = []
        all_dev_groups = []
        for i, v in enumerate(soc_binding_values):
            all_dev_non_groups += deviations[i]["non_group"]
            all_dev_groups += deviations[i]["ext"] + deviations[i]["int"]
        all_dev_non_groups = np.array(all_dev_non_groups)
        all_dev_non_groups /= 1000
        all_dev_groups = np.array(all_dev_groups)
        all_dev_groups /= 1000

        hist_non_groups = np.histogram(all_dev_non_groups, pdf_edges)[0]
        pdf_non_groups = hist_non_groups / np.sum(hist_non_groups) / bin_size
        axes[0][1].plot(
            bin_centers,
            pdf_non_groups,
            label=f"non-groups",
        )
        hist_groups = np.histogram(all_dev_groups, pdf_edges)[0]
        pdf_groups = hist_groups / np.sum(hist_groups) / bin_size
        axes[0][1].plot(
            bin_centers,
            pdf_groups,
            label=f"groups",
        )
        axes[0][1].legend()
        axes[0][1].grid(color="lightgray", linestyle="--", linewidth=0.5)

        axes[1][1].boxplot(
            [all_dev_groups, all_dev_non_groups],
            labels=["groups", "non-groups"],
            sym="",
        )

        plt.show()
