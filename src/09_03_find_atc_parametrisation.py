from pedestrians_social_binding.environment import Environment
from pedestrians_social_binding.utils import *

import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from scipy import interpolate
from scipy.spatial.distance import cdist

if __name__ == "__main__":

    atc = Environment(
        name="atc:corridor", data_dir="../../atc-diamor-pedestrians/data/formatted"
    )
    background_path = "../data/images/velocity_field_atc.png"
    background_image = Image.open(background_path)

    boundaries = atc.get_boundaries()

    fig, ax = plt.subplots()
    ax.imshow(background_image, extent=boundaries)

    # x_vert = np.arange(5000, 50000, 2500)
    # for x in x_vert:
    #     ax.plot([x_vert, x_vert], [boundaries[2], boundaries[3]], c="black")

    # Line in the middle
    points_middle = np.array(
        [
            [5000, 2500],
            # [7500, -460],
            [10000, -3600],
            # [12500, -6400],
            [15000, -9300],
            # [17500, -11700],
            [20000, -13500],
            # [22500, -14700],
            [25000, -15600],
            # [27500, -16700],
            [30000, -17400],
            # [32500, -18400],
            [35000, -19100],
            # [37500, -19900],
            [40000, -20900],
            # [42500, -22400],
            [45000, -23300],
            [47500, -24700],
        ]
    )
    points_top = np.array(
        [
            [5000, 7000],
            # [7500, 4400],
            [10000, -110],
            # [12500, -3250],
            [15000, -6400],
            # [17500, -9100],
            [20000, -11000],
            # [22500, -12900],
            [25000, -13600],
            # [27500, -14800],
            [30000, -15400],
            # [32500, -16300],
            [35000, -16600],
            # [37500, -17000],
            [40000, -16900],
            # [42500, -17300],
            [45000, -17700],
            [47500, -18000],
        ]
    )
    points_bottom = np.array(
        [
            [5000, -1400],
            # [7500, -3300],
            [10000, -6500],
            # [12500, -9000],
            [15000, -12400],
            # [17500, -14200],
            [20000, -15600],
            # [22500, -17000],
            [25000, -18000],
            # [27500, -18600],
            [30000, -19400],
            # [32500, -20400],
            [35000, -21800],
            # [37500, -23000],
            [40000, -25000],
            # [42500, -26800],
            [45000, -26800],
            [47500, -26800],
        ]
    )

    # tck_middle, _ = interpolate.splprep([points_middle[:, 0], points_middle[:, 1]], s=0)
    # unew_middle = np.arange(0, 1.01, 0.01)
    # spline_middle = interpolate.splev(unew_middle, tck_middle)

    # ax.scatter(points_middle[:, 0], points_middle[:, 1], c="black")
    # ax.plot(spline_middle[0], spline_middle[1], c="black")

    # tck_top, _ = interpolate.splprep([points_top[:, 0], points_top[:, 1]], s=0)
    # unew_top = np.arange(0, 1.01, 0.01)
    # spline_top = interpolate.splev(unew_top, tck_top)

    # ax.scatter(points_top[:, 0], points_top[:, 1], c="black")
    # ax.plot(spline_top[0], spline_top[1], c="black")

    # tck_bottom, _ = interpolate.splprep([points_bottom[:, 0], points_bottom[:, 1]], s=0)
    # unew_bottom = np.arange(0, 1.01, 0.01)
    # spline_bottom = interpolate.splev(unew_bottom, tck_bottom)

    # ax.scatter(points_bottom[:, 0], points_bottom[:, 1], c="black")
    # ax.plot(spline_bottom[0], spline_bottom[1], c="black")

    # interpolate between the splines
    t = np.arange(0, 1.01, 0.01)
    points_interp_1 = np.tensordot(t, points_middle, axes=0) + np.tensordot(
        1 - t, points_top, axes=0
    )
    points_interp_2 = (
        np.tensordot(t, points_bottom, axes=0)
        + np.tensordot(1 - t, points_middle, axes=0)
    )[1:, ...]

    points_interp = np.concatenate((points_interp_1, points_interp_2), axis=0)

    n_interp = len(points_interp)

    splines_list = []

    unew_interp = np.arange(0, 1.01, 0.001)
    n_points_interp = len(unew_interp)
    for i in range(n_interp):
        points = points_interp[i, ...]

        tck_interp, _ = interpolate.splprep([points[:, 0], points[:, 1]], s=0)
        spline_interp = interpolate.splev(unew_interp, tck_interp)
        splines_list += [spline_interp]

        # ax.scatter(line_interp[:, 0], line_interp[:, 1], c="black")
        # ax.plot(spline_interp[0], spline_interp[1], c="black")

    splines = np.stack(splines_list)
    points = np.transpose(splines, axes=(0, 2, 1)).reshape(
        n_interp * n_points_interp, 2
    )

    pickle_save("../data/pickle/splines_atc.pkl", splines)

    random_x = np.random.randint(boundaries[0], boundaries[1])
    bottom = splines[-1, ...]
    top = splines[0, ...]

    argmin_bottom = np.argmin(np.abs(bottom[0, :] - random_x))
    min_y = bottom[1, argmin_bottom]

    argmin_top = np.argmin(np.abs(top[0, :] - random_x))
    max_y = top[1, argmin_top]

    random_y = np.random.randint(int(min_y), int(max_y))

    random_start = np.array([[random_x, random_y]])

    dist = cdist(random_start, points)

    print(np.min(dist))

    spline_row = np.argmin(dist) // n_points_interp

    ax.scatter([random_start[:, 0]], [random_start[:, 1]], c="black")
    ax.plot(splines[spline_row, 0, :], splines[spline_row, 1, :], c="black")
    plt.show()
