import serial
import struct
import time

SERIAL_PORT = "/dev/serial0"
BAUD_RATE = 115200


def hex_str(data):
    return " ".join(f"{b:02X}" for b in data)


def error(err_code):
    if err_code ==0 :
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


def dwm_loc_get(serial_port):
    """
    Récupère les données de localisation depuis un module DWM1001 via UART.

    :param serial_port: Instance de l'objet série (ex: serial.Serial)
    :return: Dictionnaire contenant la position et/ou les distances aux ancres.
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
        err_len = rx_data[data_cnt+1]
        err_code = rx_data[data_cnt+2:data_cnt+2+err_len]
        if int.from_bytes(err_code) != 0:
            error(err_code)
        data_cnt += 2 + err_len

    if rx_data[data_cnt] == TLV_TYPE_POS_XYZ:
        pos_len = rx_data[data_cnt+1]
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
        an_pos_dist_len = rx_data[data_cnt+1]
        an_number = rx_data[data_cnt+2]
        data_cnt += 3

        for i in range(an_number):

            if an_pos_dist_len // an_number >= 1 + DIST_LEN + POS_LEN:

                result[f'an{i}'] = {
                    'uwb_addr': hex_str(rx_data[data_cnt:data_cnt+2]),
                    'd': struct.unpack('<i', rx_data[data_cnt+2:data_cnt+6])[0],
                    'qf': rx_data[data_cnt+6]
                }
                data_cnt += DIST_LEN

                result[f'an{i}_pos'] = {
                    'x': struct.unpack('<i', rx_data[data_cnt:data_cnt + 4])[0],
                    'y': struct.unpack('<i', rx_data[data_cnt + 4:data_cnt + 8])[0],
                    'z': struct.unpack('<i', rx_data[data_cnt + 8:data_cnt + 12])[0],
                    'qf': rx_data[data_cnt + 12]
                }

            data_cnt += POS_LEN

    return result


if __name__ == "__main__":
    print(dwm_loc_get(serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1))
)
