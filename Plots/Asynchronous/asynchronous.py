import matplotlib.pyplot as plt
import os
from matplotlib.patches import Circle, ConnectionPatch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import glob
plt.rcParams.update({'font.size': 14})


n = 30  # Number of iterations
plot_start = True

csv_files = glob.glob(os.path.join('./', "*.csv"))
csv_files.sort()
csv_files=csv_files[:4]
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


fig, ax = plt.subplots(figsize=(10, 6))

zoom_time = []
zoom_values = []

j = 0
colors = ['#1f77b4',  # Bleu classique (primary)
          '#9467bd',   # Violet doux
          '#ff7f0e',  # Orange doux
          '#2ca02c',  # Vert équilibré
          '#d62728'   # Rouge sombre
          ]

colors= ['tab:blue', 'tab:green', 'tab:red', 'tab:orange']

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

    ax.step(time[:n], values[:n], where='post', label=file_name, color=colors[j])
    j += 1
    if not plot_start:
        ax.set_xlim((last_start_time - start_time-1, time[n]))

    zoom_time.append(time[6:10])
    zoom_values.append(values[6:10])

ax.legend()
ax.set_xlim(10)
ax.set_xlabel("Time [s]")
ax.set_ylabel("Iteration")
ax.grid()
plt.tight_layout()
if plot_start:
    plt.savefig("lin_time_start.png")
else:
    plt.savefig("lin_time.png")
plt.show()