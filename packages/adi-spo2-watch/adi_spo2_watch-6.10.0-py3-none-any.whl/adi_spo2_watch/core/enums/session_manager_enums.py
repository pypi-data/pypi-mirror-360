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

from enum import Enum

from .. import utils


class SessionManagerStatus(Enum):
    """
    SessionManager Status Enum
    """
    LOWEST = [0x40]
    OK = [0x41]
    ERR_ARGS = [0x42]
    ERR_NOT_CHKD = [0xFF]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class SessionManagerCommand(Enum):
    """
    SessionManager Command Enums
    """
    LOWEST = [0x40]
    SET_STATE_REQ = [0x41]
    SET_STATE_RES = [0x42]
    GET_STATE_REQ = [0x43]
    GET_STATE_RES = [0x44]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class SessionManagerState(Enum):
    """
    SessionManager States Enums
    """
    STANDBY = [0x0]
    CONFIGURED = [0x1]
    LIVESTREAM = [0x2]
    RECORD = [0x3]
    RECORD_START_LOG = [0x4]
    RECORD_STOP_LOG = [0x5]
    END_LIVESTREAM = [0x6]
    END_RECORD = [0x7]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class SessionManagerEvent(Enum):
    """
    SessionManager Events Enums
    """
    INVALID = [0x0]
    NAV_BUTTON_RESET = [0x1]
    BATTERY_CRITICAL = [0x2]
    BATTERY_DRAINED = [0x3]
    BLE_DISCONNECT_UNEXPECTED = [0x4]
    BLE_DISCONNECT_SESSION_TERMINATED = [0x5]
    RTC_TIMER_INTERRUPT = [0x6]
    BLE_ADV_TIMEOUT = [0x7]
    USB_DISCONNECT_UNEXPECTED = [0x8]
    BATTERY_FULL = [0x9]
    FINISH_LOG_TRANSFER = [0xA]
    SYS_RST_M2M2_COMMAND = [0xB]
    SYS_HW_RST_M2M2_COMMAND = [0xC]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


class WatchResetReason(Enum):
    """
    Watch Reset Reasons Enums
    """
    INVALID = [0x0]
    RST_PIN_RESET = [0x1]
    NRF_WDT_RESET = [0x2]
    SOFT_RESET = [0x4]
    CPU_LOCKUP = [0x8]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))
