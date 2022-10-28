import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import pickle as pk


def pickle_load(file_path: str):
    """Load the content of a pickle file

    Parameters
    ----------
    file_path : str
        The path to the file which will be unpickled

    Returns
    -------
    obj
        The content of the pickle file
    """
    with open(file_path, "rb") as f:
        data = pk.load(f)
    return data


def pickle_save(file_path: str, data):
    """Save data to pickle file

    Parameters
    ----------
    file_path : str
        The path to the file where the data will be saved
    data : obj
        The data to save
    """
    with open(file_path, "wb") as f:
        pk.dump(data, f)


class Body:
    def __init__(
        self,
        mass: float,
        p_i: np.ndarray,
        v_i: np.ndarray,
        fixed: bool = False,
        name="unnamed",
    ) -> None:
        self.mass = mass
        self.p = p_i.reshape(1, 2)
        self.v = v_i.reshape(1, 2)
        self.a = np.zeros(2).reshape(1, 2)
        self.fixed = fixed
        self.name = name

    def get_p(self):
        return self.p[-1, :]

    def get_all_p(self):
        return self.p

    def get_v(self):
        return self.v[-1, :]

    def get_all_v(self):
        return self.v

    def get_a(self):
        return self.a[-1, :]

    def get_m(self):
        return self.mass

    def is_fixed(self):
        return self.fixed

    def addForce(self, f):
        if not self.fixed:
            self.a[-1, :] += f / self.mass

    def update_position(self, d_t=0.1):
        if not self.fixed:
            new_v = self.v[-1, :] + d_t * self.a[-1, :]
            self.v = np.vstack((self.v, new_v))
            # if np.linalg.norm(self.velocity) > self.max_velocity:
            # self.v *= self.max_velocity / np.linalg.norm(self.v)
            new_p = self.p[-1, :] + d_t * self.v[-1, :]
            self.p = np.vstack((self.p, new_p))
            self.a = np.vstack((self.a, np.zeros(2)))

    def __str__(self) -> str:
        return self.name


class Simulation:
    def __init__(self, boundaries=(-10, 10, -10, 10), d_t=0.1) -> None:

        self.boundaries = boundaries
        self.d_t = d_t
        self.bodies: list[Body] = []
        self.t = [0]

        # initialise plotting
        self.fig, self.ax = plt.subplots()

    def get_bodies_positions(self):
        x, y = [], []
        for b in self.bodies:
            pos = b.get_p()
            x += [pos[0]]
            y += [pos[1]]
        return np.array(x), np.array(y)

    def get_bodies_velocities(self):
        vx, vy = [], []
        for b in self.bodies:
            v = b.get_v()
            vx += [v[0]]
            vy += [v[1]]
        return np.array(vx), np.array(vy)

    def get_bodies_accelerations(self):
        ax, ay = [], []
        for b in self.bodies:
            a = b.get_a()
            ax += [a[0]]
            ay += [a[1]]
        return np.array(ax), np.array(ay)

    def add_body(self, body: Body):
        self.bodies += [body]

    def setup_plot(self, show_v, show_a):
        self.solve_physics()
        self.ax.set_aspect("equal")
        self.ax.set_xlim(self.boundaries[0], self.boundaries[1])
        self.ax.set_ylim(self.boundaries[2], self.boundaries[3])
        x, y = self.get_bodies_positions()
        self.scatter = self.ax.scatter(x, y)
        plots = [self.scatter]
        if show_v:
            vx, vy = self.get_bodies_velocities()
            self.quiver_v = self.ax.quiver(
                x, y, vx, vy, color="blue", units="xy", scale=1
            )
            plots += [self.quiver_v]
        if show_a:
            ax, ay = self.get_bodies_accelerations()
            self.quiver_a = self.ax.quiver(
                x, y, ax, ay, color="orange", units="xy", scale=1
            )
            plots += [self.quiver_a]
        return plots

    def animate(self, t=10, show_v=False, show_a=False, show=True, save_path=None):
        n_frames = int(t / self.d_t)
        self.setup_plot(show_v, show_a)
        fps = self.d_t * 1000
        if show:
            interval = fps
        else:
            interval = 1
        self.animation = animation.FuncAnimation(
            self.fig,
            self.update,
            interval=interval,
            fargs=(show_v, show_a),
            repeat=False,
            frames=n_frames,
        )
        if show:
            plt.show()
        if save_path:
            self.animation.save(save_path, fps=fps)

    def solve_physics(self):
        for i, b1 in enumerate(self.bodies):
            for b2 in self.bodies[i + 1 :]:
                r = b2.get_p() - b1.get_p()  # vec b1-b2
                r_mag = np.linalg.norm(r)
                u = r / r_mag
                f = b1.get_m() * b2.get_m() / r_mag**2
                b1.addForce(-f * u)
                b2.addForce(f * u)

    def update_positions(self):
        self.t += [self.t[-1] + self.d_t]
        # update bodies position
        for b in self.bodies:
            b.update_position(self.d_t)

    def update(self, i, show_v, show_a):
        self.solve_physics()
        x, y = self.get_bodies_positions()
        self.scatter.set_offsets(np.c_[x, y])
        plots = [self.scatter]
        if show_v:
            vx, vy = self.get_bodies_velocities()
            self.quiver_v.set_offsets(np.c_[x, y])
            self.quiver_v.set_UVC(vx, vy)
            plots += [self.quiver_v]
        if show_a:
            ax, ay = self.get_bodies_accelerations()
            self.quiver_a.set_offsets(np.c_[x, y])
            self.quiver_a.set_UVC(ax, ay)
            plots += [self.quiver_a]
        self.update_positions()
        return plots

    def save_as_csv(self, save_path):
        data = np.array(self.t).reshape((len(self.t), 1))
        for b in self.bodies:
            p = b.get_all_p()
            v = b.get_all_v()
            data = np.hstack((data, p, v))
        pd.DataFrame(data).to_csv(save_path, index=False, header=False)

    def save_as_pkl(self, save_path):
        time = np.array(self.t).reshape((len(self.t), 1))
        data = []
        for b in self.bodies:
            p = b.get_all_p()
            v = b.get_all_v()
            data += [np.hstack((time, p, v))]
        pickle_save(save_path, data)


if __name__ == "__main__":

    p1 = np.array([-100.0, -10.0])
    v1 = np.array([20.0, 0.0])
    b1 = Body(10000, p1, v1, name="b1")
    p2 = np.array([100.0, 10.0])
    v2 = np.array([-20.0, 0.0])
    b2 = Body(10000, p2, v2, name="b2")

    sim = Simulation(boundaries=(-100, 100, -100, 100), d_t=0.1)
    sim.add_body(b1)
    sim.add_body(b2)
    sim.animate(t=10, show_a=True, show_v=True, show=True)
    sim.save_as_pkl("data.pkl")
