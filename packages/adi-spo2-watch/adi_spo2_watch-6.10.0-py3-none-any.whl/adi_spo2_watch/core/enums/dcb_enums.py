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

from enum import Enum

from .. import utils


class DCBCommand(Enum):
    """
    DCBCommand Enum
    """
    READ_CONFIG_REQ = [0x97]
    READ_CONFIG_RES = [0x98]
    WRITE_CONFIG_REQ = [0x99]
    WRITE_CONFIG_RES = [0x9A]
    ERASE_CONFIG_REQ = [0x9B]
    ERASE_CONFIG_RES = [0x9C]
    QUERY_STATUS_REQ = [0x9D]
    QUERY_STATUS_RES = [0x9E]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class DCBStatus(Enum):
    """
    DCBStatus Enum
    """
    TMP_ENUM_FIX = [0x0]
    OK = [0x97]
    ERROR_NO_DCB = [0x98]
    ERROR_NOT_CHKD = [0xFF]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class DCBConfigBlockIndex(Enum):
    """
    DCBConfigBlockIndex Enum
    """
    GENERAL_BLOCK = [0x0]
    AD5940_BLOCK = [0x1]
    ADPD4000_BLOCK = [0x2]
    ADXL362_BLOCK = [0x3]
    PPG_BLOCK = [0x4]
    ECG_BLOCK = [0x5]
    EDA_LCFG_BLOCK = [0x6]
    AD7156_BLOCK = [0x7]
    PEDOMETER_BLOCK = [0x8]
    TEMPERATURE_BLOCK = [0x9]
    LT_APP_LCFG_BLOCK = [0xA]
    UI_CONFIG_BLOCK = [0xB]
    USER0_BLOCK = [0xC]
    USER1_BLOCK = [0xD]
    USER2_BLOCK = [0xE]
    USER3_BLOCK = [0xF]
    BIA_LCFG_BLOCK = [0x10]
    BIA_DCFG_BLOCK = [0x11]
    EDA_DCFG_BLOCK = [0x12]
    ADP5360_BLOCK = [0x13]
    SESSION_CONFIG_BLOCK = [0x14]
    TEMPERATURE_CORRECTION_BLOCK = [0x15]
    SH_MAX86178_BLOCK = [0x16]
    SH_ADXL367_BLOCK = [0x17]
    MAX_BLOCK = [0x18]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))
