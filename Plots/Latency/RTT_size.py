import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update({'font.size': 19})

# Données
rtt_by_size = {
    50: 59.3304,
    200: 67.0109,
    500: 71.7599,
    750: 81.2309,
    1000: 83.5771,
}

packet_sizes = sorted(rtt_by_size.keys())
rtt_values = [rtt_by_size[size] for size in packet_sizes]
T = np.array([2*size / rtt_by_size[size] for size in packet_sizes])
G = 0.7 * T

# Tracé
fig, ax1 = plt.subplots(figsize=(10, 6))

color = 'tab:blue'
ax1.set_xlabel("Packet size (bytes)")
ax1.set_ylabel("RTT (ms)", color=color)
line1, = ax1.plot(packet_sizes, rtt_values, marker='o', linestyle='-', color=color, label='Latency')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(0, 100)
ax1.grid(True)

# Axe secondaire pour T
ax2 = ax1.twinx()
color = 'tab:red'
line2, = ax2.plot(packet_sizes, T, marker='s', linestyle='-', color=color, label='Throughput')
line3, = ax2.plot(packet_sizes, G, marker='s', linestyle='--', color=color, label='Goodput')
ax2.set_ylabel("Throughput (Kb/s)", color=color)
ax2.tick_params(axis='y', labelcolor=color)

# Combinaison des légendes
lines = [line1, line2, line3]
labels = [line.get_label() for line in lines]
ax1.legend(lines, labels, loc='upper left')

fig.tight_layout()
plt.savefig('RTT_size.png')
plt.show()
