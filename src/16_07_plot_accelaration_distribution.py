from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.utils import pickle_load

from utils import *

import numpy as np

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

        observables_encounters = pickle_load(
            f"../data/pickle/{env_name_short}_observables_encounters.pkl"
        )

        bin_size_a, pdf_edges_a, bin_centers_a = get_bins(0, 10, 16)
        bin_size_v, pdf_edges_v, bin_centers_v = get_bins(0, 3, 32)

        for g in ["g", "n"]:
            fig, axes = plt.subplots(1, 2)
            for i, v in enumerate(soc_binding_values):
                a = np.array(observables_encounters[f"a_{g}"][i])
                hist = np.histogram(a, pdf_edges_a)[0]
                pdf = hist / np.sum(hist) / bin_size_a
                axes[0].plot(
                    bin_centers_a,
                    pdf,
                    label=f"{soc_binding_names[v]}-{g}",
                    color=soc_binding_colors[v],
                )

                vel = np.array(observables_encounters[f"v_{g}"][i]) / 1000
                hist = np.histogram(vel, pdf_edges_v)[0]
                pdf = hist / np.sum(hist) / bin_size_v
                axes[1].plot(
                    bin_centers_v,
                    pdf,
                    label=f"{soc_binding_names[v]}-{g}",
                    color=soc_binding_colors[v],
                )
            axes[0].legend()
            axes[1].legend()
            plt.show()
