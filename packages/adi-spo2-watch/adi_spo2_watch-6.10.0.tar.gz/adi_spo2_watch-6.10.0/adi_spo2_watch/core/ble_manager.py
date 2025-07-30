import logging
import threading
import time
from queue import Queue
from sys import platform

import usb1
from . import utils

logger = logging.getLogger(__name__)


class BLEManager:
    RID_CMD = 0x01
    RID_RSP = 0x02
    RID_NOT = 0x03

    CMD_SCAN_STOP = 0x01
    CMD_SCAN_START = 0x00
    CMD_CONNECT = 0x02
    CMD_DISCONNECT = 0x03
    CMD_RESET = 0x7F

    MAX_LENGTH = 63

    def __init__(self, vendor_id, product_id, timeout=5, dongle_serial_number=None):
        self.queue = Queue()
        self.timeout = timeout
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.dongle_serial_number = dongle_serial_number
        self.device = None

    def _open(self):
        context = usb1.USBContext()
        device_list = context.getDeviceList(skip_on_error=True)
        device = None
        for dev in device_list:
            try:
                pid = dev.getProductID()
                vid = dev.getVendorID()
                s_number = dev.getSerialNumber()
                if vid == self.vendor_id and pid == self.product_id:
                    if s_number == self.dongle_serial_number:
                        device = dev
                        break
            except:
                pass
        if device is None:
            raise Exception(f"Can't find BLE dongle with vendor_id={self.vendor_id}, "
                            f"product_id={self.product_id} and serial_number={self.dongle_serial_number}.")
        else:
            self.device = device
            self.device = self.device.open()
            self.device.resetDevice()
            if platform == "linux" or platform == "linux2":
                if self.device.kernelDriverActive(0):
                    self.device.detachKernelDriver(0)
            elif platform == "darwin":
                pass
            elif platform == "win32":
                pass
            self.device.claimInterface(0)
        threading.Thread(target=self.receive_thread, daemon=True).start()

    def receive_thread(self):
        while True:
            try:
                data = self.device.bulkRead(0x81, 64)
                logger.debug(f"BLE RX :: {':'.join(utils.convert_int_array_to_hex(data))}")
                self.queue.put(data)
            except Exception as e:
                break

    def _send(self, packet):
        packet = packet + [0 for _ in range(self.MAX_LENGTH - len(packet))]
        logger.debug(f"BLE TX :: {':'.join(utils.convert_int_array_to_hex(packet))}")
        self.device.bulkWrite(1, packet)

    def _scan_start(self, mac_address):
        default_name = "Nordic_USBD_BLE_UART"
        msg = [self.RID_CMD, self.CMD_SCAN_START, 0, 1] + [ord(i) for i in default_name]
        self._send(msg)
        try:
            while True:
                data = self.queue.get(timeout=self.timeout)
                logger.debug(f"Scan Result :: {'-'.join(['%02X' % i for i in data[4:10]])}")
                if data[0] == 3 and list(data[4:10]) == mac_address:
                    break
        except Exception as e:
            logger.debug(e)
            raise Exception(f"Failed to find BLE device {'-'.join(['%X' % i for i in mac_address])}.")

    def _scan_stop(self):
        msg = [self.RID_CMD, self.CMD_SCAN_STOP, 0]
        self._send(msg)
        try:
            while True:
                data = self.queue.get(timeout=self.timeout)
                if data[0] == 2:
                    break
        except Exception as e:
            logger.debug(e)
            raise Exception(f"Failed to stop scan.")

    def connect(self, mac_address):
        self._open()
        mac_address = list(map(int, mac_address.split("-"), [16 for _ in mac_address]))
        mac_address = list(reversed(mac_address))
        self._reset()
        self._open()
        self._scan_start(mac_address)
        self._scan_stop()
        msg = [self.RID_CMD, self.CMD_CONNECT] + mac_address
        self._send(msg)
        try:
            while True:
                data = self.queue.get(timeout=self.timeout)
                if data[0] == 3:
                    time.sleep(2)
                    break
        except Exception as e:
            logger.debug(e)
            raise Exception(f"Can't connect to BLE {'-'.join(['%X' % i for i in mac_address])}.")
        logger.info(f"BLE connected to {'-'.join(['%X' % i for i in mac_address])}.")

    def disconnect(self):
        self._open()
        msg = [self.RID_CMD, self.CMD_DISCONNECT]
        self._send(msg)
        time.sleep(1)
        self.queue.empty()
        self.device.close()

    def _reset(self):
        msg = [self.RID_CMD, self.CMD_RESET, 0]
        self._send(msg)
        time.sleep(5)
