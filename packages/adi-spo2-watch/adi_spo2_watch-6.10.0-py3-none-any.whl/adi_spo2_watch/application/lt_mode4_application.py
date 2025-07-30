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
from typing import List, Dict
from datetime import datetime, timezone, timedelta

from ..core.enums.pm_enums import PMCommand
from .common_application import CommonApplication
from ..core.enums.common_enums import Application
from ..core.packets.pm_packets import DateTimePacket
from ..core.packets.command_packet import CommandPacket
from ..core.enums.lt_mode4_enums import LTMode4State, LTMode4Command
from ..core.packets.lt_mode4_packets import LTMode4PrevStateEventPacket, LTMode4StatePacket


class LTMode4Application(CommonApplication):
    """
    lt_mode4 Application class.

    .. code-block:: python3
        :emphasize-lines: 4

        from adi_spo2_watch import SDK

        sdk = SDK("COM4")
        application = sdk.get_lt_mode4_application()

    """

    STANDBY = LTMode4State.STANDBY
    CONFIGURED = LTMode4State.CONFIGURED
    LOG_ON = LTMode4State.LOG_ON
    LOG_OFF = LTMode4State.LOG_OFF
    FS_MEMORY_FULL = LTMode4State.FS_MEMORY_FULL
    FS_MAX_FILE_COUNT = LTMode4State.FS_MAX_FILE_COUNT
    SHIPMENT_MODE = LTMode4State.SHIPMENT_MODE
    LOG_OFF_TOOL_CONNECTED = LTMode4State.LOG_OFF_TOOL_CONNECTED
    LOG_DOWNLOAD = LTMode4State.LOG_DOWNLOAD

    def __init__(self, packet_manager):
        super().__init__(Application.LT_MODE4_APP, packet_manager)
        self._dcb_size = 19

    @staticmethod
    def get_supported_states():
        """
        List all supported states for LTMode4State.

        :return: Array of lt_mode4 state ID enums.
        :rtype: List[LTMode4State]
        """
        return [enum_value for enum_value in LTMode4State]

    def clear_prev_state_event(self):
        """
         Clears the LTMode4 config app's previous state, event received and the corresponding timestamp structure
         maintained registered in the Watch Fw.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_lt_mode4_application()
            application.clear_prev_state_event()

        """
        request_packet = CommandPacket(self._destination, LTMode4Command.CLEAR_PREV_ST_EVT_REQ)
        response_packet = CommandPacket(self._destination, LTMode4Command.CLEAR_PREV_ST_EVT_RES)
        return self._send_packet(request_packet, response_packet)

    def get_prev_state_event(self):
        """
        This is a command, to get the lt_mode4 config app's previous state, event received and the corresponding timestamp
        registered in the Watch Fw.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_lt_mode4_application()
            application.get_prev_state_event()

        """
        # TODO: FIX THIS
        request_packet = CommandPacket(Application.PM, PMCommand.GET_DATE_TIME_REQ)
        response_packet = DateTimePacket(Application.PM, PMCommand.GET_DATE_TIME_RES)
        date_time_packet = self._send_packet(request_packet, response_packet)
        offset = timezone(timedelta(seconds=date_time_packet["payload"]["tz_sec"]))
        date_time = datetime(date_time_packet['payload']['year'], date_time_packet['payload']['month'],
                             date_time_packet['payload']['day'], date_time_packet['payload']['hour'],
                             date_time_packet['payload']['minute'], date_time_packet['payload']['second'],
                             tzinfo=offset)

        request_packet = CommandPacket(self._destination, LTMode4Command.GET_PREV_ST_EVT_REQ)
        response_packet = LTMode4PrevStateEventPacket(self._destination, LTMode4Command.GET_PREV_ST_EVT_RES)
        packet = self._send_packet(request_packet, response_packet)
        ts = (32000.0 * ((date_time.hour * 3600) + (date_time.minute * 60) + date_time.second))
        ref_time = date_time.timestamp()
        for i in range(len(packet["payload"]["stream_data"])):
            timestamp = packet["payload"]["stream_data"][i]["timestamp"]
            change = ts - timestamp
            change = change / 32000.0
            reference_time = ref_time - change
            packet["payload"]["stream_data"][i]["timestamp"] = reference_time * 1000
        return packet

    def get_state(self):
        """
        Get lt_mode4 state.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_lt_mode4_application()
            application.get_state()

        """
        request_packet = CommandPacket(self._destination, LTMode4Command.GET_STATE_REQ)
        response_packet = LTMode4StatePacket(self._destination, LTMode4Command.GET_STATE_RES)
        return self._send_packet(request_packet, response_packet)

    def set_state(self, state: LTMode4State):
        """
        Set lt_mode4 state.

        :param state: lt_mode4 state, use get_supported_states() to list all lt_mode4 states.
        :type state: LTMode4State
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_lt_mode4_application()
            application.set_state(application.STATE_SLEEP)

        """
        request_packet = LTMode4StatePacket(self._destination, LTMode4Command.SET_STATE_REQ)
        request_packet.set_payload("state", state)
        response_packet = LTMode4StatePacket(self._destination, LTMode4Command.SET_STATE_RES)
        return self._send_packet(request_packet, response_packet)
