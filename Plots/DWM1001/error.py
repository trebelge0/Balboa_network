import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

plt.rcParams.update({'font.size': 14})


GT = [250, 500, 750, 1000, 1250, 1500]
WINDOW_SIZE = 2


def read_data():
    # distance
    file_path = 'Final_cal/front.csv'
    i = 0
    data = {}
    for j in GT:
        data[j] = []

    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                l = line.strip().split(",")
                if float(l[0]) < len(GT):
                    i = int(l[0])
                else:
                    print(i)
                    data[GT[i]].append(float(l[0]))
    return data


def filter(data, window_size):

    filtered_data = {}
    for i in GT:
        data_i = np.array(data[i])
        Q1 = np.percentile(data_i, 25)
        Q3 = np.percentile(data_i, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        filtered_data[i] = data_i[(data_i >= lower_bound) & (data_i <= upper_bound)]

        for j in range(len(filtered_data[i])):
            window_values = []
            for j in range(max(0, j - window_size + 1), j + 1):
                window_values.append(filtered_data[i][j])
            filtered_data[i][j] = np.mean(window_values)

    return filtered_data


def calibrate(data):
    a, b, y_pred = compute_model(data)
    calibrated_data = {}
    for i in GT:
        calibrated_data[i] = list((np.array(data[i])-b)/a)
    return calibrated_data, y_pred


def cumulative_error(data, label):
    i = 100
    errors = np.abs(np.array(data[i]) - i)
    errors_sorted = np.sort(errors)
    cdf = np.arange(1, len(errors_sorted) + 1) / len(errors_sorted)
    plt.plot(errors_sorted, cdf, marker='s', label=label)
    plt.xlabel("Absolute ranging error (cm)")
    plt.ylabel("Cumulative error probability")


def compute_model(data):
    mean_values = {key: np.mean(value) for key, value in data.items()}  # Mean

    distances = list(mean_values.keys())
    moyennes_mesures = list(mean_values.values())

    X = np.array(distances).reshape(-1, 1)
    y = np.array(moyennes_mesures)

    regressor = LinearRegression()
    regressor.fit(X, y)
    y_pred = regressor.predict(X)  # Linear regression

    # measured_distance = slope * estimated_distance + oo
    # estimated_distance = (measured_distance - oo) / slope
    slope = regressor.coef_[0]
    oo = regressor.intercept_

    print("------- Calibrated model -------")
    print()
    print(f"Calibrated model slope: {1 / slope}")
    print(f"Calibrated model origin shift: {-oo / slope}")
    print("Estimated distance = slope * measured_distance + oo")
    print()

    return slope, oo, y_pred


def histogram(d, data):

    values = np.array(data[d])
    Q1 = np.percentile(values, 25)
    Q3 = np.percentile(values, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    plt.figure(figsize=(10, 6))
    plt.hist(data[d])
    plt.axvline(x=d, color='red', linestyle='--', label='Actual distance')
    plt.axvline(x=lower_bound, color='black', linestyle='--', label='IQR bounds')
    plt.axvline(x=upper_bound, color='black', linestyle='--')
    plt.xlabel("Distance classes (m)")
    plt.ylabel("Occurences")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f"histo{d}.png")
    plt.show()


def error(data, y_pred):

    mean_values = {key: np.mean(value) for key, value in filtered_data.items()}  # Mean
    std_devs = {key: np.std(value) for key, value in filtered_data.items()}  # Std
    mean_measured_distances = list(mean_values.keys())

    errors_calibrated = (np.array(mean_measured_distances) - y_pred)
    errors_raw = (-np.array(mean_measured_distances) + np.array(GT))

    fig, axs = plt.subplots(2, 1, figsize=(10, 12))

    for distance in data.keys():
        axs[0].scatter([distance] * len(data[distance]), data[distance], alpha=0.5)

    for distance in data.keys():
        axs[0].errorbar(distance, mean_values[distance], yerr=std_devs[distance], fmt='o', color='black')

    axs[0].plot(GT, y_pred, color='red', label='Estimated distance')
    axs[0].plot(GT, GT, label='Not calibrated model', linestyle='--')
    axs[0].set_ylabel("Measured distance (m)")
    axs[0].legend()
    axs[0].grid(True)

    for i, distance in enumerate(data.keys()):
        axs[1].scatter([distance] * len(data[distance]),
                       np.array(data[distance]) - np.array([list(y_pred)[i]] * len(data[distance])), alpha=0.5)
    axs[1].plot(GT, errors_calibrated, label='Average residual error', color='green')
    axs[1].set_xlabel("Actual distance (m)")
    axs[1].set_ylabel("Residual error (cm)")
    axs[1].legend()
    axs[1].grid(True)

    plt.tight_layout()
    plt.savefig("cal.png")
    plt.show()

    print("------- Statistics -------")
    print()
    print(f"Mean error before calibration (cm): {np.mean(errors_raw)}")
    print(f"RMS error before calibration (cm): {np.sqrt(np.mean(errors_raw ** 2))}")
    print(f"Mean error after calibration(cm): {np.mean(errors_calibrated)}")
    print(f"RMS error after calibration (cm): {np.sqrt(np.mean(errors_calibrated ** 2))} (cm)")


data = read_data()
#histogram(100, data)
filtered_data = filter(data, WINDOW_SIZE)
calibrated_data, y_pred = calibrate(filtered_data)
error(data, y_pred)

plt.figure(figsize=(10, 6))
cumulative_error(filtered_data, "Error before processing")
cumulative_error(calibrate(filtered_data), "Error after processing")
plt.legend()
plt.show()
