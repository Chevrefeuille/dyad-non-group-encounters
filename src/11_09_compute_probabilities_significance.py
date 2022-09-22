from email import header
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import pandas as pd

from parameters import *
from utils import *


def proportions_ztest2(p1, n1, p2, n2):
    if n1 == 0 or n2 == 0:
        return np.nan, np.nan
    z = (p1 / n1 - p2 / n2) / (
        ((p1 + p2) / (n1 + n2)) * (1 - (p1 + p2) / (n1 + n2)) * (1 / n1 + 1 / n2)
    ) ** 0.5
    return z, stats.norm.sf(abs(z)) * 2


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
            f"../data/pickle/observed_minimum_distance_{env_name_short}_with_interaction_not_alone.pkl"
        )
        straight_line_minimum_distances_with_interaction = pickle_load(
            f"../data/pickle/straight_line_minimum_distance_{env_name_short}_with_interaction_not_alone.pkl"
        )
        group_size_all = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")
        group_breadth_all = pickle_load(
            f"../data/pickle/group_breadth_{env_name_short}.pkl"
        )

        bin_size = 4 / 8
        pdf_edges = np.linspace(0, 4, 8 + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        # with scaling
        for k in range(len(pdf_edges[1:])):
            statistics = {}
            contingency_table = np.zeros((3, len(soc_binding_values)))
            for i, v in enumerate(soc_binding_values):
                observed_values = observed_minimum_distances_with_interaction[
                    v
                ] / np.nanmean(group_size_all[v])
                straight_line_values = straight_line_minimum_distances_with_interaction[
                    v
                ] / np.nanmean(group_size_all[v])

                bin_ids = np.digitize(straight_line_values, pdf_edges[1:])
                observed_for_bin = observed_values[bin_ids == k]
                n_smaller = np.sum(observed_for_bin < 1)
                n = len(observed_for_bin)
                n_bigger = n - n_smaller
                p = n_smaller / n if n else np.nan
                contingency_table[0, i] = n_smaller
                contingency_table[1, i] = n_bigger
                contingency_table[2, i] = round(p, 2)
                statistics[v] = {
                    "n": len(observed_for_bin),
                    "np": np.sum(observed_for_bin < 1),
                }

            # print(statistics)
            print(f"# [{pdf_edges[k]}, {pdf_edges[k+1]}]")
            for i, v1 in enumerate(soc_binding_values):
                for j, v2 in enumerate(soc_binding_values):
                    if j <= i:
                        continue
                    n1, np1 = statistics[v1]["n"], statistics[v1]["np"]
                    n2, np2 = statistics[v2]["n"], statistics[v2]["np"]
                    # print(n1, np1, n2, np2)
                    p1 = round(np1 / n1, 2) if n1 else np.nan
                    p2 = round(np2 / n2, 2) if n2 else np.nan
                    samp1 = np.zeros(n1)
                    samp1[:np1] = 1
                    samp2 = np.zeros(n2)
                    samp2[:np2] = 1
                    if n1 == 0 or n2 == 0 or np1 == np2 == 0:
                        continue
                    # if n1 < 30 or n2 < 30:
                    #     _, p_val = stats.ttest_ind(samp1, samp2)
                    #     p_val = round(p_val, 3)
                    #     test = "t-test"
                    # else:
                    p_val = round(proportions_ztest2(np1, n1, np2, n2)[1], 3)
                    test = "z-test"
                    print(
                        f"{soc_binding_names[v1]} ({n1, np1, p1}) - {soc_binding_names[v2]} ({n2, np2, p2}): {p_val}, ({test})"
                    )
            # print(contingency_table)
            # remove columns with 0 values
            # print(stats.contingency.expected_freq(contingency_table))
            print(
                pd.DataFrame(
                    contingency_table,
                    columns=[soc_binding_names[v] for v in soc_binding_values],
                    index=["n < 1", "n > 1", "probability"],
                ).to_markdown()
            )
            contingency_table = contingency_table[:2, :]
            col_without_zeros = np.sum(contingency_table > 0, axis=0) == 2
            contingency_table_no_zeros = contingency_table[:, col_without_zeros]
            if len(contingency_table_no_zeros[0]):
                chi_stat, p, dof, expected = stats.chi2_contingency(contingency_table)
                # print(chi_stat, p, dof, expctd)
                # print(contingency_table)
                # print(expected)
                print(f"-> χ² test: {round(p,3)}")
