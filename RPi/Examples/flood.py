"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


import os, sys, signal
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from utils import RPIS_MACS, ADJACENCY, check_args, signal_handler
from bluetooth import Bluetooth
from flooding import Flooding
from balboa import Balboa


# ------- Global variables --------

# Data saving and interrupt handling
file_path = ['/home/trebelge/Documents/Balboa_Network/data/flooding.csv']  # Remote
signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, [flooding.data], file_path))

ID = int(check_args(1)[0])
bluetooth = Bluetooth(ID, RPIS_MACS, ADJACENCY, verbose=True)
rocky = Balboa()
flooding = Flooding(bluetooth, rocky)


if __name__ == "__main__":

    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    rocky.leds(0, 0, 0)

    flooding.listen()

    while True:
        if rocky.read_buttons() != (False, False, False) and flooding.ready:
            flooding.broadcast(f"Hello from agent {ID}")
        time.sleep(0.2)