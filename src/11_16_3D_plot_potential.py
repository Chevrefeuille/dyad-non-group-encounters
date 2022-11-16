import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d


def U(r0, rb):
    return 1 - (rb / r0) ** 2


if __name__ == "__main__":

    MIN_R0, MAX_R0, N_R0 = 0, 4, 10
    MIN_RB, MAX_RB, N_RB = 0, 4, 10

    r0 = np.linspace(MIN_R0, MAX_R0, N_R0)
    rb = np.linspace(MIN_RB, MAX_RB, N_RB)

    R0, RB = np.meshgrid(r0, rb)

    U_mat = U(R0, RB)

    fig = plt.figure()
    ax = plt.axes(projection="3d")
    ax.plot_surface(
        R0, RB, U_mat, rstride=1, cstride=1, cmap="viridis", edgecolor="none"
    )
    ax.set_zlim([-4, 1])
    ax.set_xlabel("r0")
    ax.set_ylabel("rb")
    ax.set_zlabel("U")

    plt.show()
