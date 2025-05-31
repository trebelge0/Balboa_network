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


def mean_interval(times):
    if len(times) < 2:
        return 0.0
    intervals = [t2 - t1 for t1, t2 in zip(times[:-1], times[1:])]
    return sum(intervals) / len(intervals)


def find_csv_files(folder):
    files = glob.glob(os.path.join(folder.strip(), "*.csv"))
    files.sort(reverse=True)
    if not files:
        print("Aucun fichier CSV trouvé dans le dossier.")
        exit()
    return files


def get_time_bounds(files):
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

    if plot_time:
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("State")
        ax.set_xlim(0, 100)
        ax.grid(True)

        ax2 = ax.twiny()
        ticks = list(all_iter_time.values())
        labels = list(all_iter_time.keys())
        step = max(1, len(labels) // 10)
        ax2.set_xticks(ticks[::step])
        ax2.set_xticklabels(labels[::step])
        ax2.set_xlabel("Iteration")
        ax2.set_xlim(ax.get_xlim())

        if plot_start:
            ax.axvline(last_start_time - start_time, color='red', linestyle='--', label='Start')
    else:
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Value")

    ax.legend(loc='upper right', fontsize=14)
    fig.tight_layout()

    fig.savefig(f"cons_loop.png")
    plt.show()

    # === PRINTS ===
    print(mean_interval(last_time[2:]))
    print(last_start_time - start_time)
    print(last_values[-1] if last_values else None)
    print()


n = 100
plot_time = True
plot_start = True
name = "loop"

csv_files = find_csv_files(name)
plot_data(csv_files, n, name, plot_time, plot_start)
