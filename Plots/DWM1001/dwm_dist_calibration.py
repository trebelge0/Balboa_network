import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
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
    filtered_data = {}
    for key, values in data.items():
        values = np.array(values)
        Q1 = np.percentile(values, 25)
        Q3 = np.percentile(values, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        filtered_values = values[(values >= lower_bound) & (values <= upper_bound)]
        filtered_data[key] = filtered_values.tolist()
    return filtered_data


measures = lire_donnees('dwm_calibration_data')
del measures[3.0]
del measures[4.0]

filtered_measures = filter(measures)  # Remove outliers

mean_values = {key: np.mean(value) for key, value in filtered_measures.items()}  # Mean
std_devs = {key: np.std(value) for key, value in filtered_measures.items()}  # Std

distances = list(mean_values.keys())
moyennes_mesures = list(mean_values.values())

X = np.array(distances).reshape(-1, 1)
y = np.array(moyennes_mesures)

regressor = LinearRegression()
regressor.fit(X, y)
y_pred = regressor.predict(X) # Linear regression

# measured_distance = slope * estimated_distance + oo
# estimated_distance = (measured_distance - oo) / slope
slope = regressor.coef_[0]
oo = regressor.intercept_

d = 2.25
plt.figure(figsize=(10, 6))
print(measures[d])
plt.hist(measures[d])
plt.axvline(x=d, color='red', linestyle='--', label='Actual distance')
values = np.array(measures[d])
Q1 = np.percentile(values, 25)
Q3 = np.percentile(values, 75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
plt.axvline(x=lower_bound, color='black', linestyle='--', label='IQR bounds')
plt.axvline(x=upper_bound, color='black', linestyle='--')
plt.xlabel("Distance classes (m)")
plt.ylabel("Occurences")
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig(f"histo{d}.png")
plt.show()

fig, axs = plt.subplots(2, 1, figsize=(10, 12))

for distance in measures.keys():
    axs[0].scatter([distance] * len(measures[distance]), measures[distance], alpha=0.5)

for distance in measures.keys():
    axs[0].errorbar(distance, mean_values[distance], yerr=std_devs[distance], fmt='o', color='black')

axs[0].plot(distances, y_pred, color='red', label='Estimated distance')
axs[0].plot(distances, distances, label='Not calibrated model', linestyle='--')
axs[0].set_ylabel("Measured distance (m)")
axs[0].legend()
axs[0].grid(True)


errors_calibrated = (np.array(moyennes_mesures) - y_pred)*100
errors_raw = (-np.array(moyennes_mesures) + np.array(distances))*100

for i, distance in enumerate(measures.keys()):
    axs[1].scatter([distance] * len(measures[distance]), np.array(measures[distance])*100 - 100*np.array([list(y_pred)[i]] * len(measures[distance])), alpha=0.5)
    #plt.scatter([distance] * len(filtered_measures[distance]), -np.array(filtered_measures[distance])*100 + 100*np.array([list(y_pred)[i]] * len(filtered_measures[distance])), alpha=0.5)

axs[1].plot(distances, errors_calibrated, label='Average residual error', color='green')
axs[1].set_xlabel("Actual distance (m)")
axs[1].set_ylabel("Residual error (cm)")
axs[1].legend()
axs[1].grid(True)
plt.tight_layout()
plt.savefig("cal.png")
plt.show()

print("------- Calibrated model -------")
print()
print(f"Calibrated model slope: {1/slope}")
print(f"Calibrated model origin shift: {-oo/slope}")
print("Estimated distance = slope * measured_distance + oo")
print()

print("------- Statistics -------")
print()
print(f"Mean error before calibration (cm): {np.mean(errors_raw)}")
print(f"RMS error before calibration (cm): {np.sqrt(np.mean(errors_raw**2))}")
print(f"Mean error after calibration(cm): {np.mean(errors_calibrated)}")
print(f"RMS error after calibration (cm): {np.sqrt(np.mean(errors_calibrated**2))} (cm)")
