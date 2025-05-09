import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})


# Exemple de dictionnaire RTT (remplace par tes vraies données)
rtt_by_size = {
    50: 59.3304,
    200: 67.0109,
    500: 71.7599,
    750: 81.2309,
    1000: 83.5771,
}

packet_sizes = sorted(rtt_by_size.keys())
rtt_values = [rtt_by_size[size] for size in packet_sizes]

# Tracé
plt.figure(figsize=(8, 5))
plt.plot(packet_sizes, rtt_values, marker='o', linestyle='-')
plt.xlabel("Packet size (bytes)")
plt.ylabel("RTT (s)")
plt.ylim(0,100)
plt.grid(True)
plt.tight_layout()
plt.show()
plt.savefig('RTT_size.png')
