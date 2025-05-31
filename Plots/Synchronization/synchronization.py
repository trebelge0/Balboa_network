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


def mean_interval(timestamps):
    """Calcule l'intervalle moyen entre les timestamps."""
    if len(timestamps) < 2:
        return 0.0
    intervals = [t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:])]
    return sum(intervals) / len(intervals)


def read_csv_data(file_path, max_iter, start_time):
    """
    Lit les données CSV d'un fichier et extrait les temps et valeurs jusqu'à max_iter pour l'état 0.
    Renvoie les listes `times`, `values` et le dictionnaire `time_iter`.
    """
    times, values, time_iter = [], [], {}
    with open(file_path, "r") as f:
        iter_count = 0
        for line in f:
            if line.strip():
                t, v, state = map(float, line.split(","))
                if state == 0 and iter_count < max_iter:
                    adjusted_time = t - start_time
                    times.append(adjusted_time)
                    values.append(v)
                    time_iter[iter_count] = adjusted_time
                    iter_count += 1
    return times, values, time_iter


def get_start_and_last_time(file_list):
    """Retourne le temps de départ minimal et le dernier timestamp utile."""
    start_time = float('inf')
    last_start_time = 0
    for file_path in file_list:
        with open(file_path, 'r') as f:
            first_line = f.readline()
            if first_line:
                start_time = min(float(first_line.split(',')[0]), start_time)
        with open(file_path, 'r') as f:
            lines = f.readlines()
            if len(lines) > 2:
                last_start_time = max(float(lines[2].split(',')[0]), last_start_time)
    return start_time, last_start_time


# Paramètres
n_iterations = 200
folder_name = "loop_3"
subdirs = ["frequency", "phase"]
axis_labels = ["Frequency [Hz]", "Phase [s]"]

# Chargement des fichiers
csv_paths = [sorted(glob.glob(os.path.join(folder_name, subdir, "*.csv")), reverse=True)
             for subdir in subdirs]

# Création des subplots
fig, axs = plt.subplots(2, 1, figsize=(8, 12), sharex=True)

for i, (file_list, label) in enumerate(zip(csv_paths, axis_labels)):
    start_time, last_start = get_start_and_last_time(file_list)
    cumulative_time_iter = {}

    for file_path in file_list:
        rpi_name = "RPi " + os.path.basename(file_path).split(".")[0]
        times, values, time_iter = read_csv_data(file_path, n_iterations, start_time)
        axs[i].plot(times, values, label=rpi_name)

        cumulative_time_iter.update(time_iter)  # Pour les ticks twiny

        # Debug print
        print(f"{rpi_name} — Δt moyen : {mean_interval(times[2:]):.3f}s — "
              f"Durée avant start : {last_start - start_time:.3f}s — "
              f"Dernière valeur : {values[-1] if values else 'N/A'}")

    axs[i].grid(True)
    axs[i].set_ylabel(label)
    axs[i].legend(loc='upper right')
    axs[i].axvline(last_start - start_time, color='red', linestyle='--', label='Start')

    # Axe secondaire pour les itérations
    ax_top = axs[i].twiny()
    ax_top.set_xlim(axs[i].get_xlim())

    ticks = list(cumulative_time_iter.values())
    labels = list(cumulative_time_iter.keys())
    step = max(1, len(labels) // 5)

    ax_top.set_xticks(ticks[::step])
    ax_top.set_xticklabels(labels[::step])
    if i == 0:
        ax_top.set_xlabel("Iteration")

axs[1].set_xlabel("Time [s]")
plt.tight_layout()
plt.savefig(f"sync_expe_.png")
plt.show()
