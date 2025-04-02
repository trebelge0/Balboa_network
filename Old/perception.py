import numpy as np
import time
import struct


class Perception:

    def __init__(self, bt, process_id=0):
        """
        process_id has to be set if several processes need bluetooth.
        For example: you want to use synchronization and consensus:
            - self.bluetooth.PROCESSES need to be 2
            - Synchro(bt, f, onSync, process_id=0)
            - Synchro(bt, f, onSync, process_id=1)
            - self.bluetooth.buffer size is 2 x len(self.bluetooth.RPIS_MACS)
            - Each time self.bluetooth.send_message() is called, it should include the process number (short: 'h').
                - For example : self.bluetooth.send_message('<hd', self.PROCESS, self.last_blink)
                - self.bluetooth.handle_client() will recognize the process that uses the buffer and place it in the
                  right row of self.bluetooth.buffer

        - Default: if you specify nothing of that, it will automatically set the number of processes to 0,
          and you are not required to send bluetooth messages starting with the process number.
        """
        self.bluetooth = bt  # Bluetooth class instance
        self.data = []
        self.buffer = [-1 for _ in range(len(bt.RPIS_MACS))]  # Neighbors messages [iteration, value, timestamp]
        self.PROCESS = process_id


    def get_consensus(self):
        """
        Fill consensus communication buffer based on bluetooth.buffer

        For example, for 3 RPis in total, with current ID being 1, for 2 neighbors:
            self.bluetooth.buffer[self.PROCESS] is [-1, -1, -1] before the first communication
            self.bluetooth.buffer[self.PROCESS] is [0x'xxxxxx', -1, 0x'xxxxxx'] after
            self.buffer is [[iteration1, value1], [-1, -1.0], [iteration2, value2]] after calling self.get_consensus
        """

        for i in range(len(self.buffer)):
            if self.bluetooth.buffer[self.PROCESS][i] != -1:
                temp = list(struct.unpack('<hfh', self.bluetooth.buffer[self.PROCESS][i]))
                self.buffer[i] = temp[0]

        return self.buffer


    def run(self):
        """
        Run consensus algorithm.

        1. It sends its iteration and value to all neighbors
        2. It fills the consensus buffer with iteration and values sent by neighbors
        3. Go back to (2) while current iteration message has not been sent by all neighbors
        4. Compute new iteration's mean value
        5. Loop back to (1)

        Remarks:
        - self.bluetooth.buffer is filled with hex messages as soon as it is received
        - self.buffer is filled with [iteration, value] from self.bluetooth.buffer
        as soon as we call self.get_consensus
        - The first waiting while's aim is to avoid error by trying to fill consensus while every
         first messages has not been sent (self.bluetooth.buffer format would not allow it
         to be unstruct)
        """
        while True:
            # For each neighbor missing, find the shortest path
            # Send a request to this node (ID_ask, ID_target, -1)
            # If I get a -1 request and not target, go back to 2
            # If I get a -1 request and am target, 
            continue
