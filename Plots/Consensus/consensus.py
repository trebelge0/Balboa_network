import matplotlib.pyplot as plt
import os
import glob
plt.rcParams.update({'font.size': 12})


n = 10  # Number of iterations
plot_time = True
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
        for line in f:
            if line.strip():
                elem = line.split(",")
                time.append(float(elem[0]) - start_time)
                values.append(float(elem[1]))

    if plot_time:
        plt.plot(time[:n], values[:n], label=file_name)
        if not plot_start:
            plt.ylim((-7, 7))
            plt.xlim((last_start_time - start_time-1, time[n]))
    else:
        plt.plot(values[:n], label=file_name)


plt.title(f"Consensus state ({n} iterations)")
plt.legend()
plt.grid(True)

if plot_time:
    plt.xlabel("Time [s]")
    plt.ylabel("Value")
    if plot_start:
        plt.savefig("shape1_time_start.png")
    else:
        plt.savefig("shape1_time.png")

else:
    plt.xlabel("Iteration")
    plt.ylabel("Value")
    plt.savefig("shape1_it.png")

plt.show()