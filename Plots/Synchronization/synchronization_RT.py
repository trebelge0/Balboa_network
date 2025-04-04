import matplotlib.pyplot as plt
import os
import matplotlib.animation as animation
import glob
plt.rcParams.update({'font.size': 12})

name = "loop_3"

csv_freq = glob.glob(os.path.join(f'{name}/frequency', "*.csv"))
csv_phase = glob.glob(os.path.join(f'{name}/phase', "*.csv"))
csv_files = [csv_freq, csv_phase]
N = len(csv_files[0])
window = 10


if not csv_freq or not csv_phase:
    print("Aucun fichier CSV trouvé dans le dossier.")
    exit()

start_time = float('inf')
last_start_time = 0

for file_path in csv_files[0]:
    with open(file_path, 'r') as f:
        for line in f:
            start_time = min(float(line.split(',')[0]), start_time)
            break

    with open(file_path, 'r') as f:
        lines = f.readlines()
        if len(lines) > 1:
            last_start_time = max(float(lines[1].split(',')[0]), last_start_time)


time = []
values = []
file_name = []
rpi = []
labels = ["Frequency [Hz]", "Phase [s]"]
color=['purple', 'orange', 'green']


for i in range(2):

    time.append([])
    values.append([])

    for file_path in csv_files[i]:
        rpi.append(int(os.path.basename(file_path).split(".")[0]))
        if f"RPi {rpi[-1]}" not in file_name:
            file_name.append(f"RPi {rpi[-1]}")

        time[-1].append([])
        values[-1].append([])

        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    elem = line.split(",")
                    time[i][-1].append(float(elem[0]) - start_time)
                    values[i][-1].append(float(elem[1]))


def animate(t):

    for i in range(2):
        axs[i].clear()
        for j in range(N):

            axs[i].plot(time[i][j][max(1, t-window):t], values[i][j][max(1, t-window):t], label=file_name[j], color=color[j])

        axs[i].grid(True)
        axs[i].set_ylabel(labels[i])
        axs[i].legend()

    axs[0].set_title(f"Synchronization state")
    axs[1].set_xlabel("Time [s]")


fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
ani = animation.FuncAnimation(fig, animate, interval=100)
plt.show()