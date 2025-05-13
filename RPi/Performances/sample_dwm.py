"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""

import time
import os
import sys
import signal

# For being able to import files from ./../src/ and run it from anywhere in the system of the RPi (useful for the run.sh)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

import oled
from balboa import Balboa
from dwm1001 import DWM
from utils import RPIS_MACS, ADJACENCY, check_args, signal_handler


# ------- Global variables --------

# For data saving and interrupt handling
file_path = ['/home/trebelge/Documents/Balboa_Network/data/distance.csv']
signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, [distances], file_path))

# From user args
ID = int(check_args(1)[0])

# Communication
rocky = Balboa()

# Localization sensor
dwm = DWM(rocky, verbose=True)

distances = []

# ------- Main --------

if __name__ == "__main__":

    # Initialize position and distance
    read = False
    i = 0

    while True:

        btn1, btn2, btn3 = rocky.read_buttons()
        if btn1 or btn2 or btn3:

            read = not read
            if read:
                i += int(btn2)
                distances.append([i])
                print(i)
            else:
                print("stop")
            time.sleep(1)

        rocky.leds(int(read), 0, 0)

        if read:
            dwm.read()
            distances.append([dwm.distance, *dwm.position])

            time.sleep(1)
