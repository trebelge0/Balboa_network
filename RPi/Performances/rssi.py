"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


import os, sys, subprocess, signal, time

# For being able to import files from ./../src/ and run it from anywhere in the system of the RPi (useful for run.sh)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from utils import RPIS_MACS, ADJACENCY, check_args, signal_handler
from bluetooth import Bluetooth
from balboa import Balboa


rssi = []
distance_m = 1.5
file_path = [f'/home/trebelge/Documents/Balboa_Network/data/rssi_{distance_m:.2f}m.csv']  # Remote
signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, rssi, file_path))

ID = int(check_args(1)[0])  # Read program args

mac_address = RPIS_MACS[int(ID==0)]

rocky = Balboa()
bluetooth = Bluetooth(ID, RPIS_MACS, ADJACENCY, verbose=True)

if __name__ == "__main__":

    rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    rocky.leds(0, 0, 0)

    print(f"Measuring RSSI at distance {distance_m} m...")

    while True:
        result = subprocess.run(
            ["hcitool", "rssi", mac_address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if "RSSI return value" in result.stdout:
            rssi_value = int(result.stdout.strip().split()[-1])
            rssi.append([distance_m, rssi_value])
            print(f"Distance: {distance_m} m, RSSI: {rssi_value} dBm")
        else:
            print("No RSSI available (target may be disconnected)")

        time.sleep(1)
