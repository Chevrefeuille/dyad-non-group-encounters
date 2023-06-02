from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *
from pedestrians_social_binding.trajectory_utils import *


import numpy as np
import scipy.stats as stats

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
        tortuosity = pickle_load(f"../data/pickle/{env_name_short}_tortuosity.pkl")
        rbs = pickle_load(f"../data/pickle/{env_name_short}_rbs.pkl")

        intensities = [0, 1, 2, 3]
        for measure, values in zip(["dev"], [deviations]):
            # print(f"-----------\n {measure}")

            # interaction vs no-interaction for non-group
            fig, axes = plt.subplots(2, 1)

            print("--- non groups ---")

            dev_non_groups = []
            all_dev_non_groups = []
            for i in intensities:
                n = len(values[i]["non_group"])
                mean = round(np.mean(values[i]["non_group"]), 1)
                std = round(np.std(values[i]["non_group"]), 2)
                all_dev_non_groups += values[i]["non_group"]
                dev_non_groups += [np.array(values[i]["non_group"])]
                print(f" - intensity {i} → {mean} ± {std} ({n})")

            axes[0].boxplot(dev_non_groups, labels=intensities, sym="")
            axes[0].set_title("Deviation for non-groups")

            F, p = stats.f_oneway(*dev_non_groups)
            print(f"p-values for 0-1-2-3: {p: .2e}")

            print("--- groups ---")
            dev_groups = []
            all_dev_groups = []
            for i in intensities:
                v = values[i]["ext"] + values[i]["int"]
                n = len(v)
                mean = round(np.mean(v), 1)
                std = round(np.std(v), 2)
                dev_groups += [np.array(v)]
                all_dev_groups += v
                print(f" - intensity {i} → {mean} ± {std} ({n})")

            axes[1].boxplot(dev_groups, labels=intensities, sym="")
            axes[1].set_title("Deviation for groups")

            F, p = stats.f_oneway(*dev_groups)
            print(f"p-values for 0-1-2-3: {p: .2e}")

            # plt.show()

            print("--- groups vs non-groups ---")
            mean_groups = round(np.mean(all_dev_groups), 1)
            std_groups = round(np.std(all_dev_groups), 2)
            mean_non_groups = round(np.mean(all_dev_non_groups), 1)
            std_non_groups = round(np.std(all_dev_non_groups), 2)
            print(f"all groups → {mean_groups} ± {std_groups} ({len(all_dev_groups)})")
            print(
                f"all non-groups → {mean_non_groups} ± {std_non_groups} ({len(all_dev_non_groups)})"
            )
            F, p = stats.f_oneway(all_dev_non_groups, all_dev_groups)
            print(f"p-values all groups/non-groups: {p :.2e}")

            for i in intensities:
                v_groups = values[i]["ext"] + values[i]["int"]
                v_non_groups = values[i]["non_group"]
                F, p = stats.f_oneway(v_groups, v_non_groups)
                print(f" - intensity {i} → p-values groups/non-groups: {p :.2e}")

            print("--- difference non-group - group ---")
            differences = []
            for i in intensities:
                v_int = (np.array(values[i]["non_group"]) - np.array(values[i]["int"])).tolist()  # type: ignore
                v_ext = (np.array(values[i]["non_group"]) - np.array(values[i]["ext"])).tolist()  # type: ignore
                v = v_int + v_ext
                differences += [v]
                mean = round(np.mean(v), 1)
                std = round(np.std(v), 2)
                n = len(v)
                print(f" - intensity {i} → {mean} ± {std} ({n})")
            F, p = stats.f_oneway(*differences)
            print(f"p-values for 0-1-2-3: {p: .2e}")

            # dev_non_group_no_interaction = values[0]["non_group"]
            # dev_non_group_interaction = []
            # for i in [1, 2, 3]:
            #     dev_non_group_interaction += values[i]["non_group"]

            # print(len(dev_non_group_no_interaction), len(dev_non_group_interaction))
            # F, p = stats.f_oneway(
            #     dev_non_group_no_interaction, dev_non_group_interaction
            # )

            # print(
            #     f"dev non-group :\n  - 0: {np.nanmean(dev_non_group_no_interaction)}\n  - 3: {np.nanmean(dev_non_group_interaction)}\n  - p-value: {p}"
            # )

            # # interaction vs no-interaction for group
            # dev_group_no_interaction = values[0]["ext"] + values[0]["int"]
            # dev_group_interaction = []
            # for i in [1, 2, 3]:
            #     dev_group_interaction += values[i]["ext"] + values[i]["int"]

            # print(len(dev_group_no_interaction), len(dev_group_interaction))
            # F, p = stats.f_oneway(dev_group_no_interaction, dev_group_interaction)

            # print(
            #     f"dev group :\n  - 0: {np.nanmean(dev_group_no_interaction)}\n  - 3: {np.nanmean(dev_group_interaction)}\n  - p-value: {p}"
            # )

            # # int vs ext for group
            # dev_ext = (
            #     values[0]["ext"]
            #     + values[1]["ext"]
            #     + values[2]["ext"]
            #     + values[3]["ext"]
            # )
            # dev_int = (
            #     values[0]["int"]
            #     + values[1]["int"]
            #     + values[2]["int"]
            #     + values[3]["int"]
            # )
            # F, p = stats.f_oneway(dev_ext, dev_int)
            # print(
            #     f"dev no interaction ext-int :\n  - ext: {np.nanmean(dev_ext)}\n  - int: {np.nanmean(dev_int)}\n  - p-value: {p}"
            # )
