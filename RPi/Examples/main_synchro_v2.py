import time
import os
import sys
import csv
import signal
import threading

from consensus import Consensus

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from balboa import Balboa
from bluetooth import Bluetooth


def save_data():
    print(consensus.data)
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for value in consensus.data:
            writer.writerow([value])
    print(f"Data saved in {file_path}")


def signal_handler(sig, frame):
    print("Interruption detected, data saving...")
    save_data()
    sys.exit(0)


def check_args():
    """
    Manage user's args

    Usage: python script.py <ID> <init_state>
    """

    # Check if argument is provided by user
    if len(sys.argv) != 2:
        print("Usage: python script.py <ID>")
        sys.exit(1)

    try:
        id = int(sys.argv[1])
    except ValueError:
        print("Error: <ID> must be int")
        sys.exit(1)

    # Check if ID is valid
    if not (0 <= id < len(RPIS_MACS)):
        print(f"Error: ID must be between 0 and {len(RPIS_MACS) - 1}.")
        sys.exit(1)

    return id


def blink(phase):
    """
    Blink at specified frequency with a specified dephasage in order to align each rocky's phase.

    Note that the other instructions need to be fast enough for the frequency to be realist as it is sleep.
    Sleep is better than non-blocking instruction in our case because it let time to other threads to work faster.
    """
    led = False
    tol = 1/(8*frequency)
    while consensus.state-tol < time.time() % 1/(2*frequency) < consensus.state+tol:
        phase = time.time() % (1 / frequency)
        consensus.state = phase
        rocky.leds(int(not led), int(not led), int(not led))
        time.sleep(1 / (4*frequency))


# ------- Global variables --------

# Bluetooth
RPIS_MACS = ["DC:A6:32:D3:E3:D9",
             "2C:CF:67:85:E8:89",
             "2C:CF:67:85:B3:D2",
             "2C:CF:67:85:B4:E0",
             "2C:CF:67:AE:4B:DE"]

ADJACENCY = [[1, 1, 0, 0, 0],
             [1, 1, 1, 0, 0],
             [0, 1, 1, 1, 0],
             [0, 0 ,1, 1, 1],
             [0, 0, 0, 1, 1]]

ID = check_args()
bluetooth = Bluetooth(ID, RPIS_MACS, matrix=ADJACENCY, verbose=False)

# Synchro
frequency = 0.5  # [Hz]
phase = time.time() % (1 / frequency)

rocky = Balboa()
consensus = Consensus(bluetooth, phase)

file_path = '/home/trebelge/Documents/Balboa_Network/data/consensus.csv'
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":

    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    rocky.leds(0, 0, 0)

    # Run
    blink_thread = threading.Thread(target=blink, daemon=True)
    blink_thread.start()
    consensus_thread = threading.Thread(target=consensus.run, daemon=True)
    consensus_thread.start()

    while True:
        time.sleep(10)
