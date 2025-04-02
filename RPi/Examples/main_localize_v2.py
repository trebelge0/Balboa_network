import threading
import time
import os
import sys
import signal
import numpy as np

# For being able to import files from ./../src/ and run it from anywhere in the system of the RPi (useful for the run.sh)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from balboa import Balboa
from bluetooth import Bluetooth
from synchronous import Sync
from dwm1001 import DWM
from utils import RPIS_MACS, ADJACENCY, check_args, save_data, signal_handler


# ------- Functions --------

def gradient_descent(buffer):

    state = buffer[bluetooth.ID]

    # Compute the current state
    zi_t = np.array(state[2:4])

    wijxj = np.zeros(2)
    wijzj = np.zeros(2)
    wijgj = np.zeros(2)
    for j in bluetooth.neighbors_index + [bluetooth.ID]:
        wij = np.array(
            bluetooth.ADJACENCY[bluetooth.ID][j] / sum(bluetooth.ADJACENCY[bluetooth.ID]))
        xj_t = np.array(buffer[j][1:3])
        zj_t = np.array(buffer[j][3:5])
        gj_t = np.array(buffer[j][5:7])
        wijxj += wij * xj_t
        wijzj += wij * zj_t
        wijgj += wij * gj_t
        print("wij: ", wij)
        print("xj_t: ", xj_t)
        print("zj_t: ", zj_t)
        print("gj_t: ", gj_t)

    gi_t = np.array(state[4:6])

    state[0:2] = wijxj - zi_t - GAMMA * gi_t  # xi_{t+1}
    state[2:4] = wijzj - GAMMA * gi_t + GAMMA * wijgj  # zi_{t+1}
    xi_t1 = np.array(state[0:2])
    state[4:6] = 4 * (dwm.distance ** 2 - np.linalg.norm(xi_t1 - dwm.position) ** 2) * (dwm.position - xi_t1)  # gi_{t+1}

    f = (dwm.distance ** 2 - np.linalg.norm(xi_t1 - dwm.position) ** 2) ** 2
    localize.more_data = [f]

    # Print state
    print("wijxj: ", wijxj)
    print("wijzj: ", wijzj)
    print("wijgj: ", wijgj)
    print("zi_t: ", zi_t)
    print("gi_t: ", gi_t)


# ------- Global variables --------

# For data saving and interrupt handling
file_path = '/home/trebelge/Documents/Balboa_Network/data/localize.csv'
signal.signal(signal.SIGINT, signal_handler)

# From user args
ID, x, y, d = check_args(4)

# Communication
bluetooth = Bluetooth(ID, RPIS_MACS, matrix=ADJACENCY, verbose=False)
rocky = Balboa()

# Localization sensor
GAMMA = 5e-3  # step size for gradient descent
dwm = DWM()


# ------- Main --------

if __name__ == "__main__":

    # When red led shutdown, RPi connected with its neighbors
    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    rocky.leds(0, 0, 0)

    # Localization
    localize = Sync(bluetooth, [0, 0, 0, 0, 0, 0], gradient_descent, delay=1e-1)

    # Run synchronized communication over localization
    localize_thread = threading.Thread(target=localize.run, daemon=True)
    localize_thread.start()

    while True:

        # Read localization information
        dwm.read()
        dwm.postprocess()
        time.sleep(5)
