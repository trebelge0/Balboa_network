"""
Romain Englebert - Master's Thesis
© 2025 Romain Englebert.
"""


import socket
import threading
import time
import struct
from utils import hex_str


class Bluetooth:
    def __init__(self, id, rpis_macs, adjacency, processes=1, verbose=False):
        """
        rpis_macs: list of MAC addresses of each RPi
        id: index of the current RPi in rpis_macs
        verbose: bool for showing each sent/received msg
        adjacency: adjacent adjacency for connections between rpis. Default: queue.

        Remark: RPi's need to be paired manually for the first time.
        """

        # Private constants
        self._PORT = 1
        self._MAC = rpis_macs[id]
        self._VERBOSE = verbose  # Show received and sent messages
        self._PROCESSES = processes

        # Public constants
        self.ADJACENCY = adjacency
        self.RPIS_MACS = rpis_macs
        self.ID = id

        # Private variables
        self._connections = {}

        # Public variables
        self.buffer = []
        for i in range(processes):
            self.buffer.append([-1]*len(rpis_macs))  # List of last messages from each RPi
        self.neighbors = []
        self.neighbors_index = []

        self.initialize_neighbors()


    def initialize_neighbors(self):
        """
        Initialize neighbors based on adjacent matrix.
        """

        # Format check
        if len(self.ADJACENCY) != len(self.RPIS_MACS):
            print("The adjacency matrix must of the same size as self.RPIS_MACS.")
            raise Exception

        if len(self.ADJACENCY) != len(self.ADJACENCY[0]):
            print("The adjacency matrix must be square.")
            raise Exception

        for i in range(len(self.ADJACENCY)):
            for j in range(len(self.ADJACENCY)):
                if self.ADJACENCY[i][j] != self.ADJACENCY[j][i]:
                    print(f"Adjacency matrix is not symmetric at ({i},{j}) and ({j},{i})")
                    raise Exception

        for i in range(len(self.ADJACENCY)):
            if not isinstance(self.ADJACENCY[self.ID][i], int):
                print("The matrix can only contain integers")
                raise Exception

            # Fill neighbors based on adjacency matrix
            if self.ADJACENCY[self.ID][i] != 0 and i != self.ID:
                self.neighbors.append(self.RPIS_MACS[i])
                self.neighbors_index.append(i)

        if len(self.neighbors) > 7:
            print("Each RPi can connect to a maximum of 7 peripherals due to Bluetooth limitations.")
            raise Exception


    def handle_client(self, conn, addr):
        """
        Receive full_low_scale for each connection, either for a server or a connector
        As soon as a connection is made, a thread run this function to manage self.buffer
        """

        print(f"Connected to {addr}")
        while True:
            try:
                data = conn.recv(1024)
                if not data:  # Client a fermé la connexion proprement
                    print(f"Client {addr} closed the connection.")
                    break

                if self._VERBOSE:
                    print(f"\nMessage from {addr}: {hex_str(data)}")

                for i in range(len(self.RPIS_MACS)):
                    if addr == self.RPIS_MACS[i]:
                        try:
                            if len(data) >= 1:  # Vérifie que la donnée contient au moins 1 octets
                                p = data[0]
                                if 0 <= p < self._PROCESSES:
                                    self.buffer[p][i] = data[1:]
                            else:
                                raise ValueError("Received data too short")
                        except Exception as e:
                            print(f"Data processing error from {addr}: {e}")
                            self.buffer[0][i] = data
            except (ConnectionResetError, BrokenPipeError):
                print(f"Connection lost with {addr}")
                break
            except Exception as e:
                print(f"Unexpected error with {addr}: {e}")
                break

        print(f"Disconnected from {addr}")
        conn.close()

        if addr in self._connections:
            del self._connections[addr]


    def start_server(self):
        """
        Server : Listen for connections with neighbors that has lower MAC address.
        """

        server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        server.bind((self.RPIS_MACS[self.ID], self._PORT))
        server.listen(5)
        print("Server ready to receive connections...")

        while True:
            try:
                client, mac = server.accept()
                if mac[0] not in self._connections:
                    self._connections[mac[0]] = client
                    threading.Thread(target=self.handle_client, args=(client, mac[0]), daemon=True).start()
            except:
                break
        server.close()


    def connect_to_neighbor(self, mac):
        """
        Client : Initiate connection with neighbors that has higher MAC address.
        """

        while True:
            try:
                if mac in self._connections:
                    return  # Already connected

                print(f"Connection to {mac}...")
                client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                client.connect((mac, self._PORT))
                self._connections[mac] = client
                print(f"Connected to {mac}")

                threading.Thread(target=self.handle_client, args=(client, mac), daemon=True).start()

            except:
                print(f"Impossible to connect with {mac}, new attempt in 5s...")
                time.sleep(5)


    def send_message(self, type, *args, dest=None):
        """
        Send messages to specified agents

        type: Need to be specified using struct definitions. For example '<hf' is a short followed by a float in little endian.
        args: An undetermined number of variables that will be sent.
        dest []: list of the IDs of the destination agents
        Default: destination is everyone is dest is None
        """

        receivers = {}
        if dest is None:
            receivers = self._connections
        else:
            try:
                for i in range(len(dest)):
                    mac_receiver_i = self.RPIS_MACS[dest[i]]
                    try:
                        receivers[mac_receiver_i] = self._connections[mac_receiver_i]
                    except:
                        print(
                            f"Error: all elements of dest argument from Bluetooth.send_message should be the ID of a connected neighbor (ID={mac_receiver_i})")
                        raise Exception
            except:
                print("Error: dest argument from Bluetooth.send_message should be a list")
                raise TypeError


        for mac, conn in receivers.items():

            try:
                conn.send(struct.pack(type, *args))
                if self._VERBOSE:
                    print(f"Send {args} to {mac}")
            except:
                print(f"Sending error to {mac}")


    def start_network(self):
        """
        Establish connections with all neighbors and wait for them to be established.
        """

        # If a neighbor need to connect, start server in parallel
        for neighbor in self.neighbors:
            if neighbor < self._MAC:
                threading.Thread(target=self.start_server, daemon=True).start()
                break

        # Connect to neighbors that has higher MAC address
        for neighbor in self.neighbors:
            if neighbor > self._MAC:
                threading.Thread(target=self.connect_to_neighbor, args=(neighbor,), daemon=True).start()

        # Wait to be connected with each neighbor
        ready = False
        while not ready:
            time.sleep(1)
            ready = len(self._connections) == len(self.neighbors)

        time.sleep(1)
        print("Every neighbors are connected!")
        print()
