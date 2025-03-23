import time
import os
import sys
import csv
import signal
from synchro import Synchro

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from balboa import Balboa
from bluetooth import Bluetooth


def save_data():
    print(synchro.data)
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for value in synchro.data:
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
    #rocky.leds(1, 1, 1)
    time.sleep(max(0.05, 1 / (frequency * 2) - phase))
    #rocky.leds(0, 0, 0)
    time.sleep(max(0.05, 1 / (frequency * 2) - phase))


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

#rocky = Balboa()
synchro = Synchro(bluetooth, blink)

file_path = '/home/trebelge/Documents/Balboa_Network/data/consensus.csv'
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":

    #rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    #rocky.leds(0, 0, 0)

    # Run
    synchro.run()