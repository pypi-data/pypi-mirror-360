from enum import Enum

from dataclasses import dataclass
from .checksum import calc_checksum, check_checksum

# command structure
# sync byte: 0x0f
# command, 2 bytes
# payload, n bytes
# checksum, 1 byte

# bytes
SYNC = 0x0f
CMD_START = [0x16, 0x05]
CMD_STOP = [0x03, 0xfe]
CMD_POLL_VALS = [0x03, 0x55]
CMD_GET_SETTINGS = [0x03, 0x5a]  # is requested periodically when idle
CMD_SET_SETTINGS = [0x0f, 0x11]
CMD_GET_VERSION = [0x03, 0x57]  # is requested once at startup
CMD_UNKNOWN0 = [0x03, 0x5f]  # is requested periodically when idle
CMD_GET_UNKNOWN1 = [0x03, 0x66]  # is sent on startup, but has no response


CMD_REPLY_VALS = [0x22, 0x55]
CMD_REPLY_VERSION = [0x14, 0x57]
CHD_REPLY_START_ACK = [0x04, 0x05]
CHD_REPLY_STOP_ACK = [0x04, 0xfe]
CMD_REPLY_SETTINGS = [0x25, 0x5a]
CMD_REPLY_SET_SETTINGS_ACK = [0x04, 0x11]
CMD_REPLY_UNKNOWN0 = [0x0c, 0x5f]  # regular when not charging, response to [0x03, 0x5f]


class CmdIn(Enum):
    VALUES = "values"
    VERSION = "version"
    START_ACK = "start_ack"
    STOP_ACK = "stop_ack"
    SETTINGS = "settings"
    SET_SETTINGS_ACK = "set_settings_ack"
    UNKNOWN0 = "unknown0"
    UNKNOWN = "unknown"

    @staticmethod
    def from_bytes(cmd_bytes: list[int]):
        if cmd_bytes == CMD_REPLY_VALS:
            return CmdIn.VALUES
        if cmd_bytes == CMD_REPLY_VERSION:
            return CmdIn.VERSION
        if cmd_bytes == CHD_REPLY_START_ACK:
            return CmdIn.START_ACK
        if cmd_bytes == CHD_REPLY_STOP_ACK:
            return CmdIn.STOP_ACK
        if cmd_bytes == CMD_REPLY_SETTINGS:
            return CmdIn.SETTINGS
        if cmd_bytes == CMD_REPLY_SET_SETTINGS_ACK:
            return CmdIn.SET_SETTINGS_ACK
        if cmd_bytes == CMD_REPLY_UNKNOWN0:
            return CmdIn.UNKNOWN0
        return CmdIn.UNKNOWN


class Status(Enum):
    ACTIVE = 1
    IDLE = 2
    ERROR = 4
    UNKNOWN = 77

    @classmethod
    def from_value(cls, value):
        try:
            return cls(value)
        except ValueError:
            return Status.UNKNOWN


class Ack(Enum):
    ERROR = 0
    OK = 1
    UNKNOWN = 77

    @classmethod
    def from_value(cls, value):
        try:
            return cls(value)
        except ValueError:
            return Ack.UNKNOWN


class Action(Enum):
    IDLE = 99
    IDLE_2 = 100
    BALANCE = 0
    CHARGE = 1
    DISCHARGE = 2
    STORAGE = 3
    PARALLEL = 6
    UNKNOWN = 77

    @staticmethod
    def from_str(label):
        if label.upper() == 'BALANCE':
            return Action.BALANCE
        if label.upper() == 'CHARGE':
            return Action.CHARGE
        if label.upper() == 'DISCHARGE':
            return Action.DISCHARGE
        if label.upper() == 'STORAGE':
            return Action.STORAGE
        if label.upper() == 'PARALLEL':
            return Action.PARALLEL
        return Action.UNKNOWN


@dataclass
class Config:
    port: int
    action: Action
    cells: int
    cur_in: float
    cur_out: float

    @property
    def min_volt(self):
        if self.action == Action.STORAGE:
            return 3.85
        else:
            return 3.3

    @property
    def max_volt(self):
        if self.action == Action.STORAGE:
            return 3.85
        else:
            return 4.2


@dataclass
class ChargerResponse:
    is_error: bool = False
    error_str: str = ""
    command: CmdIn = CmdIn.UNKNOWN
    data: dict = None
    device_index: int = 0


####################################
# get cmd
####################################

def get_cmd_start(config: Config):
    return _get_cmd_with_config(config, CMD_START, 0xff, 0)


def get_cmd_stop(config: Config):
    return _get_cmd_with_config(config, CMD_STOP, 0xfe, 8)


def get_cmd_poll_vals(config: Config):
    return _get_cmd_with_config(config, CMD_POLL_VALS, 0x55, 90)


def get_cmd_get_version():
    return _get_cmd(CMD_GET_VERSION, [0x01], 0)


def get_cmd_get_settings():
    return _get_cmd(CMD_GET_SETTINGS, [0x01], 0)


def _get_cmd_with_config(config: Config, cmd: list[int], byte4: int, checksum_add: int):
    if config.action == Action.IDLE:
        cmd = CMD_GET_SETTINGS
        cmd = [SYNC] + cmd + [config.port]
        return finalize_cmd(cmd, checksum_add=0)
    if config.action == Action.IDLE_2:
        cmd = CMD_UNKNOWN0
        cmd = [SYNC] + cmd + [config.port]
        return finalize_cmd(cmd, checksum_add=0)

    if config.action not in [Action.BALANCE, Action.CHARGE, Action.DISCHARGE, Action.STORAGE, Action.PARALLEL]:
        return None

    cur_charge_overflow_byte = 0x00
    cur_charge = int(config.cur_in * 10)
    if cur_charge >= 256:
        cur_charge -= 256
        cur_charge_overflow_byte = 0x01
    cur_discharge = int(config.cur_out * 10)

    min_volt_bytes = u16_to_bytes(int(config.min_volt * 1000))
    max_volt_bytes = u16_to_bytes(int(config.max_volt * 1000))

    # fix byte4
    byte4 = (byte4 + config.port) % 256
    payload = [
        config.port, byte4, config.cells, config.action.value, cur_charge, cur_discharge
    ] + min_volt_bytes + max_volt_bytes + [
        0x00, 0x00, 0x00, 0x00,
        cur_charge_overflow_byte, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    return _get_cmd(cmd, payload, checksum_add=checksum_add)


def _get_cmd(cmd: list[int], payload: list[int], checksum_add: int):
    cmd = [SYNC] + cmd + payload
    return finalize_cmd(cmd, checksum_add=checksum_add)


def finalize_cmd(cmd: list[int], checksum_add: int = 0) -> bytes:
    cmd.append((calc_checksum(cmd) + checksum_add) % 256)
    while len(cmd) < 64:
        cmd.append(0x00)
    return bytes(cmd)


####################################
# parse commands
####################################

def parse_data(data):
    if len(data) <= 0:
        return ChargerResponse(is_error=True, error_str="empty data")
    if data[0] == SYNC:
        cmd_bytes = list(data[1:3])
        cmd = CmdIn.from_bytes(cmd_bytes)
        if cmd == CmdIn.VALUES:
            # battery values
            data = data[0:36]
            res = check_checksum(data)
            if not res:
                # print("checksum failed")
                return ChargerResponse(is_error=True, error_str="invalid checksum", command=cmd)
            values = {
                'port': data[3],
                'status': Status.from_value(data[4]),
                'charge_total': bytes_to_u16(data[5], data[6]) / 1000,  # Ah
                'time': bytes_to_u16(data[7], data[8]),  # s
                'volt_total': bytes_to_u16(data[9], data[10]) / 1000,  # V
                'current': bytes_to_u16(data[11], data[12]) / 1000,  # A
                # '?_13': data[13],  # 0: default, 122: (saw this once on error with wireshark, but not with py)
                'system_temp': data[14],  # ? system temperature in C
                # '?_15': data[15],  # ? const 0, probably temp port A in C
                # '?_16': data[16],  # ? const 0, probably temp port B in C
                'volt_0': bytes_to_u16(data[17], data[18]) / 1000,  # V
                'volt_1': bytes_to_u16(data[19], data[20]) / 1000,  # V
                'volt_2': bytes_to_u16(data[21], data[22]) / 1000,  # V
                'volt_3': bytes_to_u16(data[23], data[24]) / 1000,  # V
                'volt_4': bytes_to_u16(data[25], data[26]) / 1000,  # V
                'volt_5': bytes_to_u16(data[27], data[28]) / 1000,  # V
                # '?_29': data[29],  # ? const 0
                # '?_39': data[30],  # ? const 0
                # '?_31': data[31],  # ? const 0
                # '?_32': data[32],  # ? const 0
                # '?_33': data[33],  # ? const 1
                '?_34': data[34],  # 0: after charge?, 2: default
                'checksum': data[35],
            }
            # print(values)
            return ChargerResponse(data=values, command=cmd)
        if cmd == CmdIn.VERSION:
            data = data[0:36]
            res = check_checksum(data)
            # print(f"checksum: {calc_checksum(data[:-1])}, expected: {data[-1]}")
            # if not res:
            #    print("checksum failed")
            #    return None
            values = {
                'sn': ''.join(f'{x:02x}' for x in data[5:21]),
                'version': f'{data[16]}.{data[17]}'
            }
            return ChargerResponse(data=values, command=cmd)
        if cmd == CmdIn.START_ACK:
            values = {
                # '?_3': data[3],  # const 0?
                'res': Ack.from_value(data[4])  # 1: ok, 0: error
            }
            return ChargerResponse(data=values, command=cmd)
        if cmd == CmdIn.STOP_ACK:
            values = {
                # '?_3': data[3],  # const 0?
                'res': Ack.from_value(data[4])  # 1: ok, 0: error
            }
            return ChargerResponse(data=values, command=cmd)
        if cmd == CmdIn.SETTINGS:
            data = data[0:39]
            values = {
                # '?_3': data[3],
                'charge_discharge_pause': data[4],  # min
                'time_limit_enable': data[5],  # 0: off, 1: on
                'time_limit': bytes_to_u16(data[6], data[7]),  # min
                'cap_limit_enable': data[8],  # 0: off, 1: on
                'cap_limit': bytes_to_u16(data[9], data[10]),  # mAh
                'key_buzzer': data[11],  # 0: off, 1: on
                'system_buzzer': data[12],  # 0: off, 1: on
                'low_dc_input_cut_off': bytes_to_u16(data[13], data[14]) / 1000,  # V
                # '?_15': data[15],
                # '?_16': data[16],
                # '?_15_16': bytes_to_u16(data[15], data[16]),
                'temp_limit': data[17],  # C
            }
            return ChargerResponse(data=values, command=cmd)
        # if cmd_bytes == CMD_REPLY_UNKNOWN0:
        #    return Response(is_error=True, error_str="no parser implemented", command=cmd)
        else:
            return ChargerResponse(is_error=True, error_str="no parser implemented", command=cmd)
    return ChargerResponse(is_error=True, error_str="out of sync")


####################################
# utils
####################################

def bytes_to_u16(b1, b2):
    return (b1 << 8) | b2


def u16_to_bytes(val):
    return [(val >> 8) & 0xFF, val & 0xFF]


if __name__ == "__main__":
    print(get_cmd_poll_vals(Config(1, Action.IDLE, 6, 1.0, 0.5)).hex())
    print(get_cmd_start(Config(1, Action.BALANCE, 6, 1.0, 0.5)).hex())
    print(get_cmd_stop(Config(1, Action.BALANCE, 6, 1.0, 0.5)).hex())
    print(get_cmd_poll_vals(Config(1, Action.BALANCE, 6, 1.0, 0.5)).hex())
