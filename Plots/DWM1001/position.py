from collections import defaultdict
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from scipy.interpolate import griddata
from matplotlib.colors import LinearSegmentedColormap


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
        if idx == 0:
            plt.plot(circle_x, circle_y, linestyle='--', color=colors[idx % len(colors)])
            plt.plot(filtered_data[:, 0], filtered_data[:, 1], color=colors[idx % len(colors)])
            plt.scatter(data_i[:, 0], data_i[:, 1], color='tab:grey', alpha=0.2, label='Measurements')
            plt.scatter(outliers[:, 0], outliers[:, 1], color='tab:red', alpha=0.5, label='Outliers')
            plt.scatter(calibrated_data[:, 0], calibrated_data[:, 1], color='tab:green', alpha=0.5, label='Calibrated data')
            plt.scatter(i[0], i[1], marker='2', s=500, color=colors[idx % len(colors)])
        else:
            plt.plot(circle_x, circle_y, linestyle='--', color=colors[idx%len(colors)])
            plt.plot(filtered_data[:,0], filtered_data[:,1], color=colors[idx%len(colors)])
            plt.scatter(data_i[:,0], data_i[:,1], color='tab:grey', alpha=0.2)
            plt.scatter(outliers[:,0], outliers[:,1], color='tab:red', alpha=0.5)
            plt.scatter(calibrated_data[:,0], calibrated_data[:,1], color='tab:green', alpha=0.5)
            plt.scatter(i[0], i[1], marker='2', s=500, color=colors[idx%len(colors)])
        plt.xlabel('X (cm)')
        plt.ylabel('Y (cm)')

    plt.grid()
    plt.scatter([0, 194, 100, 50], [0, 0, 194, 100], marker='*', s=200, color='black', label='Anchors')
    plt.legend(loc='lower center')
    plt.tight_layout()
    plt.savefig(f'cal_pos.png')
    plt.show()


def plot_combined_errors(data, cal):
    coords = []
    errors_norm = []
    raw_errors_norm = []
    errors_ratio = []
    cal_error = []
    raw_error = []

    filtered_data_all, outliers_all, bound_all = filter(data, WINDOW_SIZE)

    for i in GT:
        data_i = np.array(data[i])
        mean_meas = np.mean(data_i, axis=0)

        filtered_data = filtered_data_all[i]
        calibrated_data = cal[i]

        err_norm = np.linalg.norm(np.mean(calibrated_data, axis=0) - i)
        err_filt = np.linalg.norm(np.mean(filtered_data, axis=0) - i)
        err_ratio = (err_norm * 100) / err_filt if err_filt != 0 else 0

        cal_error.append(np.mean(calibrated_data, axis=0) - i)
        raw_error.append(np.mean(filtered_data, axis=0) - i)

        coords.append(i[:2])
        errors_norm.append(err_norm)
        raw_errors_norm.append(err_filt)
        errors_ratio.append(err_ratio)

    coords = np.array(coords)
    errors_norm = np.array(errors_norm)
    raw_errors_norm = np.array(raw_errors_norm)
    errors_ratio = np.array(errors_ratio)
    raw_error = np.array(raw_error)
    cal_error = np.array(cal_error)

    # Interpolation grid
    grid_x, grid_y = np.mgrid[
        coords[:, 0].min():coords[:, 0].max():100j,
        coords[:, 1].min():coords[:, 1].max():100j
    ]

    grid_norm = griddata(coords, errors_norm, (grid_x, grid_y), method='linear')
    grid_ratio = griddata(coords, errors_ratio, (grid_x, grid_y), method='linear')

    colors = [(0, 0.3, 1), (1, 1, 1), (1, 0.2, 0.2)]
    cmap = LinearSegmentedColormap.from_list('custom_heatmap', colors, N=256)

    fig, axs = plt.subplots(1, 2, figsize=(18, 7))

    # Plot error norm
    im0 = axs[0].imshow(grid_norm.T, extent=(
        coords[:, 0].min(), coords[:, 0].max(),
        coords[:, 1].min(), coords[:, 1].max()
    ), origin='lower', cmap=cmap, aspect='auto')
    axs[0].scatter([0, 194, 100, 50], [0, 0, 194, 100], marker='*', s=200, color='black', label='Anchors')
    axs[0].set_xlabel('X (cm)')
    axs[0].set_ylabel('Y (cm)')
    axs[0].set_xlim(-6, 200)
    axs[0].set_ylim(-6, 200)
    axs[0].grid(True)
    fig.colorbar(im0, ax=axs[0], label=r'Calibrated error: $e_{e,cal}$ (cm)')

    # Plot error ratio
    im1 = axs[1].imshow(grid_ratio.T, extent=(
        coords[:, 0].min(), coords[:, 0].max(),
        coords[:, 1].min(), coords[:, 1].max()
    ), origin='lower', cmap=cmap, aspect='auto')
    axs[1].scatter([0, 194, 100, 50], [0, 0, 194, 100], marker='*', s=200, color='black', label='Anchors')
    axs[1].set_xlabel('X (cm)')
    axs[1].set_ylabel('Y (cm)')
    axs[1].set_xlim(-6, 200)
    axs[1].set_ylim(-6, 200)
    axs[1].grid(True)
    fig.colorbar(im1, ax=axs[1], label=r'Error gain: $\frac{e_{e,cal}}{e_{e,raw}}$ (%)')

    plt.tight_layout()
    plt.savefig(f'err_pos.png')
    plt.show()


    print("------- Statistics -------")
    print()
    print(raw_errors_norm)
    print(errors_norm)
    print(f"Mean error before calibration (cm): {np.mean(raw_error)}")
    print(f"RMS error before calibration (cm): {np.sqrt(np.mean(raw_error ** 2))}")
    print(f"Mean error after calibration(cm): {np.mean(cal_error)}")
    print(f"RMS error after calibration (cm): {np.sqrt(np.mean(cal_error ** 2))} (cm)")


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
      (100, 150), (150, 150), (150, 50), (100, 50),
      (0, 175), (175, 175), (175, 25), (0, 25)
      ]
data = read_data(GT, "Final/full.csv")

del data[GT[6]]
del data[GT[7]]
del GT[6]
del GT[6]

print(data)
print(GT)

d = (125,100)
#histogram(d, data)
filtered_data = filter(data, WINDOW_SIZE)[0]

A, b, y_pred = compute_model(filtered_data)
#a, b = 0.95, -5
#y_pred = set_model(filtered_data, a, b)

calibrated_data = calibrate(filtered_data, A, b)
show(data, calibrated_data)
#cal_error(calibrated_data)
plot_combined_errors(data, calibrated_data)

plt.figure(figsize=(10, 6))
cumulative_error(data, "Without processing", 'tab:blue')
cumulative_error(calibrated_data, "With processing", 'tab:orange')
plt.grid()
plt.legend()
plt.savefig("cumul_pos.png")
plt.show()
