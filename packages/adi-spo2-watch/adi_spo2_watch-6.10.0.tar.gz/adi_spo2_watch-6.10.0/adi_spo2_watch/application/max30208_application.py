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


from .common_stream import CommonStream, logger
from .csv_logging import CSVLogger
from ..core.enums.common_enums import Application,Stream

from typing import Dict, List, Tuple, Callable

from ..core.packets.stream_data_packets import MAX30208TemperatureDataPacket


class MAX30208Application(CommonStream):
    """
           MAX30208 Application class.

           .. code-block:: python3
               :emphasize-lines: 4

               from adi_spo2_watch import SDK

               sdk = SDK("COM4")
               application = sdk.get_max30208_application()

           """

    MAX30208_TEMPERATURE_STREAM = Stream.MAX30208_TEMPERATURE_STREAM

    def __init__(self, packet_manager):
        super().__init__(Application.MAX30208, Stream.MAX30208_TEMPERATURE_STREAM, packet_manager)

    def _max30208_stream_helper(self, stream: Stream) -> Stream:
        """
        Confirms stream is from list of Enums.
        """
        if stream in self.get_supported_streams():
            return stream
        else:
            logger.warning(f"{stream} is not supported stream, choosing {self.get_supported_streams()[0]} "
                           f"as default stream. use get_supported_streams() to know all supported streams.")
            return self.get_supported_streams()[0]

    @staticmethod
    def get_supported_streams() -> List[Stream]:
        """
        List all supported streams for MAX30208.

        :return: Array of stream ID enums.
        :rtype: List[Stream]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_max30208_application()
            x = application.get_supported_streams()
            print(x)
        """
        return [MAX30208Application.MAX30208_TEMPERATURE_STREAM]

    def _callback_data(self, packet, packet_id, callback_function=None, args=None):
        """
        Process and returns the data back to user's callback function.
        """
        self._callback_data_helper(packet, MAX30208TemperatureDataPacket())

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
            application = sdk.get_max30208_application()
            x = application.enable_csv_logging("max30208_temp.csv")
        """
        if header is None:
            header = ["Timestamp", "Temperature"]
        self._csv_logger[Stream.MAX30208_TEMPERATURE_STREAM] = CSVLogger(filename, header)

    def disable_csv_logging(self) -> None:
        """
        Stops logging stream data into CSV.

        :return: None

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_max30208_application()
            x = application.disable_csv_logging()
        """
        if self._csv_logger.get(Stream.MAX30208_TEMPERATURE_STREAM):
            self._csv_logger[Stream.MAX30208_TEMPERATURE_STREAM].stop_logging()
        self._csv_logger[Stream.MAX30208_TEMPERATURE_STREAM] = None




