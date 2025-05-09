"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


import os, sys, signal
import time

# For being able to import files from ./../src/ and run it from anywhere in the system of the RPi (useful for run.sh)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from utils import RPIS_MACS, ADJACENCY, check_args, signal_handler
from bluetooth import Bluetooth
from flooding import Flooding
from balboa import Balboa
import oled


# ------- Global variables --------

# Data saving and interrupt handling
file_path = ['/home/trebelge/Documents/Balboa_Network/data/flooding.csv']  # Remote
signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, [flooding.data], file_path))

ID = int(check_args(1)[0])  # Read program args

# Initialize classes
bluetooth = Bluetooth(ID, RPIS_MACS, ADJACENCY, verbose=True)
rocky = Balboa()
flooding = Flooding(bluetooth, rocky)


if __name__ == "__main__":

    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    rocky.leds(0, 0, 0)

    flooding.listen()  # Launch a thread listening incoming messages of current process

    ready_start_time = None  # Time since the agent has received its last message
    last_seen_message = None  # Last message from the previous iteration

    while True:
        btn1, btn2, btn3 = rocky.read_buttons()

        # Broadcast a message corresponding to the button pressed
        if flooding.ready:
            msg = None
            if btn1 or btn2 or btn3:
                msg = f"{ID}"

            if msg is not None:
                flooding.broadcast(msg)
                ready_start_time = time.time()  # Reset LED timer on send

        # If current message is different than the one from previous iteration
        if flooding.last_message != last_seen_message:
            last_seen_message = flooding.last_message
            oled.write("ACK:"*(len(last_seen_message.viewers)==len(ADJACENCY)) + last_seen_message.data.decode('utf-8'))
            ready_start_time = time.time()  # Reset LED timer on reception

        # If the elapsed time since last message is higher than 3 seconds, we shut down all leds
        if ready_start_time is not None:
            if time.time() - ready_start_time >= 3:
                rocky.leds(0, 0, 0)

        time.sleep(0.1)  # To avoid sending the same message several times