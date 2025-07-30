# ******************************************************************************
# Copyright (c) 2019 Analog Devices, Inc.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# - Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
# - Modified versions of the software must be conspicuously marked as such.
# - This software is licensed solely and exclusively for use with
#  processors/products manufactured by or for Analog Devices, Inc.
# - This software may not be combined or merged with other code in any manner
#  that would cause the software to become subject to terms and conditions
#  which differ from those listed here.
# - Neither the name of Analog Devices, Inc. nor the names of its contributors
#  may be used to endorse or promote products derived from this software
#  without specific prior written permission.
# - The use of this software may or may not infringe the patent rights of one
#  or more patent holders.  This license does not release you from the
#  requirement that you obtain separate licenses from these patent holders to
#  use this software.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES, INC. AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# NONINFRINGEMENT, TITLE, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL ANALOG DEVICES, INC. OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, DAMAGES ARISING OUT OF
# CLAIMS OF INTELLECTUAL PROPERTY RIGHTS INFRINGEMENT; PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ******************************************************************************

from enum import Enum, unique

from .adp5360_enums import ADP5360Command
from .sensorhub_enums import SHCommand
from .lt_mode4_enums import LTMode4Command, LTMode4Status
from .. import utils
from .bia_enums import BIACommand
from .ecg_enums import ECGCommand
from .eda_enums import EDACommand
from .sensorhub_enums import SHCommand
from .low_touch_enum import LTCommand
from .ad7156_enums import AD7156Command
from .fs_enums import FSCommand, FSStatus
from .display_enums import DisplayCommand
from .dcb_enums import DCBCommand, DCBStatus
from .user0_enums import User0Command, User0Status
from .pm_enums import PMCommand, PMStatus, UICRCustomerRegisterAccessStatus
from .session_manager_enums import SessionManagerStatus, SessionManagerCommand
from .low_touch_enum import LTStatus

def get_command(command, source):
    """
    Helper method for decoding commands.
    """
    if command[0] < CommonCommand.HIGHEST.value[0]:
        return CommonCommand
    elif command in [DCBCommand.READ_CONFIG_RES.value, DCBCommand.WRITE_CONFIG_RES.value,
                     DCBCommand.ERASE_CONFIG_RES.value, DCBCommand.QUERY_STATUS_RES.value]:
        return DCBCommand
    elif source == Application.PM:
        return PMCommand
    elif source == Application.ADP5360:
        return ADP5360Command
    elif source == Application.FS or source == Stream.FS:
        return FSCommand
    elif source == Application.DISPLAY:
        return DisplayCommand
    elif source == Application.AD7156:
        return AD7156Command
    elif source == Application.BIA:
        return BIACommand
    elif source == Application.EDA:
        return EDACommand
    elif source == Application.LT_APP:
        return LTCommand
    elif source == Application.ECG:
        return ECGCommand
    elif source == Application.USER0_APP:
        return User0Command
    elif source == Application.SENSORHUB:
        return SHCommand
    elif source == Application.SESSION_MANAGER_APP:
        return SessionManagerCommand
    elif source == Application.LT_MODE4_APP:
        return LTMode4Command
    else:
        return CommonCommand


def get_status(status, source, command):
    """
    Helper method for decoding status.
    """
    if command[0] == CommonCommand.ALARM_NOTIFICATION.value[0]:
        return AlarmStatus
    elif command in [PMCommand.WRITE_UICR_CUSTOMER_REG_RES.value, PMCommand.READ_UICR_CUSTOMER_REG_RES.value]:
        return UICRCustomerRegisterAccessStatus
    elif status[0] < CommonStatus.HIGHEST.value[0]:
        return CommonStatus
    elif command in [DCBCommand.READ_CONFIG_RES.value, DCBCommand.WRITE_CONFIG_RES.value,
                     DCBCommand.ERASE_CONFIG_RES.value]:
        return DCBStatus
    elif (source == Application.SENSORHUB) and command in [SHCommand.READ_MAX86178_DCB_RESP.value,
                     SHCommand.WRITE_MAX86178_DCB_RESP.value, SHCommand.ERASE_MAX86178_DCB_RESP.value,
                     SHCommand.READ_ADXL367_DCB_RESP.value, SHCommand.WRITE_ADXL367_DCB_RESP.value,
                     SHCommand.ERASE_ADXL367_DCB_RESP.value]:
        return DCBStatus
    elif source == Application.PM:
        return PMStatus
    elif source == Application.USER0_APP:
        return User0Status
    elif source == Application.LT_MODE4_APP:
        return LTMode4Status
    elif source == Application.FS or source == Stream.FS:
        return FSStatus
    elif source == Application.SESSION_MANAGER_APP:
        return SessionManagerStatus
    elif source == Application.LT_APP:
        return LTStatus
    else:
        return CommonStatus


@unique
class CommonCommand(Enum):
    """
    CommonCommand Enum
    """
    NO_RESPONSE = [-1]
    GET_VERSION_REQ = [0x0]
    GET_VERSION_RES = [0x1]
    START_SENSOR_REQ = [0x4]
    START_SENSOR_RES = [0x5]
    STOP_SENSOR_REQ = [0x6]
    STOP_SENSOR_RES = [0x7]
    SUBSCRIBE_STREAM_REQ = [0xC]
    SUBSCRIBE_STREAM_RES = [0xD]
    UNSUBSCRIBE_STREAM_REQ = [0xE]
    UNSUBSCRIBE_STREAM_RES = [0xF]
    GET_SENSOR_STATUS_REQ = [0x10]
    GET_SENSOR_STATUS_RES = [0x11]
    GET_LCFG_REQ = [0x12]
    GET_LCFG_RES = [0x13]
    SET_LCFG_REQ = [0x14]
    SET_LCFG_RES = [0x15]
    READ_LCFG_REQ = [0x16]
    READ_LCFG_RES = [0x17]
    WRITE_LCFG_REQ = [0x18]
    WRITE_LCFG_RES = [0x19]
    PING_REQ = [0x1A]
    PING_RES = [0x1B]
    ALARM_NOTIFICATION = [0x1C]
    REGISTER_READ_REQ = [0x21]
    REGISTER_READ_RES = [0x22]
    REGISTER_WRITE_REQ = [0x23]
    REGISTER_WRITE_RES = [0x24]
    GET_DCFG_REQ = [0x25]
    GET_DCFG_RES = [0x26]
    STREAM_DATA = [0x28]
    GET_STREAM_DEC_FACTOR_REQ = [0x29]
    GET_STREAM_DEC_FACTOR_RES = [0x2A]
    SET_STREAM_DEC_FACTOR_REQ = [0x2B]
    SET_STREAM_DEC_FACTOR_RES = [0x2C]
    REGISTER_READ_32_REQ = [0x2D]
    REGISTER_READ_32_RES = [0x2E]
    REGISTER_WRITE_32_REQ = [0x2F]
    REGISTER_WRITE_32_RES = [0x30]
    HIGHEST = [0x40]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class CommonStatus(Enum):
    """
    CommonStatus Enum
    """
    NO_RESPONSE = [-1]
    OK = [0x0]
    ERROR = [0x1]
    STREAM_STARTED = [0x2]
    STREAM_STOPPED = [0x3]
    STREAM_IN_PROGRESS = [0x4]
    STREAM_DEACTIVATED = [0x5]
    STREAM_COUNT_DECREMENT = [0x6]
    STREAM_NOT_STARTED = [0x7]
    STREAM_NOT_STOPPED = [0x8]
    SUBSCRIBER_ADDED = [0x9]
    SUBSCRIBER_REMOVED = [0xA]
    SUBSCRIBER_COUNT_DECREMENT = [0xB]
    STREAM_NOT_STARTED_BATTERY_LOW = [0xC]
    SUBSCRIBER_NOT_ADDED_BATTERY_LOW = [0xD]
    DOWNLOAD_IN_PROGRESS = [0xE]
    DOWNLOAD_COMPLETE = [0xF]
    DOWNLOAD_ERROR = [0x10]
    DOWNLOAD_CHECKSUM_ERROR = [0x11]
    HIGHEST = [0x20]
    NEW_STREAM_STATUS = [0x43]  # some stream such as EDA has 0x43 as status instead of 0x0

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class Stream(Enum):
    """
    Stream Enum
    """
    NULL = [0x00, 0x00]
    ADPD1 = [0xc2, 0x11]
    ADPD2 = [0xc2, 0x12]
    ADPD3 = [0xc2, 0x13]
    ADPD4 = [0xc2, 0x14]
    ADPD5 = [0xc2, 0x15]
    ADPD6 = [0xc2, 0x16]
    ADPD7 = [0xc2, 0x17]
    ADPD8 = [0xc2, 0x18]
    ADPD9 = [0xc2, 0x19]
    ADPD10 = [0xc2, 0x1a]
    ADPD11 = [0xc2, 0x1b]
    ADPD12 = [0xc2, 0x1c]
    ADXL = [0xc2, 0x02]
    BIA = [0xC4, 0x07]
    BCM = [0xC8, 0x14]
    ECG = [0xc4, 0x01]
    EDA = [0xc4, 0x02]
    FS = [0xC6, 0x01]
    PEDOMETER = [0xc4, 0x04]
    PPG = [0xC4, 0x00]
    # TEMPERATURE = [0xc4, 0x06]
    SYNC_PPG = [0xC4, 0x05]
    SQI = [0xC8, 0x0D]
    BATTERY = [0xC6, 0x91]
    DYNAMIC_AGC_STREAM = [0xC6, 0xB0]
    STATIC_AGC_STREAM = [0xC6, 0xB1]
    HRV = [0xC6, 0xC0]
    AD7156 = [0xC8, 0x15]
    TEMPERATURE1 = [0xC8, 0x16]
    TEMPERATURE2 = [0xC8, 0x17]
    TEMPERATURE3 = [0xC8, 0x18]  # C
    TEMPERATURE4 = [0xC4, 0x06]  # D
    TEMPERATURE5 = [0xC8, 0x1A]
    TEMPERATURE6 = [0xC8, 0x1B]
    TEMPERATURE7 = [0xC8, 0x1C]
    TEMPERATURE8 = [0xC8, 0x1D]
    TEMPERATURE9 = [0xC8, 0x1E]
    TEMPERATURE10 = [0xC8, 0x1F]  # J
    TEMPERATURE11 = [0xC8, 0x20]  # K
    TEMPERATURE12 = [0xC8, 0x21]  # L
    SENSORHUB_MAX86178_STREAM1 = [0xC8, 0x2A]
    SENSORHUB_MAX86178_STREAM2 = [0xC8, 0x2B]
    SENSORHUB_MAX86178_STREAM3 = [0xC8, 0x2C]
    SENSORHUB_MAX86178_STREAM4 = [0xC8, 0x2D]
    SENSORHUB_MAX86178_STREAM5 = [0xC8, 0x2E]
    SENSORHUB_MAX86178_STREAM6 = [0xC8, 0x2F]
    SENSORHUB_SPO2_STREAM = [0xC8, 0x30]
    SENSORHUB_HRM_STREAM = [0xC8, 0x31]
    SENSORHUB_ADXL367_STREAM = [0xC8, 0x32]
    SENSORHUB_REG_CONF_STREAM = [0xC8, 0x33]
    SENSORHUB_RR_STREAM = [0xC8, 0x34]
    SENSORHUB_MAX86178_ECG_STREAM = [0xC8, 0x35]
    SENSORHUB_MAX86178_BIOZ_STREAM = [0xC8, 0x36]
    SENSORHUB_AMA_STREAM = [0xC8, 0x37]
    SENSORHUB_PR_STREAM = [0xC8, 0x38]
    SENSORHUB_SPO2_DEBUG_STREAM = [0xC8, 0x39]
    SENSORHUB_DEBUG_REG_CONF_STREAM = [0xC8, 0x3A]
    MAX30208_TEMPERATURE_STREAM = [0xC8, 0x41]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class Application(Enum):
    """
    Application Enum.
    """
    POST_OFFICE = [0xC0, 0x0]
    EXTERNAL = [0xC0, 0x01]
    ADXL = [0xc1, 0x02]
    ADP5360 = [0xc1, 0x06]
    ADPD = [0xc1, 0x10]
    PPG = [0xC3, 0x00]
    ECG = [0xc3, 0x01]
    EDA = [0xc3, 0x02]
    PEDOMETER = [0xc3, 0x04]
    TEMPERATURE = [0xc3, 0x06]
    BIA = [0xC3, 0x07]
    FS = [0xC5, 0x01]
    PS = [0xc5, 0x80]
    PM = [0xc5, 0x00]
    DISPLAY = [0xC5, 0x03]
    APP_ANDROID = [0xC7, 0x0]
    APP_IOS = [0xC7, 0x1]
    APP_VS = [0xC7, 0x2]
    APP_WT = [0xC7, 0x3]
    APP_NFE = [0xC7, 0x4]
    APP_USB = [0xc7, 0x05]
    SQI = [0xC8, 0x0C]
    AD7156 = [0xC8, 0x0B]
    APP_BLE = [0xC8, 0x08]
    LT_APP = [0xC8, 0x0A]
    USER0_APP = [0xC8, 0x0F]
    LT_MODE4_APP = [0xC8, 0x24]
    SESSION_MANAGER_APP = [0xC8, 0x25]
    SENSORHUB = [0xC8, 0x27]
    SENSORHUB_MAX86178 = [0xC8, 0x28]
    SENSORHUB_ADXL367 = [0xC8, 0x29]
    MAX30208 = [0xC8, 0x40]
    NULL = [0x0, 0x0]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class AlarmStatus(Enum):
    BATTERY_LEVEL_LOW = [0x0]
    BATTERY_LEVEL_CRITICAL = [0x1]
    BATTERY_LEVEL_FULL = [0x2]
    NAND_LT_CONFIG_LOG_ENABLED = [0x3]
    ENABLE_NAND_LT_CONFIG_LOG_FAILED = [0x4]
    NAND_LT_CONFIG_LOG_DISABLED = [0x5]
    DISABLE_NAND_LT_CONFIG_LOG_FAILED = [0x6]
    DCB_LT_CONFIG_LOG_ENABLED = [0x7]
    ENABLE_DCB_LT_CONFIG_LOG_FAILED = [0x8]
    DCB_LT_CONFIG_LOG_DISABLED = [0x9]
    DISABLE_DCB_LT_CONFIG_LOG_FAILED = [0xA]
    LOW_TOUCH_LOGGING_ALREADY_STARTED = [0xB]
    LT_CONFIG_FILE_NOT_FOUND = [0xC]
    LT_CONFIG_FILE_READ_ERR = [0xD]
    LOW_TOUCH_MEMORY_FULL_ERR = [0xE]
    LOW_TOUCH_MAX_FILE_ERR = [0xF]
    FS_MEMORY_FULL = [0x10]
    FS_LOG_STOP_BATTERY_LOW = [0x11]
    FS_LOG_DOWNLOAD_STOP_BATTERY_CRITICAL = [0x12]
    FS_PWR_STATE_SHUTDOWN = [0x13]
    BLE_PKT_MISS = [0x14]
    FS_FILE_CLOSE_ERROR = [0x15]
    FS_FILE_WRITE_ERROR = [0x16]
    LT_LCFG_DCB_READ_ERROR = [0x17]
    USER0_LCFG_DCB_READ_ERROR = [0x18]
    ADPD_CONT_SATURATION_DETECTED = [0x19]
    ECG_LEADS_OFF_DETECTED = [0x1A]
    ECG_LEADS_ON_DETECTED = [0x1B]
    CHARGER_OFF_DETECTED = [0x1C]
    CHARGER_ON_DETECTED = [0x1D]
    NO_ALARM  = [0x1E]
    MAX86178_ECG_LEADS_OFF_DETECTED = [0x1F]
    MAX86178_ECG_LEADS_ON_DETECTED = [0x20]
    MAX86178_PPG_INVALID_CONFIG = [0x21]
    MAX86178_REG_WRITE_JITTER = [0x22]
    HIGHEST = [0x23]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))
