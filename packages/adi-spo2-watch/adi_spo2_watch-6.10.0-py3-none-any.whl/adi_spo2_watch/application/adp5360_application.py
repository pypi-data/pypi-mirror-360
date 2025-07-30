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

import logging
from datetime import datetime
from typing import Dict, List, Callable, Tuple

from ..core import utils
from .csv_logging import CSVLogger
from ..core.enums.dcb_enums import DCBCommand
from .common_application import CommonApplication
from ..core.enums.adp5360_enums import ADP5360Command
from ..core.packets.common_packets import StreamPacket
from ..core.packets.command_packet import CommandPacket
from ..core.enums.common_enums import Application, CommonCommand, Stream
from ..core.packets.adp5360_packets import BatteryInfoPacket, ADP5360DCBPacket, ADP5360DCBCommandPacket, \
    BatteryThresholdPacket, ADP5360RegisterReadPacket, ADP5360RegisterWritePacket

logger = logging.getLogger(__name__)


class ADP5360Application(CommonApplication):
    """
    Battery Application class.

    .. code-block:: python3
        :emphasize-lines: 4

        from adi_spo2_watch import SDK

        sdk = SDK("COM4")
        application = sdk.get_adp5360_application()
    """

    STREAM_BATTERY = Stream.BATTERY

    def __init__(self, packet_manager):
        super().__init__(Application.ADP5360, packet_manager)
        self._args = {}
        self._csv_logger = {}
        self._last_timestamp = {}
        self._callback_function = {}
        self._dcb_size = 57

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
        return [Stream.BATTERY]

    def set_battery_threshold(self, low_level: int, critical_level: int, download_level: int) -> Dict:
        """
        Set low and critical level threshold for device battery.

        :param low_level: low level threshold for device battery.
        :type low_level: int
        :param critical_level: critical level threshold for device battery.
        :type critical_level: int
        :param download_level: download level.
        :type download_level: int
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_test_application()
            x = application.set_battery_threshold(15, 10, 20)
            print(x["payload"]["status"])
            # PMStatus.OK

        """
        request_packet = BatteryThresholdPacket(self._destination, ADP5360Command.SET_BAT_THR_REQ)
        request_packet.set_payload("low_level", low_level)
        request_packet.set_payload("critical_level", critical_level)
        request_packet.set_payload("download_level", download_level)
        response_packet = CommandPacket(self._destination, ADP5360Command.SET_BAT_THR_RES)
        return self._send_packet(request_packet, response_packet)

    def get_battery_threshold(self) -> Dict:
        """
        get low and critical level threshold for device battery.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_test_application()
            x = application.get_battery_threshold()
            print(x["payload"]["status"])
            # PMStatus.OK

        """
        request_packet = CommandPacket(self._destination, ADP5360Command.GET_BAT_THR_REQ)
        response_packet = BatteryThresholdPacket(self._destination, ADP5360Command.GET_BAT_THR_RES)
        return self._send_packet(request_packet, response_packet)

    def get_battery_info(self) -> Dict:
        """
        Returns device current battery information.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adp5360_application()
            x = application.get_battery_info()
            print(x["payload"]["battery_status"], x["payload"]["battery_level"])
            # BatteryStatus.COMPLETE 100
        """
        request_packet = CommandPacket(self._destination, ADP5360Command.GET_BAT_INFO_REQ)
        response_packet = BatteryInfoPacket(self._destination, ADP5360Command.GET_BAT_INFO_RES)
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
             - 0x36

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adp5360_application()
            x = application.read_register([0x15, 0x20, 0x2E])
            print(x["payload"]["data"])
            # [['0x15', '0x0'], ['0x20', '0x0'], ['0x2E', '0x0']]

        """
        data = [[address, 0] for address in addresses]
        request_packet = ADP5360RegisterReadPacket(self._destination, CommonCommand.REGISTER_READ_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = ADP5360RegisterReadPacket(self._destination, CommonCommand.REGISTER_READ_RES)
        return self._send_packet(request_packet, response_packet)

    def write_register(self, addresses_values: List[List[int]]) -> Dict:
        """
        Writes the register values of specified addresses. This function takes a list of addresses and values to write,
        and returns a response packet as dictionary containing addresses and values.

        :param addresses_values: List of register addresses and values to write.
        :type addresses_values: List[List[int]]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. list-table::
           :widths: 75
           :header-rows: 1

           * - Address ranges
           * - [0x2-0x7], [0xA-0xE], [0x11-0x22], [0x27-0x2E], [0x30-0x33], [0x36]


        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adp5360_application()
            x = application.write_register([[0x20, 0x1], [0x21, 0x2], [0x2E, 0x3]])
            print(x["payload"]["data"])
            # [['0x20', '0x1'], ['0x21', '0x2'], ['0x2E', '0x3']]
        """
        size = len(addresses_values)
        for i in range(size):
            if not (0x2 <= addresses_values[i][0] <= 0x7 or 0xA <= addresses_values[i][0] <= 0xE or
                    0x11 <= addresses_values[i][0] <= 0x22 or 0x27 <= addresses_values[i][0] <= 0x2E or
                    0x30 <= addresses_values[i][0] <= 0x33 or addresses_values[i][0] == 0x36):
                logger.warning(f"{'0x%X' % addresses_values[i][0]} is out of range, allowed ranges are: [0x2-0x7], "
                               f"[0xA-0xE], [0x11-0x22], [0x27-0x2E], [0x30-0x33], [0x36]")
        request_packet = ADP5360RegisterWritePacket(self._destination, CommonCommand.REGISTER_WRITE_REQ)
        request_packet.set_payload("size", size)
        request_packet.set_payload("data", addresses_values)
        response_packet = ADP5360RegisterWritePacket(self._destination, CommonCommand.REGISTER_WRITE_RES)
        return self._send_packet(request_packet, response_packet)

    def delete_device_configuration_block(self) -> Dict:
        """
        Deletes PM Device configuration block.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adp5360_application()
            application.delete_device_configuration_block()
        """
        request_packet = ADP5360DCBCommandPacket(self._destination, DCBCommand.ERASE_CONFIG_REQ)
        response_packet = ADP5360DCBCommandPacket(self._destination, DCBCommand.ERASE_CONFIG_RES)
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
            application = sdk.get_adp5360_application()
            x = application.read_device_configuration_block()
            print(x["payload"]["dcb_data"])
            # []
        """
        request_packet = ADP5360DCBCommandPacket(self._destination, DCBCommand.READ_CONFIG_REQ)
        response_packet = ADP5360DCBPacket(self._destination, DCBCommand.READ_CONFIG_RES)
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

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adp5360_application()
            x = application.write_device_configuration_block([[0x2, 2], [0x1, 0x1]])
            print(x["payload"]["size"])
            # 2
        """
        request_packet = ADP5360DCBPacket(self._destination, DCBCommand.WRITE_CONFIG_REQ)
        request_packet.set_payload("size", len(addresses_values))
        request_packet.set_payload("data", addresses_values)
        response_packet = ADP5360DCBCommandPacket(self._destination, DCBCommand.WRITE_CONFIG_RES)
        return self._send_packet(request_packet, response_packet)

    def write_device_configuration_block_from_file(self, filename: str) -> Dict:
        """
        Writes the device configuration block values of specified addresses from file.

        :param filename: dcb filename
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adp5360_application()
            application.write_device_configuration_block_from_file("pm_dcb.dcfg")
        """
        result = self.device_configuration_file_to_list(filename)
        if result:
            return self.write_device_configuration_block(result)

    # noinspection PyTypeChecker
    def set_callback(self, callback_function: Callable, args: Tuple = (), stream: Stream = STREAM_BATTERY) -> None:
        """
        Sets the callback for the stream data.

        :param callback_function: callback function for specified adpd stream.
        :param args: optional arguments that will be passed with the callback.
        :param stream: Callback for specified stream, use get_supported_streams() to list all supported streams.
        :type stream: Stream
        :return: None

        .. code-block:: python3
            :emphasize-lines: 4,12

            from adi_spo2_watch import SDK

            # make sure optional arguments have default value to prevent them causing Exceptions.
            def callback(data, optional1=None, optional2=None):
                print(data)

            sdk = SDK("COM4")
            application = sdk.get_adp5360_application()
            # these optional arguments can be used to pass file, matplotlib or other objects to manipulate data.
            optional_arg1 = "1"
            optional_arg2 = "2"
            application.set_callback(callback, args=(optional_arg1, optional_arg2))
        """
        self._callback_function[stream] = callback_function
        self._args[stream] = args

    def _callback_data(self, packet, packet_id, callback_function=None, args=None, stream=None):
        """
        Process and returns the data back to user's callback function.
        """
        self._callback_data_helper(packet, BatteryInfoPacket(), self.STREAM_BATTERY)

    def _callback_data_helper(self, packet, response_packet, stream=None):
        """
        Process and returns the data back to user's callback function.
        """
        args = self._args.get(stream, ())
        callback_function = self._callback_function.get(stream, None)
        response_packet.decode_packet(packet)
        last_timestamp = self._last_timestamp.get(stream)
        first_timestamp = last_timestamp[0]
        result = response_packet.get_dict(last_timestamp)
        utils.update_timestamp(result, last_timestamp)
        csv_logger = self._csv_logger.get(stream, None)
        if csv_logger:
            csv_logger.add_row(result, first_timestamp, self.tz_sec)
        try:
            if callback_function:
                callback_function(result, *args)
        except Exception as e:
            logger.error(f"Can't send packet back to user callback function, reason :: {e}", exc_info=True)

        if not csv_logger and not callback_function:
            logger.warning(f"No callback function provided for {result['header']['source']}")

    def subscribe_stream(self, stream: Stream = STREAM_BATTERY):
        """
        Subscribe to the stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adp5360_application()
            subs_stream = application.subscribe_stream(STREAM_BATTERY)
            print(subs_stream["payload"]["status"])
            # CommonStatus.SUBSCRIBER_ADDED
        """
        request_packet = StreamPacket(self._destination, CommonCommand.SUBSCRIBE_STREAM_REQ)
        request_packet.set_payload("stream_address", stream)
        self._subscribe_stream_data(stream)
        response_packet = StreamPacket(self._destination, CommonCommand.SUBSCRIBE_STREAM_RES)
        self._update_timestamp(datetime.now(), stream)
        return self._send_packet(request_packet, response_packet)

    def _update_timestamp(self, date_time, stream=STREAM_BATTERY, generate_ts=False, tz_sec=None):
        if generate_ts:
            ts = (32000.0 * ((date_time.hour * 3600) + (date_time.minute * 60) + date_time.second))
            self.tz_sec = tz_sec
        else:
            ts = -1
        self._last_timestamp[stream] = [date_time.timestamp(), ts]

    def unsubscribe_stream(self, stream: Stream = None):
        """
        Unsubscribe the stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adp5360_application()
            unsubscribe_stream = application.unsubscribe_stream()
            print(unsubscribe_stream["payload"]["status"])
            # CommonStatus.SUBSCRIBER_REMOVED
        """
        request_packet = StreamPacket(self._destination, CommonCommand.UNSUBSCRIBE_STREAM_REQ)
        request_packet.set_payload("stream_address", stream)
        response_packet = StreamPacket(self._destination, CommonCommand.UNSUBSCRIBE_STREAM_RES)
        response_packet = self._send_packet(request_packet, response_packet)
        self._unsubscribe_stream_data(stream)
        return response_packet

    def _subscribe_stream_data(self, stream=None, callback_function=None):
        callback_function = callback_function if callback_function else self._callback_data
        data_packet_id = self._get_packet_id(CommonCommand.STREAM_DATA, stream)
        self._packet_manager.subscribe(data_packet_id, callback_function)

    def _unsubscribe_stream_data(self, stream=None, callback_function=None):
        callback_function = callback_function if callback_function else self._callback_data
        data_packet_id = self._get_packet_id(CommonCommand.STREAM_DATA, stream)
        self._packet_manager.unsubscribe(data_packet_id, callback_function)

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
            application = sdk.get_adp5360_application()
            x = application.enable_csv_logging("adp.csv")
        """
        if header is None:
            header = ["Timestamp", "Battery status", "ADP5360 Battery level", "Custom Battery level", "Battery mv"]
        self._csv_logger[Stream.BATTERY] = CSVLogger(filename, header)

    def disable_csv_logging(self) -> None:
        """
        Stops logging stream data into CSV.

        :return: None

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adp5360_application()
            x = application.disable_csv_logging()
        """
        if self._csv_logger.get(Stream.BATTERY):
            self._csv_logger[Stream.BATTERY].stop_logging()
        self._csv_logger[Stream.BATTERY] = None
