import matplotlib.pyplot as plt
import os
import glob
import numpy as np
import matplotlib.ticker as ticker  # ajoute tout en haut si pas déjà importé
plt.rcParams.update({'font.size': 18})


"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


n = 2000  # Number of iterations
plot_time = True
plot_start = False
actual_x = 50
actual_y = 100

csv_files = glob.glob(os.path.join('Final/test_5', "*.csv"))
# Check
if not csv_files:
    print("Aucun fichier CSV trouvé dans le dossier.")
    exit()
csv_files.sort()

start_time = 999999999999999999
last_start_time = 0


def find_closest_index(lst, value):
    return min(range(len(lst)), key=lambda i: abs(lst[i] - value))

for file_path in csv_files:
    with open(file_path, 'r') as f:
        for line in f:
            start_time = min(float(line.split(',')[0]), start_time)
            break

    with open(file_path, 'r') as f:
        lines = f.readlines()

        if len(lines) > 1:
            last_start_time = max(float(lines[1].split(',')[0]), last_start_time)


fig, axs = plt.subplots(2, 1, figsize=(8, 12), sharex=True)

color=['purple', 'orange', 'green']

x_agents = []
y_agents = []
agents_pos = []
agents_dist = []

for file_path in csv_files:
    i = int(os.path.basename(file_path).split(".")[0])
    file_name = f"RPi {i}"

    time = []
    cost = []
    x = []
    y = []
    d = []
    pos = []

    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                elem = line.split(",")
                time.append(float(elem[0]) - start_time)
                try:
                    if float(elem[7]) != 1.0:
                        cost.append(float(elem[8]))
                        x.append(float(elem[1]))
                        y.append(float(elem[2]))
                        pos.append([float(elem[-2]), float(elem[-1])])
                        d.append(float(elem[-3]))
                except:
                    continue

    if plot_time:
        axs[0].plot(time[1:n], cost[1:n], label=file_name, color=color[i])
        axs[1].plot(time[1:n], x[1:n], label=file_name, color=color[i])
        axs[1].plot(time[1:n], y[1:n], color=color[i])
        if not plot_start:
            axs[0].set_xlim((last_start_time - start_time-1, time[n]))
            axs[1].set_xlim((last_start_time - start_time-1, time[n]))
    else:
        axs[0].plot(cost[1:n], label=file_name, color=color[i])
        axs[1].plot(x[1:n], label=file_name, color=color[i])
        axs[1].plot(y[1:n], color=color[i])

    print(f'Average cost function: {np.mean(cost[-200:-1])}')
    print(f'Average x error {np.mean(np.array(x[-200:-1])-actual_x)}')
    print(f'Average y error {np.mean(np.array(y[-200:-1])-actual_y)}')
    print(f'Maximum absolute position error {np.max(np.sqrt((np.array(x[-100:-1])-actual_x)**2 + (np.array(y[-100:-1])-actual_y)**2))}')

    x_agents.append(x)
    y_agents.append(y)
    agents_pos.append(pos)
    agents_dist.append(d)

axs[1].plot(time[1:n], len(time[1:n]) * [actual_x], color='red', linestyle='--', label='Actual x position')
axs[1].plot(time[1:n], len(time[1:n]) * [actual_y], color='black', linestyle='--', label='Actual y position')

# Légendes et grilles
axs[0].legend(loc='upper right', fontsize=14)
axs[1].legend(loc='lower right', fontsize=14)
axs[0].grid(True)
axs[1].grid(True)
axs[1].xaxis.set_major_locator(ticker.MultipleLocator(5))


# Labels
axs[0].set_ylabel("Cost function")
axs[1].set_ylabel("Target position [m]")
axs[0].set_yscale('log')

if plot_time:
    axs[1].set_xlabel("Time [s]")

    # --- Ajout d’un second axe pour les itérations ---
    ax_top = axs[0].twiny()
    ax_top.set_xlim(axs[1].get_xlim())  # même plage que le temps
    n_points = len(time[1:n])
    iteration_ticks = np.linspace(0, n_points+1, num=6, dtype=int)
    time_ticks = [time[i] for i in iteration_ticks]
    ax_top.set_xticks(time_ticks)
    ax_top.set_xticklabels([str(i) for i in iteration_ticks])
    ax_top.set_xlabel("Iterations")
    # --------------------------------------------------

    if plot_start:
        plt.savefig("linear3_time_start.png")
    else:
        plt.tight_layout()
        plt.savefig("loc.png")
else:
    axs[1].set_xlabel("Iteration")
    plt.savefig("linear3_it.png")

plt.show()
