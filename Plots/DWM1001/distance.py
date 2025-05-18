from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
plt.rcParams.update({'font.size': 18})


GT = [25, 50, 70, 75, 90.14, 100, 113, 125, 145.77, 150]
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

    x = np.array(data[d])
    Q1 = np.percentile(x, 25)
    Q3 = np.percentile(x, 75)
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
    plt.savefig(f"histo_dist_{d}.png")
    plt.show()


def filter(data, window_size):

    x_bar = {}
    outliers = {}
    lower_bound = {}
    upper_bound = {}

    for i in GT:
        x_i = np.array(data[i])
        Q1 = np.percentile(x_i, 25)
        Q3 = np.percentile(x_i, 75)
        IQR = Q3 - Q1
        lower_bound[i] = Q1 - 1.5 * IQR
        upper_bound[i] = Q3 + 1.5 * IQR

        x_bar[i] = x_i[(x_i >= lower_bound[i]) & (x_i <= upper_bound[i])]
        outliers[i] = x_i[(x_i < lower_bound[i]) | (x_i > upper_bound[i])]

        for j in range(len(x_bar[i])):
            window_values = []
            for j in range(max(0, j - window_size + 1), j + 1):
                window_values.append(x_bar[i][j])
            x_bar[i][j] = np.mean(window_values)

    return x_bar, outliers, lower_bound, upper_bound


def plot_filter(data, d):

    x = np.array(data[d])
    x_bar, outliers, upper_bound, lower_bound = filter(data, WINDOW_SIZE)
    x_bar = x_bar[d]
    outliers = outliers[d]
    upper_bound = upper_bound[d]
    lower_bound = lower_bound[d]

    outliers_dict = {}

    for i in range(len(x)):
        if x[i] in outliers:
            outliers_dict[i] = x[i]

    plt.figure(figsize=(10, 6))
    plt.scatter(range(len(x)), x, alpha=0.9, label='Filtered')
    plt.scatter(outliers_dict.keys(), outliers_dict.values(), alpha=0.9, color='red', label='Outlier')
    plt.plot(np.arange(0, len(x), 1), [upper_bound] * len(x), alpha=0.9, linestyle='--', color='black',
             label='Outlier bounds')
    plt.plot(np.arange(0, len(x), 1), [lower_bound] * len(x), alpha=0.9, linestyle='--', color='black')
    plt.plot(np.arange(0, len(x), 1), [2.25] * len(x), alpha=0.9, linestyle='--', color='red',
             label='Actual distance')
    plt.plot(x_bar, color='orange', linewidth=2, label=f'Moving average (window size: {WINDOW_SIZE})')
    plt.xlabel('Measures')
    plt.ylabel('Measured distance (m)')
    plt.grid()
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(f'filt_dist_{WINDOW_SIZE}.png')
    plt.show()


def compute_model(data):
    x_bar = {key: np.mean(x) for key, x in data.items()}  # Mean

    y = list(x_bar.keys())
    x_bar = list(x_bar.values())

    regressor = LinearRegression()
    regressor.fit(np.array(y).reshape(-1, 1), np.array(x_bar))
    x_hat = regressor.predict(np.array(y).reshape(-1, 1))  # Linear regression

    # x = slope*y + oo
    slope = regressor.coef_[0]
    oo = regressor.intercept_

    print("------- Calibrated model -------")
    print()
    print(slope)
    print(oo)
    print(f"Calibrated estimator slope: {1/slope}")
    print(f"Calibrated estimator origin shift: {-oo/slope}")
    print("y_hat = slope * x + oo")
    print()

    return 1/slope, -oo/slope, x_hat


def calibrate(data, a, b):
    calibrated_data = {}
    for i in GT:
        calibrated_data[i] = list((np.array(data[i]))*a+b)
    return calibrated_data


def error(data, y_pred, outliers):

    mean_values = {key: np.mean(value) for key, value in data.items()}  # Mean
    std_devs = {key: np.std(value) for key, value in data.items()}  # Std
    mean_measured_distances = list(mean_values.values())

    res_error = (y_pred - np.array(mean_measured_distances))

    fig, axs = plt.subplots(2, 1, figsize=(10, 12))

    for distance in data.keys():
        axs[0].scatter([distance] * len(data[distance]), data[distance], alpha=0.5)

    for distance in data.keys():
        axs[0].errorbar(distance, mean_values[distance], yerr=std_devs[distance], fmt='o', color='black')
    axs[0].plot(GT, y_pred, color='red', label=r'Calibrated sensor model ($\hat{m}=ad+b$)')
    axs[0].plot(GT, GT, label=r'Uncalibrated sensor model ($\hat{m}=d$)', linestyle='--')
    axs[0].set_ylabel("Measured value: m (cm)")
    axs[0].legend()
    axs[0].grid(True)

    for i, distance in enumerate(data.keys()):
        axs[1].scatter([distance] * len(data[distance]),
                       -np.array(data[distance]) + np.array([list(y_pred)[i]] * len(data[distance])), alpha=0.5)

    for i, distance in enumerate(outliers.keys()):
        axs[1].scatter([distance] * len(outliers[distance]),
                       -np.array(outliers[distance]) + np.array([list(y_pred)[i]] * len(outliers[distance])), alpha=0.5, marker='x', s=100, color='red')

    axs[1].plot(GT, res_error, label=r'Filtered ($\bar{e}_r$)', color='green')
    axs[1].set_xlabel("Actual distance: d (cm)")
    axs[1].set_ylabel(r"Calibrated $e_r$ (cm)")
    axs[1].legend()
    axs[1].grid(True)

    plt.tight_layout()
    plt.savefig("cal_dist.png")
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
           70, 113, 113, 70,
           90.14, 145.77, 145.77, 90.14]
x = read_data(GT_full, "Final/full.csv")
x = dict(sorted(x.items()))
d = 113
histogram(d, x)
x_bar = filter(x, WINDOW_SIZE)
outliers = x_bar[1]
x_bar = x_bar[0]
plot_filter(x, d)

a, b, y_pred = compute_model(x_bar)
d_hat = calibrate(x_bar, a, b)
error(x, y_pred, outliers)

plt.figure(figsize=(10, 6))
cumulative_error(x, "Without processing", 'tab:blue')
cumulative_error(d_hat, "With processing", 'tab:orange')
plt.grid()
plt.legend()
plt.savefig('cumul_dist.png')
plt.show()
