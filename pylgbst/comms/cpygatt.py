import logging

import pygatt

from pylgbst.comms import Connection, LEGO_MOVE_HUB
from pylgbst.constants import MOVE_HUB_HW_UUID_CHAR
from pylgbst.utilities import str2hex

log = logging.getLogger('comms-pygatt')


class GattoolConnection(Connection):
    """
    Used for connecting to

    :type _conn_hnd: pygatt.backends.bgapi.device.BGAPIBLEDevice
    """

    def __init__(self, controller='hci0'):
        log.debug('GattoolConnection: __init__')
        Connection.__init__(self)
        self.backend = lambda: pygatt.GATTToolBackend(hci_device=controller)
        self._conn_hnd = None

    def connect(self, hub_mac=None):
        log.debug('GattoolConnection: connect')
        log.debug("Trying to connect client to MoveHub with MAC: %s", hub_mac)
        adapter = self.backend()
        adapter.start()

        if hub_mac is not None:
            log.info("Connect to %s", hub_mac)
            self._conn_hnd = adapter.connect(hub_mac)
        else:
            while not self._conn_hnd:
                log.info("Discovering devices...")
                devices = adapter.scan(1)
                log.debug("Devices: %s", devices)

                for dev in devices:
                    address = dev['address']
                    name = dev['name']
                    if name == LEGO_MOVE_HUB:
                        log.info("Found %s at %s", name, address)
                        self._conn_hnd = adapter.connect(address)
                        break

                if self._conn_hnd:
                    break

        return self

    def disconnect(self):
        log.debug('GattoolConnection: disconnect')
        self._conn_hnd.disconnect()

    def write(self, handle, data):
        log.debug('GattoolConnection: write')
        log.debug("Writing to handle %s: %s", handle, str2hex(data))
        return self._conn_hnd.char_write_handle(handle, bytearray(data))

    def set_notify_handler(self, handler):
        log.debug('GattoolConnection: set_notify_handler')
        self._conn_hnd.subscribe(MOVE_HUB_HW_UUID_CHAR, handler)

    def is_alive(self):
        log.debug('GattoolConnection: is_alive')
        return True


class BlueGigaConnection(GattoolConnection):
    def __init__(self):
        log.debug('BlueGigaConnection: __init__')
        super(BlueGigaConnection, self).__init__()
        self.backend = lambda: pygatt.BGAPIBackend()
