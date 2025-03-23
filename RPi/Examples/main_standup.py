import sys
from standup import StandUp
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)

from balance import Balancer
from bluetooth import Bluetooth


# ------- Functions --------

def check_arg():
    """
    Manage user's args

    Usage: python main_standup.py <ID>
    """

    # Check if argument is provided by user
    if len(sys.argv) != 2:
        print("Usage: python main_standup.py <ID>")
        sys.exit(1)

    try:
        id = int(sys.argv[1])
    except ValueError:
        print("Error: ID must be an integer.")
        sys.exit(1)

    # Check if ID is valid
    if not (0 <= id < len(RPIS_MACS)):
        print(f"Error: ID must be between 0 and {len(RPIS_MACS) - 1}.")
        sys.exit(1)

    return id


# ------- Global variables --------

# Bluetooth
RPIS_MACS = ["DC:A6:32:D3:E3:D9", "B8:27:EB:E6:94:A2", "E4:5F:01:28:EE:23"]
ID = check_arg()
m = [[1, 1, 0],
     [1, 1, 1],
     [0, 1, 1]]
bluetooth = Bluetooth(ID, RPIS_MACS, matrix=m, verbose=False)

# Balancer
balancer = Balancer()

# Stand-up
standup = StandUp(bluetooth, balancer)


if __name__ == "__main__":

    balancer.rocky.leds(1, 0, 0)
    bluetooth.start_network()  # Wait for each neighbor to be connected
    balancer.rocky.leds(0, 0, 0)

    standup.run()  # Blocking instruction
