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
import oled


# ------- Global variables --------

# Data saving and interrupt handling
file_path = ['/home/trebelge/Documents/Balboa_Network/data/unicast.csv']  # Remote
signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, [unicast.data], file_path))

ID = int(check_args(1)[0])
bluetooth = Bluetooth(ID, RPIS_MACS, ADJACENCY, verbose=True)
rocky = Balboa()
unicast = Unicast(bluetooth, rocky, delay=0)


if __name__ == "__main__":

    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    rocky.leds(0, 0, 0)

    unicast.listen()  # Launch a thread listening incoming messages of current process

    ready_start_time = None  # Time since the agent has received its last message
    last_seen_message = None  # Last message from the previous iteration

    msg = f"{ID}"

    while True:
        btn1, btn2, btn3 = rocky.read_buttons()

        # Send a message corresponding to the button pressed to a different agent for each button
        if unicast.ready:
            dest_id = None
            if btn1:
                dest_id = (ID + 1) % len(ADJACENCY)
            elif btn2:
                dest_id = (ID + 2) % len(ADJACENCY)
            elif btn3:
                dest_id = (ID + 3) % len(ADJACENCY)

            if dest_id is not None:
                unicast.send(msg, dest_id)
                ready_start_time = time.time()  # Reset LED timer on send

        # If current message is different than the one from previous iteration
        if unicast.last_message != last_seen_message:
            last_seen_message = unicast.last_message
            oled.write(last_seen_message.data.decode('utf-8'))
            ready_start_time = time.time()  # Reset LED timer on reception

        # If the elapsed time since last message is higher than 3 seconds, we shut down all leds
        if ready_start_time is not None:
            if time.time() - ready_start_time >= 3:
                rocky.leds(0, 0, 0)

        time.sleep(0.1)



