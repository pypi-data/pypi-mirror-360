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

from enum import unique, Enum

from .. import utils


@unique
class PMCommand(Enum):
    """
    PMCommand Enum
    """
    LOWEST = [0x40]
    SET_DATE_TIME_REQ = [0x42]
    SET_DATE_TIME_RES = [0x43]
    GET_BAT_INFO_REQ = [0x44]
    GET_BAT_INFO_RES = [0x45]
    SET_BAT_THR_REQ = [0x46]
    SET_BAT_THR_RES = [0x47]
    SET_POWER_STATE_REQ = [0x48]
    SET_POWER_STATE_RES = [0x49]
    SYS_INFO_REQ = [0x4A]
    SYS_INFO_RES = [0x4B]
    ENABLE_BAT_CHARGE_REQ = [0x4C]
    ENABLE_BAT_CHARGE_RES = [0x4D]
    DISABLE_BAT_CHARGE_REQ = [0x4E]
    DISABLE_BAT_CHARGE_RES = [0x4F]
    GET_DATE_TIME_REQ = [0x52]
    GET_DATE_TIME_RES = [0x53]
    GET_MCU_VERSION_REQ = [0x58]
    GET_MCU_VERSION_RES = [0x59]
    WRITE_EEPROM_REQ = [0x68]
    WRITE_EEPROM_RES = [0x69]
    READ_EEPROM_REQ = [0x6A]
    READ_EEPROM_RES = [0x6B]
    SYSTEM_RESET_REQ = [0x76]
    SYSTEM_RESET_RES = [0x77]
    SW_CONTROL_REQ = [0x78]
    SW_CONTROL_RES = [0x79]
    LDO_CONTROL_REQ = [0x7A]
    LDO_CONTROL_RES = [0x7B]
    CHIP_ID_REQ = [0x7C]
    CHIP_ID_RES = [0x7D]
    CAP_SENSE_TEST_REQ = [0x7E]
    CAP_SENSE_TEST_RES = [0x7F]
    ENTER_BOOTLOADER_REQ = [0x80]
    ENTER_BOOTLOADER_RES = [0x81]
    CAP_SENSE_STREAM_DATA = [0x82]
    FLASH_RESET_REQ = [0x8A]
    FLASH_RESET_RES = [0x8B]
    SYSTEM_HW_RESET_REQ = [0x8C]
    SYSTEM_HW_RESET_RES = [0x8D]
    GET_APPS_HEALTH_REQ = [0x90]
    GET_APPS_HEALTH_RES = [0x91]
    SET_MANUFACTURE_DATE_REQ = [0x96]
    SET_MANUFACTURE_DATE_RES = [0x97]
    GET_MANUFACTURE_DATE_REQ = [0x98]
    GET_MANUFACTURE_DATE_RES = [0x99]
    GET_HIBERNATE_MODE_STATUS_REQ = [0x9A]
    GET_HIBERNATE_MODE_STATUS_RES = [0x9B]
    SET_HIBERNATE_MODE_STATUS_REQ = [0x9C]
    SET_HIBERNATE_MODE_STATUS_RES = [0x9D]
    BATTERY_LEVEL_ALERT = [0x9E]
    GET_PO_MEMORY_UTILIZATION_REQ = [0x9F]
    GET_PO_MEMORY_UTILIZATION_RES = [0xA0]
    CLEAR_PO_MEMORY_UTILIZATION_REQ = [0xA1]
    CLEAR_PO_MEMORY_UTILIZATION_RES = [0xA2]
    WRITE_UICR_CUSTOMER_REG_REQ = [0xA3]
    WRITE_UICR_CUSTOMER_REG_RES = [0xA4]
    READ_UICR_CUSTOMER_REG_REQ = [0xA5]
    READ_UICR_CUSTOMER_REG_RES = [0xA6]
    SYNC_TIMER_START_STOP_REQ = [0xA7]
    SYNC_TIMER_START_STOP_RES = [0xA8]
    SYNC_TIMER_ENABLE_REQ = [0xA9]
    SYNC_TIMER_ENABLE_RES = [0xAA]
    SET_TOP_TOUCH_CONTROL_REQ = [0xAB]
    SET_TOP_TOUCH_CONTROL_RES = [0xAC]
    GET_TOP_TOUCH_CONTROL_REQ = [0xAD]
    GET_TOP_TOUCH_CONTROL_RES = [0xAE]
    LOAD_CFG_REQ = [0xAF]
    LOAD_CFG_RES = [0xB0]
    FDS_ERASE_REQ = [0xB1]
    FDS_ERASE_RES = [0xB2]
    GET_CONNECTED_TOOL_ADDR_REQ = [0xB3]
    GET_CONNECTED_TOOL_ADDR_RES = [0xB4]
    GET_BOOTLOADER_VERSION_REQ = [0xB5]
    GET_BOOTLOADER_VERSION_RES = [0xB6]
    LDO_STATUS_CHECK_REQ = [0xB7]
    LDO_STATUS_CHECK_RES = [0xB8]
    DG2502_SW_STATUS_REQ = [0xB9]
    DG2502_SW_STATUS_RES = [0xBA]
    GET_BLE_STATUS_REQ = [0xBB]
    GET_BLE_STATUS_RES = [0xBC]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class PMStatus(Enum):
    """
    PMStatus Enum
    """
    FIX_STATUS = [0x0]
    LOWEST = [0x40]
    OK = [0x41]
    ERR_ARGS = [0x42]
    ERR_RESET = [0x4F]
    BATTERY_LEVEL_LOW = [0x54]
    BATTERY_LEVEL_CRITICAL = [0x55]
    BATTERY_LEVEL_FULL = [0x56]
    TOP_TOUCH_CONTROL_FAILED = [0x57]
    CHIP_ID_ERR = [0x58]
    ERR_NOT_CHKD = [0xFF]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class MCUType(Enum):
    """
    MCUType Enum
    """
    MCU_INVALID = [0x0]
    MCU_M3 = [0x1]
    MCU_M4 = [0x2]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class ElectrodeSwitch(Enum):
    """
    ElectrodeSwitch Enum
    """
    AD8233 = [0x0]
    AD5940 = [0x1]
    ADPD4000 = [0x2]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class LDO(Enum):
    """
    LDO Enum
    """
    FS = [0x1]
    OPTICAL = [0x2]
    EPHYZ = [0x3]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class ControlStatus(Enum):
    ENABLE = [0x1]
    DISABLE = [0x0]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class ChipID(Enum):
    """
    ChipID Enum
    """
    ADXL362 = [0x1]
    ADPD4K = [0x2]
    ADP5360 = [0x3]
    AD5940 = [0x4]
    NAND_FLASH = [0x5]
    AD7156 = [0x6]
    MAX30208 = [0x7]
    SH_MAX86178 = [0x8]
    SH_ADXL367 = [0x9]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class PowerMode(Enum):
    """
    PowerMode Enum
    """
    ACTIVE = [0x0]
    HIBERNATE = [0x2]
    SHUTDOWN = [0x3]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class UICRCustomerRegisterAccessStatus(Enum):
    OK = [0x0]
    ERROR = [0x1]
    ERROR_NULL_PTR = [0x2]
    ERROR_LOGGING_IN_PROGRESS = [0x3]
    ERROR_LOW_BATTERY = [0x4]
    ERROR_ALREADY_WRITTEN = [0x5]
    ERROR_NOTHING_WRITTEN = [0x6]
    ERROR_ARGS = [0x7]
    ERROR_CRC_MISMATCH = [0x8]
