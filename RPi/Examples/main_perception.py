import threading
import time
import os
import sys
import csv
import signal
from perception import Perception

# For being able to import files from ./../src/ and run it from anywhere in the system of the RPi (useful for the run.sh)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from balboa import Balboa
from bluetooth import Bluetooth


# ------- Functions --------


def save_data():
    print(perception.data)
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for value in perception.data:
            writer.writerow(value)
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
        print("Usage: python script.py <ID> <init_state> <i2c>")
        sys.exit(1)

    try:
        id = int(sys.argv[1])
        init = float(sys.argv[2])
        i2c = bool(int(sys.argv[3]))
    except ValueError:
        print("Error: <ID> must be int")
        sys.exit(1)

    # Check if ID is valid
    if not (0 <= id < len(RPIS_MACS)):
        print(f"Error: ID must be between 0 and {len(RPIS_MACS) - 1}.")
        sys.exit(1)

    return id, init, i2c


# ------- Global variables --------

# Bluetooth
# 4 - 4L - Z1 - Z2 - Z3 - Z4
"""RPIS_MACS = ["DC:A6:32:D3:E3:D9",
             "E4:5F:01:28:EE:23",
             "2C:CF:67:85:E8:89",
             "2C:CF:67:85:B3:D2",
             "2C:CF:67:85:B4:E0",
             "2C:CF:67:AE:4B:DE"]

ADJACENCY = [[1, 1, 0, 0, 0, 0],
             [1, 1, 1, 0, 0, 0],
             [0, 1, 1, 1, 0, 0],
             [0, 0, 1, 1, 1, 0],
             [0, 0, 0, 1, 1, 1],
             [0, 0, 0, 0, 1, 1]]"""

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

ID, init_state, i2c = check_args()
bluetooth = Bluetooth(ID, RPIS_MACS, matrix=ADJACENCY, verbose=False)

# Perception
perception  = Perception(bluetooth)

rocky = Balboa()

# data export
file_path = '/home/trebelge/Documents/Balboa_Network/data/perception.csv'
signal.signal(signal.SIGINT, signal_handler)


# ------- Main --------

if __name__ == "__main__":

    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    rocky.leds(0, 0, 0)

    # Run consensus with a separate thread
    consensus_thread = threading.Thread(target=perception.run, daemon=True)
    consensus_thread.start()

    while True:
        time.sleep(5)
