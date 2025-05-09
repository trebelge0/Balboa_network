"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


import os, sys, signal
import time
from standup import standup

# For being able to import files from ./../src/ and run it from anywhere in the system of the RPi (useful for run.sh)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from utils import RPIS_MACS, ADJACENCY, check_args, signal_handler
from bluetooth import Bluetooth
from flooding import Flooding
from balboa import Balboa
from balancer import Balancer
from asynchronous import Async
from synchronous import Sync
import oled


# ------- Global variables --------

# Data saving and interrupt handling
file_path = ['/home/trebelge/Documents/Balboa_Network/data/mulit_flooding.csv']  # Remote
signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, [flooding.data], file_path))

ID = int(check_args(1)[0])  # Read program args

# Initialize classes
bluetooth = Bluetooth(ID, RPIS_MACS, ADJACENCY, verbose=True)
rocky = Balboa()
balancer = Balancer()
flooding = Flooding(bluetooth, rocky, process=0)
standup = Async(bluetooth, [balancer.balancing], standup, '?', delay=10, process=1)



if __name__ == "__main__":

    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    balancer.setup()
    balancer.start()  # Run balancer thread
    rocky.leds(0, 0, 0)

    flooding.listen()  # Launch a thread listening incoming messages of current process

    ready_start_time = None  # Time since the agent has received its last message
    last_seen_message = None  # Last message from the previous iteration

    actions = {"Consensus": consensus, "LEDs": synchro, "Standup": standup}

    while True:
        btn1, btn2, btn3 = rocky.read_buttons()

        # Broadcast a message corresponding to the button pressed
        if flooding.ready:
            msg = None
            if btn1:
                # Launch consensus with random initial values
                msg = f"{actions[0]} from agent {ID}"
            elif btn2:
                # Launch  LED's synchronization
                msg = f"{actions[1]} from agent {ID}"
            elif btn3:
                # Launch stand up
                msg = f"{actions[2]} from agent {ID}"

            if msg is not None:
                flooding.broadcast(msg)
                ready_start_time = time.time()  # Reset LED timer on send

        # If current message is different than the one from previous iteration
        if flooding.last_message != last_seen_message:
            last_seen_message = flooding.last_message
            oled.write("ACK:"*(len(last_seen_message.viewers)==len(ADJACENCY)) + last_seen_message.data.decode('utf-8'))
            ready_start_time = time.time()  # Reset LED timer on reception

        # If the elapsed time since last message is higher than 3 seconds, we shut down all leds and we start algorithm
        if ready_start_time is not None:
            if time.time() - ready_start_time >= 3:
                rocky.leds(0, 0, 0)

                for i in range(len(actions)):
                    if last_seen_message.data.decode('utf-8').strip().split(" ")[0] == actions[i]:
                        actions[i].run()

        time.sleep(0.1)  # To avoid sending the same message several times