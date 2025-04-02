import struct
import threading
import time
import numpy as np


class Synchro:

    def __init__(self, bt, onSync, process_id=0):
        """
        self.Kphase is the phase correction to be applied on onSync(f, self.KPhase)

        onSync(self.Kphase) is the function that need to be synchronized.
            - It should be a periodic function.
            - It should have one mandatory arg which is the phase correction
            - It should handle itself the waiting time based on self.Kphase

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
        self.Kphase = 0  # Initial value of phase correction
        self.buffer = [-1 for _ in range(len(bt.RPIS_MACS))]  # Neighbors messages [iteration, value, timestamp]
        self.last_blink = time.time()
        self.onSync = onSync
        self.K_PHI = 0.1
        self.PROCESS = process_id
        self.data = []


    def get_synchro(self):
        """
        Fill synchronization communication buffer with neighbor's timestamp based on bluetooth.buffer

        For example, for 3 RPis in total, with current ID being 1, for 2 neighbors:
            self.bluetooth.buffer[self.PROCESS] is [-1, -1, -1] before the first communication
            self.bluetooth.[self.PROCESS] is [0x'xxxxxx', -1, 0x'xxxxxx'] after
            self.buffer is [178730.23, -1, 178730.21] after calling self.get_synchro
        """

        for i in range(len(self.buffer)):
            if self.bluetooth.buffer[self.PROCESS][i] != -1:
                self.buffer[i] = list(struct.unpack('<d', self.bluetooth.buffer[self.PROCESS][i]))[0]


    def average_neighbors(self):
        """
        Compute average timestamp among all neighbors

        For example, self.buffer is [178730.23, -1, 178730.21] give 178730.22
        """
        return np.mean([self.buffer[n] for n in self.bluetooth.neighbors_index])


    def sync_phase(self):
        """
        It compute the phase correction to be applied on onSync() in order to align phases.

        If neighbors are in average in advance on current RPi, self.Kphase will be > 0
        so the waiting time of current RPi will diminish (based on onSync) making it faster for this iteration.
        """

        self.get_synchro()
        t1 = self.last_blink
        t2 = self.average_neighbors()
        phase = t2-t1
        print("phase: ", phase)

        """while not (-1/(2*self.frequency) < phase < 1/(2*self.frequency)):
            if phase > 1/(2*self.frequency):
                print("-")
                phase -= 1/self.frequency
            elif phase < -1/(2*self.frequency):
                print("+")
                phase += 1/self.frequency

            print("phase: ", phase)"""

        self.Kphase = self.K_PHI * phase


    def run(self):
        """
        Run synchronization algorithm.

        0. It waits for each neighbor to send the first message (to avoid format error)

        1. It sends and last blink timestamp to all neighbors
        2. It executes onSync(), which is the function that need to be synchronized
           (note that it should follow specified rules)
        3. It fills the synchronization buffer with timestamps sent by neighbors (in sync_phase)
        4. It computes the phase correction to be applied on onSync in sync_phase()
        5. Loop back to (1)

        Remarks:
        - self.bluetooth.buffer is filled with hex messages as soon as it is received
        - self.buffer is filled with 'timestamp' based on self.bluetooth.buffer as soon as we call self.get_synchro
        - The first waiting while's aim is to avoid error by trying to fill consensus while every
         first messages has not been sent (self.bluetooth.buffer format would not allow it to be unstruct)
        """

        self.bluetooth.send_message('<hd', self.PROCESS, self.last_blink)

        while sum(1 for x in self.bluetooth.buffer[self.PROCESS] if x != -1) != len(self.bluetooth.neighbors):
            time.sleep(1)
            continue

        while True:
            self.bluetooth.send_message('<hd', self.PROCESS, self.last_blink)
            self.onSync(self.Kphase)
            self.sync_phase()
            self.data.append(time.time()-self.last_blink)
            self.last_blink = time.time()

            print("Phase correction: ", self.Kphase)

            print()