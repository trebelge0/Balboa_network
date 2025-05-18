import matplotlib.pyplot as plt
import os
import glob
plt.rcParams.update({'font.size': 18})


n = 150  # Number of iterations
plot_time = True
plot_start = True

csv_files = glob.glob(os.path.join('Shape_1', "*.csv"))
csv_files.sort()
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
    #ack = []

    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                elem = line.split(",")
                time.append(float(elem[0]) - start_time)
                values.append(float(elem[1]))
                #ack.append(float(elem[2]))

    if plot_time:
        plt.plot(time[:n], values[:n], label=file_name)
        if not plot_start:
            #plt.ylim((-7, 7))
            plt.xlim((last_start_time - start_time-1, time[n]))
    else:
        plt.plot(values[:n], label=file_name)


plt.grid(True)

if plot_time:
    plt.xlabel("Time [s]")
    plt.ylabel("State")
    plt.tight_layout()
    if plot_start:
        plt.axvline(last_start_time-start_time, color='red', linestyle='--', label='Start')
        plt.legend(loc='upper right')
        plt.savefig("lin_time_start.png")
    else:
        plt.legend(loc='upper right')
        plt.savefig("lin_time.png")

else:
    plt.xlabel("Iteration")
    plt.ylabel("Value")
    plt.tight_layout()
    plt.savefig("lin_it.png")

plt.show()