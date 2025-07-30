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
from typing import Callable, Tuple

from .common_application import CommonApplication
from ..core import utils
from ..core.enums.common_enums import CommonCommand, Stream
from ..core.packets.common_packets import StreamPacket, StreamStatusPacket

logger = logging.getLogger(__name__)


class CommonStream(CommonApplication):
    """
    A Common Stream class for streaming data from sensors.
    """

    def __init__(self, destination, stream, packet_manager):
        """
        Initialize the common stream packet variable.

        :param destination: Address of the application.
        :param stream: Address of stream.
        :param packet_manager: PacketManager Object.
        """
        super().__init__(destination, packet_manager)
        self._args = {}
        self._stream = stream
        self._csv_logger = {}
        self._last_timestamp = {}
        self._callback_function = {}
        self._packet_lost = {}
        self._packet_sequence_number = {}

    def get_packet_lost_count(self, stream: Stream = None):
        """
        This API returns the number of missing packets during a stream session.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: Int
        """
        stream = stream if stream else self._stream
        return self._packet_lost.get(stream, None)

    def _sequence_number_check_with_channel(self, stream, seq_no, channel_number):
        expected_seq_no = self._packet_sequence_number.get(stream)
        packets_lost = self.get_packet_lost_count(stream)
        if packets_lost is None:
            packets_lost = [0, 0]
            self._packet_lost[stream] = packets_lost
        if expected_seq_no[channel_number - 1] == -1:
            expected_seq_no[channel_number - 1] = seq_no
        missing_packets = utils.missing_sequences(expected_seq_no[channel_number - 1], seq_no)
        self._packet_lost[stream][channel_number - 1] = packets_lost[channel_number - 1] + missing_packets
        self._packet_sequence_number[stream][channel_number - 1] = (seq_no + 1) % 65536

    def _sequence_number_check(self, stream, seq_no):
        expected_seq_no = self._packet_sequence_number.get(stream)
        packets_lost = self.get_packet_lost_count(stream)
        if packets_lost is None:
            packets_lost = 0
        if expected_seq_no == -1:
            expected_seq_no = seq_no
        missing_packets = utils.missing_sequences(expected_seq_no, seq_no)
        self._packet_lost[stream] = packets_lost + missing_packets
        self._packet_sequence_number[stream] = (seq_no + 1) % 65536

    def set_callback(self, callback_function: Callable, args: Tuple = ()):
        """
        Sets the callback for the stream data.

        :param args: optional arguments that will be passed with the callback.
        :param callback_function: callback function for stream adxl data.
        :return: None

        .. code-block:: python3
            :emphasize-lines: 4,12

            from adi_study_watch import SDK

            # make sure optional arguments have default value to prevent them causing Exceptions.
            def callback(data, optional1=None, optional2=None):
                print(data)

            sdk = SDK("COM4")
            application = sdk.get_adxl_application()
            # these optional arguments can be used to pass file, matplotlib or other objects to manipulate data.
            optional_arg1 = "1"
            optional_arg2 = "2"
            application.set_callback(callback, args=(optional_arg1, optional_arg2))
        """
        self._args[self._stream] = args
        self._callback_function[self._stream] = callback_function

    def _callback_data(self, packet, packet_id, callback_function=None, args=None):
        """
        Process and returns the data back to user's callback function.
        """
        pass

    def _update_stream_data(self, result):
        """
        Add or modify stream data values.
        """
        pass

    def _callback_data_helper(self, packet, response_packet, stream=None):
        """
        Process and returns the data back to user's callback function.
        """
        stream = stream if stream else self._stream
        args = self._args.get(stream, ())
        callback_function = self._callback_function.get(stream, None)
        response_packet.decode_packet(packet)
        last_timestamp = self._last_timestamp.get(stream)
        first_timestamp = last_timestamp[0]
        result = response_packet.get_dict(last_timestamp)
        if result["payload"].get("sequence_number", None) is not None:
            if stream in [Stream.ADPD1, Stream.ADPD2, Stream.ADPD3, Stream.ADPD4, Stream.ADPD5, Stream.ADPD6,
                          Stream.ADPD7, Stream.ADPD8, Stream.ADPD9, Stream.ADPD10, Stream.ADPD11, Stream.ADPD12,
                          Stream.SENSORHUB_MAX86178_STREAM1, Stream.SENSORHUB_MAX86178_STREAM2, Stream.SENSORHUB_MAX86178_STREAM3,
                          Stream.SENSORHUB_MAX86178_STREAM4, Stream.SENSORHUB_MAX86178_STREAM5, Stream.SENSORHUB_MAX86178_STREAM6]:
                self._sequence_number_check_with_channel(stream, result["payload"]["sequence_number"],
                                                         result["payload"]["channel_num"])
            else:
                self._sequence_number_check(stream, result["payload"]["sequence_number"])
        self._update_stream_data(result)
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

    def get_sensor_status(self):
        """
        Returns packet with number of subscribers and number of sensor start request registered.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_study_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adxl_application()
            x = application.get_sensor_status()
            print(x["payload"]["num_subscribers"], x["payload"]["num_start_registered"])
            # 0 0

        """
        request_packet = StreamStatusPacket(self._destination, CommonCommand.GET_SENSOR_STATUS_REQ)
        request_packet.set_payload("stream_address", self._destination)
        response_packet = StreamStatusPacket(self._destination, CommonCommand.GET_SENSOR_STATUS_RES)
        return self._send_packet(request_packet, response_packet)

    def start_and_subscribe_stream(self, stream: Stream = None):
        """
        Starts sensor and also subscribe to the stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Tuple[Dict, Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_study_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adxl_application()
            start_sensor, subs_stream = application.start_and_subscribe_stream()
            print(start_sensor["payload"]["status"], subs_stream["payload"]["status"])
            # CommonStatus.STREAM_STARTED CommonStatus.SUBSCRIBER_ADDED
        """
        status2 = self.subscribe_stream(stream=stream)
        status1 = self.start_sensor()
        return status1, status2

    def start_sensor(self):
        """
        Starts sensor.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_study_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adxl_application()
            start_sensor = application.start_sensor()
            print(start_sensor["payload"]["status"])
            # CommonStatus.STREAM_STARTED
        """
        request_packet = StreamPacket(self._destination, CommonCommand.START_SENSOR_REQ)
        response_packet = StreamPacket(self._destination, CommonCommand.START_SENSOR_RES)
        return self._send_packet(request_packet, response_packet)

    def stop_and_unsubscribe_stream(self, stream: Stream = None):
        """
        Stops sensor and also Unsubscribe the stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Tuple[Dict, Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_study_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adxl_application()
            stop_sensor, unsubscribe_stream = application.stop_and_unsubscribe_stream()
            print(stop_sensor["payload"]["status"], unsubscribe_stream["payload"]["status"])
            # CommonStatus.STREAM_STOPPED CommonStatus.SUBSCRIBER_REMOVED
        """
        status1 = self.stop_sensor()
        status2 = self.unsubscribe_stream(stream=stream)
        return status1, status2

    def stop_sensor(self):
        """
        Stops sensor.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_study_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adxl_application()
            stop_sensor = application.stop_sensor()
            print(stop_sensor["payload"]["status"])
            # CommonStatus.STREAM_STOPPED
        """
        request_packet = StreamPacket(self._destination, CommonCommand.STOP_SENSOR_REQ)
        response_packet = StreamPacket(self._destination, CommonCommand.STOP_SENSOR_RES)
        return self._send_packet(request_packet, response_packet)

    def subscribe_stream(self, stream: Stream = None):
        """
        Subscribe to the stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_study_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adxl_application()
            subs_stream = application.subscribe_stream()
            print(subs_stream["payload"]["status"])
            # CommonStatus.SUBSCRIBER_ADDED
        """
        stream = stream if stream else self._stream
        request_packet = StreamPacket(self._destination, CommonCommand.SUBSCRIBE_STREAM_REQ)
        request_packet.set_payload("stream_address", stream)
        self._subscribe_stream_data(stream=stream)
        response_packet = StreamPacket(self._destination, CommonCommand.SUBSCRIBE_STREAM_RES)
        self._update_timestamp(datetime.now(), stream=stream)
        return self._send_packet(request_packet, response_packet)

    def _update_timestamp(self, date_time, stream=None, generate_ts=False, tz_sec=None):
        stream = stream if stream else self._stream
        timestamp_at_12 = datetime(date_time.year, date_time.month, date_time.day).timestamp()
        if stream == Stream.SYNC_PPG:
            self._last_timestamp[stream] = [timestamp_at_12, -1, timestamp_at_12, -1]
        else:
            self._last_timestamp[stream] = [timestamp_at_12, -1]
        if stream in [Stream.ADPD1, Stream.ADPD2, Stream.ADPD3, Stream.ADPD4, Stream.ADPD5, Stream.ADPD6,
                      Stream.ADPD7, Stream.ADPD8, Stream.ADPD9, Stream.ADPD10, Stream.ADPD11, Stream.ADPD12,
                      Stream.SENSORHUB_MAX86178_STREAM1, Stream.SENSORHUB_MAX86178_STREAM2, Stream.SENSORHUB_MAX86178_STREAM3,
                      Stream.SENSORHUB_MAX86178_STREAM4, Stream.SENSORHUB_MAX86178_STREAM5, Stream.SENSORHUB_MAX86178_STREAM6]:
            self._packet_sequence_number[stream] = [-1, -1]
        else:
            self._packet_sequence_number[stream] = -1

    def unsubscribe_stream(self, stream: Stream = None):
        """
        Unsubscribe the stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_study_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_adxl_application()
            unsubscribe_stream = application.unsubscribe_stream()
            print(unsubscribe_stream["payload"]["status"])
            # CommonStatus.SUBSCRIBER_REMOVED
        """
        stream = stream if stream else self._stream
        request_packet = StreamPacket(self._destination, CommonCommand.UNSUBSCRIBE_STREAM_REQ)
        request_packet.set_payload("stream_address", stream)
        response_packet = StreamPacket(self._destination, CommonCommand.UNSUBSCRIBE_STREAM_RES)
        response_packet = self._send_packet(request_packet, response_packet)
        self._unsubscribe_stream_data(stream=stream)
        return response_packet

    def _subscribe_without_communication(self, stream=None):
        self._subscribe_stream_data(stream=stream)
        self._update_timestamp(datetime.now(), stream=stream)

    def _subscribe_stream_data(self, stream=None, callback_function=None):
        stream = stream if stream else self._stream
        callback_function = callback_function if callback_function else self._callback_data
        data_packet_id = self._get_packet_id(CommonCommand.STREAM_DATA, stream)
        self._packet_manager.subscribe(data_packet_id, callback_function)

    def _unsubscribe_stream_data(self, stream=None, callback_function=None):
        stream = stream if stream else self._stream
        callback_function = callback_function if callback_function else self._callback_data
        data_packet_id = self._get_packet_id(CommonCommand.STREAM_DATA, stream)
        self._packet_manager.unsubscribe(data_packet_id, callback_function)
