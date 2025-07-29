
import time
import threading
from typing import Callable, Optional

import usb.core
import usb.util
import usb.backend.libusb1


from .commands import (Config, Action,
                       get_cmd_start, get_cmd_stop, get_cmd_poll_vals,
                       parse_data, get_cmd_get_version, get_cmd_get_settings,
                       ChargerResponse)


VENDOR_ID = 0x0000
PRODUCT_ID = 0x0001

ENDPOINT_WRITE = 0x02
ENDPOINT_READ = 0x81


class Charger:
    def __init__(self, rec_data_callback: Optional[Callable[[ChargerResponse], None]] = None,
                 device_index: int = 0):
        self.dev = None
        self._rec_data_callback = rec_data_callback
        self._device_index = device_index
        self.read_thread = None
        self.stop_requested = False
        self._read_errors = 0
        self._write_errors = 0
        # init with a basic config otherwise data polling is not working
        self.port_configs = {1: Config(1, Action.BALANCE, 6, 1.0, 0.5),
                             2: Config(2, Action.BALANCE, 6, 1.0, 0.5)}

    @property
    def read_errors(self):
        return self._read_errors

    @property
    def write_errors(self):
        return self._write_errors

    def connect(self):
        # try to find the device and connect to it
        dev = list(usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID, find_all=True))
        if not dev:
            raise ValueError('Device not found')
        # print(dev[0].interfaces())
        if len(dev) > self._device_index:
            i = dev[self._device_index][0].interfaces()[0].bInterfaceNumber
            if dev[self._device_index].is_kernel_driver_active(i):
                # try:
                dev[self._device_index].detach_kernel_driver(i)
                # except usb.core.USBError as e:
                #    raise Exception(f'Could not detach kernel driver from interface({i}): {e}')
                #    # sys.exit(
                #    #    f"Could not detach kernel driver from interface({i}): {e}")
            self.dev = dev[self._device_index]
            # print(f"serial: {self.dev.serial_number}")
            self._start_read_thread()
        else:
            raise ValueError('Device index out of range')

    def disconnect(self):
        # disconnect from the device
        self._stop_read_thread()
        try:
            self.dev.close()
        except Exception as e:
            print(f"Error: {e}")
        self.dev = None

    def _start_read_thread(self):
        if self.read_thread is None:
            self.stop_requested = False
            self.read_thread = threading.Thread(target=self._read_data_thread, daemon=True)
            self.read_thread.start()

    def _stop_read_thread(self):
        self.stop_requested = True
        self.read_thread = None

    def start_program(self, config: Config):
        # starts a program on a single port, specified by the config
        self.port_configs[config.port] = config
        cmd = get_cmd_start(config)
        self._write_data(cmd)

    def stop_program(self, port: int):
        # stops a program on a single port
        if port in [1, 2]:
            config = self.port_configs[port]
            cmd = get_cmd_stop(config)
            self._write_data(cmd)
            # self.port_configs[config.port] = None
        else:
            raise ValueError(f"Invalid channel: {port}")

    def poll_all_vals(self):
        # requests all battery values on both channels
        for config in self.port_configs.values():
            if config is not None:
                self.poll_vals(config)

    def poll_vals(self, config: Config):
        # requests battery values on a single port, specified by the config
        cmd = get_cmd_poll_vals(config)
        self._write_data(cmd)

    def poll_version(self):
        cmd = get_cmd_get_version()
        self._write_data(cmd)

    def poll_settings(self):
        cmd = get_cmd_get_settings()
        self._write_data(cmd)

    def _write_data(self, data):
        if self.dev is None:
            return None
        try:
            # print(f"write: {data.hex()}")
            res = self.dev.write(ENDPOINT_WRITE, data)
            return res
        except usb.core.USBError:
            # print(f"Error: {e}")
            self._write_errors += 1
        return None

    def _read_data(self, length):
        if self.dev is None:
            return None
        try:
            return self.dev.read(ENDPOINT_READ, length, timeout=1000)
        except usb.core.USBError:
            # print(f"Error: {e}")
            self._read_errors += 1
        return None

    def _read_data_thread(self):
        while not self.stop_requested:
            data = self._read_data(64)
            if data is not None and self._rec_data_callback is not None:
                vals = parse_data(data)
                if vals.data is not None:
                    # vals.data["device_index"] = self._device_index
                    vals.device_index = self._device_index
                self._rec_data_callback(vals)
            time.sleep(0.1)
