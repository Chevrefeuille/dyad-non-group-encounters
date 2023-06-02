import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

cross = lambda x, y, axis=1: np.cross(x, y, axis=axis)


def compute_curvature(p):
    v = p[1:, :] - p[:-1, :]
    a = v[1:, :] - v[:-1, :]
    k = cross(v[1:, :], a, axis=1) / np.linalg.norm(v[1:, :], axis=1) ** 3
    return k


def smooth_curve(p, N):
    kernel = np.ones(N) / N
    return np.vstack(
        (
            np.convolve(p[:, 0], kernel, mode="valid"),
            np.convolve(p[:, 1], kernel, mode="valid"),
        )
    ).T


if __name__ == "__main__":

    # CIRCLE
    # R = 2
    # t = np.linspace(0, np.pi * 2, 100)
    # x = R * np.cos(t)
    # y = R * np.sin(t)
    # p = np.vstack((x, y)).T
    # k = compute_curvature(p, 0.01)
    # fig, axes = plt.subplots(2, 1)
    # axes[0].scatter(x[1:-1], y[1:-1], s=2, c=k, vmin=0, vmax=1)
    # # axes[0].quiver(x[1:], y[1:], v[:, 0], v[:, 1])
    # # axes[0].quiver(x[1:-1], y[1:-1], a[:, 0], a[:, 1])
    # axes[0].set_aspect("equal")
    # axes[1].plot(k)
    # axes[1].set_ylim(0, 1)
    # plt.show()

    # LISSAJOU
    A, B = 1, 1
    a, b = 3, 2
    delta = np.pi / 2
    t = np.linspace(0, np.pi * 2, 200)

    sigma = 0.01
    x = A * np.sin(a * t + delta) + np.random.normal(0, scale=sigma, size=len(t))
    y = B * np.sin(b * t) + np.random.normal(0, scale=sigma, size=len(t))
    p = np.vstack((x, y)).T

    N = 32
    # p = smooth_curve(p, N)
    p = savgol_filter((x, y), N, 5).T

    k = compute_curvature(p)

    fig, axes = plt.subplots(2, 1)
    sc = axes[0].scatter(p[1:-1, 0], p[1:-1, 1], s=2, c=k)
    plt.colorbar(sc, ax=axes[0])
    # axes[0].quiver(x[1:], y[1:], v[:, 0], v[:, 1])
    # axes[0].quiver(x[1:-1], y[1:-1], a[:, 0], a[:, 1])
    axes[0].set_aspect("equal")
    axes[1].plot(k)
    axes[1].set_ylim(-20, 20)
    plt.show()
