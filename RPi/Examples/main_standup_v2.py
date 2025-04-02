import sys
import os
import signal

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from balance import Balancer
from bluetooth import Bluetooth
from asynchronous import Async
from utils import RPIS_MACS, ADJACENCY, check_args, save_data, signal_handler


# ------- Functions --------

def standup(buffer):

    # Send stand up command to rocky if one neighbor is up
    if not balancer.balancing and buffer != [False] * len(buffer):
        balancer.stand_up()
    return [balancer.balancing]

# ---- Global variables ----

# For data saving and interrupt handling
file_path = '/home/trebelge/Documents/Balboa_Network/data/standup.csv'
signal.signal(signal.SIGINT, signal_handler)

ID = check_args(1)

bluetooth = Bluetooth(ID, RPIS_MACS, matrix=ADJACENCY, verbose=False)

# Balancer
balancer = Balancer()

# Stand-up
standup = Async(bluetooth, [balancer.balancing], standup, '?')


if __name__ == "__main__":

    balancer.rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    balancer.rocky.leds(0, 0, 0)

    standup.run()  # Blocking instruction
