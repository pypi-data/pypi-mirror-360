from JHFDRONE.JHFDRONE import JHFDRONE
from JHFDRONE.peripheral import Peripheral
from JHFDRONE.serialHelper import find_serial_port

if __name__ == '__main__':
    port_name = find_serial_port()
    print(port_name)
    if len(port_name) > 0:
        peripheral = Peripheral(port_name[0])
        tuxing = JHFDRONE(peripheral)
        tuxing.start()
        tuxing.init_uav()
        tuxing.stop()
