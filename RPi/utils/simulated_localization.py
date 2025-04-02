import numpy as np
import matplotlib.pyplot as plt


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
       "192.168.164.210",
       "192.168.164.122",
       "192.168.164.45",
       "192.168.164.55"]


agents_position = [[-1.0, 0.5], [1.0, 2.0], [3.0, -0.5], [2.0, -2.0], [0, -1]]
target_position = [1, 0]
agents_distance = []  # Actual distances between target and each agent

d = ''
for i in range(len(agents_position)):
    agents_distance.append(round(np.linalg.norm(np.array(target_position) - np.array(agents_position[i])), 4))
    d += f'{IPS[i]}:{agents_position[i][0]},{agents_position[i][1]},{round(np.linalg.norm(np.array(target_position) - np.array(agents_position[i])), 4)} '
print(d)


# ------------ Gradient descent --------------

# Global variables

ADJACENCY = [[1, 1, 0, 0, 1],
             [1, 1, 1, 0, 0],
             [0, 1, 1, 1, 0],
             [0, 0, 1, 1, 1],
             [1, 0, 0, 1, 1]]


NEIGHBORS_INDEX = initialize_neighbors(ADJACENCY)
print(NEIGHBORS_INDEX)

T = 400  # Iterations

state = np.zeros((T+1, len(ADJACENCY), 6))  # [x1, x2, z1, z2, g1, g2]
gradient = np.zeros((6, T))  # For plot
f = np.zeros((6, T))  # For plot (cost function)
y = np.zeros((6, T))  # For plot
x = np.zeros((6, T))  # For plot

gamma = 5e-3  # Step

for t in range(T):

    for n in range(len(ADJACENCY)):

        position = agents_position[n]
        distance = agents_distance[n]

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
            if n == 1:
                print("Agent: ", n)
                print("wij: ", wij)
                print("xj_t: ", xj_t)
                print("zj_t: ", zj_t)
                print("gj_t: ", gj_t)

        gi_t = state[t][n][4:6]

        state[t+1][n][0:2] = wijxj - zi_t - gamma * gi_t  # xi_{t+1}
        state[t+1][n][2:4] = wijzj - gamma * gi_t + gamma * wijgj  # zi_{t+1}
        xi_t1 = np.array(state[t+1][n][0:2])
        state[t+1][n][4:6] = 4 * (distance**2 - np.linalg.norm(xi_t1 - position)**2) * (position - xi_t1)  # gi_{t+1}

        for j in range(6):
            state[t+1][n][j] = round(state[t+1][n][j], 6)

        if n == 1:
            print("wijxj: ", wijxj)
            print("wijzj: ", wijzj)
            print("wijgj: ", wijgj)
            print("zi_t: ", zi_t)
            print("gi_t: ", gi_t)
            print("Next state : ", state[t+1][n])
            print("iteration : ", t)
            print()
        f[n][t] = (distance**2 - np.linalg.norm(xi_t1 - position)**2)**2
        x[n][t] = state[t][n][0]
        y[n][t] = state[t][n][1]


for n in range(len(agents_position)):
    plt.scatter(agents_position[n][0], agents_position[n][1], color='blue')
plt.scatter(target_position[0], target_position[1], color='red')
plt.title("Agents and target position")
plt.grid()
plt.show()

fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

for n in range(len(agents_position)):
    axs[0].plot(f[n])
    axs[1].plot(x[n])
    axs[1].plot(y[n])
axs[0].set_ylabel('cost')
axs[1].set_ylabel('position')
axs[0].set_yscale('log')
axs[0].grid()
axs[1].grid()

plt.show()