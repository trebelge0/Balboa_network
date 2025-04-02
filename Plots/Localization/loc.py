import matplotlib.pyplot as plt
import os
import glob
import numpy as np
plt.rcParams.update({'font.size': 12})


n = 200  # Number of iterations
plot_time = True
plot_start = True

csv_files = glob.glob(os.path.join('../data/', "*.csv"))
# Check
if not csv_files:
    print("Aucun fichier CSV trouvé dans le dossier.")
    exit()


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


fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

for file_path in csv_files:
    file_name = "RPi " + os.path.basename(file_path).split(".")[0]

    time = []
    cost = []
    x = []
    y = []

    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                elem = line.split(",")
                time.append(float(elem[0]) - start_time)
                try:
                    cost.append(float(elem[7]))
                    x.append(float(elem[1]))
                    y.append(float(elem[2]))
                except:
                    continue

    if plot_time:
        axs[0].plot(time[1:n], cost[1:n], label=file_name)
        axs[1].plot(time[1:n], x[1:n], label=file_name)
        axs[1].plot(time[1:n], y[1:n], label=file_name)
        if not plot_start:
            axs[0].set_xlim((last_start_time - start_time-1, time[n]))
            axs[1].set_xlim((last_start_time - start_time-1, time[n]))
    else:
        axs[0].plot(cost[1:n], label=file_name)
        axs[1].plot(x[1:n], label=file_name)
        axs[1].plot(y[1:n], label=file_name)


axs[0].set_title(f"Localization state ({n} iterations)")
axs[0].legend()
axs[0].grid(True)
axs[1].grid(True)

if plot_time:
    axs[1].set_xlabel("Time [s]")
    axs[0].set_ylabel("Cost")
    axs[1].set_ylabel("Position")
    axs[0].set_yscale('log')
    plt.tight_layout()
    if plot_start:
        plt.savefig("loop5_time_start.png")
    else:
        plt.savefig("loop5_time.png")

else:
    axs[1].set_xlabel("Iteration")
    axs[0].set_ylabel("Cost")
    axs[1].set_ylabel("Position")
    axs[0].set_yscale('log')
    plt.tight_layout()
    plt.savefig("loop5_it.png")

print(y)
plt.show()