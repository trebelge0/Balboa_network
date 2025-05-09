import matplotlib.pyplot as plt
import os
import glob
plt.rcParams.update({'font.size': 12})


n = 50  # Number of iterations
plot_start = False

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


plt.figure(figsize=(10, 6))

for file_path in csv_files:
    file_name = "RPi " + os.path.basename(file_path).split(".")[0]

    time = []
    values = []

    with open(file_path, "r") as f:
        i = 0
        for line in f:
            if line.strip():
                elem = line.split(",")
                time.append(float(elem[0]) - start_time)
                values.append(i)
                i += 1

    plt.step(time[:n], values[:n], label=file_name)
    if not plot_start:
        plt.xlim((last_start_time - start_time-1, time[n]))


plt.title(f"Synchronous iterations")
plt.legend()
plt.grid(True)

plt.xlabel("Time [s]")
plt.ylabel("Iteration")
if plot_start:
    plt.savefig("shape1_time_start.png")
else:
    plt.savefig("shape1_time.png")

plt.show()