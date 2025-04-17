"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


import time
import threading
import struct
from collections import namedtuple
from utils import hex_str

BroadcastMessage = namedtuple('Message', ['id', 'sender', 'size', 'data', 'viewers'])


class Flooding:
    def __init__(self, bt, rocky, process_id=0, verbose=True, delay=0):

        # Public
        self.buffer = [BroadcastMessage(0, -1, 0, b"", set()) for _ in range(len(bt.RPIS_MACS))]
        self.ready = True
        self.data = []

        # Private
        self._listening = False
        self._bluetooth = bt
        self._rocky = rocky
        self._all_rpis_id = set(range(len(self._bluetooth.RPIS_MACS)))
        self._message_id = 0
        self._last_viewers = {n: set() for n in self._bluetooth.neighbors_index}

        # Constants
        self._PROCESS = process_id
        self._VERBOSE = verbose
        self._ID = bt.ID
        self._DELAY = delay


    def broadcast(self, data: str):

        data_byte = data.encode('utf-8')
        self.ready = False
        self._message_id += 1

        msg = BroadcastMessage(
            id=self._message_id ,
            sender=self._ID,
            size=len(data_byte),
            data=data_byte,
            viewers={self._ID}
        )
        self._last_viewers = {n: set() for n in self._bluetooth.neighbors_index}
        self._flood(msg)
        self._rocky.leds(0, 1, 0)  # Yellow
        print(f"[{self._ID}] Initiating flood: {msg}")


    def listen(self, mode=True):
        if mode:
            if not self._listening:
                self._listening = True
                threading.Thread(target=self._listen_loop, daemon=True).start()
        else:
            self._listening = False


    def _get_buffer(self):

        for i in range(len(self.buffer)):
            if self._bluetooth.buffer[self._PROCESS][i] != -1:
                packed = self._bluetooth.buffer[self._PROCESS][i]
                id = struct.unpack('H', packed[:2])[0]
                sender = struct.unpack('B', packed[2:3])[0]
                size = struct.unpack('H', packed[3:5])[0]
                data = struct.unpack(f'{size}s', packed[5:5 + size])[0]
                viewers = set(struct.unpack(f'{(len(packed[5 + size:]))}B', packed[5 + size:]))
                self.buffer[i] = BroadcastMessage(id, sender, size, data, viewers)


    def _listen_loop(self):

        while self._listening:

            self._get_buffer()

            for n in self._bluetooth.neighbors_index:

                message = self.buffer[n]

                if message.sender != -1:

                    print()
                    print(f"[{self._ID}] New message from {message.sender}: {message.data.decode('utf-8')}")
                    print(self._message_id)
                    print(self._last_viewers)
                    print(n)
                    print()

                    if self._ID not in message.viewers and self.ready:  # Receive new message

                        next_msg = BroadcastMessage(
                            id=message.id,
                            sender=message.sender,
                            size=message.size,
                            data=message.data,
                            viewers=message.viewers | {self._ID}
                        )
                        if message.viewers | {self._ID} == self._all_rpis_id:
                            print(f"[{self._ID}] All nodes reached! Turning GREEN")
                            self._rocky.leds(0, 0, 1)
                            self.ready = True
                        else:
                            self._rocky.leds(0, 1, 0)  # Yellow
                            self.ready = False

                        self._flood(next_msg)
                        if self._message_id != message.id:
                            self._last_viewers = {n: set() for n in self._bluetooth.neighbors_index}
                        self._message_id = message.id
                        self._last_viewers[n] = message.viewers | {self._ID}


                    elif self._message_id == message.id and not self.ready:

                        if message.viewers == self._all_rpis_id:

                            print(f"[{self._ID}] All nodes reached! Turning GREEN")
                            self._rocky.leds(0, 0, 1)
                            self.ready = True
                            self._flood(message)

                        elif message.viewers != self._last_viewers[n]:  # Viewers changed
                            next_msg = BroadcastMessage(
                                id=message.id,
                                sender=message.sender,
                                size=message.size,
                                data=message.data,
                                viewers=message.viewers | self._last_viewers[n]
                            )
                            self._last_viewers[n] = message.viewers | self._last_viewers[n]

                            if message.viewers | self._last_viewers[n] == self._all_rpis_id:
                                print(f"[{self._ID}] All nodes reached! Turning GREEN")
                                self._rocky.leds(0, 0, 1)
                                self.ready = True

                            self._flood(next_msg)
                            self.ready = False

            time.sleep(0.1)
            time.sleep(self._DELAY)


    def _flood(self, msg: BroadcastMessage):

        msg_type = f'<BHBH{len(msg.data)}s{len(msg.viewers)}B'
        self._bluetooth.send_message(msg_type,
                                     self._PROCESS,
                                     msg.id,
                                     msg.sender,
                                     msg.size,
                                     msg.data,
                                     *msg.viewers)

        print(f"[{self._ID}] Sent to neighbors")

        time.sleep(0.05)
