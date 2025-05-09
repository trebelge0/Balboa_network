"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


import time
import os
import sys
import signal
import threading
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

import oled
from balboa import Balboa
from bluetooth import Bluetooth
from synchronous import Sync
from utils import RPIS_MACS, ADJACENCY, check_args, signal_handler


def blink(phase_consensus, freq_consensus):
    """
    Blink at specified frequency with a specified dephasage in order to align each rocky's phase.

    Note that the other instructions need to be fast enough for the frequency to be realist as it is sleep.
    Sleep is better than non-blocking instruction in our case because it let time to other threads to work faster.
    """

    while True:

        tol = 1 / (32 * freq_consensus.state[0])

        if phase_consensus.state[0]-tol < time.time() % (1/freq_consensus.state[0]) < phase_consensus.state[0]+tol:

            phase_consensus.state[0] = time.time() % (1 / freq_consensus.state[0])

            rocky.leds(0, 0, 0)
            time.sleep(1 / ( 2 * freq_consensus.state[0]))
            rocky.leds(1, 1, 1)
            time.sleep(1 / (4 * freq_consensus.state[0]))

        time.sleep(tol)


# ------- Global variables --------

signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, [phase_consensus.data, freq_consensus.data], file_path))
file_path = ['/home/trebelge/Documents/Balboa_Network/data/synchro_phase.csv', '/home/trebelge/Documents/Balboa_Network/data/synchro_freq.csv']

ID, init_freq = check_args(2)
ID = int(ID)
phase = time.time() % (1 / init_freq)

# Communication
rocky = Balboa()
bluetooth = Bluetooth(ID, RPIS_MACS, ADJACENCY, verbose=False, processes=2)

# Iterative function: next state is the average with its neighbors state
compute_average = lambda buf: [np.mean([buf[n][1] for n in bluetooth.neighbors_index + [bluetooth.ID]])]

# Synchronized communication instances for each process
phase_consensus = Sync(bluetooth, [phase], compute_average, 'f', process_id=0, delay=5e-1)
freq_consensus  = Sync(bluetooth, [init_freq], compute_average, 'f', process_id=1, delay=5e-1)


if __name__ == "__main__":

    # When red led shutdown, RPi connected with its neighbors
    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    rocky.leds(0, 0, 0)

    # Run the synchronized communication using the iterative problem: compute_average for both frequency and average
    consensus_thread = threading.Thread(target=phase_consensus.run, daemon=True)
    consensus_thread.start()
    synchro_thread = threading.Thread(target=freq_consensus.run, daemon=True)
    synchro_thread.start()
    blink_thread = threading.Thread(target=blink, args=(phase_consensus, freq_consensus), daemon=True)
    blink_thread.start()

    while True:
        oled.write(f"f: {round(freq_consensus.state, 4)}, ph: {round(phase_consensus.state, 4)}")
        time.sleep(0.1)
