"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""

import threading
import serial
import time
import os
import sys
import signal
import numpy as np

# For being able to import files from ./../src/ and run it from anywhere in the system of the RPi (useful for the run.sh)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

import oled
from balboa import Balboa
from bluetooth import Bluetooth
from synchronous import Sync
from balance import Balancer
from dwm1001 import DWM
from utils import RPIS_MACS, ADJACENCY, check_args, signal_handler


# ------- Functions --------

def gradient_descent(buffer):

    state = buffer[bluetooth.ID][1:-1]

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

    gi_t = np.array(state[4:6])

    state[0:2] = wijxj - zi_t - GAMMA * gi_t  # xi_{t+1}
    state[2:4] = wijzj - GAMMA * gi_t + GAMMA * wijgj  # zi_{t+1}
    xi_t1 = np.array(state[0:2])
    state[4:6] = 4 * (dwm.distance ** 2 - np.linalg.norm(xi_t1 - dwm.position) ** 2) * (dwm.position - xi_t1)  # gi_{t+1}

    f = (dwm.distance ** 2 - np.linalg.norm(xi_t1 - dwm.position) ** 2) ** 2
    localize.more_data = [f, dwm.distance, *dwm.position]

    return state


# ------- Global variables --------

# For data saving and interrupt handling
file_path = ['/home/trebelge/Documents/Balboa_Network/data/localize.csv']
signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, [localize.data], file_path))

# From user args
ID = int(check_args(1)[0])

# Communication
bluetooth = Bluetooth(ID, RPIS_MACS, ADJACENCY, verbose=False)
rocky = Balboa()

balancer = Balancer()

# Localization sensor
GAMMA = 5e-7  # step size for gradient descent
dwm = DWM(rocky, verbose=False, window_size=100)


# ------- Main --------

if __name__ == "__main__":

    # When red led shutdown, RPi connected with its neighbors
    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    balancer.setup()
    balancer.start()  # Run balancer thread
    rocky.leds(0, 0, 0)

    # Localization
    localize = Sync(bluetooth, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], gradient_descent, 'ffffff', delay=0.5)

    #sp = serial.Serial("/dev/serial0", 115200, timeout=1)

    # Initialize position and distance
    #dwm.dwm_loc_get(sp)
    dwm.read()
    dwm.postprocess()

    while not balancer.balancing:
        continue

    # Run synchronized communication over localization
    #localize_thread = threading.Thread(target=localize.run, daemon=True)
    #localize_thread.start()

    while True:

        # Read localization information
        #dwm.dwm_loc_get(sp)
        dwm.read()
        dwm.postprocess()

        print()
        print("Distances: ", dwm.distances)
        print("Positions: ", dwm.positions)

        print("Distance: ", dwm.distance)
        print("Position: ", dwm.position)
        print()

        oled.write(f"x: {round(localize.state[0], 2)}, y: {round(localize.state[1], 2)}")

        time.sleep(1)
