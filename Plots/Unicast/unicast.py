import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import glob

plt.rcParams.update({'font.size': 16})


"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


csv_files = glob.glob(os.path.join('REC_loop_4/', "*.csv"))

if not csv_files:
    print("Aucun fichier CSV trouvé dans le dossier.")
    exit()

start_time = float("inf")
first_change_time = float('inf')
last_end_time = 0
events_agents = []
agent_ids = []
drift_compensator = [0]*len(csv_files)
drift_compensator[1] = 0.05
drift_compensator[2] = 0
drift_compensator[3] = -0.03
drift_compensator[4] = 0

for file_path in csv_files:
    timestamps = []
    states = []
    agent_id = int(os.path.basename(file_path).split(".")[0])
    agent_ids.append(agent_id)
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                t, s = line.strip().split(",")
                timestamps.append(float(t)+drift_compensator[agent_id])
                s = int(s=="True")
                states.append(s)
                if s == 1:
                    first_change_time = min(first_change_time, float(t))

    start_time = min(start_time, timestamps[0])
    last_end_time = max(last_end_time, timestamps[-1])

    events = []
    for i in range(len(timestamps) - 1):
        start = timestamps[i]
        duration = timestamps[i + 1] - start
        state = states[i]
        events.append((start, duration, state))

    events.append((timestamps[-1], 5.0, states[-1]))

    events_agents.append(events)

start_time = first_change_time

fig, ax = plt.subplots(figsize=(8, 0.8 * len(events_agents)))
colors = {0: "lightcoral", 1: "mediumseagreen"}

sorted_indices = sorted(range(len(agent_ids)), key=lambda i: agent_ids[i])
agent_ids = [agent_ids[i] for i in sorted_indices]
events_agents = [events_agents[i] for i in sorted_indices]


for idx, (agent_id, events) in enumerate(zip(agent_ids, events_agents)):
    for start, duration, state in events:

        ax.add_patch(mpatches.Rectangle(
            (start - start_time, idx), duration, 0.8,
            color=colors[state], edgecolor='black'
        ))


ax.set_ylim(0, len(events_agents))
ax.set_xlim(first_change_time - start_time - 1, last_end_time - start_time + 1)
ax.set_xlim(38,48)
ax.set_yticks([i + 0.4 for i in range(len(agent_ids))])
ax.set_yticklabels([f"RPi {aid}" for aid in agent_ids])

ax.set_xlabel("Time (s)")
ax.grid(True, axis='x', linestyle='--', alpha=0.4)

ready_patch = mpatches.Patch(color="mediumseagreen", label="Ready")
not_ready_patch = mpatches.Patch(color="lightcoral", label="Busy")
ax.legend(handles=[not_ready_patch, ready_patch], loc="upper left")

plt.tight_layout()
plt.savefig('123_lin.png')
plt.show()
