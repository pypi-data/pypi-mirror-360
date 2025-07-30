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


class EDACommand(Enum):
    """
    EDACommand Enum
    """
    LOWEST = [0x40]
    DYNAMIC_SCALE_REQ = [0x42]
    DYNAMIC_SCALE_RES = [0x43]
    SET_DFT_NUM_REQ = [0x46]
    SET_DFT_NUM_RES = [0x47]
    DEBUG_INFO_REQ = [0x48]
    DEBUG_INFO_RES = [0x49]
    RESISTOR_TIA_CAL_REQ = [0x4A]
    RESISTOR_TIA_CAL_RES = [0x4B]
    BASELINE_IMP_SET_REQ = [0x4C]
    BASELINE_IMP_SET_RES = [0x4D]
    BASELINE_IMP_RESET_REQ = [0x4E]
    BASELINE_IMP_RESET_RES = [0x4F]
    LOAD_DCFG_REQ = [0x50]
    LOAD_DCFG_RES = [0x51]
    WRITE_DCFG_REQ = [0x52]
    WRITE_DCFG_RES = [0x53]
    READ_DCFG_REQ = [0x54]
    READ_DCFG_RES = [0x55]
    BASELINE_IMP_GET_REQ = [0x56]
    BASELINE_IMP_GET_RES = [0x57]
    GET_RTIA_TABLE_FDS_REQ = [0x58]
    GET_RTIA_TABLE_FDS_RES = [0x59]
    GET_RTIA_TABLE_RAM_REQ = [0x5A]
    GET_RTIA_TABLE_RAM_RES = [0x5B]
    DELETE_RTIA_TABLE_IN_FDS_REQ = [0x5C]
    DELETE_RTIA_TABLE_IN_FDS_RES = [0x5D]
    CONTROL_AD5940_SLEEP_WAKEUP_REQ = [0x62]
    CONTROL_AD5940_SLEEP_WAKEUP_RES = [0x63]
    SLEEP_WAKEUP_STATUS_REQ = [0x64]
    SLEEP_WAKEUP_STATUS_RES = [0x65]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class EDAPowerMode(Enum):
    """
    EDAPowerMode Enum
    """
    POWER_INVALID = [0x0]
    POWER_SLEEP = [0x1]
    POWER_WAKEUP = [0x2]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class EDADFTWindow(Enum):
    """
    EDADFTWindow Enum
    """
    DFT_WINDOW_4 = [0x0]
    DFT_WINDOW_8 = [0x1]
    DFT_WINDOW_16 = [0x2]
    DFT_WINDOW_32 = [0x3]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class ScaleResistor(Enum):
    """
    ScaleResistor Enum
    """
    DISABLED = [0, 0]
    SCALE_RESISTOR_110 = [1, 0]
    SCALE_RESISTOR_1K = [2, 0]
    SCALE_RESISTOR_2K = [3, 0]
    SCALE_RESISTOR_3K = [4, 0]
    SCALE_RESISTOR_4K = [5, 0]
    SCALE_RESISTOR_6K = [6, 0]
    SCALE_RESISTOR_8K = [7, 0]
    SCALE_RESISTOR_10K = [8, 0]
    SCALE_RESISTOR_12K = [9, 0]
    SCALE_RESISTOR_16K = [10, 0]
    SCALE_RESISTOR_20K = [11, 0]
    SCALE_RESISTOR_24K = [12, 0]
    SCALE_RESISTOR_30K = [13, 0]
    SCALE_RESISTOR_32K = [14, 0]
    SCALE_RESISTOR_40K = [15, 0]
    SCALE_RESISTOR_48K = [16, 0]
    SCALE_RESISTOR_64K = [17, 0]
    SCALE_RESISTOR_85K = [18, 0]
    SCALE_RESISTOR_96K = [19, 0]
    SCALE_RESISTOR_100K = [20, 0]
    SCALE_RESISTOR_120K = [21, 0]
    SCALE_RESISTOR_128K = [22, 0]
    SCALE_RESISTOR_160K = [23, 0]
    SCALE_RESISTOR_196K = [24, 0]
    SCALE_RESISTOR_256K = [25, 0]
    SCALE_RESISTOR_512K = [26, 0]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))
