import matplotlib.pyplot as plt
import os
import glob

plt.rcParams.update({'font.size': 18})


def mean_interval(times):
    """Retourne l'intervalle moyen entre les éléments d'une liste."""
    if len(times) < 2:
        return 0.0
    intervals = [t2 - t1 for t1, t2 in zip(times[:-1], times[1:])]
    return sum(intervals) / len(intervals)


def find_csv_files(folder):
    """Récupère et trie les fichiers CSV dans un dossier."""
    files = glob.glob(os.path.join(folder.strip(), "*.csv"))
    files.sort(reverse=True)
    if not files:
        print("Aucun fichier CSV trouvé dans le dossier.")
        exit()
    return files


def get_time_bounds(files):
    """Trouve le temps de début et de fin pour tous les fichiers."""
    start_time = float('inf')
    last_start_time = 0

    for file_path in files:
        with open(file_path, 'r') as f:
            for line in f:
                start_time = min(float(line.split(',')[0]), start_time)
                break

        with open(file_path, 'r') as f:
            lines = f.readlines()
            if len(lines) > 2:
                last_start_time = max(float(lines[2].split(',')[0]), last_start_time)

    return start_time, last_start_time


def parse_csv(file_path, start_time, max_iter):
    """Extrait les temps et valeurs depuis un fichier CSV."""
    time, values = [], []
    iter_time_map = {}
    with open(file_path, "r") as f:
        for i, line in enumerate(f):
            if line.strip():
                elems = line.split(",")
                if float(elems[2]) == 0 and len(values) < max_iter:
                    t = float(elems[0]) - start_time
                    v = float(elems[1])
                    time.append(t)
                    values.append(v)
                    iter_time_map[len(values) - 1] = t
    return time, values, iter_time_map


def plot_data(files, n, name, plot_time=True, plot_start=True):
    """Génère et sauvegarde la figure à partir des fichiers CSV."""
    start_time, last_start_time = get_time_bounds(files)

    fig, ax = plt.subplots(figsize=(8, 6))
    all_iter_time = {}
    last_time = []
    last_values = []

    for file_path in files:
        label = "RPi " + os.path.splitext(os.path.basename(file_path))[0]
        time, values, iter_map = parse_csv(file_path, start_time, n)

        if plot_time:
            ax.plot(time[:n], values[:n], label=label)
        else:
            ax.plot(values[:n], label=label)

        all_iter_time.update(iter_map)
        last_time = time
        last_values = values

    # Axe inférieur (temps ou itération)
    if plot_time:
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("State")
        ax.set_xlim(0, 100)
        ax.grid(True)

        # Axe supérieur : itérations
        ax2 = ax.twiny()
        ticks = list(all_iter_time.values())
        labels = list(all_iter_time.keys())
        step = max(1, len(labels) // 5)
        ax2.set_xticks(ticks[::step])
        ax2.set_xticklabels(labels[::step])
        ax2.set_xlabel("Iteration")
        ax2.set_xlim(ax.get_xlim())

        if plot_start:
            ax.axvline(last_start_time - start_time, color='red', linestyle='--', label='Start')
    else:
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Value")

    ax.legend(loc='upper right')
    fig.tight_layout()

    suffix = "_time_start" if plot_time and plot_start else "_time" if plot_time else "_it"
    fig.savefig(f"{name.strip()}{suffix}.png")
    plt.show()

    # === PRINTS ===
    print(mean_interval(last_time[2:]))               # Moyenne des intervalles
    print(last_start_time - start_time)               # Temps entre le 3e et 1er point de chaque fichier
    print(last_values[-1] if last_values else None)   # Dernière valeur lue
    print()                                           # Ligne vide


# === PARAMÈTRES ===
n = 100
plot_time = True
plot_start = True
name = "loop"

# === LANCEMENT ===
csv_files = find_csv_files(name)
plot_data(csv_files, n, name, plot_time, plot_start)
