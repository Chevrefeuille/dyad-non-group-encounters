from pedestrians_social_binding.constants import *
from pedestrians_social_binding.utils import *
from parameters import *
from utils import *
import numpy as np
from pedestrians_social_binding.environment import Environment


from tqdm import tqdm


""" The goal of this script is to plot the deflection of pedestrians in the corridor environment
    """

LIMITS = {
    "maximum_scaled_lateral_deviation": [0.02, 0.06],
}

if __name__ == "__main__":

    for env_name in ["diamor:corridor"]:
        env_name_short = env_name.split(":")[0]

        env = Environment(
            env_name, data_dir="../../atc-diamor-pedestrians/data/formatted"
        )

        days = get_all_days(env_name)
        deviation = pickle_load(
            f"../data/pickle/{env_name_short}no_encounters_deviations.pkl"
        )
        soc_binding_type, soc_binding_names, soc_binding_values, colors = get_social_values(
            env_name
        )
        thresholds_ped = get_pedestrian_thresholds(env_name)
        thresholds_group = get_groups_thresholds()

        for day in days:
            print(f"Day {day}:")

            non_groups = env.get_pedestrians(
                days=[day],
                no_groups=True,
                thresholds=thresholds_ped,
                sampling_time=500,
            )

            groups = env.get_groups(
                days=[day],
                size=2,
                ped_thresholds=thresholds_ped,
                group_thresholds=thresholds_group,
                sampling_time=500,
            )

            for group in tqdm(groups):
                group_id = group.get_id()

                print("group_id", group_id)

                if(str(group_id) not in(deviation["group"].keys())):
                    print("hey")
                    continue

                soc_binding = group.get_annotation(soc_binding_type)
                if soc_binding not in soc_binding_values:
                    print("bey")
                    continue



                color = colors[soc_binding]

                ax = plt.subplots()

                intermediate = deviation["group"][str(group_id)]["max_dev"]
                print("intermediate", intermediate)
                trajectory = intermediate["position of max lateral deviation"]
                print("trajectory", trajectory)
                x, y = trajectory[1], trajectory[2]
                print("x", x)
                print("y", y)
                ax.scatter(x / 1000, y / 1000, c=color, s=10)
                plt.show()











        # for measure in DEFLECTION_MEASURES:
        #     deflections_per_length_group = []
        #     deflections_per_length_group_members = []
        #     deflections_per_length_non_group = []
        #     for segment_length in SEGMENT_LENGTHS:
        #         all_deflections_group = deflections["group"][measure][segment_length]
        #         all_deflections_group_members = deflections["group_members"][measure][
        #             segment_length
        #         ]
        #         all_deflections_non_group = deflections["non_group"][measure][
        #             segment_length
        #         ]
        #         deflections_per_length_group += [np.nanmean(all_deflections_group)]
        #         deflections_per_length_group_members += [
        #             np.nanmean(all_deflections_group_members)
        #         ]
        #         deflections_per_length_non_group += [
        #             np.nanmean(all_deflections_non_group)
        #         ]
        #     plt.plot(SEGMENT_LENGTHS, deflections_per_length_group, label="group")
        #     plt.plot(
        #         SEGMENT_LENGTHS,
        #         deflections_per_length_group_members,
        #         label="group_members",
        #     )
        #     plt.plot(
        #         SEGMENT_LENGTHS, deflections_per_length_non_group, label="non group"
        #     )
        #     plt.ylim(LIMITS[measure])
        #     plt.title(measure)
        #     plt.legend()
        #     # plt.show()

        #     plt.savefig(
        #         f"../data/figures/deflection/{env_name_short}_{measure}_no_interaction.png"
        #     )
        #     plt.clf()
