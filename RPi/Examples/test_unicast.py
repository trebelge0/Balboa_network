"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


import os, sys, signal, time

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from utils import RPIS_MACS, ADJACENCY, check_args, signal_handler
from bluetooth import Bluetooth
from unicast import Unicast
from balboa import Balboa


# ------- Global variables --------

# Data saving and interrupt handling
file_path = ['/home/trebelge/Documents/Balboa_Network/data/unicast.csv']  # Remote
signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, [unicast.data], file_path))

ID = int(check_args(1)[0])
bluetooth = Bluetooth(ID, RPIS_MACS, ADJACENCY, verbose=True)
rocky = Balboa()
unicast = Unicast(bluetooth, rocky, delay=1)


if __name__ == "__main__":

    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    rocky.leds(0, 0, 0)

    unicast.listen()

    while True:
        if rocky.read_buttons() != (False, False, False) and unicast.ready:
            unicast.send(f"Hello from agent {ID}", 2)
        time.sleep(0.2)