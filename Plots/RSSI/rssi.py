import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import os


"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


# Charger tous les fichiers CSV de type "rssi_*.csv"
csv_files = glob.glob("rssi_*.csv")

all_data = []

for file in csv_files:
    distance_str = os.path.basename(file).split("_")[1].replace("m.csv", "")
    distance = float(distance_str)
    df = pd.read_csv(file)
    df["distance_m"] = distance
    all_data.append(df)

data = pd.concat(all_data, ignore_index=True)

# Moyenne et écart-type du RSSI par distance
means = data.groupby("distance_m")["rssi_dbm"].mean()
stds = data.groupby("distance_m")["rssi_dbm"].std()

# Plot
plt.figure(figsize=(8, 6))
plt.errorbar(means.index, means, yerr=stds, fmt='o-', capsize=5, label="RSSI moyen ± écart-type")
plt.xlabel("Distance (m)")
plt.ylabel("RSSI (dBm)")
plt.title("RSSI en fonction de la distance (Bluetooth Classic)")
plt.grid(True)
plt.gca().invert_yaxis()  # Pour que les RSSI plus forts soient en haut
plt.legend()
plt.tight_layout()
plt.show()
