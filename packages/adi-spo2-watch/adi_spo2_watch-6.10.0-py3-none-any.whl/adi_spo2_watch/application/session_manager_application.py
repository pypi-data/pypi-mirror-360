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

import logging
from typing import Dict, List

from .ecg_application import ECGApplication
from ..core import utils
from ..core.enums.dcb_enums import DCBCommand
from .common_application import CommonApplication
from ..core.enums.session_manager_enums import SessionManagerState
from ..core.enums.common_enums import Application, CommonCommand, Stream
from ..core.packets.common_packets import StreamPacket
from ..core.packets.session_manager_packets import SessionManagerLibraryConfigPacket, SessionManagerDCBPacket

logger = logging.getLogger(__name__)


class SessionManagerApplication(CommonApplication):
    """
    Session Manager Application class.

    .. code-block:: python3
        :emphasize-lines: 4

        from adi_spo2_watch import SDK

        sdk = SDK("COM4")
        application = sdk.get_session_manager_application()
    """

    def __init__(self, packet_manager):
        super().__init__(Application.SESSION_MANAGER_APP, packet_manager)
        # self._dcb_size = 57  # Not required as such

    @staticmethod
    def get_session_states():
        """
        List all supported streams.

        :return: Array of stream ID enums.
        :rtype: List[Stream]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_session_manager_application()
            x = application.get_session_states()
            print(x)
        """
        return [x for x in SessionManagerState]

    def start_sensor(self):
        """
        Starts sensor.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_session_manager_application()
            start_sensor = application.start_sensor()
            print(start_sensor["payload"]["status"])
            # CommonStatus.STREAM_STARTED
        """
        request_packet = StreamPacket(self._destination, CommonCommand.START_SENSOR_REQ)
        response_packet = StreamPacket(self._destination, CommonCommand.START_SENSOR_RES)


        ecg_app = ECGApplication(self._packet_manager)
        ecg_app._subscribe_without_communication(stream=Stream.ECG)


        return self._send_packet(request_packet, response_packet)

    def stop_sensor(self):
        """
        Stops sensor.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_session_manager_application()
            stop_sensor = application.stop_sensor()
            print(stop_sensor["payload"]["status"])
            # CommonStatus.STREAM_STOPPED
        """
        request_packet = StreamPacket(self._destination, CommonCommand.STOP_SENSOR_REQ)
        response_packet = StreamPacket(self._destination, CommonCommand.STOP_SENSOR_RES)

        ecg_app = ECGApplication(self._packet_manager)
        ecg_app._unsubscribe_stream_data(stream=Stream.ECG)

        return self._send_packet(request_packet, response_packet)

    def read_library_configuration(self, fields: List[int]) -> Dict:
        """
        Reads library configuration from specified index values.

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
             - 0x19

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_session_manager_application()
            x = application.read_library_configuration([0x02, 0x06, 0x07])
            print(x["payload"]["data"])
            # [['0x0', '0x0']]
        """
        if len(fields) == 0:
            raise ValueError("Please enter atleast one field")
        for i in range(len(fields)):
            if not (0x02 == fields[i] or 0x06 <= fields[i] <= 0x19):
                logger.warning("fields 0, 1, 3, 4 and 5 are not allowed.")
                raise ValueError("Firmware is unable to deal with this issue.")
        data = [[field, 0] for field in fields]
        request_packet = SessionManagerLibraryConfigPacket(self._destination, CommonCommand.READ_LCFG_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = SessionManagerLibraryConfigPacket(self._destination, CommonCommand.READ_LCFG_RES)
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
            application = sdk.get_session_manager_application()
            x = application.write_library_configuration([[0x02, 0x2]])
            print(x["payload"]["data"])
            # [['0x0', '0x1']]

        """
        if len(fields_values) == 0:
            raise ValueError("Please enter atleast one pair of index and value")
        for i in range(len(fields_values)):
            if not (0x02 == fields_values[i][0] or 0x06 <= fields_values[i][0] <= 0x19):
                logger.warning("fields 0, 1, 3, 4 and 5 are not allowed.")
                raise ValueError("Firmware is unable to deal with this issue.")
        request_packet = SessionManagerLibraryConfigPacket(self._destination, CommonCommand.WRITE_LCFG_REQ)
        request_packet.set_payload("size", len(fields_values))
        request_packet.set_payload("data", fields_values)
        response_packet = SessionManagerLibraryConfigPacket(self._destination, CommonCommand.WRITE_LCFG_RES)
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
             - 0x19

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_session_manager_application()
            application.write_device_configuration_block_from_file("session_config_dcb.lcfg")
        """
        result = self.device_configuration_file_to_list(filename)
        if result:
            return self.write_device_configuration_block(result)

    def write_device_configuration_block(self, addresses_values: List[List[int]]) -> Dict:
        """
        Writes the device configuration block values of specified addresses.
        This function takes a list of addresses and values to write, and returns a response packet as
        dictionary containing addresses and values.

        :param addresses_values: List of addresses and values to write.
        :type addresses_values: List[List[int]]
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
            x = application.write_device_configuration_block([[0x10, 0x10], [0x02, 0x02])
            print(x["payload"]["size"])
            # 2
        """
        dcb_array = []
        for address_value in addresses_values:
            dcb_array.append(address_value[1])
        request_packet = SessionManagerDCBPacket(self._destination, DCBCommand.WRITE_CONFIG_REQ)
        request_packet.set_payload("size", len(dcb_array))
        request_packet.set_payload("data", dcb_array)
        response_packet = SessionManagerDCBPacket(self._destination, DCBCommand.WRITE_CONFIG_RES)
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
            application = sdk.get_session_manager_application()
            x = application.read_device_configuration_block()
            print(x["payload"]["data"])
            # []
        """
        request_packet = SessionManagerDCBPacket(self._destination, DCBCommand.READ_CONFIG_REQ)
        response_packet = SessionManagerDCBPacket(self._destination, DCBCommand.READ_CONFIG_RES)
        response_dict = self._send_packet(request_packet, response_packet)
        response_dict['payload']['data'] = utils.add_index_to_array(response_dict['payload']['data'], to_hex=True)
        return response_dict

    def delete_device_configuration_block(self) -> Dict:
        """
        Deletes PM Device configuration block.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_session_manager_application()
            application.delete_device_configuration_block()
        """
        request_packet = SessionManagerDCBPacket(self._destination, DCBCommand.ERASE_CONFIG_REQ)
        response_packet = SessionManagerDCBPacket(self._destination, DCBCommand.ERASE_CONFIG_RES)
        return self._send_packet(request_packet, response_packet)
