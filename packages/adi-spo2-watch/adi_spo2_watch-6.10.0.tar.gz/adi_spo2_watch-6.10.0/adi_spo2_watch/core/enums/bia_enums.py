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


class BIACommand(Enum):
    """
    BIACommand Enum
    """
    LOWEST = [0x40]
    SET_DFT_NUM_REQ = [0x46]
    SET_DFT_NUM_RES = [0x47]
    SET_HS_TRANS_IMPEDANCE_AMPLIFIER_CAL_REQ = [0x48]
    SET_HS_TRANS_IMPEDANCE_AMPLIFIER_CAL_RES = [0x49]
    FDS_STATUS_REQ = [0x4A]
    FDS_STATUS_RES = [0x4B]
    DCB_TIMING_INFO_REQ = [0x4C]
    DCB_TIMING_INFO_RES = [0x4D]
    ALGO_STREAM_RES = [0x4E]
    LOAD_DCFG_REQ = [0x4F]
    LOAD_DCFG_RES = [0x50]
    WRITE_DCFG_REQ = [0x51]
    WRITE_DCFG_RES = [0x52]
    READ_DCFG_REQ = [0x53]
    READ_DCFG_RES = [0x54]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class HSResistorTIA(Enum):
    """
    HSResistorTIA Enum
    """
    RESISTOR_200 = [0x0, 0x0]
    RESISTOR_1K = [0x0, 0x1]
    RESISTOR_5K = [0x0, 0x2]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class BIADFTWindow(Enum):
    """
    BIADFTWindow Enum
    """
    DFT_WINDOW_4 = [0x0, 0x0]
    DFT_WINDOW_8 = [0x0, 0x1]
    DFT_WINDOW_16 = [0x0, 0x2]
    DFT_WINDOW_32 = [0x0, 0x3]
    DFT_WINDOW_64 = [0x0, 0x4]
    DFT_WINDOW_128 = [0x0, 0x5]
    DFT_WINDOW_256 = [0x0, 0x6]
    DFT_WINDOW_512 = [0x0, 0x7]
    DFT_WINDOW_1024 = [0x0, 0x8]
    DFT_WINDOW_2048 = [0x0, 0x9]
    DFT_WINDOW_4096 = [0x0, 0x10]
    DFT_WINDOW_8192 = [0x0, 0x11]
    DFT_WINDOW_16384 = [0x0, 0x12]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class BIASweepFrequency(Enum):
    """
    BIASweepFrequency Enum
    """
    FREQ_1000HZ = [0x0]
    FREQ_3760HZ = [0x1]
    FREQ_14140HZ = [0x2]
    FREQ_53180HZ = [0x3]
    FREQ_200KHZ = [0x4]
    FREQ_50KHZ = [0xFF]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class BIAAppInfo(Enum):
    """
    BIAAppInfo Enum
    """
    BITSET_LEADS_OFF = [0x0]
    BITSET_LEADS_ON = [0x1]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))
