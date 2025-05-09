"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


import time, os, sys, struct, signal

# For being able to import files from ./../src/ and run it from anywhere in the system of the RPi (useful for run.sh)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from utils import RPIS_MACS, ADJACENCY, check_args, signal_handler
from bluetooth import Bluetooth
from balboa import Balboa


# Data saving and interrupt handling
latency = []
file_path = ['/home/trebelge/Documents/Balboa_Network/data/latency.csv']  # Remote
signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, [latency], file_path))

ID = int(check_args(1)[0])  # Read program args
rocky = Balboa()
bluetooth = Bluetooth(ID, RPIS_MACS, ADJACENCY, verbose=True)


if __name__ == "__main__":

    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    rocky.leds(0, 0, 0)

    size = 500
    packets = size*[0]

    if ID == 0:
        while True:
            t = time.time()
            bluetooth.send_message(f'<Bd{size}B', 0, t, *packets)
            packed = bluetooth.buffer[0][1]

            while packed == -1:
                packed = bluetooth.buffer[0][1]

            rt = struct.unpack('d', packed[:8])[0]
            while rt != t:
                packed = bluetooth.buffer[0][1]
                rt = struct.unpack('d', packed[:8])[0]
            latency.append([time.time() - t])
            time.sleep(3)

    if ID == 1:
        packed = bluetooth.buffer[0][0]
        while True:
            if packed != bluetooth.buffer[0][0]:
                packed = bluetooth.buffer[0][0]
                rt = struct.unpack('d', packed[:8])[0]
                bluetooth.send_message(f'<Bd{size}B', 0, rt, *packets)
