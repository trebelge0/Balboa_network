import numpy as np
import time
import struct


class Localize:

    def __init__(self, bt, init_state, delay=0, process_id=0, gamma=5e-3):
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
        self.state = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Initial state of current RPi
        self.data = [[time.time(), 0, 0, 0, 0, 0, 0]]
        self.buffer = [[-1, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 0.0] for _ in range(len(bt.RPIS_MACS))]  # Neighbors messages [iteration, value(4), gradient(2), ACK]
        self.distance = init_state[2]
        self.position = np.array(init_state[:2])
        self.PROCESS = process_id
        self.DELAY = delay
        self.GAMMA = gamma


    def get_buffer(self):
        """
        Fill consensus communication buffer based on bluetooth.buffer

        For example, for 3 RPis in total, with current ID being 1, for 2 neighbors:
            self.bluetooth.buffer[self.PROCESS] is [-1, -1, -1] before the first communication
            self.bluetooth.buffer[self.PROCESS] is [0x'xxxxxx', -1, 0x'xxxxxx'] after
            self.buffer is [[iteration1, value1], [-1, -1.0], [iteration2, value2]] after calling self.get_consensus
        """

        for i in range(len(self.buffer)):
            if self.bluetooth.buffer[self.PROCESS][i] != -1:
                temp = list(struct.unpack('<hddddddh', self.bluetooth.buffer[self.PROCESS][i]))
                self.buffer[i][:] = temp
        self.buffer[self.bluetooth.ID][1:-1] = self.state


    def get_ack(self, iteration):
        if iteration == 0:
            return False
        try:
            return any([struct.unpack('<hddddddh', self.bluetooth.buffer[self.PROCESS][n])[7] != iteration for n in self.bluetooth.neighbors_index])
        except:
            return True


    def run(self):
        """
        Run localization algorithm.

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
            while self.get_ack(i):
                time.sleep(1e-2)
                continue

            # Messages has the structure : [iteration, frequency value] ([short, float] = 6 bytes)
            self.bluetooth.send_message('<hhddddddh', self.PROCESS, i, *self.state, i)  # Send state to neighbors

            # Wait to receive initial neighbor's state
            while any([self.bluetooth.buffer[self.PROCESS][n] == -1 for n in self.bluetooth.neighbors_index]):
                time.sleep(1e-1)
                continue

            # Wait for the message of the current iteration from all neighbors
            while any([self.buffer[n][0] != i for n in self.bluetooth.neighbors_index]):
                time.sleep(1e-1)
                self.get_buffer()  # Update neighbor's state knowledge

            time.sleep(self.DELAY)

            # Send ack
            self.bluetooth.send_message('<hhddddddh', self.PROCESS, i, *self.state, i+1)

            # Compute the current state
            xi_t = np.array(self.state[0:2])
            zi_t = np.array(self.state[2:4])

            wijxj = np.zeros(2)
            wijzj = np.zeros(2)
            wijgj = np.zeros(2)
            for j in self.bluetooth.neighbors_index + [self.bluetooth.ID]:
                wij = np.array(self.bluetooth.ADJACENCY[self.bluetooth.ID][j] / sum(self.bluetooth.ADJACENCY[self.bluetooth.ID]))
                xj_t = np.array(self.buffer[j][1:3])
                zj_t = np.array(self.buffer[j][3:5])
                gj_t = np.array(self.buffer[j][5:7])
                wijxj += wij*xj_t
                wijzj += wij*zj_t
                wijgj += wij*gj_t
                print("wij: ", wij)
                print("xj_t: ", xj_t)
                print("zj_t: ", zj_t)
                print("gj_t: ", gj_t)


            gi_t = np.array(self.state[4:6])

            self.state[0:2] = wijxj - zi_t - self.GAMMA * gi_t  # xi_{t+1}
            self.state[2:4] = wijzj - self.GAMMA * gi_t + self.GAMMA * wijgj  # zi_{t+1}
            xi_t1 = np.array(self.state[0:2])
            self.state[4:6] = 4 * (self.distance**2 - np.linalg.norm(xi_t1 - self.position)**2) * (self.position - xi_t1)  # gi_{t+1}

            for j in range(6):
                self.state[j] = round(self.state[j], 6)

            f = (self.distance ** 2 - np.linalg.norm(xi_t1 - self.position) ** 2) ** 2
            self.data.append([time.time(), *self.state, f])

            # Print state
            print("wijxj: ", wijxj)
            print("wijzj: ", wijzj)
            print("wijgj: ", wijgj)
            print("zi_t: ", zi_t)
            print("gi_t: ", gi_t)
            print("state : ", self.state)
            print("iteration : ", i)
            print()

            time.sleep(self.DELAY)

        print("Finished loop")
