import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 18})


"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


# Puissance consommée par chaque composant (en watts)
components = ['Decawave', 'Balboa', 'Raspberry Pi', 'Actuators']
power_values = [0.2, 0.249, 1.18, 1.43]  # Total = 3.06 W (proche de 3.16 W max mesuré)
components.reverse()
power_values.reverse()
colors = ['tab:blue', 'tab:green', 'tab:orange', 'tab:red']

fig, ax = plt.subplots(figsize=(6, 6))

# Empilement
bottom = 0
for power, label, color in zip(power_values, components, colors):
    ax.bar('Agent', power, bottom=bottom, label=label, color=color)
    bottom += power

ax.set_ylabel("Power consumption [W]")
ax.legend(loc='upper right')
ax.set_ylim(0, sum(power_values) + 0.5)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("consumption_stack.png")
plt.show()
