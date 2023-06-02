import numpy as np
import matplotlib.pyplot as plt

from pedestrians_social_binding.trajectory_utils import (
    compute_straightness_index,
    compute_maximum_lateral_deviation,
)
from bezier import Bezier

if __name__ == "__main__":

    control_points = np.array([[0, 0], [2, 0], [3, 3], [7, 20], [8, 0], [12, 0]])

    n_points = np.arange(3, 20, 1)
    tortuosities = []
    deviations = []

    fig, axes = plt.subplot_mosaic(
        [["top", "top"], ["left", "right"]], constrained_layout=True
    )

    for n in n_points:
        t_points = np.linspace(0, 1, n)
        trajectory = Bezier.Curve(t_points, control_points)

        if n == n_points[-1]:
            axes["top"].scatter(trajectory[:, 0], trajectory[:, 1], s=2)

        s = compute_straightness_index(trajectory)
        tortuosities += [s]

        d = compute_maximum_lateral_deviation(trajectory, scaled=False)
        # print(d)
        deviations += [d]
        # print(f"- {n_points} points → {s}")

    deviations = np.array(deviations)
    tortuosities = np.array(tortuosities)

    perc_deviations = (deviations - deviations[-1]) / deviations[-1]
    perc_tortuosities = (tortuosities - tortuosities[-1]) / tortuosities[-1]

    axes["top"].set_aspect("equal")

    axes["left"].plot(n_points, tortuosities)
    axes["left"].set_xlabel("# points")
    axes["left"].set_ylim([0, 1])
    axes["left"].set_ylabel("tortuosity")

    axes["right"].plot(n_points, deviations)
    axes["right"].set_xlabel("# points")
    axes["right"].set_ylim(bottom=0)
    axes["right"].set_ylabel("deviation")

    plt.show()
