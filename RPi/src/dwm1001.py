"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


import struct
import numpy as np
from utils import hex_str


def error(err_code):
    if err_code == 0:
        print("OK")
    elif err_code == 1:
        print("unknown command or broken TLV frame")
    elif err_code == 2:
        print("internal error")
    elif err_code == 3:
        print("invalid parameter")
    elif err_code == 4:
        print("busy")
    elif err_code == 5:
        print("operation not permitted")


class DWM:

    def __init__(self, balboa, window_size=5, verbose=False):

        # Use self.dwm_loc_get() if DWM1001 is connected to the RPi
        self.rocky = balboa

        self.distances = []
        self.positions = []
        self.distance = 0
        self.position = 0

        self.WINDOW = window_size  # Number of measures kept for moving average filtering
        self.VERBOSE = verbose


    def read(self):
        """
        Only use when DWM1001 is connected on the Balboa UART port, use self.dwm_loc_get() if it is connected to the RPi UART port
        """

        data = self.rocky.read_uwb()  # Read values from Balboa via i2c
        print(data)
        # Fill memory buffer for postprocessing
        self.distances.append(data[0]/10)
        self.positions.append(list(np.array(data[1:3])/10))

        # Update current distance and position
        self.distance = data[0]/10
        self.position = list(np.array(data[1:3])/10)


    def postprocess(self):
        """
        Remove outliers and use an approximate linear model of the sensor for distance measurements.

        To get a model of the sensor (a and b), use ../utils/dwm_calibration.py
        """

        if len(self.distances) > self.WINDOW:
            del self.distances[0]
            del self.positions[0]

        # Filter distances
        distances = np.array(self.distances)
        Q1 = np.percentile(distances, 40)
        Q3 = np.percentile(distances, 60)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        distances = distances[(distances >= lower_bound) & (distances <= upper_bound)]
        d = np.mean(distances)

        # Calibrate distances
        a = 0.9469764536578285
        b = -5.96484910568
        self.distance = a * d + b

        # Filter position
        pos_meas = np.array(self.positions)
        mean_meas = np.mean(pos_meas, axis=0)
        pos_dist = np.linalg.norm(pos_meas - mean_meas, axis=1)
        Q1 = np.percentile(pos_dist, 40)
        Q3 = np.percentile(pos_dist, 60)
        IQR = Q3 - Q1
        bound = Q3 + 1.5 * IQR
        pos_meas = pos_meas[pos_dist <= bound]
        pos_meas = np.mean(pos_meas, axis=0)

        # Calibrate position
        A = np.array([np.array([ 0.93538932,  0.00353817]),
                      np.array([-0.01071457,  0.94470965])])
        b = np.array([4.6239576, 5.0861534])

        self.position = (A @ pos_meas.T).T + b


    def dwm_loc_get(self, serial_port):
        """
        Only use when DWM1001 is connected on the RPi UART port, use self.read() if it is connected to the Balboa UART port.

        Send command to the DWM1001 through the UART bus and decode the response in order to get tag position
        and distance with all anchors
        """

        DWM1001_TLV_TYPE_CMD_LOC_GET = 0x0C

        TLV_TYPE_RET_VAL = 0x40
        TLV_TYPE_POS_XYZ = 0x41
        TLV_TYPE_RNG_AN_POS_DIST = 0x49

        POS_LEN = 13
        DIST_LEN = 7

        an_number = 0

        tx_data = bytearray([DWM1001_TLV_TYPE_CMD_LOC_GET, 0x00])
        serial_port.write(tx_data)

        rx_data = serial_port.read(150)
        if self.VERBOSE:
            print(hex_str(rx_data))

        result = {}

        data_cnt = 0

        if rx_data[data_cnt] == TLV_TYPE_RET_VAL:
            err_len = rx_data[data_cnt + 1]
            err_code = rx_data[data_cnt + 2:data_cnt + 2 + err_len]
            if int.from_bytes(err_code) != 0:
                error(err_code)
            data_cnt += 2 + err_len

        if rx_data[data_cnt] == TLV_TYPE_POS_XYZ:
            pos_len = rx_data[data_cnt + 1]
            data_cnt += 2
            if pos_len == POS_LEN:
                result['tag_pos'] = {
                    'x': struct.unpack('<i', rx_data[data_cnt:data_cnt + 4])[0],
                    'y': struct.unpack('<i', rx_data[data_cnt + 4:data_cnt + 8])[0],
                    'z': struct.unpack('<i', rx_data[data_cnt + 8:data_cnt + 12])[0],
                    'qf': rx_data[data_cnt + 12]
                }
            data_cnt += pos_len

        if rx_data[data_cnt] == TLV_TYPE_RNG_AN_POS_DIST:
            an_pos_dist_len = rx_data[data_cnt + 1]
            an_number = rx_data[data_cnt + 2]
            data_cnt += 3


            for i in range(an_number):

                result[f'an{i}'] = {
                    'uwb_addr': hex_str(rx_data[data_cnt:data_cnt + 2]),
                    'd': struct.unpack('<i', rx_data[data_cnt + 2:data_cnt + 6])[0],
                    'qf': rx_data[data_cnt + 6]
                }
                data_cnt += DIST_LEN

                result[f'an{i}_pos'] = {
                    'x': struct.unpack('<i', rx_data[data_cnt:data_cnt + 4])[0],
                    'y': struct.unpack('<i', rx_data[data_cnt + 4:data_cnt + 8])[0],
                    'z': struct.unpack('<i', rx_data[data_cnt + 8:data_cnt + 12])[0],
                    'qf': rx_data[data_cnt + 12]
                }

                data_cnt += POS_LEN

        if self.VERBOSE:
            print(result)

        try:
            for i in range(an_number):
                if result[f'an{i}']['uwb_addr'] == self.TARGET_ADDR:
                    self.distances.append(result[f'an{i}']['d'])

            self.positions.append([result['tag_pos']['x'], result['tag_pos']['y']])

            self.distance = self.distances[-1] / 1000
            self.position = list(np.array(self.positions[-1]) / 1000)

        except:
            print("DWM data missing")
