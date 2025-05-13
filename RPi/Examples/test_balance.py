"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""

import sys
import os
import signal
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from balance import Balancer
from utils import RPIS_MACS, ADJACENCY, check_args, signal_handler


# ---- Global variables ----

# For data saving and interrupt handling
file_path = ['/home/trebelge/Documents/Balboa_Network/data/standup.csv']
signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, [], file_path))

ID = int(check_args(1)[0])

# Balancer
balancer = Balancer()


if __name__ == "__main__":

    balancer.rocky.leds(1, 0, 0)
    balancer.setup()
    balancer.start()  # Run balancer thread
    balancer.rocky.leds(0, 0, 0)

    while True:
        time.sleep(1)
        print(balancer.angle)
