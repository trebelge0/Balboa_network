import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === Charger les données ===
df = pd.read_csv("../pos.csv")

# === Grouper par position connue ===
grouped = df.groupby('pos_id')

# === Positions théoriques connues (dans l'ordre des IDs) ===
known_positions = {
    0: [0.5, 0.5],
    1: [0.5, 1.5],
    2: [0.5, 2.5],
    3: [1.5, 0.5],
    4: [1.5, 1.5],
    5: [1.5, 2.5],
    6: [2.5, 0.5],
    7: [2.5, 1.5],
    8: [2.5, 2.5],
}

# === Calcul de la moyenne pour chaque groupe ===
means = grouped[['x', 'y']].mean()

# === Création des arrays de régression ===
true_positions = []
measured_positions = []

for pos_id, row in means.iterrows():
    if pos_id in known_positions:
        true_positions.append(known_positions[pos_id])
        measured_positions.append([row['x'], row['y']])

true_positions = np.array(true_positions)
measured_positions = np.array(measured_positions)

# === Correction simple par offset ===
offset = np.mean(true_positions - measured_positions, axis=0)

print(f"Correction to apply on measured positions: dx = {offset[0]:.3f} m, dy = {offset[1]:.3f} m")

# === Affichage ===
plt.figure(figsize=(8, 8))
colors = plt.cm.tab10(np.linspace(0, 1, len(means)))

for i, color in zip(means.index, colors):
    group = grouped.get_group(i)
    plt.scatter(group['x'], group['y'], color=color, alpha=0.4, label=f'pos_id {i}')

# Mesures corrigées
corrected_positions = measured_positions + offset
plt.scatter(measured_positions[:, 0], measured_positions[:, 1], color='red', marker='x', label="Measured Mean")
plt.scatter(corrected_positions[:, 0], corrected_positions[:, 1], color='green', marker='o', label="Corrected Mean")
plt.scatter(true_positions[:, 0], true_positions[:, 1], color='black', marker='*', s=100, label="True Position")

plt.xlabel("X (m)")
plt.ylabel("Y (m)")
plt.legend()
plt.title("Measured vs Corrected Positions (Calibration)")
plt.grid(True)
plt.axis("equal")
plt.tight_layout()
plt.show()
