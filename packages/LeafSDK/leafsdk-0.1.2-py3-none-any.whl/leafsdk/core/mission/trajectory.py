# leafsdk/core/mission/trajectory.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.interpolate import CubicSpline
from leafsdk.core.utils.transform import gps_to_relative_3d, wrap_to_pi, deg2rad

class WaypointTrajectory:
    def __init__(self, waypoints=None, yaws_deg=None, speed: float=2.0, yaw_mode: str='lock', 
                 home=(0, 0, 0), home_yaw=0, dt: float=1/200, cartesian: bool=False):
        self.home = home
        self.home_yaw = home_yaw
        self.raw_waypoints = waypoints
        self.yaws_deg = yaws_deg
        self.speed = speed
        self.yaw_mode = yaw_mode
        self.dt = dt
        self.cartesian = cartesian
        self.relative_yaws = self._convert_yaw_to_relative()
        self.relative_points = self._convert_cartesian_to_relative() if cartesian else self._convert_gps_to_relative()
        self.ts, self.pos, self.vel, self.acc, self.yaw, self.yaw_rate = self._generate_trajectory()

    def _convert_gps_to_relative(self):
        if not self.raw_waypoints:
            return None
        # Convert GPS coordinates to relative coordinates using the home position
        return np.asarray([
            gps_to_relative_3d(*self.home, lat, lon, alt)
            for lat, lon, alt in self.raw_waypoints
        ])

    def _convert_cartesian_to_relative(self):
        if not self.raw_waypoints:
            return None
        # Convert the waypoints to relative coordinates
        relative_points = np.asarray(self.raw_waypoints) - np.asarray(self.home)
        relative_points = np.vstack((np.zeros((1, 3)), relative_points))
        return relative_points

    def _convert_yaw_to_relative(self):
        if not self.yaws_deg:
            return None
        # Ensure home_yaw is in radians and wrapped to [-pi, pi]
        self.home_yaw = wrap_to_pi(self.home_yaw)
        # Convert yaw angles to relative angles based on the home yaw
        relative_yaws = wrap_to_pi(wrap_to_pi(deg2rad(np.asarray(self.yaws_deg))) - np.asarray(self.home_yaw))
        relative_yaws = np.append(0, relative_yaws)
        return relative_yaws

    def _generate_trajectory(self):
        # Define return variables
        ts = None
        pos = None
        vel = None
        acc = None
        yaw = None
        yaw_rate = None

        # Position setpoints
        if self.relative_points is not None:
            points = np.asarray(self.relative_points)
            distances = [0]
            for i in range(1, len(points)):
                distances.append(distances[-1] + np.linalg.norm(points[i] - points[i-1]))
            total_length = distances[-1]
            total_time = total_length / self.speed
            t_vals = np.linspace(0, total_time, len(points))
            ts = np.arange(0, total_time, self.dt)
            cs_x = CubicSpline(t_vals, points[:, 0], bc_type='clamped')
            cs_y = CubicSpline(t_vals, points[:, 1], bc_type='clamped')
            cs_z = CubicSpline(t_vals, points[:, 2], bc_type='clamped')
            pos = np.stack([cs_x(ts), cs_y(ts), cs_z(ts)], axis=1)
            vel = np.stack([cs_x(ts, 1), cs_y(ts, 1), cs_z(ts, 1)], axis=1)
            acc = np.zeros_like(vel)

        # Yaw setpoints
        if self.relative_yaws is not None:
            yaw_spline = CubicSpline(t_vals, self.relative_yaws, bc_type='clamped')
            yaw_interp = yaw_spline(ts)
            if self.yaw_mode == "lock":
                yaw = yaw_interp
            elif self.yaw_mode == "follow":
                vx, vy = vel[:, 0], vel[:, 1]
                follow_yaw = np.arctan2(vy, vx)
                yaw = follow_yaw + yaw_interp
            else:
                raise ValueError("The parameter yaw_mode must be 'follow' or 'lock'!")
            yaw_rate = np.gradient(yaw, self.dt)

        return ts, pos, vel, acc, yaw, yaw_rate

    def get_setpoints(self):
        return self.ts, self.pos, self.vel, self.acc, self.yaw, self.yaw_rate
    
    def get_relative_coordinates(self):
        return self.relative_points
    
    def get_waypoints(self):
        return self.raw_waypoints
    
    def animate_projections_with_velocity(self):
        xs, ys, zs = self.pos[:, 0], self.pos[:, 1], self.pos[:, 2]
        vxs, vys, vzs = self.vel[:, 0], self.vel[:, 1], self.vel[:, 2]
        fig = plt.figure(figsize=(15, 10))
        grid = plt.GridSpec(2, 3, hspace=0.4, wspace=0.3)
        # Projection subplots
        axes_proj = [fig.add_subplot(grid[0, i]) for i in range(3)]
        views = [("XY View", xs, ys, "X [m]", "Y [m]"),
                ("XZ View", xs, zs, "X [m]", "Z [m]"),
                ("YZ View", ys, zs, "Y [m]", "Z [m]")]
        # Velocity subplots
        axes_vel = [fig.add_subplot(grid[1, i]) for i in range(3)]
        vlabels = [("vx", vxs), ("vy", vys), ("vz", vzs)]
        # Plot trajectory projections
        lines_proj, dots_proj = [], []
        for ax, (title, x_data, y_data, xlabel, ylabel) in zip(axes_proj, views):
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.plot(x_data, y_data, 'gray', lw=0.5, label='Trajectory')
            # Add waypoint scatter
            if self.relative_points is not None:
                wp_x, wp_y, wp_z = self.relative_points[:, 0], self.relative_points[:, 1], self.relative_points[:, 2]
                if xlabel == "X [m]" and ylabel == "Y [m]":
                    ax.scatter(wp_x, wp_y, c='k', marker='x', s=60, label='Waypoints')
                elif xlabel == "X [m]" and ylabel == "Z [m]":
                    ax.scatter(wp_x, wp_z, c='k', marker='x', s=60, label='Waypoints')
                elif xlabel == "Y [m]" and ylabel == "Z [m]":
                    ax.scatter(wp_y, wp_z, c='k', marker='x', s=60, label='Waypoints')
            line, = ax.plot([], [], 'b-', lw=2)
            dot, = ax.plot([], [], 'ro')
            ax.grid(True)
            ax.axis('equal')
            ax.legend()
            lines_proj.append(line)
            dots_proj.append(dot)
        # Plot velocity components
        lines_vel, dots_vel = [], []
        for ax, (label, v_data) in zip(axes_vel, vlabels):
            ax.set_title(f"{label.upper()} Velocity")
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Velocity [m/s]")
            ax.plot(self.ts, v_data, 'gray', lw=0.5, label=f'{label}(t)')
            line, = ax.plot([], [], 'b-', lw=2)
            dot, = ax.plot([], [], 'ro')
            ax.set_xlim([self.ts[0], self.ts[-1]])
            ax.set_ylim([1.1 * np.min(v_data), 1.1 * np.max(v_data)])
            ax.grid(True)
            ax.legend()
            lines_vel.append(line)
            dots_vel.append(dot)
        # --- Animation update function ---
        def update(frame):
            # Update trajectory plots
            for i, (line, dot, (title, x_data, y_data, _, _)) in enumerate(zip(lines_proj, dots_proj, views)):
                line.set_data(x_data[:frame+1], y_data[:frame+1])
                dot.set_data([x_data[frame]], [y_data[frame]])
            # Update velocity plots
            for i, (line, dot, (_, v_data)) in enumerate(zip(lines_vel, dots_vel, vlabels)):
                line.set_data(self.ts[:frame+1], v_data[:frame+1])
                dot.set_data([self.ts[frame]], [v_data[frame]])
            return lines_proj + dots_proj + lines_vel + dots_vel
        ani = FuncAnimation(fig, update, frames=len(self.ts), interval=100, blit=True)
        plt.show()


class TrajectorySampler:
    def __init__(self, trajectory: WaypointTrajectory):
        self.trajectory = trajectory
        self.ts, self.pos, self.vel, self.acc, self.yaw, self.yaw_rate = trajectory.get_setpoints()
        self.current_index_pos = 0
        self.current_index_yaw = 0

    def sample_pos(self):
        pos = 0
        vel = 0
        acc = 0
        if self.current_index_pos < len(self.ts):
            t = self.ts[self.current_index_pos]
            if self.trajectory.relative_points is not None:
                pos = self.pos[self.current_index_pos]
                vel = self.vel[self.current_index_pos]
                acc = self.acc[self.current_index_pos]
            self.current_index_pos += 1
            return t, pos, vel, acc
        else:
            raise StopIteration("End of trajectory reached for position.")
        
    def sample_yaw(self):
        yaw = 0
        yaw_rate = 0
        if self.current_index_yaw < len(self.ts):
            t = self.ts[self.current_index_yaw]
            if self.trajectory.relative_yaws is not None:
                yaw = self.yaw[self.current_index_yaw]
                yaw_rate = self.yaw_rate[self.current_index_yaw]
            self.current_index_yaw += 1
            return t, yaw, yaw_rate
        else:
            raise StopIteration("End of trajectory reached for yaw.")