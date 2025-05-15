from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

plt.rcParams.update({'font.size': 18})

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
                if float(l[0]) <= len(GT):
                    i = int(l[0])
                else:
                    data[GT[i]].append((float(l[1])/10, float(l[2])/10))
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
    mean_measurement = np.mean(values)
    distances = np.linalg.norm(values - mean_measurement, axis=1)
    _, bound = iqr_filter(distances)

    plt.figure(figsize=(10, 6))
    plt.hist(distances)
    plt.axvline(x=bound, color='black', linestyle='--')
    plt.xlabel("Distance classes (cm)")
    plt.ylabel("Occurences")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f"histo{d}.png")
    plt.show()


def iqr_filter(values):
    Q1 = np.percentile(values, 40)
    Q3 = np.percentile(values, 60)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return lower_bound, upper_bound


def filter(data, window_size):

    filtered_data = {}
    outliers = {}
    bound = {}

    for i in GT:

        data_i = np.array(data[i])
        mean_meas = np.mean(data_i, axis=0)
        distances = np.linalg.norm(data_i - mean_meas, axis=1)
        _, bound[i] = iqr_filter(distances)
        filtered_data[i] = data_i[distances <= bound[i]]
        outliers[i] = data_i[distances > bound[i]]

        for j in range(len(filtered_data[i])):
            window_values = []
            for j in range(max(0, j - window_size + 1), j + 1):
                window_values.append(filtered_data[i][j])
            filtered_data[i][j] = np.mean(window_values, axis=0)

    return filtered_data, outliers, bound


def compute_model(data):
    mean_positions = {key: np.mean(value, axis=0) for key, value in data.items()}

    actual_positions = np.array(list(mean_positions.keys()))
    measured_positions = np.array(list(mean_positions.values()))

    regressor = LinearRegression()
    print(measured_positions)
    print(actual_positions)
    regressor.fit(measured_positions, actual_positions)

    A = regressor.coef_          # Matrice 2x2 de transformation
    b = regressor.intercept_     # Vecteur 2D de décalage
    y_pred = regressor.predict(measured_positions)

    print("------- Calibrated model -------\n")
    print(f"Calibrated model slope matrix (A):\n{A}")
    print(f"Measured model origin shift (b): {b}")
    print("\n Estimated position = A @ Measured + b\n")

    return A, b, y_pred


def calibrate(data, A, b):
    calibrated_data = {}
    for i in GT:
        calibrated_data[i] = (A @ np.array(data[i]).T).T + b
    return calibrated_data


def show(data, cal):

    plt.figure(figsize=(10, 10))
    colors = [
        '#1f77b4',  # bleu
        '#ff7f0e',  # orange
        '#2ca02c',  # vert
        '#d62728',  # rouge
        '#9467bd',  # violet
        '#8c564b',  # brun
        '#e377c2',  # rose
        '#7f7f7f',  # gris
        '#bcbd22',  # vert-jaune
        '#17becf',  # turquoise
        '#aec7e8',  # bleu clair
        '#ffbb78',  # orange clair
        '#98df8a',  # vert clair
        '#ff9896',  # rouge clair
        '#c5b0d5'  # violet clair
    ]

    for idx, i in enumerate(GT):
        data_i = np.array(data[i])
        mean_meas = np.mean(data_i, axis=0)
        filtered_data, outliers, bound = filter(data, WINDOW_SIZE)
        filtered_data = filtered_data[i]
        outliers = outliers[i]
        bound = bound[i]
        calibrated_data = cal[i]

        #plot un cercle de centre d
        theta = np.linspace(0, 2 * np.pi, 200)
        circle_x = mean_meas[0] + bound * np.cos(theta)
        circle_y = mean_meas[1] + bound * np.sin(theta)
        plt.plot(circle_x, circle_y, linestyle='--', color=colors[idx%len(colors)])
        plt.plot(filtered_data[:,0], filtered_data[:,1], color=colors[idx%len(colors)])
        plt.scatter(data_i[:,0], data_i[:,1], color='tab:grey', alpha=0.2)
        plt.scatter(outliers[:,0], outliers[:,1], color='tab:red', alpha=0.5)
        plt.scatter(calibrated_data[:,0], calibrated_data[:,1], color='tab:green', alpha=0.5)
        plt.scatter(i[0], i[1], marker='2', s=300, color=colors[idx%len(colors)])
        plt.xlabel('x')
        plt.ylabel('y')

    plt.grid()
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(f'filt_{WINDOW_SIZE}.png')
    plt.show()


def error():



    """print("------- Statistics -------")
    print()
    print(f"Mean error before calibration (cm): {np.mean(errors_raw)}")
    print(f"RMS error before calibration (cm): {np.sqrt(np.mean(errors_raw ** 2))}")
    print(f"Mean error after calibration(cm): {np.mean(errors_calibrated)}")
    print(f"RMS error after calibration (cm): {np.sqrt(np.mean(errors_calibrated ** 2))} (cm)")"""


def cumulative_error(data, label, color):

    errors = []

    for p in GT:
        errors += list(np.linalg.norm(np.array(data[p]) - p, axis=1))

    errors.sort()
    cdf = np.arange(1, len(errors) + 1) / len(errors)

    plt.plot(errors, cdf, label=label, color=color)
    plt.xlabel("Absolute ranging error (cm)")
    plt.ylabel("Cumulative error probability")


"""GT_front = [(75, 100), (100, 100), (125, 100), (150, 100), (175, 100), (200, 100)]
GT_left = [(50, 75), (50, 50), (50, 25), (50, 0)]
GT_right = [(50, 125), (50, 150), (50, 175)]

data = read_data(GT_front, "Final/front.csv")
data = fuse(data, read_data(GT_right, "Final/right.csv"))
data = fuse(data, read_data(GT_left, "Final/left.csv"))
GT = GT_front + GT_right + GT_left"""

GT = [(25, 100), (75, 100), (100, 100), (125, 100), (150, 100), (175, 100), (200, 100),
      (50, 0), (50, 25), (50, 50), (50, 75), (50, 125), (50, 150), (50, 175),
      (100, 150), (150, 150), (150, 50), (100, 50)
      ]
data = read_data(GT, "Final/full.csv")


d = (125,100)
#histogram(d, data)
filtered_data = filter(data, WINDOW_SIZE)[0]

A, b, y_pred = compute_model(filtered_data)
#a, b = 0.95, -5
#y_pred = set_model(filtered_data, a, b)

calibrated_data = calibrate(filtered_data, A, b)
show(data, calibrated_data)

plt.figure(figsize=(10, 6))
cumulative_error(data, "Before processing", 'tab:blue')
cumulative_error(calibrated_data, "After processing", 'tab:orange')
plt.grid()
plt.legend()
plt.show()
