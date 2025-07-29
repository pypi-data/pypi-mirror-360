import glob
import sys
import serial


# Convert byte array to hex string
def byte_array_to_hex_str(byte_list: bytearray):
    return " ".join("%02X" % b for b in byte_list)


# Lists serial port names
# raises EnvironmentError:
#   On unsupported or unknown platforms
# :returns:
# A list of the serial ports available on the system
def find_serial_port():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# nb_char should be even. Odd number will be converted into a floor even number
def hex_str(my_str: str, nb_char: int = 2):
    nb_char_even = (nb_char // 2) * 2
    my_str_truncated = my_str[-nb_char_even:]
    return " ".join([''.join(item) for item in zip(my_str_truncated[::2], my_str_truncated[1::2])])
