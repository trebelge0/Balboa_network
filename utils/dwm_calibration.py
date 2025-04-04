import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
plt.rcParams.update({'font.size': 12})


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
#del measures[3.0]
#del measures[4.0]
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

plt.figure(figsize=(10, 6))
for distance in measures.keys():
    plt.scatter([distance] * len(measures[distance]), measures[distance], alpha=0.5)

for distance in measures.keys():
    plt.errorbar(distance, mean_values[distance], yerr=std_devs[distance], fmt='o', color='black')

plt.plot(distances, y_pred, color='red', label='Linear regression')
plt.plot(distances, distances, label='Actual value', linestyle='--')

plt.xlabel("Actual distance (m)")
plt.ylabel("Measured distance (m)")
plt.legend()
plt.grid(True)
plt.show()


plt.figure(figsize=(10, 6))

errors_calibrated = (-np.array(moyennes_mesures) + y_pred)*100
errors_raw = (-np.array(moyennes_mesures) + np.array(distances))*100

for i, distance in enumerate(measures.keys()):
    plt.scatter([distance] * len(measures[distance]), -np.array(measures[distance])*100 + 100*np.array([list(y_pred)[i]] * len(measures[distance])), alpha=0.5)
    #plt.scatter([distance] * len(filtered_measures[distance]), -np.array(filtered_measures[distance])*100 + 100*np.array([list(y_pred)[i]] * len(filtered_measures[distance])), alpha=0.5)

plt.plot(distances, errors_calibrated, label='Calibration error', color='green')
plt.xlabel("Actual distance (m)")
plt.ylabel("Calibrated measure error (cm)")
plt.legend()
plt.grid(True)
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
