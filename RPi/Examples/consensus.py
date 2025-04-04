"""
Romain Englebert - Master's Thesis
© 2025 Romain Englebert.
"""


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
from utils import RPIS_MACS, ADJACENCY, check_args, save_data, signal_handler


# ------- Functions --------


def blink():
    """
    Blink Balboa's led at frequency f
    """

    while True:
        rocky.leds(0, 0, 0)
        time.sleep(1 / f)
        rocky.leds(1, 1, 1)
        time.sleep(1 / f)


# ------- Global variables --------

# Data saving and interrupt handling
file_path = ['/home/trebelge/Documents/Balboa_Network/data/consensus.csv']  # Remote
signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, [consensus.data], file_path))

ID, init_state, i2c = check_args(3)  # From program args
ID = int(ID)
i2c = bool(i2c)
f = init_state

# Communication
bluetooth = Bluetooth(ID, RPIS_MACS, matrix=ADJACENCY, verbose=True)
if i2c:
    rocky = Balboa()

# Iterative function: next state is the average with its neighbors state
compute_average = lambda buf: [np.mean([buf[n][1] for n in bluetooth.neighbors_index + [bluetooth.ID]])]

# Synchronized communication instance
consensus = Sync(bluetooth, [init_state], compute_average, 'f', delay=5e-1)


# ------- Main --------

if __name__ == "__main__":

    # When red led shutdown, RPi connected with its neighbors
    if i2c:
        rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    if i2c:
        rocky.leds(0, 0, 0)

    # Run the synchronized communication using the iterative problem: compute_average
    consensus.run()
