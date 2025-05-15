from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
plt.rcParams.update({'font.size': 20})


GT = [25, 50, 70, 75, 100, 113, 125, 150]
WINDOW_SIZE = 5


def read_data(GT, file_path):
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
                    data[GT[i]].append(float(l[0])/10)
    return data


def fuse(d1, d2):
    merged = defaultdict(list)
    for key, value in d1.items():
        merged[key].extend(value)
    for key, value in d2.items():
        merged[key].extend(value)
    return dict(merged)


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
    plt.xlabel("Distance classes (cm)")
    plt.ylabel("Occurences")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f"histo{d}.png")
    plt.show()


def filter(data, window_size):

    filtered_data = {}
    outliers = {}
    lower_bound = {}
    upper_bound = {}

    for i in GT:
        data_i = np.array(data[i])
        Q1 = np.percentile(data_i, 25)
        Q3 = np.percentile(data_i, 75)
        IQR = Q3 - Q1
        lower_bound[i] = Q1 - 1.5 * IQR
        upper_bound[i] = Q3 + 1.5 * IQR

        filtered_data[i] = data_i[(data_i >= lower_bound[i]) & (data_i <= upper_bound[i])]
        outliers[i] = data_i[(data_i < lower_bound[i]) | (data_i > upper_bound[i])]

        for j in range(len(filtered_data[i])):
            window_values = []
            for j in range(max(0, j - window_size + 1), j + 1):
                window_values.append(filtered_data[i][j])
            filtered_data[i][j] = np.mean(window_values)

    return filtered_data, outliers, lower_bound, upper_bound


def plot_filter(data, d):

    values = np.array(data[d])
    filtered_data, outliers, upper_bound, lower_bound = filter(data, WINDOW_SIZE)
    filtered_data = filtered_data[d]
    outliers = outliers[d]
    upper_bound = upper_bound[d]
    lower_bound = lower_bound[d]

    outliers_dict = {}

    for i in range(len(values)):
        if values[i] in outliers:
            outliers_dict[i] = values[i]

    plt.figure(figsize=(10, 6))
    plt.scatter(range(len(values)), values, alpha=0.9, label='Filtered')
    plt.scatter(outliers_dict.keys(), outliers_dict.values(), alpha=0.9, color='red', label='Outlier')
    plt.plot(np.arange(0, len(values), 1), [upper_bound] * len(values), alpha=0.9, linestyle='--', color='black',
             label='Outlier bounds')
    plt.plot(np.arange(0, len(values), 1), [lower_bound] * len(values), alpha=0.9, linestyle='--', color='black')
    plt.plot(np.arange(0, len(values), 1), [2.25] * len(values), alpha=0.9, linestyle='--', color='red',
             label='Actual distance')
    plt.plot(filtered_data, color='orange', linewidth=2, label=f'Moving average (window size: {WINDOW_SIZE})')
    plt.xlabel('Measures')
    plt.ylabel('Measured distance (m)')
    plt.grid()
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(f'filt_{WINDOW_SIZE}.png')
    plt.show()


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
    print(f"Calibrated model slope: {1/slope}")
    print(f"Calibrated model origin shift: {-oo/slope}")
    print("Estimated distance = slope * measured_distance + oo")
    print()

    return 1/slope, -oo/slope, y_pred


def set_model(data, a, b):
    regressor = LinearRegression()
    mean_values = {key: np.mean(value) for key, value in data.items()}  # Mean
    distances = list(mean_values.keys())
    X = np.array(distances).reshape(-1, 1)
    regressor.coef_ = np.array([1 / a])
    regressor.intercept_ = -b / a
    return regressor.predict(X)


def calibrate(data, a, b, y_pred):
    calibrated_data = {}
    for i in GT:
        calibrated_data[i] = list((np.array(data[i]))*a+b)
    return calibrated_data


def error(data, y_pred):

    mean_values = {key: np.mean(value) for key, value in data.items()}  # Mean
    std_devs = {key: np.std(value) for key, value in data.items()}  # Std
    mean_measured_distances = list(mean_values.values())

    res_error = (y_pred - np.array(mean_measured_distances))

    fig, axs = plt.subplots(2, 1, figsize=(10, 12))

    for distance in data.keys():
        axs[0].scatter([distance] * len(data[distance]), data[distance], alpha=0.5)

    for distance in data.keys():
        axs[0].errorbar(distance, mean_values[distance], yerr=std_devs[distance], fmt='o', color='black')
    axs[0].plot(GT, y_pred, color='red', label='Estimated distance')
    axs[0].plot(GT, GT, label='Not calibrated model', linestyle='--')
    axs[0].set_ylabel("Measured distance (cm)")
    axs[0].legend()
    axs[0].grid(True)

    for i, distance in enumerate(data.keys()):
        axs[1].scatter([distance] * len(data[distance]),
                       np.array(data[distance]) - np.array([list(y_pred)[i]] * len(data[distance])), alpha=0.5)

    axs[1].plot(GT, res_error, label='Average residual error', color='green')
    axs[1].set_xlabel("Actual distance (cm)")
    axs[1].set_ylabel("Residual error (cm)")
    axs[1].legend()
    axs[1].grid(True)

    plt.tight_layout()
    plt.savefig("cal.png")
    plt.show()

    filtered_error = (np.array(mean_measured_distances) - np.array(GT))

    print("------- Statistics -------")
    print()
    print(f"Mean error before calibration (cm): {np.mean(filtered_error)}")
    print(f"RMS error before calibration (cm): {np.sqrt(np.mean(filtered_error ** 2))}")
    print(f"Mean error after calibration(cm): {np.mean(res_error)}")
    print(f"RMS error after calibration (cm): {np.sqrt(np.mean(res_error ** 2))} (cm)")


def cumulative_error(data, label, color):

    errors = []

    for d in GT:
        errors += list(np.abs(np.array(data[d]) - d))

    errors.sort()
    cdf = np.arange(1, len(errors) + 1) / len(errors)

    plt.plot(errors, cdf, label=label, color=color)
    plt.xlabel("Absolute ranging error (cm)")
    plt.ylabel("Cumulative error probability")


#data = read_data("Final/front.csv")
#data = fuse(data, read_data("Final/right.csv"))
#data = fuse(data, read_data("Final/left.csv"))
GT_full = [25, 25, 50, 75, 100, 125, 150,
            100, 75, 50, 25, 25, 50, 75,
            70, 113, 113, 70]
data = read_data(GT_full, "Final/full.csv")
data = dict(sorted(data.items()))
d = 113
histogram(d, data)
filtered_data = filter(data, WINDOW_SIZE)[0]
plot_filter(data, d)

a, b, y_pred = compute_model(filtered_data)
#a, b = 0.95, -5
#y_pred = set_model(filtered_data, a, b)

calibrated_data = calibrate(filtered_data, a, b, y_pred)
error(data, y_pred)

plt.figure(figsize=(10, 6))
cumulative_error(data, "Before processing", 'tab:blue')
cumulative_error(calibrated_data, "After processing", 'tab:orange')
plt.grid()
plt.legend()
plt.show()
