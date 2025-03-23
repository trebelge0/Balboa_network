import threading
import time
import os
import sys
from synchro import Synchro
from consensus import Consensus

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from balboa import Balboa
from bluetooth import Bluetooth


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


def blink(phase):
    """
    Blink at specified frequency with a specified dephasage in order to align each rocky's phase.

    Note that the other instructions need to be fast enough for the frequency to be realist as it is sleep.
    Sleep is better than non-blocking instruction in our case because it let time to other threads to work faster.
    """
    print(consensus.state)
    rocky.leds(1, 1, 1)
    time.sleep(max(0.05, 1 / consensus.state / 2 - phase))
    rocky.leds(0, 0, 0)
    time.sleep(max(0.05, 1 / consensus.state / 2 - phase))


# ------- Global variables --------

# Bluetooth
RPIS_MACS = ["DC:A6:32:D3:E3:D9", "B8:27:EB:E6:94:A2", "E4:5F:01:28:EE:23"]
ADJACENCY = [[1, 1, 0],
             [1, 1, 1],
             [0, 1, 1]]

ID, f = check_args()

bluetooth = Bluetooth(ID, RPIS_MACS, matrix=ADJACENCY, verbose=False, processes=2)
rocky = Balboa()

synchro = Synchro(bluetooth, blink, process_id=0)
consensus = Consensus(bluetooth, f, process_id=1)


if __name__ == "__main__":

    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    rocky.leds(0, 0, 0)

    # Run
    consensus_thread = threading.Thread(target=consensus.run, daemon=True)
    consensus_thread.start()
    consensus_thread = threading.Thread(target=synchro.run, daemon=True)
    consensus_thread.start()

    while True:
        time.sleep(10)

