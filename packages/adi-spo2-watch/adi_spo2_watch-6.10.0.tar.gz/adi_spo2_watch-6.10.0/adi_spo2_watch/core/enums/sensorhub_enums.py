# ******************************************************************************
# Copyright (c) 2023 Analog Devices, Inc.  All rights reserved.
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

from .. import utils

@unique
class SHCommand(Enum):
    """
        SensorHubCommand Enum
    """
    CONFIG_OP_MODE_REQ = [0x42]
    CONFIG_OP_MODE_RESP = [0x43]
    BL_GET_OP_MODE_REQ = [0x44]
    BL_GET_OP_MODE_RESP = [0x45]
    BL_SET_MODE_REQ = [0x46]
    BL_SET_MODE_RESP = [0x47]
    BL_SET_NUM_PAGE_REQ = [0x48]
    BL_SET_NUM_PAGE_RESP = [0x49]
    BL_SET_IV_REQ = [0x4A]
    BL_SET_IV_RESP = [0x4B]
    BL_SET_AUTH_REQ = [0x4C]
    BL_SET_AUTH_RESP = [0x4D]
    BL_GET_PAGE_SZ_REQ = [0x4E]
    BL_GET_PAGE_SZ_RESP = [0x4F]
    BL_ERASE_FLASH_REQ = [0x50]
    BL_ERASE_FLASH_RESP = [0x51]
    DOWNLOAD_PAGE_INIT_REQ = [0x52]
    DOWNLOAD_PAGE_INIT_RESP = [0x53]
    DOWNLOAD_PAGE_START_REQ = [0x54]
    DOWNLOAD_PAGE_START_RESP = [0x55]
    BL_GET_TEST_DATA_REQ = [0x56]
    BL_GET_TEST_DATA_RESP = [0x57]
    BL_EXIT_MODE_REQ = [0x58]
    BL_EXIT_MODE_RESP = [0x59]
    SET_FS_REQ = [0x5A]
    SET_FS_RESP = [0x5B]
    ADXL367_SELF_TEST_REQ = [0x5C]
    ADXL367_SELF_TEST_RESP = [0x5D]
    FIRMWARE_VERSION_REQ = [0x5E]
    FIRMWARE_VERSION_RESP = [0x5F]
    MAX86178_READ_REG_REQ =  [0x60]
    MAX86178_READ_REG_RESP =  [0x61]
    MAX86178_WRITE_REG_REQ =  [0x62]
    MAX86178_WRITE_REG_RESP =  [0x63]
    ADXL367_READ_REG_REQ =  [0x64]
    ADXL367_READ_REG_RESP =  [0x65]
    ADXL367_WRITE_REG_REQ =  [0x66]
    ADXL367_WRITE_REG_RESP =  [0x67]
    LOAD_MAX86178_CFG_REQ = [0X68]
    LOAD_MAX86178_CFG_RESP = [0X69]
    LOAD_ADXL367_CFG_REQ = [0X6A]
    LOAD_ADXL367_CFG_RESP = [0X6B]
    READ_MAX86178_DCB_REQ = [0x6C]
    READ_MAX86178_DCB_RESP = [0x6D]
    WRITE_MAX86178_DCB_REQ = [0x6E]
    WRITE_MAX86178_DCB_RESP = [0x6F]
    ERASE_MAX86178_DCB_REQ = [0x70]
    ERASE_MAX86178_DCB_RESP = [0x71]
    READ_ADXL367_DCB_REQ = [0x72]
    READ_ADXL367_DCB_RESP = [0x73]
    WRITE_ADXL367_DCB_REQ = [0x74]
    WRITE_ADXL367_DCB_RESP = [0x75]
    ERASE_ADXL367_DCB_REQ = [0x76]
    ERASE_ADXL367_DCB_RESP = [0x77]
    ALGO_VERSION_REQ = [0x78]
    ALGO_VERSION_RESP = [0x79]
    GET_ADXL367_G_CALIBRATION_EN_REQ = [0x7A]
    GET_ADXL367_G_CALIBRATION_EN_RESP = [0x7B]
    SET_ADXL367_G_CALIBRATION_EN_REQ = [0x7C]
    SET_ADXL367_G_CALIBRATION_EN_RESP = [0x7D]
    GET_ADXL367_G_CALIBRATION_REQ = [0x7E]
    GET_ADXL367_G_CALIBRATION_RESP = [0x7F]
    SET_ADXL367_G_CALIBRATION_REQ = [0x80]
    SET_ADXL367_G_CALIBRATION_RESP = [0x81]
    HARD_RESET_REQ = [0x82]
    HARD_RESET_RESP = [0x83]
    SH_REG_DUMP_REQ = [0x84]
    SH_REG_DUMP_RESP = [0x85]
    GET_FS_REQ = [0x86]
    GET_FS_RESP = [0x87]
    ENABLE_MAX86178_ECG_PACKETIZATION_REQ = [0x88]
    ENABLE_MAX86178_ECG_PACKETIZATION_RESP = [0x89]
    AEC_VERSION_REQ = [0x8A]
    AEC_VERSION_RESP = [0x8B]
    LP_SELF_TEST_REQ = [0x8C]
    LP_SELF_TEST_RESP = [0x8D]
    SET_DECIMATION_REQ = [0x8E]
    SET_DECIMATION_RESP = [0x8F]
    GET_DECIMATION_REQ = [0x90]
    GET_DECIMATION_RESP = [0x91]
    SET_LP_MODE2_REQ = [0x92]
    SET_LP_MODE2_RESP = [0x93]
    GET_LP_MODE2_REQ = [0x94]
    GET_LP_MODE2_RESP = [0x95]
    GET_MAX86178_DCFG_REQ = [0x96]
    GET_MAX86178_DCFG_RESP = [0x97]
    GET_ADXL367_DCFG_REQ = [0x98]
    GET_ADXL367_DCFG_RESP = [0x99]
    EN_MOTION_ACTIVATED_WAKEUP_REQ = [0x9A]
    EN_MOTION_ACTIVATED_WAKEUP_RESP = [0x9B]
    EN_DEBUG_REG_CFG_REQ = [0x9C]
    EN_DEBUG_REG_CFG_RESP = [0x9D]
    SET_SPO2_COEFF_REQ = [0x9E]
    SET_SPO2_COEFF_RESP = [0x9F]
    GET_SPO2_COEFF_REQ = [0xA0]
    GET_SPO2_COEFF_RESP = [0xA1]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))

class SHDevice(Enum):
    """
        SensorHubDevice Enum
    """
    MAX86178_DEVICE = [0x01]
    ADXL367_DEVICE = [0x02]
    SENSORHUB_DEVICE = [0x03]
    MAX86178_ECG_DEVICE = [0x04]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))

class SHSlotMode(Enum):
    """
        SensorHubSlotMode Enum
    """
    SLOTMODE_DISABLED = [0x0]
    SLOTMODE_2CH_G = [0x1]
    SLOTMODE_2CH_R_IR = [0x2]
    SLOTMODE_2CH_G_R_IR = [0x3]
    SLOTMODE_RAW_PPG_ADXL = [0x4]  # 2-GREEN, RED, IR, ADXL
    SLOTMODE_ADXL = [0x5]
    SLOTMODE_SPO2 = [0x6]
    SLOTMODE_HRM = [0x7]
    SLOTMODE_SPO2_HRM = [0x8]
    SLOTMODE_PPG_ADXL_SPO2_HRM = [0x9]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))

class SHMode(Enum):
    SENSORHUB_APPLICATION_MODE = [0x00]
    SENSORHUB_BOOTLOADER_MODE = [0x01]
    SENSORHUB_UNKNOWN_MODE = [0x02]
    SENSORHUB_ERROR_MODE = [0x03]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))

class SHConfigID(Enum):
    SENSORHUB_RAW_MODE = [0x00]
    SENSORHUB_ALGO_MODE = [0x01]
    SENSORHUB_PPG_MODE = [0x02]
    SENSORHUB_ADXL_MODE = [0x03]
    SENSORHUB_ECG_MODE = [0x04]
    SENSORHUB_BIOZ_MODE = [0x05]
    SENSORHUB_AMA_MODE = [0x06]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))

class ADXL367MeasRange(Enum):
    """
        SensorHubDevice Enum
    """
    MEAS_RANGE_2G = [0x00]
    MEAS_RANGE_4G = [0x01]
    MEAS_RANGE_8G = [0x02]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))

class MAX86178Device(Enum):
    """
    MAX86178 device
    """
    DEVICE_G_R_IR = [0x30]
    DEVICE_ECG = [0x31]
    DEVICE_BIOZ = [0x32]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))

class ALGODevice(Enum):
    """
    WAS Algo device
    """
    DEVICE_WAS = [0x46]
    DEVICE_AMA = [0x47]

class ADXL367Device(Enum):
    """
    ADXL367 device
    """
    DEVICE_367 = [0x6F, 0x01]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))

class LowPowerSelfTestResult(Enum):
    """
    Sensorhub low power self test result
    """
    OK = [0x00]
    ENTER_LP_ERROR = [0x01]
    GET_TIME_ERROR = [0x02]
    LP_NOT_DETECTED = [0x03]

class AlgoDecimation(Enum):
    """
    Available Algo Decimation
    """    
    EN_RR_DECIMATION = 0x00
    EN_HR_DECIMATION = 0x01
    EN_SPO2_DECIMATION = 0x02
    EN_REG_DECIMATION = 0x03
    EN_PR_DECIMATION = 0x04
    EN_AMA_DECIMATION = 0x05

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))

class Spo2Coeff(Enum):
    """
    Various SpO2 coefficients
    """
    SPO2_COEFF_MLP = [0x00]
    SPO2_COEFF_PTR = [0x01]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))
