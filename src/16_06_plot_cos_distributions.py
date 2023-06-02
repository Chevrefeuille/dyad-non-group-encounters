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

        d_min, d_max, n_bins = 1000, 4000, 16
        bin_size, pdf_edges, bin_centers = get_bins(d_min, d_max, n_bins)

        d_interaction = np.array(
            observables_encounters["d"][1]
            + observables_encounters["d"][2]
            + observables_encounters["d"][3]
        )

        for g in ["g", "n"]:
            cos_interaction = np.arccos(
                np.abs(
                    np.array(
                        observables_encounters[f"cos_{g}"][1]
                        + observables_encounters[f"cos_{g}"][2]
                        + observables_encounters[f"cos_{g}"][3]
                    )
                )
            )
            v_interaction = np.array(
                observables_encounters[f"v_{g}"][1]
                + observables_encounters[f"v_{g}"][2]
                + observables_encounters[f"v_{g}"][3]
            )
            a_interaction = np.array(
                observables_encounters[f"a_{g}"][1]
                + observables_encounters[f"a_{g}"][2]
                + observables_encounters[f"a_{g}"][3]
            )

            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            for i, v in enumerate(soc_binding_values):
                cos = np.arccos(np.abs(np.array(observables_encounters[f"cos_{g}"][i])))
                vel = np.array(observables_encounters[f"v_{g}"][i])
                a = np.array(observables_encounters[f"a_{g}"][i])
                d = np.array(observables_encounters["d"][i])
                mean_cos, std_cos, ste_cos, _ = get_mean_std_ste_n_over_bins(
                    d, cos, pdf_edges[1:]
                )
                axes[0, 0].errorbar(
                    bin_centers,
                    mean_cos,
                    ste_cos,
                    label=f"{g}-{soc_binding_names[v]}",
                    color=soc_binding_colors[v],
                    capsize=2,
                )

                mean_v, std_v, ste_v, _ = get_mean_std_ste_n_over_bins(
                    d, vel, pdf_edges[1:]
                )
                axes[0, 1].errorbar(
                    bin_centers,
                    mean_v,
                    ste_v,
                    label=f"{g}-{soc_binding_names[v]}",
                    color=soc_binding_colors[v],
                    capsize=2,
                )

                mean_a, std_a, ste_a, _ = get_mean_std_ste_n_over_bins(
                    d, a, pdf_edges[1:]
                )
                axes[1, 0].errorbar(
                    bin_centers,
                    mean_a,
                    ste_a,
                    label=f"{g}-{soc_binding_names[v]}",
                    color=soc_binding_colors[v],
                    capsize=2,
                )

            # for aggregated interaction
            mean_cos, std_cos, ste_cos, _ = get_mean_std_ste_n_over_bins(
                d_interaction, cos_interaction, pdf_edges[1:]
            )
            axes[0, 0].errorbar(
                bin_centers,
                mean_cos,
                ste_cos,
                label=f"{g}-interaction",
                color="purple",
                capsize=2,
            )
            mean_v, std_v, ste_v, _ = get_mean_std_ste_n_over_bins(
                d_interaction, v_interaction, pdf_edges[1:]
            )
            axes[0, 1].errorbar(
                bin_centers,
                mean_v,
                ste_v,
                label=f"{g}-interaction",
                color="purple",
                capsize=2,
            )
            mean_a, std_a, ste_a, _ = get_mean_std_ste_n_over_bins(
                d_interaction, a_interaction, pdf_edges[1:]
            )
            axes[1, 0].errorbar(
                bin_centers,
                mean_a,
                ste_a,
                label=f"{g}-interaction",
                color="purple",
                capsize=2,
            )

            axes[0, 0].set_xlim(d_min, d_max)
            axes[0, 0].legend()

            axes[0, 1].set_xlim(d_min, d_max)
            axes[0, 1].legend()

            axes[1, 0].set_xlim(d_min, d_max)
            axes[1, 0].legend()
            plt.show()
