import numpy as np

UNDISTURBED_VICINITY = 10000
VICINITY = 4000
VICINITIES = [3000, 4000, 5000, 6000, 7000, 8000, 9000]

MIN_NUMBER_OBSERVATIONS = 16

SEGMENT_LENGTHS = [2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
# SEGMENT_LENGTHS = [4000]

# for the pair distributions
N_BINS_PAIR_DISTRIBUTION_R = 100
PAIR_DISTRIBUTION_MIN_R, PAIR_DISTRIBUTION_MAX_R = 0, 3000

N_BINS_PAIR_DISTRIBUTION_X = 100
PAIR_DISTRIBUTION_MIN_X, PAIR_DISTRIBUTION_MAX_X = -3000, 3000

N_BINS_PAIR_DISTRIBUTION_Y = 100
PAIR_DISTRIBUTION_MIN_Y, PAIR_DISTRIBUTION_MAX_Y = -3000, 3000

N_BINS_PAIR_DISTRIBUTION_THETA = 100
PAIR_DISTRIBUTION_MIN_THETA, PAIR_DISTRIBUTION_MAX_THETA = -np.pi, np.pi

# for the time to collisions
N_BINS_PAIR_DISTRIBUTION_T_COLL = 32
PAIR_DISTRIBUTION_MIN_T_COLL, PAIR_DISTRIBUTION_MAX_T_COLL = 0, 10  # 10 sec

# for the group breadth distributions
N_BINS_BREADTH_DISTRIBUTION = 32
BREADTH_DISTRIBUTION_MIN, BREADTH_DISTRIBUTION_MAX = 400, 2000

# for the relative orientations distributions
N_BINS_ORIENTATION_DISTRIBUTION = 64
ORIENTATION_DISTRIBUTION_MIN, ORIENTATION_DISTRIBUTION_MAX = -np.pi, np.pi

# for the turning angles distributions
N_BINS_TURNING_DISTRIBUTION = 64
TURNING_DISTRIBUTION_MIN, TURNING_DISTRIBUTION_MAX = -np.pi, np.pi


# for the 2D distributions
N_BINS_2D_RX = 64
N_BINS_2D_RY = 64
RX_MIN, RX_MAX = -5000, 5000
RY_MIN, RY_MAX = -5000, 5000

# for ro
N_BINS_RO = 16
RO_MIN, RO_MAX = 0, 4000
# for rp
N_BINS_RP = 16
RP_MIN, RP_MAX = 0, 4000

# velocity threshold
VEL_MIN = 500
VEL_MAX = 3000

# turning angle threshold
THETA_MAX = np.pi / 3

# minimum walked distance threshold
D_MIN = 4000

# group breath threshold
GROUP_BREADTH_MIN = 100
GROUP_BREADTH_MAX = 5000

# velocity field
VEL_FIELD_CELL_SIZE = 100

# for the random sub-trajectory sizes
N_BINS_RND_TRAJ_SIZE = 4
RND_TRAJ_SIZE_MIN, RND_TRAJ_SIZE_MAX = 1500, 5500

# for the distributions of trajectories sizes
N_BINS_TRAJ_SIZE = 20
TRAJ_SIZE_MIN, TRAJ_SIZE_MAX = 0, 6000

# for the straightness index distributions
N_BINS_STRAIGHTNESS_INDEX_DISTRIBUTION = 20
STRAIGHTNESS_INDEX_DISTRIBUTION_MIN, STRAIGHTNESS_INDEX_DISTRIBUTION_MAX = 0.96, 1

# for the scaled maximum lateral deviation distributions
N_BINS_SCALED_MAX_LAT_DEV_DISTRIBUTION = 20
SCALED_MAX_LAT_DEV_DISTRIBUTION_MIN, SCALED_MAX_LAT_DEV_DISTRIBUTION_MAX = 0, 0.15

# for the sinuosity distributions
N_BINS_SINUOSITY = 20
SINUOSITY_DISTRIBUTION_MIN, SINUOSITY_DISTRIBUTION_MAX = 0, 0.03

DEFLECTIONS_DISTRIBUTIONS_PARAMETERS = {
    "straightness_index": {
        "n_bins": N_BINS_STRAIGHTNESS_INDEX_DISTRIBUTION,
        "min": STRAIGHTNESS_INDEX_DISTRIBUTION_MIN,
        "max": STRAIGHTNESS_INDEX_DISTRIBUTION_MAX,
    },
    "sinuosity": {
        "n_bins": N_BINS_SINUOSITY,
        "min": SINUOSITY_DISTRIBUTION_MIN,
        "max": SINUOSITY_DISTRIBUTION_MAX,
    },
    "maximum_scaled_lateral_deviation": {
        "n_bins": N_BINS_SCALED_MAX_LAT_DEV_DISTRIBUTION,
        "min": SCALED_MAX_LAT_DEV_DISTRIBUTION_MIN,
        "max": SCALED_MAX_LAT_DEV_DISTRIBUTION_MAX,
    },
}


LIMITS = {
    "straightness_index": [0.97, 1],
    "sinuosity": [0, 0.01],
    "maximum_scaled_lateral_deviation": [0.02, 0.06],
}


COLORS_SOC_REL = ["black", "red", "blue", "green", "orange"]
COLORS_INTERACTION = ["blue", "red", "green", "orange"]

LINE_TYPES = {"group": "dashed", "non_group": "solid", "group_members": "dashdot"}
