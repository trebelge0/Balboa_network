import matplotlib.pyplot as plt
import numpy as np
import csv
plt.rcParams.update({'font.size': 19})


"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


packet_size = 200  # en bytes

filename = f'RTT{packet_size}.csv'
latencies = []

with open(filename, 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if row:  # éviter les lignes vides
            latencies.append(float(row[0])*1000)

mean_latency = np.mean(latencies)
std = np.std(latencies)
print(std)
print(f"Moyenne de latence pour un paquet de {packet_size} bytes : {mean_latency:.4f} ms")

plt.figure(figsize=(10, 6))
plt.hist(latencies, bins=10, color='skyblue', density=True, edgecolor='black')
plt.axvline(mean_latency, color='red', linestyle='--', label=f'Average')
plt.xlabel('RTT (ms)')
plt.ylabel('Frequency')
plt.xlim(min(latencies) - 20, max(latencies) + 20)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(f'{packet_size}.png')
plt.show()
