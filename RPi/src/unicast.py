"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""

import time
import threading
import struct
from collections import deque, namedtuple
from copy import deepcopy
from multiprocessing.reduction import sendfds

UnicastMessage = namedtuple('UnicastMessage', ['id', 'sender', 'receiver', 'ACK', 'index', 'size', 'data', 'path'])


class Unicast:
    def __init__(self, bt, rocky, process_id=0, verbose=True, delay=0):

        # Public
        self.buffer = [UnicastMessage(0, -1, -1, False, 0, 0, b"", []) for _ in range(len(bt.RPIS_MACS))]
        self.last_message = None
        self.ready = True
        self.data = []
        self.message_id = 0

        # Private
        self._bluetooth = bt
        self._rocky = rocky
        self._listening = False

        self._ID = bt.ID
        self._ADJACENCY = bt.ADJACENCY
        self._PROCESS = process_id
        self._VERBOSE = verbose
        self._DELAY = delay


    def _get_path(self, dst):
        visited = set()
        queue = deque([[self._ID]])

        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == dst:
                return path
            if node not in visited:
                visited.add(node)
                for i in range(len(self._ADJACENCY[node])):
                    if self._ADJACENCY[node][i] == 1:
                        if i not in path:
                            queue.append(path + [i])
        return []


    def _get_buffer(self):

        for i in range(len(self.buffer)):
            if self._bluetooth.buffer[self._PROCESS][i] != -1:
                packed = self._bluetooth.buffer[self._PROCESS][i]
                id = struct.unpack('H', packed[:2])[0]
                sender = struct.unpack('B', packed[2:3])[0]
                receiver = struct.unpack('B', packed[3:4])[0]
                ack = struct.unpack('?', packed[4:5])[0]
                index = struct.unpack('B', packed[5:6])[0]
                size = struct.unpack('H', packed[6:8])[0]
                data = struct.unpack(f'{size}s', packed[8:8 + size])[0]
                path = struct.unpack(f'{len(packed[8+size:])}B', packed[8+size:])
                self.buffer[i] = UnicastMessage(id, sender, receiver, ack, index, size, data, path)


    def listen(self, mode=True):
        if mode:
            if not self._listening:
                self._listening = True
                threading.Thread(target=self._listen_loop, daemon=True).start()
        else:
            self._listening = False


    def send(self, data: str, destination: int, ack=False, id=0):
        path = self._get_path(destination)
        if not path or len(path) < 2:
            print(f"No path to {destination}")
            return

        data_bytes = data.encode('utf-8')
        message = UnicastMessage(
            id=self.message_id*int(not ack) + id*int(ack),
            sender=self._ID,
            receiver=destination,
            ACK=ack,
            index=0,
            size=len(data_bytes),
            data=data_bytes,
            path=path
        )
        self.message_id += int(not ack)
        self._forward(message)
        self._rocky.leds(0, int(not ack), int(ack))  # Yellow
        print(f"[{self._ID}] Initiating unicast: {message}")


    def _listen_loop(self):

        while self._listening:

            message = None
            while message is None:
                last_buffer = deepcopy(self.buffer)
                self._get_buffer()
                for i in range(len(self.buffer)):
                    if last_buffer[i] != self.buffer[i]:
                        message = self.buffer[i]
                        self.last_message = message
                        break

            if self._ID == message.receiver:

                if self._VERBOSE:
                    print(f"Received unicast from {message.sender}: {message.data.decode('utf-8')}")
                self._rocky.leds(0, 0, 1)  # Green on receive
                self.ready = True

                # Send ACK back to sender
                if not message.ACK:
                    self.send(f"ACK:{message.data.decode('utf-8')}", message.sender, ack=True, id=message.id)
                elif self._VERBOSE:
                    print("Acknowledgement received")
                    print()


            else:
                if self._VERBOSE:
                    print(f"Forwarding message from {message.sender} to {message.receiver}")
                self._forward(message._replace(index=message.index + 1))

                if not message.ACK:
                    self.ready = False
                    self._rocky.leds(0, 1, 0)  # Yellow on forward
                elif not self.ready:
                    self._rocky.leds(0, 0, 1)  # Green on ACK
                    self.ready = True

            time.sleep(self._DELAY)


    def _forward(self, msg: UnicastMessage):
        if msg.index >= len(msg.path) - 1:
            return

        next_hop = msg.path[msg.index + 1]
        path_len = len(msg.path)

        msg_type = f'<BHBB?BH{msg.size}s{path_len}B'

        self._bluetooth.send_message(
            msg_type,
            self._PROCESS,
            msg.id,
            msg.sender,
            msg.receiver,
            msg.ACK,
            msg.index,
            msg.size,
            msg.data,
            *msg.path,
            dest=[next_hop]
        )
        if self._VERBOSE:
            print(f"Sent unicast from {self._ID} to {next_hop} (next index: {msg.index + 1})")

        time.sleep(0.05)
