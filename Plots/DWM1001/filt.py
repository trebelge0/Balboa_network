import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 20})


def lire_donnees(fichier):
    with open(fichier, 'r') as f:
        lignes = f.readlines()

    mesures = {}
    distance = None
    valeurs = []

    for ligne in lignes:
        ligne = ligne.strip()
        if 'm' in ligne:
            if distance is not None:
                mesures[distance] = valeurs
            distance = float(ligne.replace('m', '').strip())
            valeurs = []
        else:
            try:
                valeurs.append(float(ligne))
            except ValueError:
                continue
    if distance is not None:
        mesures[distance] = valeurs

    return mesures


def filter(data):
    data = np.array(data)
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return data[(data >= lower_bound) & (data <= upper_bound)], data[(data < lower_bound) | (data > upper_bound)], lower_bound, upper_bound


def filtered_moving_average(data, window_size, outlier_indices):
    result = []
    for i in range(len(data)):
        window_values = []
        for j in range(max(0, i - window_size + 1), i + 1):
            if j not in outlier_indices:
                window_values.append(data[j])
        if len(window_values) > 0:
            result.append(np.mean(window_values))
        else:
            result.append(np.nan)
    return result


# --- Lecture et filtrage ---
measures = lire_donnees('dwm_calibration_data')
measures = measures[2.25]
WINDOW_SIZE = 15

filtered_measures, outliers, lower, upper = filter(measures)

measures_dict = {}
filtered_dict = {}
outliers_dict = {}
outlier_indices = []

for i in range(len(measures)):
    measures_dict[i] = measures[i]
    if measures[i] in filtered_measures:
        filtered_dict[i] = measures[i]
    elif measures[i] in outliers:
        outliers_dict[i] = measures[i]
        outlier_indices.append(i)

mean = np.mean(filtered_measures)
std = np.std(filtered_measures)

# --- Moving average filtrée ---
ma = filtered_moving_average(measures, window_size=WINDOW_SIZE, outlier_indices=outlier_indices)

# --- Plot ---
plt.figure(figsize=(10, 6))

plt.scatter(filtered_dict.keys(), filtered_dict.values(), alpha=0.9, label='Filtered')
plt.scatter(outliers_dict.keys(), outliers_dict.values(), alpha=0.9, color='red', label='Outlier')
plt.plot(np.arange(0, len(measures), 1), [upper]*len(measures), alpha=0.9, linestyle='--', color='black', label='Outlier bounds')
plt.plot(np.arange(0, len(measures), 1), [lower]*len(measures), alpha=0.9, linestyle='--', color='black')
plt.plot(np.arange(0, len(measures), 1), [2.25]*len(measures), alpha=0.9, linestyle='--', color='red', label='Actual distance')
plt.plot(ma, color='orange', linewidth=2, label=f'Moving average (window size: {WINDOW_SIZE})')
plt.xlabel('Measures')
plt.ylabel('Measured distance (m)')
plt.grid()
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig(f'filt_{WINDOW_SIZE}.png')
plt.show()