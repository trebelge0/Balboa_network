import numpy as np
import time
import struct
import psutil


class Consensus:

    def __init__(self, bt, init_state, delay=0, process_id=0):
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
        self.state = init_state  # Initial value of current RPi
        self.data = [[time.time(), init_state]]
        self.buffer = [[-1, -1.0, 0.0] for _ in range(len(bt.RPIS_MACS))]  # Neighbors messages [iteration, value, timestamp]
        self.PROCESS = process_id
        self.DELAY = delay


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
                self.buffer[i][0] = temp[0]
                self.buffer[i][1] = temp[1]

        return self.buffer


    def get_ACK(self, iteration):
        if iteration == 0:
            return False
        try:
            return any([struct.unpack('<hfh', self.bluetooth.buffer[self.PROCESS][n])[2] != iteration for n in self.bluetooth.neighbors_index])
        except:
            return True

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

        for i in range(0, 1000):

            # While not ack i-1
            while self.get_ACK(i):
                time.sleep(1e-2)
                continue

            # Messages has the structure : [iteration, frequency value] ([short, float] = 6 bytes)
            self.bluetooth.send_message('<hhfh', self.PROCESS, i, self.state, i)  # Send state to neighbors

            # Wait to receive initial neighbor's state
            while any([self.bluetooth.buffer[self.PROCESS][n] == -1 for n in self.bluetooth.neighbors_index]):
                time.sleep(1e-2)
                start_time = time.time()
                continue

            consensus_buffer = self.get_consensus()  # Update neighbor's state knowledge

            # Wait for the message of the current iteration from all neighbors
            while any([consensus_buffer[n][0] != i for n in self.bluetooth.neighbors_index]):
                time.sleep(1e-2)
                consensus_buffer = self.get_consensus()  # Update neighbor's state knowledge

            # Send ack
            self.bluetooth.send_message('<hhfh', self.PROCESS, i, self.state, i+1)

            # Compute the current mean value between neighbors and itself
            self.state = np.mean([consensus_buffer[n][1] for n in self.bluetooth.neighbors_index] + [self.state])
            self.data.append([time.time(), float(self.state)])

            # Print state
            print("state : ", self.state)
            print("iteration : ", i)
            print()

            time.sleep(self.DELAY)

        print("Finished loop")
