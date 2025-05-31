import matplotlib.pyplot as plt
import os
import glob

plt.rcParams.update({'font.size': 18})


"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


def find_closest_index(lst, value):
    return min(range(len(lst)), key=lambda i: abs(lst[i] - value))

def plot_from_folder(folder, subplot_index, total_subplots):
    csv_files = glob.glob(os.path.join(folder, "*.csv"))
    if not csv_files:
        print(f"Aucun fichier CSV trouvé dans le dossier {folder}.")
        return
    csv_files.sort()

    start_time = float('inf')
    last_start_time = 0

    for file_path in csv_files:
        with open(file_path, 'r') as f:
            for line in f:
                start_time = min(float(line.split(',')[0]), start_time)
                break

        with open(file_path, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                last_start_time = max(float(lines[1].split(',')[0]), last_start_time)

    x_agents = []
    y_agents = []
    agents_pos = []

    for file_path in csv_files:
        i = int(os.path.basename(file_path).split(".")[0])

        time = []
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
                            x.append(float(elem[1]))
                            y.append(float(elem[2]))
                            pos.append([float(elem[-2]), float(elem[-1])])
                            d.append(float(elem[-3]))
                    except:
                        continue

        x_agents.append(x)
        y_agents.append(y)
        agents_pos.append(pos)

    agents_position = [[50, 150], [100, 50], [150, 150]]
    anchor_position = [[0.0, 0.0], [197, 0], [100, 194]]
    target_position = [50, 100]

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    plt.subplot(total_subplots, 1, subplot_index)
    for i in range(len(x_agents)):
        target_x = x_agents[i]
        target_y = y_agents[i]

        agent_x = [p[0] for p in agents_pos[i]]
        agent_y = [p[1] for p in agents_pos[i]]

        if i == 2:
            plt.plot(agent_x, agent_y, zorder=5, color=colors[i], label=f'Agent position')
            plt.plot(target_x, target_y, linestyle='--', zorder=1, color=colors[i], label=f'Target position')
        else:
            plt.plot(target_x, target_y, linestyle='--', zorder=1, color=colors[i])
            plt.plot(agent_x, agent_y, zorder=1, color=colors[i])

    plt.scatter(agents_position[0][0], agents_position[0][1], color='royalblue', label='Agent actual pos.', zorder=0)
    for n in range(1, len(agents_position)):
        plt.scatter(agents_position[n][0], agents_position[n][1], color='royalblue', zorder=0)

    plt.scatter(anchor_position[0][0], anchor_position[0][1], color='black', label='Anchor', marker='*', s=200)
    for n in range(1, len(anchor_position)):
        plt.scatter(anchor_position[n][0], anchor_position[n][1], color='black', marker='*', s=200)

    plt.scatter(target_position[0], target_position[1], color='red', label='Target', marker='*', s=200, zorder=5)

    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.axis("equal")
    plt.grid(True)
    if subplot_index == total_subplots:
        plt.legend(fontsize=14)

# === Main ===

plt.figure(figsize=(8, 12))

plot_from_folder('Final/test_2', subplot_index=1, total_subplots=2)
plot_from_folder('Final/test_5', subplot_index=2, total_subplots=2)
plt.xlim(0, 200)

plt.tight_layout()
plt.savefig("2D_double_plot.png")
plt.show()
