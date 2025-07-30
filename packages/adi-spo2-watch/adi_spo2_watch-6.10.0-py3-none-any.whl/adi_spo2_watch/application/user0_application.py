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

from ..core import utils
from ..core.enums.dcb_enums import DCBCommand
from .common_application import CommonApplication
from ..core.enums.pm_enums import PMCommand
from ..core.packets.command_packet import CommandPacket
from ..core.enums.common_enums import Application, CommonCommand
from ..core.enums.user0_enums import User0State, User0Command, User0OperationMode
from ..core.packets.pm_packets import DateTimePacket
from ..core.packets.user0_packets import User0LibraryConfigPacket, User0DCBPacket, User0StatePacket, \
    User0ExperimentIDPacket, User0HardwareIDPacket, User0PrevStateEventPacket, BypassUser0TimingPacket, \
    User0DCBCommandPacket


class User0Application(CommonApplication):
    """
    User0 Application class.

    .. code-block:: python3
        :emphasize-lines: 4

        from adi_spo2_watch import SDK

        sdk = SDK("COM4")
        application = sdk.get_user0_application()

    """

    STATE_SLEEP = User0State.SLEEP
    STATE_ADMIT_STANDBY = User0State.ADMIT_STANDBY
    STATE_END_MONITORING = User0State.END_MONITORING
    STATE_CHARGING_BATTERY = User0State.CHARGING_BATTERY
    STATE_START_MONITORING = User0State.START_MONITORING
    STATE_INTERMITTENT_MONITORING = User0State.INTERMITTENT_MONITORING
    STATE_INTERMITTENT_MONITORING_STOP_LOG = User0State.INTERMITTENT_MONITORING_STOP_LOG
    STATE_INTERMITTENT_MONITORING_START_LOG = User0State.INTERMITTENT_MONITORING_START_LOG
    STATE_OUT_OF_BATTERY_STATE_BEFORE_START_MONITORING = User0State.OUT_OF_BATTERY_STATE_BEFORE_START_MONITORING
    STATE_OUT_OF_BATTERY_STATE_DURING_INTERMITTENT_MONITORING = \
        User0State.OUT_OF_BATTERY_STATE_DURING_INTERMITTENT_MONITORING

    def __init__(self, packet_manager):
        super().__init__(Application.USER0_APP, packet_manager)
        self._dcb_size = 19

    @staticmethod
    def get_supported_states():
        """
        List all supported states for User0.

        :return: Array of user0 state ID enums.
        :rtype: List[User0State]
        """
        return [enum_value for enum_value in User0State]

    def clear_prev_state_event(self):
        """
         Clears the user0 config app's previous state, event received and the corresponding timestamp structure
         maintained registered in the Watch Fw.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.clear_prev_state_event()

        """
        request_packet = CommandPacket(self._destination, User0Command.CLEAR_PREV_ST_EVT_REQ)
        response_packet = CommandPacket(self._destination, User0Command.CLEAR_PREV_ST_EVT_RES)
        return self._send_packet(request_packet, response_packet)

    def get_prev_state_event(self):
        """
        This is a command, to get the user0 config app's previous state, event received and the corresponding timestamp
        registered in the Watch Fw.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
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

        request_packet = CommandPacket(self._destination, User0Command.GET_PREV_ST_EVT_REQ)
        response_packet = User0PrevStateEventPacket(self._destination, User0Command.GET_PREV_ST_EVT_RES)
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

    def set_hardware_id(self, value: int):
        """
        Set Hardware ID.

        :param value: Hardware ID.
        :type value: int
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.set_hardware_id(5)

        """
        request_packet = User0HardwareIDPacket(self._destination, User0Command.ID_OP_REQ)
        request_packet.set_payload("operation", User0OperationMode.WRITE)
        request_packet.set_payload("value", value)
        response_packet = User0HardwareIDPacket(self._destination, User0Command.ID_OP_RES)
        return self._send_packet(request_packet, response_packet)

    def get_hardware_id(self):
        """
        Get Hardware ID.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.get_hardware_id()

        """
        request_packet = User0HardwareIDPacket(self._destination, User0Command.ID_OP_REQ)
        request_packet.set_payload("operation", User0OperationMode.READ)
        response_packet = User0HardwareIDPacket(self._destination, User0Command.ID_OP_RES)
        return self._send_packet(request_packet, response_packet)

    def delete_hardware_id(self):
        """
        Delete Hardware ID.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.delete_hardware_id()

        """
        request_packet = User0HardwareIDPacket(self._destination, User0Command.ID_OP_REQ)
        request_packet.set_payload("operation", User0OperationMode.DELETE)
        response_packet = User0HardwareIDPacket(self._destination, User0Command.ID_OP_RES)
        return self._send_packet(request_packet, response_packet)

    def set_experiment_id(self, value: int):
        """
        Set experiment ID.

        :param value: experiment ID.
        :type value: int
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.set_experiment_id(5)

        """
        request_packet = User0ExperimentIDPacket(self._destination, User0Command.ID_OP_REQ)
        request_packet.set_payload("operation", User0OperationMode.WRITE)
        request_packet.set_payload("value", value)
        response_packet = User0ExperimentIDPacket(self._destination, User0Command.ID_OP_RES)
        return self._send_packet(request_packet, response_packet)

    def get_experiment_id(self):
        """
        Get experiment ID.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.get_experiment_id()

        """
        request_packet = User0ExperimentIDPacket(self._destination, User0Command.ID_OP_REQ)
        request_packet.set_payload("operation", User0OperationMode.READ)
        response_packet = User0ExperimentIDPacket(self._destination, User0Command.ID_OP_RES)
        return self._send_packet(request_packet, response_packet)

    def delete_experiment_id(self):
        """
        Remove experiment ID.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.delete_experiment_id()

        """
        request_packet = User0ExperimentIDPacket(self._destination, User0Command.ID_OP_REQ)
        request_packet.set_payload("operation", User0OperationMode.DELETE)
        response_packet = User0ExperimentIDPacket(self._destination, User0Command.ID_OP_RES)
        return self._send_packet(request_packet, response_packet)

    def get_state(self):
        """
        Get User0 state.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.get_state()

        """
        request_packet = CommandPacket(self._destination, User0Command.GET_STATE_REQ)
        response_packet = User0StatePacket(self._destination, User0Command.GET_STATE_RES)
        return self._send_packet(request_packet, response_packet)

    def set_state(self, state: User0State):
        """
        Set User0 state.

        :param state: User0 state, use get_supported_states() to list all User0 states.
        :type state: User0State
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.set_state(application.STATE_SLEEP)

        """
        request_packet = User0StatePacket(self._destination, User0Command.SET_STATE_REQ)
        request_packet.set_payload("state", state)
        response_packet = User0StatePacket(self._destination, User0Command.SET_STATE_RES)
        return self._send_packet(request_packet, response_packet)

    def read_library_configuration(self, fields: List[int]) -> Dict:
        """
        Reads library configuration from specified field values.

        :param fields: List of field values to read.
        :type fields: List[int]
        :return: A response packet as dictionary
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Fields Lower Limit
             - Fields Upper Limit
           * - 0x00
             - 0x13

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            x = application.read_library_configuration([0x00])
            print(x["payload"]["data"])
            # [['0x0', '0x0']]
        """
        data = [[field, 0] for field in fields]
        request_packet = User0LibraryConfigPacket(self._destination, CommonCommand.READ_LCFG_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = User0LibraryConfigPacket(self._destination, CommonCommand.READ_LCFG_RES)
        return self._send_packet(request_packet, response_packet)

    def write_library_configuration(self, fields_values: List[List[int]]) -> Dict:
        """
        Writes library configuration from List of fields and values.

        :param fields_values: List of fields and values to write.
        :type fields_values: List[List[int]]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Fields Lower Limit
             - Fields Upper Limit
           * - 0x00
             - 0x13

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            x = application.write_library_configuration([[0x01, 0x2]])
            print(x["payload"]["data"])
            # [['0x0', '0x1']]

        """
        request_packet = User0LibraryConfigPacket(self._destination, CommonCommand.WRITE_LCFG_REQ)
        request_packet.set_payload("size", len(fields_values))
        request_packet.set_payload("data", fields_values)
        response_packet = User0LibraryConfigPacket(self._destination, CommonCommand.WRITE_LCFG_RES)
        return self._send_packet(request_packet, response_packet)

    def delete_device_configuration_block(self) -> Dict:
        """
        Delete device configuration block.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.delete_device_configuration_block()

        """
        request_packet = User0DCBCommandPacket(self._destination, DCBCommand.ERASE_CONFIG_REQ)
        response_packet = User0DCBCommandPacket(self._destination, DCBCommand.ERASE_CONFIG_RES)
        return self._send_packet(request_packet, response_packet)

    def read_device_configuration_block(self) -> Dict:
        """
        Returns entire device configuration block.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            x = application.read_device_configuration_block()
            print(x["payload"]["data"])
            # []

        """
        request_packet = User0DCBCommandPacket(self._destination, DCBCommand.READ_CONFIG_REQ)
        response_packet = User0DCBPacket(self._destination, DCBCommand.READ_CONFIG_RES)
        response_dict = self._send_packet(request_packet, response_packet)
        response_dict["payload"]["data"] = utils.add_index_to_array(response_dict["payload"]["data"], to_hex=True)
        return response_dict

    def write_device_configuration_block(self, values: List[int]) -> Dict:
        """
        Writes the device configuration block values of specified addresses.
        This function takes a list of addresses and values to write, and returns a response packet as
        dictionary containing addresses and values.

        :param values: List of addresses and values to write.
        :type values: List[int]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x00
             - 0x13

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            x = application.write_device_configuration_block([0x10, 0x01])
            print(x["payload"]["size"])
            # 2
        """
        request_packet = User0DCBPacket(self._destination, DCBCommand.WRITE_CONFIG_REQ)
        request_packet.set_payload("size", len(values))
        request_packet.set_payload("data", values)
        response_packet = User0DCBCommandPacket(self._destination, DCBCommand.WRITE_CONFIG_RES)
        return self._send_packet(request_packet, response_packet)

    def write_device_configuration_block_from_file(self, filename: str) -> Dict:
        """
        Writes the device configuration block values of specified addresses from file.

        :param filename: dcb filename
        :return: A response packet as dictionary.
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x00
             - 0x13

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.write_device_configuration_block_from_file("user0_dcb.lcfg")
        """
        result = self.device_configuration_file_to_list(filename, address=False)
        if result:
            return self.write_device_configuration_block(result)

    def enable_user0_bypass_timings(self) -> Dict:
        """
        Enable user0 bypass timings.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.enable_user0_bypass_timings()

        """
        request_packet = BypassUser0TimingPacket(self._destination, User0Command.BYPASS_USER0_TIMINGS_REQ)
        request_packet.set_payload("enabled", True)
        response_packet = BypassUser0TimingPacket(self._destination, User0Command.BYPASS_USER0_TIMINGS_RES)
        return self._send_packet(request_packet, response_packet)

    def disable_user0_bypass_timings(self) -> Dict:
        """
        Disable user0 bypass timings.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_user0_application()
            application.disable_user0_bypass_timings()

        """
        request_packet = BypassUser0TimingPacket(self._destination, User0Command.BYPASS_USER0_TIMINGS_REQ)
        request_packet.set_payload("enabled", False)
        response_packet = BypassUser0TimingPacket(self._destination, User0Command.BYPASS_USER0_TIMINGS_RES)
        return self._send_packet(request_packet, response_packet)
