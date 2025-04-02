"""
Romain Englebert - Master's Thesis
© 2025 Romain Englebert.
"""


import struct
import numpy as np


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


def hex_str(data):
    return " ".join(f"{b:02X}" for b in data)


class DWM:

    def __init__(self, balboa, window_size=5):

        # Use self.dwm_loc_get() if DWM1001 is connected to the RPi
        self.rocky = balboa

        self.distances = []
        self.positions = []
        self.distance = 0
        self.position = 0
        self.read()

        self.WINDOW = window_size  # Number of measures kept for postprocessing


    def read(self):
        """
        Only use when DWM1001 is connected on the Balboa UART port, use self.dwm_loc_get() if it is connected to the RPi UART port
        """

        data = self.rocky.read_uwb()  # Read values from Balboa via i2c

        # Fill memory buffer for postprocessing
        self.distances.append(data[0])
        self.positions.append(data[1:3])
        if len(self.distances) >= self.WINDOW:
            del self.distances[0]
            del self.positions[0]

        # Update current distance and position
        self.distance = data[0]
        self.position = data[1:3]


    def postprocess(self):
        """
        Remove outliers and use an approximate linear model of the sensor for distance measurements.

        To get a model of the sensor (a and b), use ../utils/dwm_calibration.py
        """

        values = np.array(self.distance)
        Q1 = np.percentile(values, 20)
        Q3 = np.percentile(values, 80)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        values = values[(values >= lower_bound) & (values <= upper_bound)]

        d = np.mean(values)
        a = 0.94922
        b = -0.103395

        self.distance = a * d + b


    def dwm_loc_get(self, serial_port):
        """
        Only use when DWM1001 is connected on the RPi UART port, use self.read() if it is connected to the Balboa UART port.

        Send command to the DWM1001 through the UART bus and decode the response in order to get tag position
        and distance with all anchors
        """

        DWM1001_TLV_TYPE_CMD_LOC_GET = 0x0C

        TLV_TYPE_RET_VAL = 0x40
        TLV_TYPE_POS_XYZ = 0x41
        TLV_TYPE_RNG_AN_DIST = 0x48
        TLV_TYPE_RNG_AN_POS_DIST = 0x49

        POS_LEN = 13
        DIST_LEN = 7

        tx_data = bytearray([DWM1001_TLV_TYPE_CMD_LOC_GET, 0x00])
        serial_port.write(tx_data)

        rx_data = serial_port.read(100)
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

        if rx_data[data_cnt] in [TLV_TYPE_RNG_AN_POS_DIST, TLV_TYPE_RNG_AN_DIST]:
            an_pos_dist_len = rx_data[data_cnt + 1]
            an_number = rx_data[data_cnt + 2]
            data_cnt += 3

            for i in range(an_number):

                if an_pos_dist_len // an_number >= 1 + DIST_LEN + POS_LEN:
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

        self.positions.append(result['an0']['d'])
        self.distances.append([result['tag_pos']['x'], result['tag_pos']['y']])
