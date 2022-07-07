from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.plot_utils import *
from pedestrians_social_binding.trajectory_utils import *
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

from utils import *

if __name__ == "__main__":

    group_ids = [
        1303590113040000,
        1311440213114403,
        1336090013361000,
        1324450113244600,
        1354510113545103,
        1357310013573200,
        1407330014073400,
        1516530115165400,
        1148390011484001,
        1242410012424101,
        1348140013481500,
        1405110014052700,
        1408380114083802,
        1507550015075501,
    ]

    non_group_ids = [
        13451200,
        11230100,
        12153002,
        16404600,
        13065201,
        13253700,
        13341600,
        13542600,
        13451200,
        14171901,
        14372100,
        14523801,
        15142201,
        12415100,
        13032900,
        13100200,
        15504400,
        16464605,
        16521701,
        13212300,
        13225700,
        13253700,
        13422600,
        13542600,
        14523801,
        15142201,
        15280201,
        12021200,
        13100200,
        15360700,
        15484001,
        15504400,
        16244800,
        16531502,
        13225700,
        13253700,
        13542600,
        14193500,
        14260500,
        14455500,
        14523801,
        15280201,
        15360700,
        15484001,
        16531502,
        13100500,
        14193500,
        14455500,
        14523801,
        15280201,
        11575500,
        15360700,
        15484001,
        14193500,
        14455500,
        14523801,
        11575500,
        15360700,
        14072001,
        14193500,
        14455500,
        14523801,
        11575500,
        15360700,
        14072001,
        14193500,
        14523801,
        11575500,
        15360700,
        14072001,
        14193500,
        14523801,
        11575500,
        15360700,
        11575500,
    ]

    env = Environment("diamor", data_dir="../../atc-diamor-pedestrians/data/formatted")

    days = DAYS_DIAMOR

    # thresholds_ped = get_pedestrian_thresholds("diamor")

    # groups = env.get_groups(
    #     ids=group_ids,
    # )

    # for group in groups:
    #     groups_as_indiv = group.get_as_individual()
    #     groups_as_indiv.plot_2D_trajectory()

    non_groups = env.get_pedestrians(
        ids=non_group_ids,
    )

    for ped in non_groups:
        trajectory = ped.get_trajectory()
        resampled_trajectory = resample_trajectory(trajectory, step=500)

        