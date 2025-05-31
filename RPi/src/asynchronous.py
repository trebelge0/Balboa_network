"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


import time
import struct


class Async:

    def __init__(self, bt, init_state, next_msg, msg_struct, delay=0, process_id=0, verbose=True):
        """
        Args:
            bt:                     instance of Bluetooth used for this process.
            init_state:             list of initial value of the RPi state (size:len(bluetooth.buffer)-2)
            next_msg(buffer):              execute something based on buffer
            msg_struct:               str corresponding to the state type base on struct types (size:len(init_state))
            delay:                  optional delay between each message
            process_id:             optional int corresponding to the process id

        Notes:
            process_id has to be set if several processes need bluetooth.
            For example: you want to use synchronization and consensus:
                - self.bluetooth.PROCESSES need to be 2
                - phase_consensus = Consensus(bluetooth, phase, process_id=0)
                - freq_consensus = Consensus(bluetooth, init_freq, delay=0, process_id=1)
                - self.bluetooth.buffer size is 2 x len(self.bluetooth.RPIS_MACS)
                - Default: if self.bluetooth.PROCESSES is 0, you are not required to send bluetooth messages starting
                  with the process number.


            Each time self.bluetooth.send_message() is called, it should include the process number (ushort: 'H').
                - For example : self.bluetooth.send_message('<Hd', self.PROCESS, self.last_blink)
                - self.bluetooth.handle_client() will recognize the process that uses the buffer and place it in the
                  right row of self.bluetooth.buffer

            However, the process number will not be included into bluetooth.buffer.
                - Using above example: self.bluetooth.buffer will in the following structure: ['d', ..., 'd']
        """

        if len(msg_struct) != len(init_state):
            print("The specified data type must be the same length of initial state")
            raise Exception

        self.bluetooth = bt  # Bluetooth class instance
        self.message = init_state  # Initial value of current RPi
        self.data = [[time.time(), *init_state]]  # For data saving
        self.more_data = [-1]  # For saving more than only the state (not used when self.more_data[0] == -1)
        self.buffer = [[-1.0]*len(init_state) for _ in range(len(bt.RPIS_MACS))]  # Neighbors messages [value(4)]
        self.next_msg = next_msg

        self.PROCESS = process_id
        self.DELAY = delay
        self.TYPE = f'<{msg_struct}'
        self.VERBOSE = verbose


    def get_buffer(self):
        """
        Fill the synchronized communication buffer based on bluetooth.buffer

        For example, for 3 RPis in total, with current ID being 1, for 2 neighbors:
            self.bluetooth.buffer[self.PROCESS] is [-1, -1, -1] before the first communication
            self.bluetooth.buffer[self.PROCESS] is [0x'xxxxxx', -1, 0x'xxxxxx'] after
            self.buffer is [[iteration1, value1], [-1, -1.0], [iteration2, value2]] after calling self.get_consensus
        """

        for i in range(len(self.buffer)):
            if self.bluetooth.buffer[self.PROCESS][i] != -1:
                temp = list(struct.unpack(self.TYPE, self.bluetooth.buffer[self.PROCESS][i]))
                self.buffer[i][:] = temp
        self.buffer[self.bluetooth.ID] = self.message


    def run(self):
        """
        Run asynchronous communication

            1. It sends a message to all neighbors
            2. It fills the communication buffer with messages sent by neighbors
            4. Execute next_msg and assign new message
            5. Loop back to (1)

        Notes:
            - self.bluetooth.buffer is filled with hex messages as soon as it is received
            - self.buffer is filled with [message] from self.bluetooth.buffer as soon as we call self.get_buffer
        """

        i = 0  # iteration value
        while True:

            # Messages has the structure : [PROCESS_ID, iteration, state, ACK] ([short, short, self.TYPE, short])
            self.bluetooth.send_message(f'<B{self.TYPE[1:]}', self.PROCESS, *self.message)  # Send state to neighbors

            # Wait to receive initial neighbor's state
            while any([self.bluetooth.buffer[self.PROCESS][n] == -1 for n in self.bluetooth.neighbors_index]):
                time.sleep(1e-2)
                continue

            self.get_buffer()  # Update neighbor's state knowledge

            self.message = self.next_msg(self.buffer)  # Execute some tasks. It must return the next message as well

            # For data saving
            self.data.append([time.time(), *self.message])
            if self.more_data[0] != -1:
                for j in range(len(self.more_data)):
                    self.data[-1].append(self.more_data[j])

            # Print state
            if self.VERBOSE:
                print("state : ", self.message)
                print()

            # Optional delay
            time.sleep(self.DELAY)

            i += 1
