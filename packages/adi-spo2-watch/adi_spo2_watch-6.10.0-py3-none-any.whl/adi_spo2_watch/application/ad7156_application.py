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

from .csv_logging import CSVLogger
from .common_stream import CommonStream
from ..core.enums.dcb_enums import DCBCommand
from ..core.enums.ad7156_enums import AD7156Command
from ..core.packets.command_packet import CommandPacket
from ..core.packets.stream_data_packets import AD7156DataPacket
from ..core.enums.common_enums import Application, CommonCommand, Stream
from ..core.packets.ad7156_packets import AD7156DCBPacket, AD7156RegisterReadPacket, AD7156RegisterWritePacket, \
    AD7156DCBCommandPacket


class AD7156Application(CommonStream):
    """
    AD7156 Application class.

    .. code-block:: python3
        :emphasize-lines: 4

        from adi_spo2_watch import SDK

        sdk = SDK("COM4")
        application = sdk.get_ad7156_application()
    """

    def __init__(self, packet_manager):
        super().__init__(Application.AD7156, Stream.AD7156, packet_manager)
        self._dcb_size = 20

    @staticmethod
    def get_supported_streams() -> List[Stream]:
        """
        List all supported streams.

        :return: Array of stream ID enums.
        :rtype: List[Stream]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adpd_application()
            x = application.get_supported_streams()
            print(x)
            # [<Stream.ADPD1: ['0xC2', '0x11']>, ... , <Stream.ADPD12: ['0xC2', '0x1D']>]
        """
        return [Stream.AD7156]

    def _callback_data(self, packet, packet_id, callback_function=None, args=None):
        """
        Process and returns the data back to user's callback function.
        """
        self._callback_data_helper(packet, AD7156DataPacket())

    def delete_device_configuration_block(self) -> Dict:
        """
        Deletes AD7156 Device configuration block.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_ad7156_application()
            application.delete_device_configuration_block()
        """
        request_packet = AD7156DCBCommandPacket(self._destination, DCBCommand.ERASE_CONFIG_REQ)
        response_packet = AD7156DCBCommandPacket(self._destination, DCBCommand.ERASE_CONFIG_RES)
        return self._send_packet(request_packet, response_packet)

    def load_configuration(self) -> Dict:
        """
        Loads configuration.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_ad7156_application()
            x = application.load_configuration()
            print(x["payload"]["status"])
            # CommonStatus.OK
        """
        request_packet = CommandPacket(self._destination, AD7156Command.LOAD_CONFIG_REQ)
        response_packet = CommandPacket(self._destination, AD7156Command.LOAD_CONFIG_RES)
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
            application = sdk.get_ad7156_application()
            x = application.read_device_configuration_block()
            print(x["payload"]["data"])
            # []
        """
        request_packet = AD7156DCBCommandPacket(self._destination, DCBCommand.READ_CONFIG_REQ)
        response_packet = AD7156DCBPacket(self._destination, DCBCommand.READ_CONFIG_RES)
        return self._send_packet(request_packet, response_packet)

    def read_register(self, addresses: List[int]) -> Dict:
        """
        Reads the register values of specified addresses. This function takes a list of addresses to read,
        and returns a response packet as dictionary containing addresses and values.

        :param addresses: List of register addresses to read.
        :type addresses: List[int]
        :return: A response packet as dictionary
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x00
             - 0x17

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_ad7156_application()
            x = application.read_register([0x10, 0x12])
            print(x["payload"]["data"])
            # [['0x10', '0x0'], ['0x12', '0x0']]
        """
        data = [[address, 0] for address in addresses]
        request_packet = AD7156RegisterReadPacket(self._destination, CommonCommand.REGISTER_READ_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = AD7156RegisterReadPacket(self._destination, CommonCommand.REGISTER_READ_RES)
        return self._send_packet(request_packet, response_packet)

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
           * - 0x09
             - 0x12

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_ad7156_application()
            x = application.write_device_configuration_block([[0x10, 2], [0x12, 0x1]])
            print(x["payload"]["size"])
            # 2
        """
        request_packet = AD7156DCBPacket(self._destination, DCBCommand.WRITE_CONFIG_REQ)
        request_packet.set_payload("size", len(addresses_values))
        request_packet.set_payload("data", addresses_values)
        response_packet = AD7156DCBCommandPacket(self._destination, DCBCommand.WRITE_CONFIG_RES)
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
           * - 0x09
             - 0x12

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_ad7156_application()
            application.write_device_configuration_block_from_file("adxl_dcb.dcfg")
        """
        result = self.device_configuration_file_to_list(filename)
        if result:
            return self.write_device_configuration_block(result)

    def write_register(self, addresses_values: List[List[int]]) -> Dict:
        """
        Writes the register values of specified addresses. This function takes a list of addresses and values to write,
        and returns a response packet as dictionary containing addresses and values.

        :param addresses_values: List of register addresses and values to write.
        :type addresses_values: List[List[int]]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x09
             - 0x12

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_ad7156_application()
            x = application.write_register([[0x10, 0x1], [0x12, 0x2]])
            print(x["payload"]["data"])
            # [['0x10', '0x1'], ['0x12', '0x2']]
        """
        request_packet = AD7156RegisterWritePacket(self._destination, CommonCommand.REGISTER_WRITE_REQ)
        request_packet.set_payload("size", len(addresses_values))
        request_packet.set_payload("data", addresses_values)
        response_packet = AD7156RegisterWritePacket(self._destination, CommonCommand.REGISTER_WRITE_RES)
        return self._send_packet(request_packet, response_packet)

    def enable_csv_logging(self, filename: str, header: List = None) -> None:
        """
        Start logging stream data into CSV.

        :param filename: Name of the CSV file.
        :param header: Header list of the CSV file.
        :return: None

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_ad7156_application()
            x = application.enable_csv_logging("ad7156.csv")
        """
        if header is None:
            header = ["Timestamp", "CH1", "CH2", "CH1 ADCCode", "CH2 ADCCode", "OUT1 val", "OUT2 val"]
        self._csv_logger[Stream.AD7156] = CSVLogger(filename, header)

    def disable_csv_logging(self) -> None:
        """
        Stops logging stream data into CSV.

        :return: None

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_ad7156_application()
            x = application.disable_csv_logging()
        """
        if self._csv_logger[Stream.AD7156]:
            self._csv_logger[Stream.AD7156].stop_logging()
        self._csv_logger[Stream.AD7156] = None
