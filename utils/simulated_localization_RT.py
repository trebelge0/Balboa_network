"""
Romain Englebert - Master's Thesis
© 2025 Romain Englebert.
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
plt.rcParams.update({'font.size': 12})


def initialize_neighbors(m):
    """
    Initialize neighbors based on adjacent matrix.
    """
    neighbors_index = []

    # Fill neighbors based on adjacency matrix
    for i in range(len(m)):
        neighbors_index.append([])
        for j in range(len(m[i])):
            if m[i][j] != 0:
                neighbors_index[i].append(j)
    return neighbors_index


# ---------- Utils for localization ------------

IPS = ["192.168.164.86",
       "192.168.164.107",
       "192.168.164.55"]


agents_position = [[-0.91, 0.3], [2.67, 0.12], [1.63, 2.59]]
target_position = [2.38, 2.6]
agents_distance = []  # Actual distances between target and each agent

d = ''
for i in range(len(agents_position)):
    agents_distance.append(round(np.linalg.norm(np.array(target_position) - np.array(agents_position[i])), 4))
    d += f'{IPS[i]}:{agents_position[i][0]},{agents_position[i][1]},{round(np.linalg.norm(np.array(target_position) - np.array(agents_position[i])), 4)} '
print(d)

# ------------ Gradient descent --------------

# Global variables

ADJACENCY = [[1, 1, 0],
             [1, 1, 1],
             [0, 1, 1]]


NEIGHBORS_INDEX = initialize_neighbors(ADJACENCY)

T = 500  # Iterations

state = np.zeros((T+1, len(ADJACENCY), 6))  # [x1, x2, z1, z2, g1, g2]
gradient = np.zeros((len(ADJACENCY), T))  # For plot
f = np.zeros((len(ADJACENCY), T))  # For plot (cost function)
y = np.zeros((len(ADJACENCY), T))  # For plot
x = np.zeros((len(ADJACENCY), T))  # For plot

gamma = 2e-3  # Step

# --------- Model of the time averaged error ----------
# This will lead to a static error at the end

RMS_dist_error = 0.0  # RMS error of measurements over distance (not time)
for i in range(len(agents_distance)):
    cal_error = random.uniform(-0.0, 0.0)  # Calibration model error because different calibration over each device
    agents_distance[i] += random.gauss(cal_error, RMS_dist_error)


RMS_pos_error = 0.0  # RMS error of position over distance due to the RMS_dist_error
for i in range(len(agents_position)):
    anchor_pos_error = random.uniform(-0.0, 0.0)  # Positioning error of the anchors
    agents_position[i][0] += random.gauss(anchor_pos_error, RMS_pos_error)
    agents_position[i][1] += random.gauss(anchor_pos_error, RMS_pos_error)


for t in range(T):

    for n in range(len(ADJACENCY)):

        position = agents_position[n]
        distance = agents_distance[n]

        # Time variation of measures
        # Every 30 iteration, a new measure is performed
        if t%30000 == 0:
            RMS_time_dist = 0.001 + 0.001*distance
            distance += random.gauss(0, RMS_time_dist)
            position[0] += random.gauss(0, RMS_time_dist)
            position[1] += random.gauss(0, RMS_time_dist)


        xi_t = np.array(state[t][n][0:2])
        zi_t = np.array(state[t][n][2:4])

        wijxj = np.zeros(2)
        wijzj = np.zeros(2)
        wijgj = np.zeros(2)
        for j in NEIGHBORS_INDEX[n]:
            wij = np.array(ADJACENCY[n][j] / sum(ADJACENCY[n]))
            xj_t = np.array(state[t][j][0:2])
            zj_t = np.array(state[t][j][2:4])
            gj_t = np.array(state[t][j][4:6])
            wijxj += wij*xj_t
            wijzj += wij*zj_t
            wijgj += wij*gj_t

        gi_t = state[t][n][4:6]

        state[t+1][n][0:2] = wijxj - zi_t - gamma * gi_t  # xi_{t+1}
        state[t+1][n][2:4] = wijzj - gamma * gi_t + gamma * wijgj  # zi_{t+1}
        xi_t1 = np.array(state[t+1][n][0:2])
        state[t+1][n][4:6] = 4 * (distance**2 - np.linalg.norm(xi_t1 - position)**2) * (position - xi_t1)  # gi_{t+1}

        f[n][t] = (distance**2 - np.linalg.norm(xi_t1 - position)**2)**2
        x[n][t] = state[t][n][0]
        y[n][t] = state[t][n][1]


color=['purple', 'orange', 'green']
window = 100
iteration = np.arange(0, len(f[0]), 1)

def animate(t):

    axs[0].clear()
    axs[1].clear()

    for n in range(len(agents_position)):
        axs[0].plot(iteration[max(1, t-window):t], f[n][max(1, t-window):t], label=f'RPi {n}', color=color[n])
        axs[1].plot(iteration[max(1, t-window):t], x[n][max(1, t-window):t], label=f'RPi {n}', color=color[n])
        axs[1].plot(iteration[max(1, t-window):t], y[n][max(1, t-window):t], color=color[n])

    axs[1].plot(iteration[max(1, t-window):t], [target_position[0]]*len(iteration[max(1, t-window):t]), label='Actual x position', color='red', linestyle='--')
    axs[1].plot(iteration[max(1, t-window):t], [target_position[1]]*len(iteration[max(1, t-window):t]), label='Actual y position', color='black', linestyle='--')
    axs[0].set_ylabel('Cost function')
    axs[1].set_ylabel('Target position [m]')
    axs[1].set_xlabel('Iteration')
    axs[0].set_yscale('log')
    axs[0].grid()
    axs[1].grid()
    axs[1].legend()
    axs[0].legend()

fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

ani = animation.FuncAnimation(fig, animate, interval=10)

plt.show()