import time
import struct


class Sync:

    def __init__(self, bt, init_state, compute_state, msg_type, delay=0, process_id=0, verbose=True):
        """
        Args:
            bt:                     instance of Bluetooth used for this process.
            init_state:             list of initial value of the RPi state (size:len(bluetooth.buffer)-2)
            compute_state(buffer):  returns the next state based on buffer (self.buffer)
            msg_type:               str corresponding to the state type base on struct types (size:len(init_state))
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


            Each time self.bluetooth.send_message() is called, it should include the process number (short: 'h').
                - For example : self.bluetooth.send_message('<hd', self.PROCESS, self.last_blink)
                - self.bluetooth.handle_client() will recognize the process that uses the buffer and place it in the
                  right row of self.bluetooth.buffer

            However, the process number will not be included into bluetooth.buffer.
                - Using above example: self.bluetooth.buffer will in the following structure: ['d', ..., 'd']
        """

        if len(msg_type) != len(init_state):
            print("The specified data type must be the same length of initial state")
            raise Exception

        self.bluetooth = bt  # Bluetooth class instance
        self.state = init_state  # Initial value of current RPi
        self.data = [[time.time(), *init_state]]  # For data saving
        self.more_data = [-1]  # For saving more than only the state (not used when self.more_data[0] == -1)
        temp = [-1.0]*len(init_state)
        self.buffer = [[-1, *temp, 0] for _ in range(len(bt.RPIS_MACS))]  # Neighbors messages [iteration, state, ACK]
        self.compute_state = compute_state

        self.PROCESS = process_id
        self.DELAY = delay
        self.TYPE = f'h{msg_type}h'  # First and last 'h' are respectively used for iteration and acknowledgement synchronization loop
        self.VERBOSE = verbose


    def get_buffer(self):
        """
        Fill the synchronized communication buffer based on bluetooth.buffer

        For example, for 3 RPis in total, with current ID being 1, for 2 neighbors:
            self.bluetooth.buffer[self.PROCESS] is [-1, -1, -1] before the first communication
            self.bluetooth.buffer[self.PROCESS] is [0x'xxxxxx', -1, 0x'xxxxxx'] after
            self.buffer is [[iteration1, value1], [-1, -1.0], [iteration2, value2]] after calling self.get_buffer
        """

        for i in range(len(self.buffer)):
            if self.bluetooth.buffer[self.PROCESS][i] != -1:
                temp = list(struct.unpack(self.TYPE, self.bluetooth.buffer[self.PROCESS][i]))
                self.buffer[i][:] = temp
        self.buffer[self.bluetooth.ID][1:-1] = self.state


    def get_ACK(self, iteration):
        """
        Sometimes, RPi A may sent its message from iteration i while RPi B did not fetch its message from iteration i-1.
        As a result, RPi B will skip message from A at iteration i-1
        To solve that, RPi wait for each RPi to receive its message from iteration i-1 before sending message from iteration i.
        In order to get this information, an acknowledgement is sent after each read in bluetooth.buffer.
        This acknowledgement is a number corresponding to the next iteration
        """

        if iteration == 0:
            return False
        try:
            return any([struct.unpack(self.TYPE, self.bluetooth.buffer[self.PROCESS][n])[-1] != iteration for n in self.bluetooth.neighbors_index])
        except:
            return True


    def run(self):
        """
        Run synchronous communication

            0. Wait for ACK from each neighbors before going to 1.
            1. It sends its iteration and value to all neighbors
            2. It fills the communication buffer with iteration and values sent by neighbors
            3. Go back to (2) while current iteration message has not been sent by all neighbors
            4. Compute new iteration's state
            5. Loop back to (1)

        Notes:
            - self.bluetooth.buffer is filled with hex messages as soon as it is received
            - self.buffer is filled with [iteration, state, ACK] from self.bluetooth.buffer as soon as we call self.get_buffer
            - There are 2 synchronization loop:
                - First: acknowledgement loop used to avoid skipping iterations
                - Second: iteration loop used to wait for reception of all states from the current iteration.
        """

        i = 0  # iteration value
        while True:

            # First synchronization loop
            # While not ack i-1
            while self.get_ACK(i):
                time.sleep(1e-2)
                continue

            # Messages has the structure : [PROCESS_ID, iteration, state, ACK] ([short, short, self.TYPE, short])
            self.bluetooth.send_message(f'<h{self.TYPE}', self.PROCESS, i, *self.state, i)  # Send state to neighbors

            # Wait to receive initial neighbor's state
            while any([self.bluetooth.buffer[self.PROCESS][n] == -1 for n in self.bluetooth.neighbors_index]):
                time.sleep(1e-2)
                continue

            self.get_buffer()  # Update neighbor's state knowledge

            # Second synchronization loop
            # Wait for the message of the current iteration from all neighbors
            while any([self.buffer[n][0] != i for n in self.bluetooth.neighbors_index]):
                time.sleep(1e-2)
                self.get_buffer()  # Update neighbor's state knowledge

            # If the RPi lost connection after few iterations, increase this delay
            time.sleep(self.DELAY)

            # Send acknowledgement
            self.bluetooth.send_message(f'<h{self.TYPE}', self.PROCESS, i, *self.state, i+1)

            # Compute the current state
            self.state = self.compute_state(self.buffer, self.state)

            # For data saving
            self.data.append([time.time(), *self.state])
            if self.more_data != -1:
                for j in range(len(self.more_data)):
                    self.data[-1].append(self.more_data[j])

            # Optional delay in order to observe convergence
            time.sleep(self.DELAY)

            # Print state
            if self.VERBOSE:
                print("state : ", self.state)
                print("iteration : ", i)
                print()

            i += 1
