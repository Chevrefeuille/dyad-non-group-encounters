from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from parameters import *
from utils import *

import scipy.stats as stats
import statsmodels.api as sm


if __name__ == "__main__":
    count_normal = 0
    count_equal_variance = 0
    count_not_normal = 0
    count_not_equal_variance = 0
    count_anova_ok = 0
    count_anova_not_ok = 0
    for env_name in ["atc:corridor", "diamor:corridor"]:
        env_name_short = env_name.split(":")[0]

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        # if "atc" in env_name:
        #     soc_binding_values = [1, 2]

        observed_minimum_distances_with_interaction = pickle_load(
            f"../data/pickle/tgf_observed_minimum_distance_{env_name_short}_with_interaction.pkl"
        )
        straight_line_minimum_distances_with_interaction = pickle_load(
            f"../data/pickle/tgf_straight_line_minimum_distance_{env_name_short}_with_interaction.pkl"
        )

        group_size_all = pickle_load(f"../data/pickle/group_size_{env_name_short}.pkl")
        group_breadth_all = pickle_load(
            f"../data/pickle/group_breadth_{env_name_short}.pkl"
        )

        values_per_bin = []

        N_BINS = 8
        bin_size = 4 / N_BINS
        pdf_edges = np.linspace(0, 4, N_BINS + 1)
        bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

        for k in range(N_BINS):
            bin_values = []
            for i, v in enumerate(soc_binding_values):
                rb = straight_line_minimum_distances_with_interaction[v] / np.nanmean(
                    group_size_all[v]
                )
                r0 = observed_minimum_distances_with_interaction[v] / np.nanmean(
                    group_size_all[v]
                )
                bin_ids = np.digitize(rb, pdf_edges[1:])

                bin_values += [r0[bin_ids == k]]
            values_per_bin += [bin_values]

        p_values = []
        for i in range(len(values_per_bin)):
            #     all_normal = True
            #     one_normal = False
            #     for v in values_per_bin[i]:
            #         if len(v) >= 8:
            #             k2_normal, p_normal = stats.normaltest(v)
            #             if p_normal > 0.05:
            #                 one_normal = True
            #             else:
            #                 all_normal = False

            #     if all_normal:
            #         count_normal += 1
            #     else:
            #         count_not_normal += 1
            # print("not normal")
            # print(f"bin {i}: p-normal {round(p_normal,3)}")
            # print(f"bin {i}: p-levene {round(p_levene,3)}")

            stat_levene, p_levene = stats.levene(*values_per_bin[i])
            # if p_levene > 0.05:
            #     count_equal_variance += 1
            #     if all_normal:
            #         count_anova_ok += 1
            #         anova_ok = True
            #     else:
            #         count_anova_not_ok += 1
            # else:
            #     count_not_equal_variance += 1
            #     count_anova_not_ok += 1

            # compute residuals
            residuals = []
            for v in values_per_bin[i]:
                for value in v:
                    residuals += [value - np.mean(v)]
            # fig = sm.qqplot(np.array(residuals), line="45")
            # plt.show()
            k2_normal, p_normal = stats.normaltest(residuals)
            print(f"bin {i}: p-normal {round(p_normal,3)}")
            if p_normal > 0.05:
                count_normal += 1
            else:
                count_not_normal += 1
            if p_levene > 0.05:
                count_equal_variance += 1
            else:
                count_not_equal_variance += 1

            if p_levene > 0.05 and p_normal > 0.05:
                count_anova_ok += 1
            else:
                count_anova_not_ok += 1

            F, p = stats.f_oneway(*values_per_bin[i])
            # print(f"bin {i}: {round(p,3)}")
            p_values += [p]

        data = np.array([bin_centers, p_values]).T
        # pd.DataFrame(data).to_csv(
        #     f"../data/plots/tgf/distance_anovas/{env_name_short}_pvalues.csv",
        #     index=False,
        #     header=False,
        # )
        fig, ax = plt.subplots()
        ax.plot(bin_centers, p_values)
        ax.set_ylim(0.0001, 1)
        ax.plot([0, 4], [0.05, 0.05], c="red")
        ax.set_yscale("log")
        ax.grid(color="lightgray", linestyle="--", linewidth=0.5)
        ax.set_ylabel(f"p-value")
        ax.set_xlabel("r_b (scaled with group size)")
        ax.set_title(f"p-value")
        # fig.savefig(
        #     f"../data/figures/intrusion/scattering_p_values_{env_name_short}.png",
        #     dpi=300,
        # )
        # plt.show()

    print(count_equal_variance, count_not_equal_variance)
    print(count_normal, count_not_normal)
    print(
        f"percentage equal variance: {count_equal_variance / (count_equal_variance + count_not_equal_variance)}"
    )
    print(f"percentage normal: {count_normal / (count_normal + count_not_normal)}")
    print(
        f"percentage anova ok: {count_anova_ok / (count_anova_ok + count_anova_not_ok)}"
    )
