"""
Romain Englebert - Master's Thesis
© 2025 Romain Englebert.
"""


import numpy as np
import matplotlib.pyplot as plt
import random
plt.rcParams.update({'font.size': 18})


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


agents_position = [[50, 150], [100, 50], [150, 150]]
noisy_agents_position = [[50, 150], [100, 50], [150, 150]]

anchor_position = [[0.0, 0.0], [197, 0], [100, 194]]
target_position = [50, 100]
agents_distance = []  # Actual distances between target and each agent
noisy_agents_distance = []  # Actual distances between target and each agent

d = ''
for i in range(len(agents_position)):
    agents_distance.append(round(np.linalg.norm(np.array(target_position) - np.array(agents_position[i])), 4))
    noisy_agents_distance.append(round(np.linalg.norm(np.array(target_position) - np.array(agents_position[i])), 4))
    d += f'{IPS[i]}:{agents_position[i][0]},{agents_position[i][1]},{round(np.linalg.norm(np.array(target_position) - np.array(agents_position[i])), 4)} '


for i in range(len(agents_position)):
    agents_position[i][0] = np.random.uniform(agents_position[i][0]*0.95, agents_position[i][0]*1.05)
    agents_position[i][1] = np.random.uniform(agents_position[i][1]*0.95, agents_position[i][1]*1.05)
    noisy_agents_position[i][0] = agents_position[i][0]
    noisy_agents_position[i][1] = agents_position[i][1]
    noisy_agents_distance[i] = np.random.uniform(agents_distance[i]*0.95, agents_distance[i]*1.05)

# ------------ Gradient descent --------------

# Global variables

ADJACENCY = [[1, 1, 0],
             [1, 1, 1],
             [0, 1, 1]]


NEIGHBORS_INDEX = initialize_neighbors(ADJACENCY)

T = 250  # Iterations

state = np.zeros((T+1, len(ADJACENCY), 6))  # [x1, x2, z1, z2, g1, g2]
gradient = np.zeros((len(ADJACENCY), T))  # For plot
f = np.zeros((len(ADJACENCY), T))  # For plot (cost function)
y = np.zeros((len(ADJACENCY), T))  # For plot
x = np.zeros((len(ADJACENCY), T))  # For plot

gamma = 4e-6  # Step


for t in range(T):

    for n in range(len(ADJACENCY)):

        if t % 5 == 1:
            print('oui')
            noisy_agents_position[n][0] = np.random.uniform(agents_position[n][0] * 0.98, agents_position[n][0] * 1.02)
            noisy_agents_position[n][1] = np.random.uniform(agents_position[n][1] * 0.98, agents_position[n][1] * 1.02)
            noisy_agents_distance[n] = np.random.uniform(agents_distance[n] * 0.98, agents_distance[n] * 1.02)

        position = noisy_agents_position[n]
        distance = noisy_agents_distance[n]

        # Time variation of measures
        # Every 30 iteration, a new measure is performed
        if t%30 == 0:
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

fig, axs = plt.subplots(2, 1, figsize=(8, 12), sharex=True)

color=['green', 'orange', 'royalblue']
for n in reversed(range(len(agents_position))):
    axs[0].plot(f[n], label=f'RPi {n}', color=color[n])
    axs[1].plot(x[n], label=f'RPi {n}', color=color[n])
    axs[1].plot(y[n], color=color[n])

axs[1].plot([target_position[0]]*len(f[0]), label='Actual x position', color='red', linestyle='--')
axs[1].plot([target_position[1]]*len(f[0]), label='Actual y position', color='black', linestyle='--')
axs[0].set_ylabel('Cost function')
axs[1].set_ylabel('Target position [m]')
axs[1].set_xlabel('Iteration')
axs[0].set_yscale('log')
axs[0].grid()
axs[1].grid()
axs[1].legend(loc='lower right', fontsize=15)
axs[0].legend(loc='upper right', fontsize=15)
plt.tight_layout()
plt.savefig('simu_loc_precision_bias.png')
plt.show()

print(f'x error: {abs(x[0][-1]-target_position[0])*100} cm')
print(f'y error: {abs(y[0][-1]-target_position[1])*100} cm')
print(f'Distance from actual target: {np.sqrt((y[0][-1]-target_position[1])**2+(x[0][-1]-target_position[0])**2)*100} cm')

plt.scatter(agents_position[0][0], agents_position[0][1], color='royalblue', label='agent')
for n in range(1, len(agents_position)):
    plt.scatter(agents_position[n][0], agents_position[n][1], color='royalblue')

plt.scatter(anchor_position[0][0], anchor_position[0][1], color='black', label='anchor', marker='*', s=200)
for n in range(1, len(anchor_position)):
    plt.scatter(anchor_position[n][0], anchor_position[n][1], color='black', marker='*', s=200)

plt.scatter(target_position[0], target_position[1], color='red', label='target', marker='*', s=200)
plt.xlabel("X (m)")
plt.ylabel("Y (m)")
plt.grid()
plt.legend()
plt.tight_layout()
plt.savefig("loc_setup.png")
plt.show()

"""
5e-7
x error: 0.0010593177144357924 cm
y error: 0.0013895376852701702 cm
Distance from actual target: 0.0017472747348094557 cm

4e-6
x error: 0.0010618153304164935 cm
y error: 0.0014010119357976691 cm
Distance from actual target: 0.0017579209994066911 cm
"""