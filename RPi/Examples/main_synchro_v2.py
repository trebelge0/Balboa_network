import time
import os
import sys
import csv
import signal
import threading
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from balboa import Balboa
from bluetooth import Bluetooth
from synchronous import Sync


def save_data(consensus, file_path):
    print(consensus.data)
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for value in consensus.data:
            writer.writerow(value)
    print(f"Data saved in {file_path}")


def signal_handler(sig, frame):
    print("Interruption detected, data saving...")
    save_data(phase_consensus, file_path+"phase.csv")
    save_data(freq_consensus, file_path+"freq.csv")
    sys.exit(0)


def check_args():
    """
    Manage user's args

    Usage: python script.py <ID> <init_state>
    """

    # Check if argument is provided by user
    if len(sys.argv) != 3:
        print("Usage: python script.py <ID> <init_state>")
        sys.exit(1)

    try:
        id = int(sys.argv[1])
        init = float(sys.argv[2])
    except ValueError:
        print("Error: <ID> must be int, <init_state> must be float.")
        sys.exit(1)

    # Check if ID is valid
    if not (0 <= id < len(RPIS_MACS)):
        print(f"Error: ID must be between 0 and {len(RPIS_MACS) - 1}.")
        sys.exit(1)

    return id, init


def blink():
    """
    Blink at specified frequency with a specified dephasage in order to align each rocky's phase.

    Note that the other instructions need to be fast enough for the frequency to be realist as it is sleep.
    Sleep is better than non-blocking instruction in our case because it let time to other threads to work faster.
    """

    while True:

        tol = 1 / (64 * freq_consensus.state)

        if phase_consensus.state-tol < time.time() % (1/freq_consensus.state) < phase_consensus.state+tol:

            phase = time.time() % (1 / freq_consensus.state)
            phase_consensus.state = phase

            rocky.leds(0, 0, 0)
            time.sleep(1 / ( 2 * freq_consensus.state))
            rocky.leds(1, 1, 1)
            time.sleep(1 / (4 * freq_consensus.state))

        time.sleep(tol)


# ------- Global variables --------

signal.signal(signal.SIGINT, signal_handler)
file_path = '/home/trebelge/Documents/Balboa_Network/data/'

# Bluetooth
RPIS_MACS = ["DC:A6:32:D3:E3:D9",
             "2C:CF:67:85:B3:D2",
             "E4:5F:01:28:EE:23"]

ADJACENCY = [[1, 1, 0],
             [1, 1, 1],
             [0, 1, 1]]

ID, init_freq = check_args()
phase = time.time() % (1 / init_freq)

# Communication
rocky = Balboa()
bluetooth = Bluetooth(ID, RPIS_MACS, matrix=ADJACENCY, verbose=False, processes=2)

# Iterative function: next state is the average with its neighbors state
compute_average = lambda buf, state: [np.mean([buf[n][1] for n in bluetooth.neighbors_index] + [state])]

# Synchronized communication instances for each process
phase_consensus = Sync(bluetooth, [phase], compute_average, process_id=0)
freq_consensus  = Sync(bluetooth, [init_freq], compute_average, process_id=1)


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

    blink()
