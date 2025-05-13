import matplotlib.pyplot as plt
import os
from matplotlib.patches import Circle, ConnectionPatch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import glob
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
plt.rcParams.update({'font.size': 14})


n = 30  # Number of iterations
plot_start = False

csv_files = glob.glob(os.path.join('3_lin/REC', "*.csv"))
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


fig, ax = plt.subplots(figsize=(10, 6))

zoom_time = []
zoom_values = []
zoom_ack = []
zoom_tack = []

j = 0
colors = ['#1f77b4',  # Bleu classique (primary)
          '#9467bd',   # Violet doux
          '#ff7f0e',  # Orange doux
          '#2ca02c',  # Vert équilibré
          '#d62728'   # Rouge sombre
          ]

colors= ['tab:blue', 'tab:green', 'tab:red']

for file_path in csv_files:
    file_name = "RPi " + os.path.basename(file_path).split(".")[0]

    time = []
    tack = []
    values = []
    ack = []

    with open(file_path, "r") as f:
        i = 0
        for line in f:
            if line.strip():
                elem = line.split(",")

                acki = elem[2]
                if int(acki) == 1:
                    tack.append(float(elem[0]) - start_time)
                    ack.append(i//2)
                else:
                    time.append(float(elem[0]) - start_time)
                    values.append(i//2)
                i += 1

    ax.step(time[:n], values[:n], where='post', label=file_name, color=colors[j])
    ax.scatter(tack[:n-1], ack[:n-1], s=20, color=colors[j])
    j += 1
    if not plot_start:
        ax.set_xlim((last_start_time - start_time-1, time[n]))

    zoom_time.append(time[6:10])
    zoom_values.append(values[6:10])
    zoom_ack.append(ack[6:10])
    zoom_tack.append(tack[6:10])

# Coordonnées à zoomer
x1, x2 = 11.5, 12.2
y1, y2 = 5.5, 8.5
zoom_center = (11.85, 7.0)



# Ajouter l'inset (zoom) en bas à droite
axins = inset_axes(ax, width=2.4, height=2.4, loc='lower right',
                   bbox_to_anchor=(0.95, 0.1),  # position manuelle
                   bbox_transform=ax.transAxes, borderpad=0)

con = ConnectionPatch(xyA=(0.2, 1.08), coordsA=axins.transAxes,
                      xyB=zoom_center, coordsB=ax.transData,
                      arrowstyle="->", color="grey", lw=1.5)
fig.add_artist(con)
con = ConnectionPatch(xyA=(0.3, -0.12), coordsA=axins.transAxes,
                      xyB=zoom_center, coordsB=ax.transData,
                      arrowstyle="->", color="grey", lw=1.5)
fig.add_artist(con)

circle = Circle((0.5, 0.5), 0.65, transform=axins.transAxes,
                facecolor='White', edgecolor='black', lw=2, clip_on=False)
axins.set_clip_path(circle)
axins.add_patch(circle)

for i in range(len(csv_files)):
    print(zoom_time[i])
    print(zoom_values[i])
    print(zoom_tack[i])
    print(zoom_ack[i])
    print()
    axins.step(zoom_time[i], zoom_values[i], where='post', color=colors[i])
    axins.scatter(zoom_tack[i], zoom_ack[i], s=30, color=colors[i])
axins.set_xlim(x1, x2)
axins.set_ylim(y1, y2)
axins.set_xticks([])
axins.set_yticks([])

for spine in axins.spines.values():
    spine.set_visible(False)

ax.legend()
plt.grid(True)
ax.set_xlabel("Time [s]")
ax.set_ylabel("Iteration")
ax.grid()
plt.tight_layout()
if plot_start:
    plt.savefig("lin_time_start.png")
else:
    plt.savefig("lin_time.png")
plt.show()