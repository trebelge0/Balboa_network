import struct
import time


class StandUp:

    def __init__(self, bt, balancer, process_id=0):
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
        self.balancer = balancer  # Balancer class instance
        self.buffer = [False for _ in range(len(bt.RPIS_MACS))]  # Neighbors messages
        self.PROCESS = process_id


    def get_standup(self):
        """
        Fill consensus communication buffer based on bluetooth.buffer

        For example, for 3 RPis in total, with current ID being 1, for 2 neighbors:
            self.bluetooth.buffer[self.PROCESS] is [-1, -1, -1] before the first communication
            self.bluetooth.buffer[self.PROCESS] is [0x'x', -1, 0x'x'] after
            self.buffer is [isBalancing(?), -1, isBalancing(?)] after calling self.get_standup
        """

        for i in range(len(self.buffer)):
            if self.bluetooth.buffer[self.PROCESS][i] != -1:
                self.buffer[i] = list(struct.unpack('<?', self.bluetooth.buffer[self.PROCESS][i]))[0]

        return self.buffer


    def run(self):
        """
        Bidirectional reverse domino : if one RPi stand up (manually or by pushing on a button),
        neighbors stand up as well, like reverse dominos.

        1. Send balancing state to neighbors
        2. Fill buffer with neighbors sent balancing states
        3. If rocky is down and neighbors is up, stand up

        Remarks:
        - self.bluetooth.buffer is filled with hex messages as soon as it is received
        - self.buffer is filled with balancing state from self.bluetooth.buffer
        as soon as we call self.get_standup()
        """

        self.balancer.setup()
        self.balancer.start()  # Run balancer thread

        while True:

            # Send rocky's state to neighbors
            self.bluetooth.send_message('<h?', self.PROCESS, self.balancer.balancing)

            # Update neighbor's state knowledge
            self.get_standup()

            print(self.bluetooth.buffer[self.PROCESS])
            print(self.buffer)
            print()

            # Send stand up command to rocky if one neighbor is up
            if not self.balancer.balancing and self.buffer != [False]*len(self.buffer):
                self.balancer.stand_up()

            time.sleep(5)