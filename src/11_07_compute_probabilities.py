from email import header
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import numpy as np
from parameters import *
from utils import *

import scipy.stats as stats
import pandas as pd

if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

        print(f"# {env_name_short}")

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        observed_minimum_distances_with_interaction = pickle_load(
            f"../data/pickle/observed_minimum_distance_{env_name_short}_with_interaction.pkl"
        )
        straight_line_minimum_distances_with_interaction = pickle_load(
            f"../data/pickle/straight_line_minimum_distance_{env_name_short}_with_interaction.pkl"
        )
        group_size_all = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")
        group_breadth_all = pickle_load(
            f"../data/pickle/group_breadth_{env_name_short}.pkl"
        )

        bin_size = 4 / 16
        pdf_edges = np.linspace(0, 4, 16 + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        # with scaling
        print(" - Scaling by group size")
        ps = []
        fig, ax = plt.subplots()
        for k in range(len(pdf_edges[1:])):
            values = []
            for i, v in enumerate(soc_binding_values):
                observed_values = observed_minimum_distances_with_interaction[
                    v
                ] / np.nanmean(group_size_all[v])
                straight_line_values = straight_line_minimum_distances_with_interaction[
                    v
                ] / np.nanmean(group_size_all[v])

                bin_ids = np.digitize(straight_line_values, pdf_edges[1:])
                observed_for_bin = observed_values[bin_ids == k]
                if len(observed_for_bin):
                    values += [observed_for_bin]

            f, p = stats.f_oneway(*values)
            ps += [p]

        ax.plot(bin_centers, ps)
        ax.set_ylabel("p-values")
        ax.set_xlabel("r_p (scaled with group size)")
        ax.set_yscale("log")
        ax.set_title(f"{env_name_short}")
        # plt.show()

        all_probabilities = []

        data_bin = np.empty((len(bin_centers), 1 + len(soc_binding_values)))
        data_bin[:, 0] = bin_centers.T

        fig, ax = plt.subplots()
        for i, v in enumerate(soc_binding_values):
            observed_values = observed_minimum_distances_with_interaction[
                v
            ] / np.nanmean(group_size_all[v])
            straight_line_values = straight_line_minimum_distances_with_interaction[
                v
            ] / np.nanmean(group_size_all[v])

            probabilities = []
            for k in range(len(pdf_edges[1:])):
                bin_ids = np.digitize(straight_line_values, pdf_edges[1:])
                observed_for_bin = observed_values[bin_ids == k]
                probabilities += [
                    np.sum(observed_for_bin < 1) / len(observed_for_bin)
                    if len(observed_for_bin)
                    else np.nan
                ]
            all_probabilities += [probabilities]
            ax.plot(probabilities, label=soc_binding_names[v], c=soc_binding_colors[v])

            data_bin[:, 1 + i : 2 + i] = np.array(probabilities)[..., None]

        pd.DataFrame(data_bin).to_csv(
            f"../data/plots/probabilities/{env_name_short}_probabilities.csv",
            index=False,
            header=False,
        )

        ax.legend()
        ax.set_ylabel("p(r_o < 1)")
        ax.set_xlabel("r_p (scaled with group size)")
        ax.set_title(f"{env_name_short}")
        # plt.show()

        # all_probabilities_without_nan = [
        #     [p for p in probabilities if p is not np.nan and p > 0]
        #     for probabilities in all_probabilities
        # ]
        # f, p = stats.f_oneway(*all_probabilities_without_nan)
        # print(all_probabilities_without_nan)
        # print(f"ANOVA probabilities: {p}")

        # print(" - Scaling by group breadth")
        # ps = []
        # fig, ax = plt.subplots()
        # for k in range(len(pdf_edges[1:])):
        #     values = []
        #     for i, v in enumerate(soc_binding_values):
        #         observed_values = observed_minimum_distances_with_interaction[
        #             v
        #         ] / np.nanmean(group_breadth_all[v])
        #         straight_line_values = straight_line_minimum_distances_with_interaction[
        #             v
        #         ] / np.nanmean(group_breadth_all[v])

        #         bin_ids = np.digitize(straight_line_values, pdf_edges[1:])
        #         observed_for_bin = observed_values[bin_ids == k]
        #         if len(observed_for_bin):
        #             values += [observed_for_bin]

        #     f, p = stats.f_oneway(*values)
        #     ps += [p]

        # ax.plot(ps)
        # ax.set_ylabel("p-values")
        # ax.set_xlabel("r_p (scaled with group breadth)")
        # ax.set_title(env_name_short)
        # ax.set_yscale("log")
        # plt.show()

        # all_probabilities = []
        # fig, ax = plt.subplots()
        # for i, v in enumerate(soc_binding_values):
        #     observed_values = observed_minimum_distances_with_interaction[
        #         v
        #     ] / np.nanmean(group_breadth_all[v])
        #     straight_line_values = straight_line_minimum_distances_with_interaction[
        #         v
        #     ] / np.nanmean(group_breadth_all[v])

        #     probabilities = []
        #     for k in range(len(pdf_edges[1:])):
        #         bin_ids = np.digitize(straight_line_values, pdf_edges[1:])
        #         observed_for_bin = observed_values[bin_ids == k]
        #         probabilities += [
        #             np.sum(observed_for_bin < 1) / len(observed_for_bin)
        #             if len(observed_for_bin)
        #             else np.nan
        #         ]
        #     all_probabilities += [probabilities]
        #     ax.plot(probabilities)
        # ax.set_ylabel("p(r_o < 1)")
        # ax.set_xlabel("r_p (scaled with group breadth)")
        # ax.set_title(env_name_short)
        # plt.show()

        # all_probabilities_without_nan = [
        #     [p for p in probabilities if p is not np.nan]
        #     for probabilities in all_probabilities
        # ]
        # f, p = stats.f_oneway(*all_probabilities_without_nan)
        # print(f"ANOVA probabilities: {p}")

        # # without scaling
        # print(" - No scaling")

        # bin_size = 4000 / 8
        # pdf_edges = np.linspace(0, 4000, 8 + 1)
        # bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        # ps = []
        # fig, ax = plt.subplots()
        # for k in range(len(pdf_edges[1:])):
        #     values = []
        #     for i, v in enumerate(soc_binding_values):
        #         observed_values = observed_minimum_distances_with_interaction[v]
        #         straight_line_values = straight_line_minimum_distances_with_interaction[
        #             v
        #         ]
        #         bin_ids = np.digitize(straight_line_values, pdf_edges[1:])
        #         observed_for_bin = observed_values[bin_ids == k]
        #         if len(observed_for_bin):
        #             values += [observed_for_bin]

        #     if len(values) > 1:
        #         f, p = stats.f_oneway(*values)
        #         ps += [p]
        #     else:
        #         ps += [np.nan]

        # ax.plot(bin_centers, ps)
        # ax.set_ylabel("p-values")
        # ax.set_xlabel("r_p")
        # ax.set_title(env_name_short)
        # ax.set_yscale("log")
        # plt.show()

        # all_probabilities = []
        # fig, ax = plt.subplots()
        # for i, v in enumerate(soc_binding_values):
        #     observed_values = observed_minimum_distances_with_interaction[v]
        #     straight_line_values = straight_line_minimum_distances_with_interaction[v]

        #     probabilities = []
        #     for k in range(len(pdf_edges[1:])):
        #         bin_ids = np.digitize(straight_line_values, pdf_edges[1:])
        #         observed_for_bin = observed_values[bin_ids == k]
        #         probabilities += [
        #             np.sum(observed_for_bin < 800) / len(observed_for_bin)
        #             if len(observed_for_bin)
        #             else np.nan
        #         ]
        #     all_probabilities += [probabilities]
        #     ax.plot(
        #         bin_centers,
        #         probabilities,
        #         label=soc_binding_names[v],
        #         c=soc_binding_colors[v],
        #     )

        # ax.legend()
        # ax.set_ylabel("p(r_o < 800)")
        # ax.set_xlabel("r_p")
        # ax.set_title(env_name_short)
        # plt.show()

        # all_probabilities_without_nan = [
        #     [p for p in probabilities if p is not np.nan]
        #     for probabilities in all_probabilities
        # ]
        # f, p = stats.f_oneway(*all_probabilities_without_nan)
        # print(f"ANOVA probabilities: {p}")
