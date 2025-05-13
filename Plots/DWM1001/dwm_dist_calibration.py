import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
plt.rcParams.update({'font.size': 14})


def lire_donnees(fichier):
    with open(fichier, 'r') as f:
        lignes = f.readlines()

    mesures = {}
    distance = None
    valeurs = []
    GT = [50, 100, 150, 200]
    for i in GT:
        mesures[i] = []

    for ligne in lignes:
        ligne = ligne.strip()
        if float(ligne) < 10:
            if distance is not None:
                mesures[distance].append(valeurs)
            distance = GT[int(ligne)-1]
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


measures = lire_donnees('distance.csv')
print(measures)

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

d = 50
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


errors_calibrated = (np.array(moyennes_mesures) - y_pred)
errors_raw = (-np.array(moyennes_mesures) + np.array(distances))

for i, distance in enumerate(measures.keys()):
    axs[1].scatter([distance] * len(measures[distance]), np.array(measures[distance]) - np.array([list(y_pred)[i]] * len(measures[distance])), alpha=0.5)
    #plt.scatter([distance] * len(filtered_measures[distance]), -np.array(filtered_measures[distance])*100 + 100*np.array([list(y_pred)[i]] * len(filtered_measures[distance])), alpha=0.5)

axs[1].plot(distances, errors_calibrated, label='Average residual error', color='green')
axs[1].set_xlabel("Actual distance (m)")
axs[1].set_ylabel("Residual error (cm)")
axs[1].legend()
axs[1].grid(True)
plt.tight_layout()
plt.savefig("cal.png")
plt.show()

