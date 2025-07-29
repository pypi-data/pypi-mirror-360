import threading
import serial


class Peripheral:
    def __init__(self, port_name: str, baud_rate: int = 115200, stop_bits: float = None, byte_size: int = 8,
                 parity: str = None):
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.stop_bits = stop_bits
        self.byte_size = byte_size
        self.parity = parity
        self.buf = bytes()
        self.BUF_SIZE = 1024
        self.__serial = serial.Serial()
        self.thread_read = None
        # try:
        #     self.thread_read = threading.Thread(target=self.read)
        #     self.thread_read.start()
        #     print("start threading")
        # except:
        #     print(f"Error: 无法启动线程\n")

    @property
    def port_name(self):
        return self.__port_name

    @port_name.setter
    def port_name(self, new_port_name: str):
        self.__port_name = new_port_name

    @property
    def baud_rate(self):
        return self.__baud_rate

    @baud_rate.setter
    def baud_rate(self, new_baud_rate: int = 115200):
        self.__baud_rate = new_baud_rate

    @property
    def stop_bits(self):
        return self.__stop_bits

    @stop_bits.setter
    def stop_bits(self, new_stop_bits: float = None):
        self.__stop_bits = new_stop_bits

    @property
    def byte_size(self):
        return self.__byte_size

    @byte_size.setter
    def byte_size(self, new_byte_size: int = 8):
        if new_byte_size < 5:
            self.__byte_size = 5
        elif new_byte_size > 8:
            self.__byte_size = 8
        else:
            self.__byte_size = new_byte_size

    @property
    def parity(self):
        return self.__parity

    @parity.setter
    def parity(self, new_parity: str = None):
        if new_parity is None:
            self.__parity = serial.PARITY_NONE
        else:
            if new_parity == "偶":
                self.__parity = serial.PARITY_EVEN
            elif new_parity == "奇":
                self.__parity = serial.PARITY_ODD
            elif new_parity == "高":
                self.__parity = serial.PARITY_MARK
            elif new_parity == "低":
                self.__parity = serial.PARITY_SPACE
            else:
                self.__parity = serial.PARITY_NONE

    def start(self):
        self.__serial.port = self.port_name
        self.__serial.baudrate = self.baud_rate
        self.__serial.bytesize = self.byte_size
        if self.stop_bits is not None:
            self.__serial.stopbits = self.stop_bits
        self.__serial.parity = self.parity
        self.__serial.open()
        try:
            self.thread_read = threading.Thread(target=self.read)
            self.thread_read.start()
            # print("start threading")
        except:
            print(f"Error: 无法启动线程\n")

    def stop(self):
        try:
            self.__serial.close()
            self.thread_read.join()

        except:

            pass

    def read(self):
        try:
            while True:
                if self.__serial is None or not self.__serial.isOpen():
                    continue
                data_size = self.__serial.in_waiting
                if data_size < 1:
                    continue
                self.buf += self.__serial.read(data_size)
                data_buf = " ".join("%02X" % b for b in self.buf)
                print(f"buf:{data_buf}")
                if len(self.buf) > self.BUF_SIZE:
                    self.buf = self.buf[len(self.buf) - self.BUF_SIZE:]
        except:
            pass
        finally:
            pass
        print("\ntuxing thread 1 Done")

    def write(self, data: str):
        self.__serial.write(bytearray.fromhex(data))
        print(f"send message:{data}")

    def parse_data(self, prefix: str, postfix: str, start: int, end: int):
        data_hex = "".join("%02X" % b for b in self.buf)
        prefix_ = prefix.replace(" ", "")
        postfix_ = postfix.replace(" ", "")
        index_header = data_hex.rfind(prefix_)
        index_tailer = data_hex.rfind(postfix_)
        if -1 < index_header < index_tailer:
            return data_hex[start:end]

        if -1 < index_tailer < index_header:
            data_hex = data_hex[:index_tailer]
            index_header = data_hex.rfind(prefix_)
            data_hex = data_hex[index_header:]
            return data_hex[start:end]
        return ""
