import matplotlib.pyplot as plt
import numpy as np
from pedestrians_social_binding.trajectory_utils import *
import pandas as pd
from bezier import Bezier

if __name__ == "__main__":

    t_points = np.arange(0, 1.01, 0.01)

    # straight line
    points_straight = np.array([[0, 0], [8, 0]])
    curve_straight = Bezier.Curve(t_points, points_straight)

    # deviation on one side
    points_dev_one_side = np.array([[0, 0], [1, 2], [7, 2], [8, 0]])
    curve_dev_one_side = Bezier.Curve(t_points, points_dev_one_side)

    points_dev_one_side_small = np.array([[0, 0], [1, 0.5], [7, 0.5], [8, 0]])
    curve_dev_one_side_small = Bezier.Curve(t_points, points_dev_one_side_small)

    # deviation on both side
    points_dev_both_sides = np.array([[0, 0], [0, 2], [6, 2], [2, -2], [8, -2], [8, 0]])
    curve_dev_both_sides = Bezier.Curve(t_points, points_dev_both_sides)

    # oscillating
    f = 6
    s = 1 / 6.66
    curve_oscillating = np.stack(
        (t_points * 8, np.sin(2 * np.pi * f * t_points) * s), axis=1
    )

    for measure in [
        "straightness_index",
        "sinuosity",
        "maximum_scaled_lateral_deviation",
        "maximum_lateral_deviation",
    ]:

        straightness_straight = compute_deflection(curve_straight, measure=measure)
        straightness_dev_one_side = compute_deflection(
            curve_dev_one_side, measure=measure
        )
        straightness_dev_one_side_small = compute_deflection(
            curve_dev_one_side_small, measure=measure
        )
        straightness_dev_both_sides = compute_deflection(
            curve_dev_both_sides, measure=measure
        )
        straightness_oscillating = compute_deflection(
            curve_oscillating, measure=measure
        )

        print(
            measure,
            straightness_straight,
            straightness_dev_one_side,
            straightness_dev_one_side_small,
            straightness_dev_both_sides,
            straightness_oscillating,
        )

    data = np.array(
        [
            curve_straight[:, 0],
            curve_straight[:, 1],
            curve_dev_one_side[:, 0],
            curve_dev_one_side[:, 1],
            curve_dev_one_side_small[:, 0],
            curve_dev_one_side_small[:, 1],
            curve_dev_both_sides[:, 0],
            curve_dev_both_sides[:, 1],
            curve_oscillating[:, 0],
            curve_oscillating[:, 1],
        ]
    ).T
    pd.DataFrame(data).to_csv(
        f"../data/plots/toy_example/measures.csv",
        index=False,
        header=False,
    )

    # plt.figure()
    # plt.plot(curve_straight[:, 0], curve_straight[:, 1])
    # plt.plot(curve_dev_one_side[:, 0], curve_dev_one_side[:, 1])
    # plt.plot(curve_dev_one_side_small[:, 0], curve_dev_one_side_small[:, 1])
    # plt.plot(curve_dev_both_sides[:, 0], curve_dev_both_sides[:, 1])
    # plt.plot(curve_oscillating[:, 0], curve_oscillating[:, 1])
    # # plt.plot(
    # #     points_oscillating[:, 0],  # x-coordinates.
    # #     points_oscillating[:, 1],  # y-coordinates.
    # #     "ro:",  # Styling (red, circles, dotted).
    # # )
    # plt.axis("scaled")
    # plt.grid()
    # plt.show()

    turning_angles_straight = compute_turning_angles(curve_straight)
    turning_angles_dev_one_side = compute_turning_angles(curve_dev_one_side)
    turning_angles_dev_one_side_small = compute_turning_angles(curve_dev_one_side_small)
    turning_angles_dev_both_sides = compute_turning_angles(curve_dev_both_sides)
    turning_angles_oscillating = compute_turning_angles(curve_oscillating)

    # plt.plot(np.linspace(0, 1, len(turning_angles_straight)), turning_angles_straight)
    # plt.plot(
    #     np.linspace(0, 1, len(turning_angles_dev_one_side)), turning_angles_dev_one_side
    # )
    # plt.plot(
    #     np.linspace(0, 1, len(turning_angles_dev_one_side_small)),
    #     turning_angles_dev_one_side_small,
    # )
    # plt.plot(
    #     np.linspace(0, 1, len(turning_angles_dev_both_sides)),
    #     turning_angles_dev_both_sides,
    # )
    # plt.plot(
    #     np.linspace(0, 1, len(turning_angles_oscillating)), turning_angles_oscillating
    # )
    # plt.show()

    data = np.array(
        [
            np.linspace(0, 1, len(turning_angles_straight)),
            turning_angles_straight,
            turning_angles_dev_one_side,
            turning_angles_dev_one_side_small,
            turning_angles_dev_both_sides,
            turning_angles_oscillating,
        ]
    ).T
    pd.DataFrame(data).to_csv(
        f"../data/plots/toy_example/turning_angles.csv",
        index=False,
        header=False,
    )

    # D_MIN = -np.pi / 300
    # D_MAX = np.pi / 300
    # n_pdf_bins = 40
    # pdf_edges = np.linspace(D_MIN, D_MAX, n_pdf_bins)
    # bin_size = (D_MAX - D_MIN) / n_pdf_bins
    # bin_centers = 0.5 * (pdf_edges[0:-1] + pdf_edges[1:])

    # histog_straight = np.histogram(turning_angles_straight, pdf_edges)[0]
    # pdf_straight = histog_straight / sum(histog_straight)

    # histog_dev_one_side = np.histogram(turning_angles_dev_one_side, pdf_edges)[0]
    # pdf_dev_one_side = histog_dev_one_side / sum(histog_dev_one_side)

    # histog_dev_one_side_small = np.histogram(
    #     turning_angles_dev_one_side_small, pdf_edges
    # )[0]
    # pdf_dev_one_side_small = histog_dev_one_side_small / sum(histog_dev_one_side_small)

    # histog_dev_both_sides = np.histogram(turning_angles_dev_both_sides, pdf_edges)[0]
    # pdf_both_sides = histog_dev_both_sides / sum(histog_dev_both_sides)

    # histog_oscillating = np.histogram(turning_angles_oscillating, pdf_edges)[0]
    # pdf_oscillating = histog_oscillating / sum(histog_oscillating)

    # data = np.array(
    #     [
    #         pdf_edges[:-1],
    #         pdf_straight,
    #         pdf_dev_one_side,
    #         pdf_dev_one_side_small,
    #         pdf_both_sides,
    #         pdf_oscillating,
    #     ]
    # )
    # data = data.T
    # with open(f"figures/toy_example/pdfs.txt", "w+") as f:
    #     np.savetxt(
    #         f,
    #         data,
    #         fmt=[
    #             "%0.5f",
    #             "%0.5f",
    #             "%0.5f",
    #             "%0.5f",
    #             "%0.5f",
    #             "%0.5f",
    #         ],
    #     )

    # plt.plot(
    #     pdf_edges[:-1],
    #     pdf_straight,
    #     label=f"straigth",
    # )
    # plt.plot(
    #     pdf_edges[:-1],
    #     pdf_dev_one_side,
    #     label=f"one side",
    # )
    # plt.plot(
    #     pdf_edges[:-1],
    #     pdf_dev_one_side_small,
    #     label=f"one side small",
    # )
    # plt.plot(
    #     pdf_edges[:-1],
    #     pdf_both_sides,
    #     label=f"both sides",
    # )
    # plt.plot(
    #     pdf_edges[:-1],
    #     pdf_oscillating,
    #     label=f"oscillating",
    # )
    # plt.legend()
    # plt.show()
