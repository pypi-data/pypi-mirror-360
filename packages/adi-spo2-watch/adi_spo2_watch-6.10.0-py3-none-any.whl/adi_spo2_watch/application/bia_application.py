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
from typing import List, Dict, Callable, Tuple

from ..core import utils
from .csv_logging import CSVLogger
from .common_stream import CommonStream
from ..core.packets.command_packet import CommandPacket
from ..core.packets.common_packets import StreamStatusPacket
from ..core.packets.stream_data_packets import BIADataPacket, BCMDataPacket
from ..core.enums.dcb_enums import DCBCommand, DCBConfigBlockIndex
from ..core.enums.common_enums import Application, Stream, CommonCommand
from ..core.enums.bia_enums import BIACommand, HSResistorTIA, BIADFTWindow
from ..core.packets.bia_packets import HSRTIAPacket, BIADFTPacket, BIALibraryConfigPacket, \
    BIADCFGPacket, BIADCBLCFGPacket, BIADCBDCFGPacket, BIADCBCommandPacket

logger = logging.getLogger(__name__)


class BIAApplication(CommonStream):
    """
    BIA Application class.

    .. code-block:: python3
        :emphasize-lines: 4

        from adi_spo2_watch import SDK

        sdk = SDK("COM4")
        application = sdk.get_bia_application()

    """

    STREAM_BIA = Stream.BIA
    STREAM_BCM = Stream.BCM

    RESISTOR_200 = HSResistorTIA.RESISTOR_200
    RESISTOR_1K = HSResistorTIA.RESISTOR_1K
    RESISTOR_5K = HSResistorTIA.RESISTOR_5K

    BIA_LCFG_BLOCK = DCBConfigBlockIndex.BIA_LCFG_BLOCK
    BIA_DCFG_BLOCK = DCBConfigBlockIndex.BIA_DCFG_BLOCK

    DFT_WINDOW_4 = BIADFTWindow.DFT_WINDOW_4
    DFT_WINDOW_8 = BIADFTWindow.DFT_WINDOW_8
    DFT_WINDOW_16 = BIADFTWindow.DFT_WINDOW_16
    DFT_WINDOW_32 = BIADFTWindow.DFT_WINDOW_32
    DFT_WINDOW_64 = BIADFTWindow.DFT_WINDOW_64
    DFT_WINDOW_128 = BIADFTWindow.DFT_WINDOW_128
    DFT_WINDOW_256 = BIADFTWindow.DFT_WINDOW_256
    DFT_WINDOW_512 = BIADFTWindow.DFT_WINDOW_512
    DFT_WINDOW_1024 = BIADFTWindow.DFT_WINDOW_1024
    DFT_WINDOW_2048 = BIADFTWindow.DFT_WINDOW_2048
    DFT_WINDOW_4096 = BIADFTWindow.DFT_WINDOW_4096
    DFT_WINDOW_8192 = BIADFTWindow.DFT_WINDOW_8192
    DFT_WINDOW_16384 = BIADFTWindow.DFT_WINDOW_16384

    def __init__(self, packet_manager):
        super().__init__(Application.BIA, Stream.BIA, packet_manager)

    def _bia_stream_helper(self, stream: Stream) -> Stream:
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
        List all supported streams for BIA.

        :return: Array of stream ID enums.
        :rtype: List[Stream]
        """
        return [BIAApplication.STREAM_BIA, BIAApplication.STREAM_BCM]

    @staticmethod
    def get_supported_dcb_block() -> List[DCBConfigBlockIndex]:
        """
        List all supported DCBConfigBlockIndex for BIA.

        :return: Array of DCBConfigBlockIndex enums.
        :rtype: List[DCBConfigBlockIndex]
        """
        return [BIAApplication.BIA_LCFG_BLOCK, BIAApplication.BIA_DCFG_BLOCK]

    @staticmethod
    def get_supported_dft_windows() -> List[BIADFTWindow]:
        """
        List all supported DFT window for BIA.

        :return: Array of DFT window enums.
        :rtype: List

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.get_supported_dft_windows()
            print(x)
            # [<BIADFTWindow.DFT_WINDOW_4: ['0x0', '0x0']>, ... , <BIADFTWindow.DFT_WINDOW_16384: ['0x0', '0x12']>]
        """
        return [BIAApplication.DFT_WINDOW_4, BIAApplication.DFT_WINDOW_8, BIAApplication.DFT_WINDOW_16,
                BIAApplication.DFT_WINDOW_32, BIAApplication.DFT_WINDOW_64, BIAApplication.DFT_WINDOW_128,
                BIAApplication.DFT_WINDOW_256, BIAApplication.DFT_WINDOW_512, BIAApplication.DFT_WINDOW_1024,
                BIAApplication.DFT_WINDOW_2048, BIAApplication.DFT_WINDOW_4096, BIAApplication.DFT_WINDOW_8192,
                BIAApplication.DFT_WINDOW_16384]

    @staticmethod
    def get_supported_hs_resistor_tia_ids() -> List[HSResistorTIA]:
        """
        List all supported High Speed Resistor Trans Impedance Amplifier for BIA.

        :return: Array of High Speed Resistor Trans Impedance Amplifier enums.
        :rtype: List

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.get_supported_hs_resistor_tia_ids()
            print(x)
            # [<HSResistorTIA.RESISTOR_200: ['0x0', '0x0']>, ... , <HSResistorTIA.RESISTOR_5K: ['0x0', '0x2']>]

        """
        return [BIAApplication.RESISTOR_200, BIAApplication.RESISTOR_1K, BIAApplication.RESISTOR_5K]

    def calibrate_hs_resistor_tia(self, hs_resistor_tia_id: HSResistorTIA) -> Dict:
        """
        Calibrate High Speed Resistor Trans Impedance Amplifier.

        :param hs_resistor_tia_id: High Speed Resistor Trans Impedance Amplifier to calibrate,
                                  | use get_supported_hs_resistor_tia_ids() to list all supported resistor.
        :type hs_resistor_tia_id: HSResistorTIA
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.get_supported_hs_resistor_tia_ids()
            print(x)
            # [<HSResistorTIA.RESISTOR_200: ['0x0', '0x0']>, ... , <HSResistorTIA.RESISTOR_5K: ['0x0', '0x2']>]
            x = application.calibrate_hs_resistor_tia(application.RESISTOR_1K)
            print(x["payload"]["hs_resistor_tia"])
            # HSResistorTIA.RESISTOR_1K

        """
        request_packet = HSRTIAPacket(self._destination, BIACommand.SET_HS_TRANS_IMPEDANCE_AMPLIFIER_CAL_REQ)
        request_packet.set_payload("hs_resistor_tia", hs_resistor_tia_id)
        response_packet = HSRTIAPacket(self._destination, BIACommand.SET_HS_TRANS_IMPEDANCE_AMPLIFIER_CAL_RES)
        return self._send_packet(request_packet, response_packet)

    def set_discrete_fourier_transformation(self, dft_window: BIADFTWindow) -> Dict:
        """
        Set Discrete Fourier Transformation for BIA.

        :param dft_window: DFT window for Discrete Fourier Transformation, use get_supported_dft_windows()
                          | to list all supported DFT window.
        :type dft_window: BIADFTWindow
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.get_supported_dft_windows()
            print(x)
            # [<BCMDFTWindow.DFT_WINDOW_4: ['0x0', '0x0']>, ... ,<BCMDFTWindow.DFT_WINDOW_16384: ['0x0', '0x12']>]
            x = application.set_discrete_fourier_transformation(application.DFT_WINDOW_16384)
            print(x["payload"]["dft_window"])
            # BCMDFTWindow.DFT_WINDOW_16384
        """
        request_packet = BIADFTPacket(self._destination, BIACommand.SET_DFT_NUM_REQ)
        request_packet.set_payload("dft_window", dft_window)
        response_packet = BIADFTPacket(self._destination, BIACommand.SET_DFT_NUM_RES)
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
             - 0x12

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.read_library_configuration([0x00])
            print(x["payload"]["data"])
            # [['0x0', '0x0']]

        """
        data = [[field, 0] for field in fields]
        request_packet = BIALibraryConfigPacket(self._destination, CommonCommand.READ_LCFG_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = BIALibraryConfigPacket(self._destination, CommonCommand.READ_LCFG_RES)
        response_dict = self._send_packet(request_packet, response_packet)
        response_dict["payload"]["data"] = self._decode_bia_lcfg_payload_data(response_dict["payload"]["data"])
        return response_dict

    @staticmethod
    def _decode_bia_lcfg_payload_data(data):
        import struct
        output = []
        for val in data:
            address = int(val[0], 16)
            value = int(val[1], 16)
            if 0 <= address <= 9 or 0x12 <= address:
                byte = value.to_bytes(4, 'little')
                float_data = int(struct.unpack("f", byte)[0])
                value = '0x%02X' % float_data
                output.append([val[0], value])
            else:
                output.append([val[0], val[1]])
        return output

    @staticmethod
    def _encode_bia_lcfg_payload_data(data):
        import struct
        output = []
        for val in data:
            address = int(val[0])
            value = int(val[1])
            if 0 <= address <= 9 or 0x12 <= address:
                float_bytes = list(struct.pack("f", value))
                int_bytes = struct.unpack("L", bytes(float_bytes))[0]
                output.append([val[0], int_bytes])
            else:
                output.append([val[0], val[1]])
        return output

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
             - 0x1B

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.write_library_configuration([[0x00, 0x1]])
            print(x["payload"]["data"])
            # [['0x0', '0x1']]

        """
        request_packet = BIALibraryConfigPacket(self._destination, CommonCommand.WRITE_LCFG_REQ)
        request_packet.set_payload("size", len(fields_values))
        fields_values = self._encode_bia_lcfg_payload_data(fields_values)
        request_packet.set_payload("data", fields_values)
        response_packet = BIALibraryConfigPacket(self._destination, CommonCommand.WRITE_LCFG_RES)
        response_dict = self._send_packet(request_packet, response_packet)
        response_dict["payload"]["data"] = self._decode_bia_lcfg_payload_data(response_dict["payload"]["data"])
        return response_dict

    def write_dcb_to_lcfg(self) -> Dict:
        """
        Writes Device configuration block data to library configuration.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.write_dcb_to_lcfg()
            print(x["payload"]["status"])
            # CommonStatus.OK
        """
        request_packet = CommandPacket(self._destination, CommonCommand.SET_LCFG_REQ)
        response_packet = CommandPacket(self._destination, CommonCommand.SET_LCFG_RES)
        return self._send_packet(request_packet, response_packet)

    def delete_device_configuration_block(self, dcb_block_index: DCBConfigBlockIndex) -> Dict:
        """
        Deletes BIA Device configuration block. use dcb_flag to see if packet is for lcfg or dcfg.

        :param dcb_block_index: dcb block index (lcfg/dcfg), use get_supported_dcb_block() to get all supported DCB index.
        :return: A response packet as dictionary.
        :rtype: dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            application.delete_device_configuration_block()
        """
        request_packet = BIADCBCommandPacket(self._destination, DCBCommand.ERASE_CONFIG_REQ)
        response_packet = BIADCBCommandPacket(self._destination, DCBCommand.ERASE_CONFIG_RES)
        request_packet.set_payload("dcb_block_index", dcb_block_index)
        return self._send_packet(request_packet, response_packet)

    def read_device_configuration_block(self, dcb_block_index: DCBConfigBlockIndex) -> Dict:
        """
        Returns entire device configuration block.

        :param dcb_block_index: dcb block index (lcfg/dcfg), use get_supported_dcb_block() to get list of all supported DCB index.
        :return: A response packet as dictionary.
        :rtype: dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.read_device_configuration_block()

        """
        request_packet = BIADCBCommandPacket(self._destination, DCBCommand.READ_CONFIG_REQ)
        if dcb_block_index == self.BIA_LCFG_BLOCK:
            response_packet = BIADCBLCFGPacket(self._destination, DCBCommand.READ_CONFIG_RES)
        else:
            response_packet = BIADCBDCFGPacket(self._destination, DCBCommand.READ_CONFIG_RES)
        request_packet.set_payload("dcb_block_index", dcb_block_index)
        packet = self._send_packet(request_packet, response_packet)
        if dcb_block_index == self.BIA_LCFG_BLOCK:
            packet["payload"]["data"] = utils.add_index_to_array(packet["payload"]["data"], to_hex=True)
        return packet

    def write_device_configuration_block(self, addresses_values: List[List[int]],
                                         dcb_block_index: DCBConfigBlockIndex) -> Dict:
        """
        Writes the device configuration block values of specified addresses.
        This function takes a list of addresses and values to write, and returns a response packet as
        dictionary containing addresses and values. use dcb_flag to see if packet is for lcfg or dcfg.

        :param addresses_values: List of addresses and values to write.
        :type addresses_values: List[List[int]]
        :param dcb_block_index: dcb block index (lcfg/dcfg), use get_supported_dcb_block() to get list of all supported DCB index.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x00
             - 0x1B

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.write_device_configuration_block([[0x0, 2], [0x1, 0x1]])
            print(x["payload"]["size"])
            # 2

        """
        dcb_array = []
        for address_value in addresses_values:
            dcb_array.append(address_value[1])

        if dcb_block_index == self.BIA_LCFG_BLOCK:
            request_packet = BIADCBLCFGPacket(self._destination, DCBCommand.WRITE_CONFIG_REQ)
        else:
            request_packet = BIADCBDCFGPacket(self._destination, DCBCommand.WRITE_CONFIG_REQ)
        request_packet.set_payload("dcb_block_index", dcb_block_index)
        request_packet.set_payload("size", len(dcb_array))
        if dcb_block_index == self.BIA_LCFG_BLOCK:
            request_packet.set_payload("data", dcb_array)
        else:
            request_packet.set_payload("data", addresses_values)
        response_packet = BIADCBCommandPacket(self._destination, DCBCommand.WRITE_CONFIG_RES)
        return self._send_packet(request_packet, response_packet)

    def write_device_configuration_block_from_file(self, filename: str, dcb_block_index: DCBConfigBlockIndex) -> Dict:
        """
        Writes the device configuration block values of specified addresses from file.

        :param filename: dcb filename
        :param dcb_block_index: dcb block index (lcfg/dcfg), use get_supported_dcb_block() to get list of all supported DCB index.
        :return: A response packet as dictionary.
        :rtype: dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x00
             - 0x12

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            application.write_device_configuration_block_from_file("bia_dcb.dcfg")

        """
        result = self.device_configuration_file_to_list(filename)
        if result:
            return self.write_device_configuration_block(result, dcb_block_index)

    def _callback_data(self, packet, packet_id, callback_function=None, args=None):
        """
        Process and returns the data back to user's callback function.
        """
        stream = Stream(packet[:2])
        if stream == self.STREAM_BIA:
            self._callback_data_helper(packet, BIADataPacket(), stream)
        else:
            self._callback_data_helper(packet, BCMDataPacket(), stream)

    def enable_csv_logging(self, filename: str, header: List = None, stream: Stream = STREAM_BIA) -> None:
        """
        Start logging stream data into CSV.

        :param filename: Name of the CSV file.
        :param header: Header list of the CSV file.
        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.enable_csv_logging("bcm.csv")
        """
        stream = self._bia_stream_helper(stream)
        if header is None:
            if stream == self.STREAM_BIA:
                header = ["Timestamp", "IMP Real(Ohms)", "IMP Img(Ohms)", "IMP Module(Ohms)", "IMP Phase(Rad)",
                          "ADM Real(Ohms)", "ADM Img(Ohms)", "ADM Module(Ohms)", "ADM Phase(Rad)", "Seq No.",
                          "Frequency Index"]
            else:
                header = ["Timestamp", "FFM Estimated", "BMI", "Fat Percent", "Sequence Number"]
        self._csv_logger[stream] = CSVLogger(filename, header)

    def disable_csv_logging(self, stream: Stream = STREAM_BIA) -> None:
        """
        Stops logging stream data into CSV.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.disable_csv_logging()
        """
        stream = self._bia_stream_helper(stream)
        if self._csv_logger.get(stream):
            self._csv_logger[stream].stop_logging()
        self._csv_logger[stream] = None

    def get_device_configuration(self, addresses: List[int]) -> Dict:
        """
        Get device configuration.

        :param addresses: List of field values to read.
        :type addresses: List[int]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.get_device_configuration([0x00, 0x1])
        """
        data = [[address, 0] for address in addresses]
        request_packet = BIADCFGPacket(self._destination, BIACommand.READ_DCFG_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = BIADCFGPacket(self._destination, BIACommand.READ_DCFG_RES)
        return self._send_packet(request_packet, response_packet)

    def set_device_configuration(self, addresses_values: List[List[int]]) -> Dict:
        """
        Set device configuration.

        :param addresses_values: List of addresses and values to set.
        :type addresses_values: List[List[int]]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.set_device_configuration([[0x0, 2], [0x1, 0x1]])
        """
        request_packet = BIADCFGPacket(self._destination, BIACommand.WRITE_DCFG_REQ)
        request_packet.set_payload("size", len(addresses_values))
        request_packet.set_payload("data", addresses_values)
        response_packet = BIADCFGPacket(self._destination, BIACommand.WRITE_DCFG_RES)
        return self._send_packet(request_packet, response_packet)

    def load_device_configuration(self) -> Dict:
        """
        Load device configuration.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.load_device_configuration()
        """
        request_packet = CommandPacket(self._destination, BIACommand.LOAD_DCFG_REQ)
        response_packet = CommandPacket(self._destination, BIACommand.LOAD_DCFG_RES)
        return self._send_packet(request_packet, response_packet)

    # noinspection PyTypeChecker
    def set_callback(self, callback_function: Callable, args: Tuple = (), stream: Stream = STREAM_BIA) -> None:
        """
        Sets the callback for the stream data.

        :param callback_function: callback function for specified BIA stream.
        :param args: optional arguments that will be passed with the callback.
        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :type stream: Stream
        :return: None

        .. code-block:: python3
            :emphasize-lines: 4,12

            from adi_spo2_watch import SDK

            # make sure optional arguments have default value to prevent them causing Exceptions.
            def callback(data, optional1=None, optional2=None):
                print(data)

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            # these optional arguments can be used to pass file, matplotlib or other objects to manipulate data.
            optional_arg1 = "1"
            optional_arg2 = "2"
            application.set_callback(callback, args=(optional_arg1, optional_arg2), stream=application.STREAM_BIA)
        """
        stream = self._bia_stream_helper(stream)
        self._callback_function[stream] = callback_function
        self._args[stream] = args

    def get_sensor_status(self, stream: Stream = STREAM_BIA) -> Dict:
        """
        Returns packet with number of subscribers and number of sensor start request registered.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.get_sensor_status(application.STREAM_BIA)
            print(x["payload"]["num_subscribers"], x["payload"]["num_start_registered"])
            # 0 0
        """
        stream = self._bia_stream_helper(stream)
        request_packet = StreamStatusPacket(self._destination, CommonCommand.GET_SENSOR_STATUS_REQ)
        request_packet.set_payload("stream_address", stream)
        response_packet = StreamStatusPacket(self._destination, CommonCommand.GET_SENSOR_STATUS_RES)
        return self._send_packet(request_packet, response_packet)

    def start_and_subscribe_stream(self, stream: Stream = STREAM_BIA) -> Tuple[Dict, Dict]:
        """
        Starts BIA sensor and also subscribe to the specified BIA stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :type stream: Stream
        :return: A response packet as dictionary.
        :rtype: Tuple[Dict, Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.get_supported_streams()
            start_sensor, subs_stream = application.start_and_subscribe_stream()
            print(start_sensor["payload"]["status"], subs_stream["payload"]["status"])
            # CommonStatus.STREAM_STARTED CommonStatus.SUBSCRIBER_ADDED
        """
        stream = self._bia_stream_helper(stream)
        return super().start_and_subscribe_stream(stream)

    def stop_and_unsubscribe_stream(self, stream: Stream = STREAM_BIA) -> Tuple[Dict, Dict]:
        """
        Stops BIA sensor and also Unsubscribe the specified BIA stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :type stream: Stream
        :return: A response packet as dictionary.
        :rtype: Tuple[Dict, Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.get_supported_streams()
            stop_sensor, unsubscribe_stream = application.stop_and_unsubscribe_stream()
            print(stop_sensor["payload"]["status"], unsubscribe_stream["payload"]["status"])
            # CommonStatus.STREAM_STOPPED CommonStatus.SUBSCRIBER_REMOVED
        """
        stream = self._bia_stream_helper(stream)
        return super().stop_and_unsubscribe_stream(stream)

    def subscribe_stream(self, stream: Stream = STREAM_BIA) -> Dict:
        """
        Subscribe to the specified BIA stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :type stream: Stream
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.get_supported_streams()
            subs_stream = application.subscribe_stream()
            print(subs_stream["payload"]["status"])
            # CommonStatus.SUBSCRIBER_ADDED
        """
        stream = self._bia_stream_helper(stream)
        return super().subscribe_stream(stream)

    def unsubscribe_stream(self, stream: Stream = STREAM_BIA) -> Dict:
        """
        Unsubscribe the specified BIA stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :type stream: Stream
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_bia_application()
            x = application.get_supported_streams()
            unsubscribe_stream = application.unsubscribe_stream()
            print(unsubscribe_stream["payload"]["status"])
            # CommonStatus.SUBSCRIBER_REMOVED
        """
        stream = self._bia_stream_helper(stream)
        return super().unsubscribe_stream(stream)
