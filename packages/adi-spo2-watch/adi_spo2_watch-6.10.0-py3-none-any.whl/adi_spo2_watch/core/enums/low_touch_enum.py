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

from .. import utils


@unique
class LTCommand(Enum):
    """
    LTCommand Enum
    """
    ACTIVATE_LT_REQ = [0x42]
    ACTIVATE_LT_RES = [0x43]
    DEACTIVATE_LT_REQ = [0x44]
    DEACTIVATE_LT_RES = [0x45]
    ENABLE_LT_CONFIG_LOG_REQ = [0x46]
    ENABLE_LT_CONFIG_LOG_RES = [0x47]
    DISABLE_LT_CONFIG_LOG_REQ = [0x48]
    DISABLE_LT_CONFIG_LOG_RES = [0x49]
    READ_CH2_CAP_REQ = [0x4A]
    READ_CH2_CAP_RES = [0x4B]
    WRIST_DETECT_REQ = [0X4C]
    WRIST_DETECT_RES = [0X4D]
    GET_LT_LOGGING_STATUS_REQ = [0X4E]
    GET_LT_LOGGING_STATUS_RES = [0X4F]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class LTStatus(Enum):
    """
    LTStatus Enum
    """
    LOWEST = [0x40]
    OK = [0x41]
    ERROR_ARGS = [0x42]
    LT_APP_STOPPED = [0x43]
    LT_APP_STARTED = [0x44]
    LT_APP_START_IN_PROGRESS = [0x45]
    LT_APP_STOP_IN_PROGRESS = [0x46]
    ERROR_NOT_CHKD = [0xFF]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))

@unique
class LTWristDetectStatus(Enum):
    """
    LTWristDetectStatus Enum
    """
    WRIST_DETECT_INVALID = [0x0]
    WRIST_DETECT_ON = [0x1]
    WRIST_DETECT_OFF = [0x2]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))

@unique
class LTWristDetectSensor(Enum):
    """
    LTWristDetectSensor Enum
    """
    LT_SENSOR_INVALID = [0x0]
    LT_SENSOR_EDA = [0x1]
    LT_SENSOR_ECG = [0x2]
    LT_SENSOR_BIA = [0x3]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class CommandType(Enum):
    START = [1]
    STOP = [2]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))
