import threading
import time
import os
import sys
import csv
import signal
from localize import Localize

# For being able to import files from ./../src/ and run it from anywhere in the system of the RPi (useful for the run.sh)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from balboa import Balboa
from bluetooth import Bluetooth


# ------- Functions --------


def save_data():
    print(localize.data)
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for value in localize.data:
            writer.writerow(value)
    print(f"Data saved in {file_path}")


def signal_handler(sig, frame):
    print("Interruption detected, data saving...")
    save_data()
    sys.exit(0)


def check_args():
    """
    Manage user's args

    Usage: python script.py <ID> <x><y><d>
    """

    # Check if argument is provided by user
    if len(sys.argv) != 5:
        print("Usage: python script.py <ID> <x><y><d>")
        sys.exit(1)

    try:
        id = int(sys.argv[1])
        x = float(sys.argv[2])
        y = float(sys.argv[3])
        d = float(sys.argv[4])
    except ValueError:
        print("Error: <ID> must be int, <x><y><d> must be float")
        sys.exit(1)

    # Check if ID is valid
    if not (0 <= id < len(RPIS_MACS)):
        print(f"Error: ID must be between 0 and {len(RPIS_MACS) - 1}.")
        sys.exit(1)

    return id, x, y, d


# ------- Global variables --------

# Bluetooth
# Z1 - Z2 - Z3 - Z4 - 4 - 41 - 42 - 4L
RPIS_MACS = ["2C:CF:67:85:E8:89",
             "2C:CF:67:85:B3:D2",
             "2C:CF:67:85:B4:E0",
             "2C:CF:67:AE:4B:DE",
             "DC:A6:32:D3:E3:D9",
             "2C:CF:67:AE:E0:E4",
             "2C:CF:67:AE:E3:3B",
             "E4:5F:01:28:EE:23"]

ADJACENCY = [[1, 1, 0, 0, 0, 0, 0, 0],
             [1, 1, 1, 0, 0, 0, 0, 0],
             [0, 1, 1, 1, 0, 0, 0, 0],
             [0, 0, 1, 1, 1, 0, 0, 0],
             [0, 0, 0, 1, 1, 1, 0, 0],
             [0, 0, 0, 0, 1, 1, 1 ,0],
             [0, 0, 0, 0, 0, 1, 1 ,1],
             [0, 0, 0, 0, 0, 0, 1 ,1]]

# Z1 - 41 - Z3 - 42 - Z3
RPIS_MACS = ["2C:CF:67:85:E8:89",
             "2C:CF:67:AE:E0:E4",
             "2C:CF:67:85:B4:E0",
             "2C:CF:67:AE:E3:3B",
             "2C:CF:67:AE:4B:DE"]

ADJACENCY = [[1, 1, 0, 0, 1],
             [1, 1, 1, 0, 0],
             [0, 1, 1, 1, 0],
             [0, 0, 1, 1, 1],
             [1, 0, 0, 1, 1]]


ID, x, y, d = check_args()
bluetooth = Bluetooth(ID, RPIS_MACS, matrix=ADJACENCY, verbose=False)
rocky = Balboa()

# data export
file_path = '/home/trebelge/Documents/Balboa_Network/data/localize.csv'
signal.signal(signal.SIGINT, signal_handler)


# ------- Main --------

if __name__ == "__main__":

    bluetooth.start_network()  # Wait for each neighbor to be connected

    d, x, y, z = rocky.read_uwb()

    # Localization
    localize = Localize(bluetooth, [x, y, d], delay=1e-1, gamma=8e-3)

    # Run localization with a separate thread
    localize_thread = threading.Thread(target=localize.run, daemon=True)
    localize_thread.start()

    while True:
        time.sleep(10)
