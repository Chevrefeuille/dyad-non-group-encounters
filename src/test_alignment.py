from pedestrians_social_binding.utils import *
from pedestrians_social_binding.plot_utils import *

import numpy as np
from bezier import Bezier


if __name__ == "__main__":

    # pos_A = np.zeros((20, 2))
    # pos_A[:, 0] = np.linspace(-3, 3, 20) * 1000
    # pos_B = np.ones((20, 2)) * 1000
    # pos_B[:, 0] = np.linspace(-3, 3, 20)[::-1] * 1000

    # t = np.linspace(0, 1, len(pos_A))

    # v_A = (pos_A[1:] - pos_A[:-1]) / (t[1:] - t[:-1])[:, None]
    # v_B = (pos_B[1:] - pos_B[:-1]) / (t[1:] - t[:-1])[:, None]

    # traj_A = np.zeros((len(t), 7))
    # traj_A[:, 0] = t
    # traj_A[:, 1:3] = pos_A
    # traj_A[1:, 5:7] = v_A

    # traj_B = np.zeros((len(t), 7))
    # traj_B[:, 0] = t
    # traj_B[:, 1:3] = pos_B
    # traj_A[1:, 5:7] = v_B

    # plot_animated_2D_trajectories([traj_A, traj_B], vel=True)

    # traj_A_aligned, [traj_B_aligned] = align_trajectories_at_origin(traj_A, [traj_B])

    # plot_static_2D_trajectories([traj_A_aligned, traj_B_aligned])

    # rp = compute_straight_line_minimum_distance(traj_B)
    # ro = compute_observed_minimum_distance(traj_B, interpolate=True)
    # print(ro, rp)

    # # more complex curve
    # t = np.linspace(0, 1, 100)

    # # points_A = np.array([[0, 0], [1, 2], [3, 2], [4, 0]]) * 1000
    # # pos_A = Bezier.Curve(t, points_A)
    # pos_A = np.zeros((100, 2))
    # pos_A[:, 0] = np.linspace(0, 4, 100) * 1000
    # v_A = (pos_A[1:] - pos_A[:-1]) / ((t[1:] - t[:-1])[:, None] * 1000)
    # traj_A = np.zeros((len(t), 7))
    # traj_A[:, 0] = t * 1000
    # traj_A[:, 1:3] = pos_A
    # traj_A[1:, 5:7] = v_A

    # points_B = np.array([[4, 0], [3, -1], [1, -1], [0, 0]]) * 1000
    # pos_B = Bezier.Curve(t, points_B)
    # v_B = (pos_B[2:] - pos_B[:-2]) / ((t[2:] - t[:-2])[:, None] * 1000)
    # traj_B = np.zeros((len(t), 7))
    # traj_B[:, 0] = t * 1000
    # traj_B[:, 1:3] = pos_B
    # traj_B[2:, 5:7] = v_B

    # # plot_animated_2D_trajectories([traj_A, traj_B])
    # plot_animated_2D_trajectories([traj_B, traj_A])

    # # traj_A_aligned, [traj_B_aligned] = align_trajectories_at_origin(traj_A, [traj_B])
    # traj_B_aligned, [traj_A_aligned] = align_trajectories_at_origin(traj_B, [traj_A])

    # # plot_animated_2D_trajectories([traj_A_aligned, traj_B_aligned])
    # plot_animated_2D_trajectories([traj_B_aligned, traj_A_aligned])
    # rp = compute_straight_line_minimum_distance(traj_B_aligned)
    # ro = compute_observed_minimum_distance(traj_B_aligned, interpolate=True)
    # print(ro, rp)

    # even more complex curve
    t = np.linspace(0, 1, 100)

    points_A = np.array([[0, 0.2], [1, 0.5], [3, 0.5], [4, 0.2]]) * 1000
    pos_A_dev = Bezier.Curve(np.linspace(0, 1, int(len(t) / 2)), points_A)
    pos_A_straight_start = np.full((int(len(t) / 4), 2), 0.2) * 1000
    pos_A_straight_start[:, 0] = np.linspace(-2, 0, int(len(t) / 4)) * 1000
    pos_A_straight_end = np.full((int(len(t) / 4), 2), 0.2) * 1000
    pos_A_straight_end[:, 0] = np.linspace(4, 6, int(len(t) / 4)) * 1000
    pos_A = np.vstack([pos_A_straight_start, pos_A_dev, pos_A_straight_end])
    print(pos_A)

    v_A = (pos_A[2:] - pos_A[:-2]) / ((t[2:] - t[:-2])[:, None] * 1000)
    traj_A = np.zeros((len(t), 7))
    traj_A[:, 0] = t * 1000
    traj_A[:, 1:3] = pos_A
    traj_A[2:, 5:7] = v_A

    points_B = np.array([[4, 0], [3, -1], [1, -1], [0, 0]]) * 1000
    pos_B_dev = Bezier.Curve(np.linspace(0, 1, int(len(t) / 2)), points_B)
    pos_B_straight_start = np.zeros((int(len(t) / 4), 2))
    pos_B_straight_start[:, 0] = np.linspace(6, 4, int(len(t) / 4)) * 1000
    pos_B_straight_end = np.zeros((int(len(t) / 4), 2))
    pos_B_straight_end[:, 0] = np.linspace(0, -2, int(len(t) / 4)) * 1000
    pos_B = np.vstack([pos_B_straight_start, pos_B_dev, pos_B_straight_end])

    v_B = (pos_B[2:] - pos_B[:-2]) / ((t[2:] - t[:-2])[:, None] * 1000)
    traj_B = np.zeros((len(t), 7))
    traj_B[:, 0] = t * 1000
    traj_B[:, 1:3] = pos_B
    traj_B[2:, 5:7] = v_B

    plot_animated_2D_trajectories([traj_A, traj_B])

    # center_of_mass = compute_center_of_mass([traj_A, traj_B])
    # plot_animated_2D_trajectory(center_of_mass)

    traj_A_aligned, [traj_B_aligned] = align_trajectories_at_origin(traj_A, [traj_B])
    # plot_animated_2D_trajectories([traj_A_aligned, traj_B_aligned])

    traj_B_aligned2, [traj_A_aligned2] = align_trajectories_at_origin(traj_B, [traj_A])
    plot_animated_2D_trajectories(
        [traj_A_aligned, traj_B_aligned, traj_B_aligned2, traj_A_aligned2]
    )

    rp = compute_straight_line_minimum_distance(traj_B_aligned)
    ro = compute_observed_minimum_distance(traj_B_aligned, interpolate=True)
    print(ro, rp)
