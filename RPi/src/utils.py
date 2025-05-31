"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""



import csv
import sys


# ---------- Configuration variables -----------

# Z1 - Z2 - Z3 - Z4 - 4 - 41 - 42 - 4L
RPIS_MACS = ["2C:CF:67:85:E8:89",
             "2C:CF:67:85:B3:D2",
             "2C:CF:67:85:B4:E0",
             "2C:CF:67:AE:4B:DE",
             "DC:A6:32:D3:E3:D9",
             "2C:CF:67:AE:E0:E4",
             "2C:CF:67:AE:E3:3B",
             "E4:5F:01:28:EE:23"]

ADJACENCY = [[1, 1, 0, 0, 0, 0, 0, 1],
             [1, 1, 1, 0, 0, 0, 0, 0],
             [0, 1, 1, 1, 0, 0, 0, 0],
             [0, 0, 1, 1, 1, 0, 0, 0],
             [0, 0, 0, 1, 1, 1, 0, 0],
             [0, 0, 0, 0, 1, 1, 1 ,0],
             [0, 0, 0, 0, 0, 1, 1 ,1],
             [1, 0, 0, 0, 0, 0, 1 ,1]]


RPIS_MACS = ["2C:CF:67:85:E8:89",
             "2C:CF:67:85:B3:D2",
             "2C:CF:67:85:B4:E0",
             "2C:CF:67:AE:4B:DE",
             "DC:A6:32:D3:E3:D9"]

ADJACENCY = [[1, 1, 0, 0, 1],
             [1, 1, 1, 0, 0],
             [0, 1, 1, 1, 0],
             [0, 0, 1, 1, 1],
             [1, 0, 0, 1, 1]]


def save_data(data, file_path):
    """
    Save data into file_path on the RPi
    """
    if len(data) != len(file_path):
        print("file_path must have the same length as data")
        return

    for i in range(len(data)):
        with open(file_path[i], mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for value in data[i]:
                writer.writerow(value)
        print(f"Data saved in {file_path[i]}")


def signal_handler(signum, frame, data, file_path):

    print("Interruption detected, data saving...")
    save_data(data, file_path)
    sys.exit(0)


def check_args(n):
    """
    Manage user's args

    Usage: python script.py <ID> <args[1]>...<args[n]>
    """

    # Check if argument is provided by user
    if len(sys.argv) != n+1:
        print(f"Please provide {n} arguments")
        sys.exit(1)

    args = []

    try:
        for i in range(1, n+1):
            args.append(float(sys.argv[i]))
    except ValueError:
        print("Error: args must be numeric")
        sys.exit(1)

    # Check if ID is valid
    if not (0 <= args[0] < len(RPIS_MACS)):
        print(f"Error: ID must be between 0 and {len(RPIS_MACS) - 1}.")
        sys.exit(1)

    return args


def hex_str(data):
    return " ".join(f"{b:02X}" for b in data)
