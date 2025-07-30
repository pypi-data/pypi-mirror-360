from enum import Enum, unique

from .. import utils


@unique
class LTMode4Command(Enum):
    """
    LTMode4 Command Enum
    """
    LOWEST = [0x40]
    SET_STATE_REQ = [0x42]
    SET_STATE_RES = [0x43]
    GET_STATE_REQ = [0x44]
    GET_STATE_RES = [0x45]
    CLEAR_PREV_ST_EVT_REQ = [0x48]
    CLEAR_PREV_ST_EVT_RES = [0x49]
    GET_PREV_ST_EVT_REQ = [0x4A]
    GET_PREV_ST_EVT_RES = [0x4B]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class LTMode4Status(Enum):
    """
    LTMode4 status Enum
    """
    LOWEST = [0x40]
    OK = [0x41]
    ERR_ARGS = [0x42]
    ERR_NOT_CHKD = [0xFF]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class LTMode4State(Enum):
    """
    LTMode4 status Enum
    """
    STANDBY = [0x0]
    CONFIGURED = [0x1]
    LOG_ON = [0x2]
    LOG_OFF = [0x3]
    FS_MEMORY_FULL = [0x4]
    FS_MAX_FILE_COUNT = [0x5]
    SHIPMENT_MODE = [0x6]
    LOG_OFF_TOOL_CONNECTED = [0x7]
    LOG_DOWNLOAD = [0x8]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class LTMode4Event(Enum):
    """
    LTMode4 event Enum
    """
    NO_EVENT = [0x0]
    WATCH_OFF_CRADLE_NAV_BUTTON_RESET = [0x1]
    WATCH_ON_CRADLE_NAV_BUTTON_RESET = [0x2]
    WATCH_CHARGING_STARTED = [0x3]
    WATCH_CHARGING_STOPPED_MEMORY_FULL = [0x4]
    WATCH_CHARGING_STOPPED_MAXIMUM_FILE_COUNT = [0x5]
    WATCH_CHARGING_STOPPED_MEMORY_OK = [0x6]
    FS_MEMORY_FULL = [0x7]
    FS_MAX_FILE_COUNT = [0x8]
    GET_VERSION_M2M2_CMD = [0x9]
    SHIPMENT_M2M2_CMD = [0xA]
    DELETE_LT_CONFIG_M2M2_CMD = [0xB]
    SET_STATE_M2M2_CMD = [0xC]
    WATCH_BOOT_NO_SOFT_RESET = [0xD]
    SYS_RST_M2M2_COMMAND = [0xE]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class LTMode4WatchResetReason(Enum):
    """
    LTMode4 Watch Reset Reason Enum
    """
    INVALID = [0x0]
    RST_PIN_RESET = [0x1]
    NRF_WDT_RESET = [0x2]
    SOFT_RESET = [0x4]
    CPU_LOCKUP = [0x8]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))
