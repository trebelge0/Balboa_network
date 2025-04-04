import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import glob
plt.rcParams.update({'font.size': 12})


actual_x = 2.38
actual_y = 2.6

csv_files = glob.glob(os.path.join('../data/', "*.csv"))
# Check
if not csv_files:
    print("Aucun fichier CSV trouvé dans le dossier.")
    exit()

N = len(csv_files)

start_time = 999999999999999999
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


color=['purple', 'orange', 'green']
time = []
cost = []
x = []
y = []
file_name = []
i = []
window = 100

for file_path in csv_files:

    i.append(int(os.path.basename(file_path).split(".")[0]))
    file_name.append(f"RPi {i[-1]}")

    time.append([])
    cost.append([])
    x.append([])
    y.append([])

    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                elem = line.split(",")
                time[-1].append(float(elem[0]) - start_time)
                try:
                    cost[-1].append(float(elem[7]))
                    x[-1].append(float(elem[1]))
                    y[-1].append(float(elem[2]))
                except:
                    continue

def animate(t):

    axs[0].clear()
    axs[1].clear()

    for j in range(N):
        axs[0].plot(time[j][max(1, t-window):t], cost[j][max(1, t-window):t], label=file_name[j], color=color[i[j]])
        axs[1].plot(time[j][max(1, t-window):t], x[j][max(1, t-window):t], label=file_name[j], color=color[i[j]])
        axs[1].plot(time[j][max(1, t-window):t], y[j][max(1, t-window):t], color=color[i[j]])


    axs[1].plot(time[0][max(1, t-window):t], len(time[0][max(1, t-window):t])*[actual_x], color='red', linestyle='--', label='Actual x position')
    axs[1].plot(time[0][max(1, t-window):t], len(time[0][max(1, t-window):t])*[actual_y], color='black', linestyle='--', label='Actual y position')
    axs[0].legend()
    axs[1].legend()
    axs[0].grid(True)
    axs[1].grid(True)
    axs[0].set_ylabel("Cost function")
    axs[1].set_ylabel("Target position [m]")
    axs[0].set_yscale('log')
    axs[1].set_xlabel("Time [s]")


fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

ani = animation.FuncAnimation(fig, animate, interval=10)

plt.show()