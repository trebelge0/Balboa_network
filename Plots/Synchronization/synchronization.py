import matplotlib.pyplot as plt
import os
import glob
plt.rcParams.update({'font.size': 14})


n = 200  # Number of iterations
plot_time = True
plot_start = True
name = "Final"

csv_freq = glob.glob(os.path.join(f'{name}/frequency', "*.csv"))
csv_freq.sort()
csv_phase = glob.glob(os.path.join(f'{name}/phase', "*.csv"))
csv_phase.sort()
csv_files = [csv_freq, csv_phase]
labels = ["Frequency [Hz]", "Phase [s]"]

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


fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

for i in range(2):


    for file_path in csv_files[i]:
        file_name = "RPi " + os.path.basename(file_path).split(".")[0]

        time, values = [], []
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    elem = line.split(",")
                    time.append(float(elem[0]) - start_time)
                    values.append(float(elem[1]))

        if plot_time:
            axs[i].plot(time[:n], values[:n], label=file_name)
            if not plot_start:
                axs[i].set_xlim((last_start_time - start_time - 1, time[n]))
        else:
            axs[i].plot(values[:n], label=file_name)
        axs[i].grid(True)
        axs[i].set_ylabel(labels[i])
        axs[i].legend()



plt.legend()
if plot_time:
    axs[1].set_xlabel("Time [s]")
    plt.tight_layout()
    if plot_start:
        plt.savefig(f"{name}/{name}_time_start_{n}.png")
    else:
        plt.savefig(f"{name}/{name}_time_{n}.png")

else:
    axs[1].set_xlabel("Iteration")
    plt.tight_layout()
    plt.savefig(f"{name}/{name}_it_{n}.png")

plt.show()