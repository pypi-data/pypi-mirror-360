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
from typing import List, Dict

from ..core import utils
from .csv_logging import CSVLogger
from .common_stream import CommonStream
from ..core.packets.common_packets import VersionPacket
from ..core.packets.command_packet import CommandPacket
from ..core.packets.stream_data_packets import EDADataPacket
from ..core.packets.common_packets import DecimationFactorPacket
from ..core.enums.dcb_enums import DCBCommand, DCBConfigBlockIndex
from ..core.enums.common_enums import Application, Stream, CommonCommand
from ..core.enums.eda_enums import EDACommand, EDADFTWindow, ScaleResistor, EDAPowerMode
from ..core.packets.eda_packets import DynamicScalingPacket, ResistorTIACalibratePacket, \
    EDALibraryConfigPacket, EDADFTPacket, EDARegisterReadPacket, EDARegisterWritePacket, EDABaselineImpedancePacket, \
    EDAGetBaselineImpedancePacket, EDADCFGPacket, EDADCBLCFGPacket, EDADCBDCFGPacket, EDADCBCommandPacket, \
    EDASleepWakeupPacket

logger = logging.getLogger(__name__)


class EDAApplication(CommonStream):
    """
    EDA Application class.

    .. code-block:: python3
        :emphasize-lines: 4

        from adi_spo2_watch import SDK

        sdk = SDK("COM4")
        application = sdk.get_eda_application()

    """
    DFT_WINDOW_4 = EDADFTWindow.DFT_WINDOW_4
    DFT_WINDOW_8 = EDADFTWindow.DFT_WINDOW_8
    DFT_WINDOW_16 = EDADFTWindow.DFT_WINDOW_16
    DFT_WINDOW_32 = EDADFTWindow.DFT_WINDOW_32

    EDA_LCFG_BLOCK = DCBConfigBlockIndex.EDA_LCFG_BLOCK
    EDA_DCFG_BLOCK = DCBConfigBlockIndex.EDA_DCFG_BLOCK

    POWER_INVALID = EDAPowerMode.POWER_INVALID
    POWER_SLEEP = EDAPowerMode.POWER_SLEEP
    POWER_WAKEUP = EDAPowerMode.POWER_WAKEUP

    SCALE_RESISTOR_110 = ScaleResistor.SCALE_RESISTOR_110
    SCALE_RESISTOR_1K = ScaleResistor.SCALE_RESISTOR_1K
    SCALE_RESISTOR_2K = ScaleResistor.SCALE_RESISTOR_2K
    SCALE_RESISTOR_3K = ScaleResistor.SCALE_RESISTOR_3K
    SCALE_RESISTOR_4K = ScaleResistor.SCALE_RESISTOR_4K
    SCALE_RESISTOR_6K = ScaleResistor.SCALE_RESISTOR_6K
    SCALE_RESISTOR_8K = ScaleResistor.SCALE_RESISTOR_8K
    SCALE_RESISTOR_10K = ScaleResistor.SCALE_RESISTOR_10K
    SCALE_RESISTOR_12K = ScaleResistor.SCALE_RESISTOR_12K
    SCALE_RESISTOR_16K = ScaleResistor.SCALE_RESISTOR_16K
    SCALE_RESISTOR_20K = ScaleResistor.SCALE_RESISTOR_20K
    SCALE_RESISTOR_24K = ScaleResistor.SCALE_RESISTOR_24K
    SCALE_RESISTOR_30K = ScaleResistor.SCALE_RESISTOR_30K
    SCALE_RESISTOR_32K = ScaleResistor.SCALE_RESISTOR_32K
    SCALE_RESISTOR_40K = ScaleResistor.SCALE_RESISTOR_40K
    SCALE_RESISTOR_48K = ScaleResistor.SCALE_RESISTOR_48K
    SCALE_RESISTOR_64K = ScaleResistor.SCALE_RESISTOR_64K
    SCALE_RESISTOR_85K = ScaleResistor.SCALE_RESISTOR_85K
    SCALE_RESISTOR_96K = ScaleResistor.SCALE_RESISTOR_96K
    SCALE_RESISTOR_100K = ScaleResistor.SCALE_RESISTOR_100K
    SCALE_RESISTOR_120K = ScaleResistor.SCALE_RESISTOR_120K
    SCALE_RESISTOR_128K = ScaleResistor.SCALE_RESISTOR_128K
    SCALE_RESISTOR_160K = ScaleResistor.SCALE_RESISTOR_160K
    SCALE_RESISTOR_196K = ScaleResistor.SCALE_RESISTOR_196K
    SCALE_RESISTOR_256K = ScaleResistor.SCALE_RESISTOR_256K
    SCALE_RESISTOR_512K = ScaleResistor.SCALE_RESISTOR_512K

    def __init__(self, packet_manager):
        super().__init__(Application.EDA, Stream.EDA, packet_manager)
        self._dcb_size = 2

    def _eda_stream_helper(self, stream: Stream) -> Stream:
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
        List all supported streams.

        :return: Array of stream ID enums.
        :rtype: List[Stream]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.get_supported_streams()
            print(x)
            # [<Stream.EDA: ['0xC4', '0x02']>]
        """
        return [Stream.EDA]

    @staticmethod
    def get_supported_dcb_block() -> List[DCBConfigBlockIndex]:
        """
        List all supported DCBConfigBlockIndex.

        :return: Array of DCBConfigBlockIndex enums.
        :rtype: List[DCBConfigBlockIndex]
        """
        return [EDAApplication.EDA_LCFG_BLOCK, EDAApplication.EDA_DCFG_BLOCK]

    @staticmethod
    def get_supported_scales() -> List[ScaleResistor]:
        """
        List all supported scales for EDA.

        :return: Array of scales enums.
        :rtype: List

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.get_supported_scales()
            print(x)
            # [<ScaleResistor.SCALE_RESISTOR_100K: ['0x0', '0x14']>, ...]
        """
        return [EDAApplication.SCALE_RESISTOR_110, EDAApplication.SCALE_RESISTOR_1K, EDAApplication.SCALE_RESISTOR_2K,
                EDAApplication.SCALE_RESISTOR_3K, EDAApplication.SCALE_RESISTOR_4K, EDAApplication.SCALE_RESISTOR_6K,
                EDAApplication.SCALE_RESISTOR_8K, EDAApplication.SCALE_RESISTOR_10K, EDAApplication.SCALE_RESISTOR_12K,
                EDAApplication.SCALE_RESISTOR_16K, EDAApplication.SCALE_RESISTOR_20K, EDAApplication.SCALE_RESISTOR_24K,
                EDAApplication.SCALE_RESISTOR_30K, EDAApplication.SCALE_RESISTOR_32K, EDAApplication.SCALE_RESISTOR_40K,
                EDAApplication.SCALE_RESISTOR_48K, EDAApplication.SCALE_RESISTOR_64K, EDAApplication.SCALE_RESISTOR_85K,
                EDAApplication.SCALE_RESISTOR_96K, EDAApplication.SCALE_RESISTOR_100K,
                EDAApplication.SCALE_RESISTOR_120K, EDAApplication.SCALE_RESISTOR_128K,
                EDAApplication.SCALE_RESISTOR_160K, EDAApplication.SCALE_RESISTOR_196K,
                EDAApplication.SCALE_RESISTOR_256K, EDAApplication.SCALE_RESISTOR_512K]

    @staticmethod
    def get_supported_power_modes() -> List[EDAPowerMode]:
        """
        List all supported power mode for EDA.

        :return: Array of power modes enums.
        :rtype: List

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.get_supported_power_modes()
            print(x)
        """
        return [EDAApplication.POWER_INVALID, EDAApplication.POWER_SLEEP, EDAApplication.POWER_WAKEUP]

    @staticmethod
    def get_supported_dft_windows() -> List[EDADFTWindow]:
        """
        List all supported dft window for EDA.

        :return: Array of dft window enums.
        :rtype: List

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.get_supported_dft_windows()
            print(x)
            # [<EDADFTWindow.DFT_WINDOW_4: ['0x0']>, ... , <EDADFTWindow.DFT_WINDOW_32: ['0x3']>]
        """
        return [EDAApplication.DFT_WINDOW_4, EDAApplication.DFT_WINDOW_8, EDAApplication.DFT_WINDOW_16,
                EDAApplication.DFT_WINDOW_32]

    def calibrate_resistor_tia(self, min_scale: ScaleResistor, max_scale: ScaleResistor,
                               lp_resistor_tia: ScaleResistor) -> Dict:
        """
         Calibrate Resistor Trans Impedance Amplifier.

         :param min_scale: min scale for Resistor Trans Impedance Amplifier, use get_supported_scales()
                          | to list all supported scales.
         :param max_scale: max scale for Resistor Trans Impedance Amplifier, use get_supported_scales()
                          | to list all supported scales.
         :param lp_resistor_tia: lp_resistor_tia, use get_supported_scales() to list all supported scales.
         :type min_scale: ScaleResistor
         :type max_scale: ScaleResistor
         :type lp_resistor_tia: ScaleResistor
         :return: A response packet as dictionary.
         :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.get_supported_scales()
            print(x)
            # [<ScaleResistor.SCALE_RESISTOR_100K: ['0x0', '0x14']>, ... ]
            x = application.calibrate_resistor_tia(application.SCALE_RESISTOR_128K, application.SCALE_RESISTOR_256K,
                                                    application.SCALE_RESISTOR_256K)
            print(x["payload"]["status"])
            # CommonStatus.OK
         """
        request_packet = ResistorTIACalibratePacket(self._destination, EDACommand.RESISTOR_TIA_CAL_REQ)
        request_packet.set_payload("min_scale", min_scale)
        request_packet.set_payload("max_scale", max_scale)
        request_packet.set_payload("lp_resistor_tia", lp_resistor_tia)
        size = utils.join_multi_length_packets(max_scale.value) - utils.join_multi_length_packets(min_scale.value) + 1
        request_packet.set_payload("size", size)
        response_packet = ResistorTIACalibratePacket(self._destination, EDACommand.RESISTOR_TIA_CAL_RES)
        return self._send_packet(request_packet, response_packet)

    def get_decimation_factor(self) -> Dict:
        """
        Returns stream decimation factor.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.get_decimation_factor()
            print(x["payload"]["decimation_factor"])
            # 1

        """
        request_packet = DecimationFactorPacket(self._destination, CommonCommand.GET_STREAM_DEC_FACTOR_REQ)
        request_packet.set_payload("stream_address", self._stream)
        response_packet = DecimationFactorPacket(self._destination, CommonCommand.GET_STREAM_DEC_FACTOR_RES)
        return self._send_packet(request_packet, response_packet)

    def set_decimation_factor(self, decimation_factor: int) -> Dict:
        """
        Sets decimation factor for EDA stream.

        :param decimation_factor: decimation factor for stream
        :type decimation_factor: int
        :return: A response packet as dictionary
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Decimation Lower Limit
             - Decimation Upper Limit
           * - 0x01
             - 0x05

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.set_decimation_factor(2)
            print(x["payload"]["decimation_factor"])
            # 2

        """
        request_packet = DecimationFactorPacket(self._destination, CommonCommand.SET_STREAM_DEC_FACTOR_REQ)
        request_packet.set_payload("stream_address", self._stream)
        request_packet.set_payload("decimation_factor", decimation_factor)
        response_packet = DecimationFactorPacket(self._destination, CommonCommand.SET_STREAM_DEC_FACTOR_RES)
        return self._send_packet(request_packet, response_packet)

    def delete_device_configuration_block(self, dcb_block_index: DCBConfigBlockIndex) -> Dict:
        """
        Deletes EDA Device configuration block. use dcb_flag to see if packet is for lcfg or dcfg.

        :param dcb_block_index: dcb block index (lcfg/dcfg), use get_supported_dcb_block() to get list of all supported DCB index.
        :return: A response packet as dictionary.
        :rtype: dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            application.delete_device_configuration_block()
        """
        request_packet = EDADCBCommandPacket(self._destination, DCBCommand.ERASE_CONFIG_REQ)
        response_packet = EDADCBCommandPacket(self._destination, DCBCommand.ERASE_CONFIG_RES)
        request_packet.set_payload("dcb_block_index", dcb_block_index)
        return self._send_packet(request_packet, response_packet)

    def disable_dynamic_scaling(self) -> Dict:
        """
        Disables Dynamic scaling.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            application.disable_dynamic_scaling()
        """
        request_packet = DynamicScalingPacket(self._destination, EDACommand.DYNAMIC_SCALE_REQ)
        request_packet.set_payload("enabled", 0)
        response_packet = DynamicScalingPacket(self._destination, EDACommand.DYNAMIC_SCALE_RES)
        return self._send_packet(request_packet, response_packet)

    def enable_dynamic_scaling(self, min_scale: ScaleResistor, max_scale: ScaleResistor,
                               lp_resistor_tia: ScaleResistor) -> Dict:
        """
         Enables Dynamic scaling.

         :param min_scale: min scale for Resistor Trans Impedance Amplifier, use get_supported_scales()
                          | to list all supported scales.
         :param max_scale: max scale for Resistor Trans Impedance Amplifier, use get_supported_scales()
                          | to list all supported scales.
         :param lp_resistor_tia: lp_resistor_tia, use get_supported_scales() to list all supported scales.
         :type min_scale: ScaleResistor
         :type max_scale: ScaleResistor
         :type lp_resistor_tia: ScaleResistor
         :return: A response packet as dictionary.
         :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.get_supported_scales()
            print(x)
            # [<ScaleResistor.SCALE_RESISTOR_100K: ['0x0', '0x14']>, ... ]
            x = application.enable_dynamic_scaling(application.SCALE_RESISTOR_128K, application.SCALE_RESISTOR_256K,
                                                    application.SCALE_RESISTOR_256K)
            print(x["payload"]["status"])
            # CommonStatus.OK

         """
        request_packet = DynamicScalingPacket(self._destination, EDACommand.DYNAMIC_SCALE_REQ)
        request_packet.set_payload("enabled", 1)
        request_packet.set_payload("min_scale", min_scale)
        request_packet.set_payload("max_scale", max_scale)
        request_packet.set_payload("lp_resistor_tia", lp_resistor_tia)
        response_packet = DynamicScalingPacket(self._destination, EDACommand.DYNAMIC_SCALE_RES)
        return self._send_packet(request_packet, response_packet)

    def get_version(self) -> Dict:
        """
        Returns EDA version info.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_ecg_application()
            x = application.get_version()
            print(x["payload"]["major_version"])
            # 3
            print(x["payload"]["minor_version"])
            # 4
            print(x["payload"]["patch_version"])
            # 3
            print(x["payload"]["version_string"])
            # EDA_App
            print(x["payload"]["build_version"])
            # TEST EDA_VERSION STRING
        """
        request_packet = CommandPacket(self._destination, CommonCommand.GET_VERSION_REQ)
        response_packet = VersionPacket(self._destination, CommonCommand.GET_VERSION_RES)
        return self._send_packet(request_packet, response_packet)

    def read_device_configuration_block(self, dcb_block_index: DCBConfigBlockIndex) -> Dict:
        """
        Returns entire device configuration block.

        Note: read_device_configuration_block API has a size limit of 3.

        :param dcb_block_index: dcb block index (lcfg/dcfg), use get_supported_dcb_block() to get list of all supported DCB index.
        :return: A response packet as dictionary.
        :rtype: dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.read_device_configuration_block()

        """
        request_packet = EDADCBCommandPacket(self._destination, DCBCommand.READ_CONFIG_REQ)
        if dcb_block_index == self.EDA_LCFG_BLOCK:
            response_packet = EDADCBLCFGPacket(self._destination, DCBCommand.READ_CONFIG_RES)
        else:
            response_packet = EDADCBDCFGPacket(self._destination, DCBCommand.READ_CONFIG_RES)
        request_packet.set_payload("dcb_block_index", dcb_block_index)
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
             - 0x02

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.read_library_configuration([0x00])
            print(x["payload"]["data"])
            # [['0x0', '0x0']]

        """
        data = [[field, 0] for field in fields]
        request_packet = EDALibraryConfigPacket(self._destination, CommonCommand.READ_LCFG_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = EDALibraryConfigPacket(self._destination, CommonCommand.READ_LCFG_RES)
        return self._send_packet(request_packet, response_packet)

    def set_discrete_fourier_transformation(self, dft_window: EDADFTWindow) -> Dict:
        """
        Set Discrete Fourier Transformation for EDA.

        :param dft_window: DFT window for Discrete Fourier Transformation, use get_supported_dft_windows()
                          | to list all supported DFT window.
        :type dft_window: EDADFTWindow
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.get_supported_dft_windows()
            print(x)
            # [<EDADFTWindow.DFT_WINDOW_4: ['0x0']>, ... ,<EDADFTWindow.DFT_WINDOW_32: ['0x3']>]
            x = application.set_discrete_fourier_transformation(application.DFT_WINDOW_32)
            print(x["payload"]["dft_window"])
            # EDADFTWindow.DFT_WINDOW_32
        """
        request_packet = EDADFTPacket(self._destination, EDACommand.SET_DFT_NUM_REQ)
        request_packet.set_payload("dft_window", dft_window)
        response_packet = EDADFTPacket(self._destination, EDACommand.SET_DFT_NUM_RES)
        return self._send_packet(request_packet, response_packet)

    def write_device_configuration_block(self, addresses_values: List[List[int]],
                                         dcb_block_index: DCBConfigBlockIndex) -> Dict:
        """
        Writes the device configuration block values of specified addresses.
        This function takes a list of addresses and values to write, and returns a response packet as
        dictionary containing addresses and values.

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
             - 0x02

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.write_device_configuration_block([[0x0, 2], [0x1, 0x1]])
            print(x["payload"]["size"])
            # 2

        """
        if dcb_block_index == self.EDA_LCFG_BLOCK:
            request_packet = EDADCBLCFGPacket(self._destination, DCBCommand.WRITE_CONFIG_REQ)
        else:
            request_packet = EDADCBDCFGPacket(self._destination, DCBCommand.WRITE_CONFIG_REQ)
        request_packet.set_payload("dcb_block_index", dcb_block_index)
        request_packet.set_payload("size", len(addresses_values))
        request_packet.set_payload("data", addresses_values)
        response_packet = EDADCBCommandPacket(self._destination, DCBCommand.WRITE_CONFIG_RES)
        return self._send_packet(request_packet, response_packet)

    def write_device_configuration_block_from_file(self, filename: str, dcb_block_index: DCBConfigBlockIndex) -> Dict:
        """
        Writes the device configuration block values of specified addresses from file.
        use dcb_flag to see if packet is for lcfg or dcfg.

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
             - 0x02

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            application.write_device_configuration_block_from_file("eda_dcb.dcfg")

        """
        result = self.device_configuration_file_to_list(filename)
        if result:
            return self.write_device_configuration_block(result, dcb_block_index)

    def write_dcb_to_lcfg(self) -> Dict:
        """
        Writes Device configuration block data to library configuration.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.write_dcb_to_lcfg()
            print(x["payload"]["status"])
            # CommonStatus.OK
        """
        request_packet = CommandPacket(self._destination, CommonCommand.SET_LCFG_REQ)
        response_packet = CommandPacket(self._destination, CommonCommand.SET_LCFG_RES)
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
             - 0x02

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.write_library_configuration([[0x00, 0x1]])
            print(x["payload"]["data"])
            # [['0x0', '0x1']]

        """
        request_packet = EDALibraryConfigPacket(self._destination, CommonCommand.WRITE_LCFG_REQ)
        request_packet.set_payload("size", len(fields_values))
        request_packet.set_payload("data", fields_values)
        response_packet = EDALibraryConfigPacket(self._destination, CommonCommand.WRITE_LCFG_RES)
        return self._send_packet(request_packet, response_packet)

    def set_baseline_impedance(self, real_dft16: float, imaginary_dft16: float, real_dft8: float, imaginary_dft8: float,
                               resistor_baseline: int) -> Dict:
        """
        Set Baseline Impedance for EDA.

        :param real_dft16: Real DFT16
        :type real_dft16: float
        :param imaginary_dft16: Imaginary DFT16
        :type imaginary_dft16: float
        :param real_dft8: Real DFT8
        :type real_dft8: float
        :param imaginary_dft8: Imaginary DFT8
        :type imaginary_dft8: float
        :param resistor_baseline: Resistor Baseline
        :type resistor_baseline: int
        :return: A response packet as dictionary
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            packet = application.set_baseline_impedance(25000.5, 25000.5, 25000.5, 25000.5, 19900)
            print(packet)
        """
        request_packet = EDABaselineImpedancePacket(self._destination, EDACommand.BASELINE_IMP_SET_REQ)
        request_packet.set_payload("real_dft16", real_dft16)
        request_packet.set_payload("imaginary_dft16", imaginary_dft16)
        request_packet.set_payload("real_dft8", real_dft8)
        request_packet.set_payload("imaginary_dft8", imaginary_dft8)
        request_packet.set_payload("resistor_baseline", resistor_baseline)
        response_packet = EDABaselineImpedancePacket(self._destination, EDACommand.BASELINE_IMP_SET_RES)
        return self._send_packet(request_packet, response_packet)

    def get_baseline_impedance(self) -> Dict:
        """
        Get Baseline Impedance for EDA.

        :return: A response packet as dictionary
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            packet = application.get_baseline_impedance()
            print(packet)
        """
        request_packet = CommandPacket(self._destination, EDACommand.BASELINE_IMP_GET_REQ)
        response_packet = EDAGetBaselineImpedancePacket(self._destination, EDACommand.BASELINE_IMP_GET_RES)
        return self._send_packet(request_packet, response_packet)

    def reset_baseline_impedance(self) -> Dict:
        """
        Reset baseline impedance.

        :return: A response packet as dictionary
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.reset_baseline_impedance()
            print(x)
        """
        request_packet = EDABaselineImpedancePacket(self._destination, EDACommand.BASELINE_IMP_RESET_REQ)
        request_packet.set_payload("real_dft16", 0)
        request_packet.set_payload("imaginary_dft16", 0)
        request_packet.set_payload("real_dft8", 0)
        request_packet.set_payload("imaginary_dft8", 0)
        request_packet.set_payload("resistor_baseline", 0)
        response_packet = EDABaselineImpedancePacket(self._destination, EDACommand.BASELINE_IMP_RESET_RES)
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
             - 0x2E

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.read_register([0x15, 0x20, 0x2E])
            print(x["payload"]["data"])
            # [['0x15', '0x0'], ['0x20', '0x0'], ['0x2E', '0x0']]
        """
        data = [[address, 0] for address in addresses]
        request_packet = EDARegisterReadPacket(self._destination, CommonCommand.REGISTER_READ_32_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = EDARegisterReadPacket(self._destination, CommonCommand.REGISTER_READ_32_RES)
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
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x20
             - 0x2E

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.write_register([[0x20, 0x1], [0x21, 0x2], [0x2E, 0x3]])
            print(x["payload"]["data"])
            # [['0x20', '0x1'], ['0x21', '0x2'], ['0x2E', '0x3']]

        """
        request_packet = EDARegisterWritePacket(self._destination, CommonCommand.REGISTER_WRITE_32_REQ)
        request_packet.set_payload("size", len(addresses_values))
        request_packet.set_payload("data", addresses_values)
        response_packet = EDARegisterWritePacket(self._destination, CommonCommand.REGISTER_WRITE_32_RES)
        return self._send_packet(request_packet, response_packet)

    def _callback_data(self, packet, packet_id, callback_function=None, args=None):
        """
        Process and returns the data back to user's callback function.
        """
        self._callback_data_helper(packet, EDADataPacket())

    def get_sensor_status(self):
        """
        Returns packet with number of subscribers and number of sensor start request registered.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.get_sensor_status()
            print(x["payload"]["num_subscribers"], x["payload"]["num_start_registered"])
            # 0 0

        """
        return super().get_sensor_status()

    def start_and_subscribe_stream(self, stream: Stream = Stream.EDA):
        """
        Starts sensor and also subscribe to the stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Tuple[Dict, Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            start_sensor, subs_stream = application.start_and_subscribe_stream()
            print(start_sensor["payload"]["status"], subs_stream["payload"]["status"])
            # CommonStatus.STREAM_STARTED CommonStatus.SUBSCRIBER_ADDED
        """
        stream = self._eda_stream_helper(stream)
        return super().start_and_subscribe_stream(stream)

    def start_sensor(self):
        """
        Starts sensor.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            start_sensor = application.start_sensor()
            print(start_sensor["payload"]["status"])
            # CommonStatus.STREAM_STARTED
        """
        return super().start_sensor()

    def stop_and_unsubscribe_stream(self, stream: Stream = Stream.EDA):
        """
        Stops sensor and also Unsubscribe the stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Tuple[Dict, Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            stop_sensor, unsubscribe_stream = application.stop_and_unsubscribe_stream()
            print(stop_sensor["payload"]["status"], unsubscribe_stream["payload"]["status"])
            # CommonStatus.STREAM_STOPPED CommonStatus.SUBSCRIBER_REMOVED
        """
        stream = self._eda_stream_helper(stream)
        return super().stop_and_unsubscribe_stream(stream)

    def stop_sensor(self):
        """
        Stops sensor.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            stop_sensor = application.stop_sensor()
            print(stop_sensor["payload"]["status"])
            # CommonStatus.STREAM_STOPPED
        """
        return super().stop_sensor()

    def subscribe_stream(self, stream: Stream = Stream.EDA):
        """
        Subscribe to the stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            subs_stream = application.subscribe_stream()
            print(subs_stream["payload"]["status"])
            # CommonStatus.SUBSCRIBER_ADDED
        """
        stream = self._eda_stream_helper(stream)
        return super().subscribe_stream()

    def unsubscribe_stream(self, stream: Stream = Stream.EDA):
        """
        Unsubscribe the stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            unsubscribe_stream = application.unsubscribe_stream()
            print(unsubscribe_stream["payload"]["status"])
            # CommonStatus.SUBSCRIBER_REMOVED
        """
        stream = self._eda_stream_helper(stream)
        return super().unsubscribe_stream()

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
            application = sdk.get_eda_application()
            x = application.enable_csv_logging("eda.csv")
        """
        if header is None:
            header = ["Timestamp", "IMP Real(Ohms)", "IMP Img(Ohms)", "IMP Module(Ohms)", "IMP Phase(Rad)",
                      "ADM Real(Ohms)", "ADM Img(Ohms)", "ADM Module(Ohms)", "ADM Phase(Rad)", "Seq No."]
        self._csv_logger[Stream.EDA] = CSVLogger(filename, header)

    def disable_csv_logging(self) -> None:
        """
        Stops logging stream data into CSV.

        :return: None

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.disable_csv_logging()
        """
        if self._csv_logger.get(Stream.EDA):
            self._csv_logger[Stream.EDA].stop_logging()
        self._csv_logger[Stream.EDA] = None

    def get_ram_rtia_calibration_table(self) -> Dict:
        """
        Get RAM RTIA calibration table.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.get_ram_rtia_calibration_table()
        """
        request_packet = CommandPacket(self._destination, EDACommand.GET_RTIA_TABLE_RAM_REQ)
        response_packet = ResistorTIACalibratePacket(self._destination, EDACommand.GET_RTIA_TABLE_RAM_RES)
        return self._send_packet(request_packet, response_packet)

    def get_fds_rtia_calibration_table(self) -> Dict:
        """
        Get FDS RTIA calibration table.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.get_fds_rtia_calibration_table()
        """
        request_packet = CommandPacket(self._destination, EDACommand.GET_RTIA_TABLE_FDS_REQ)
        response_packet = ResistorTIACalibratePacket(self._destination, EDACommand.GET_RTIA_TABLE_FDS_RES)
        return self._send_packet(request_packet, response_packet)

    def delete_rtia_calibration_table(self) -> Dict:
        """
        Delete RTIA calibration table.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.delete_rtia_calibration_table()
        """
        request_packet = CommandPacket(self._destination, EDACommand.DELETE_RTIA_TABLE_IN_FDS_REQ)
        response_packet = CommandPacket(self._destination, EDACommand.DELETE_RTIA_TABLE_IN_FDS_RES)
        return self._send_packet(request_packet, response_packet)

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
            application = sdk.get_eda_application()
            x = application.get_device_configuration([0x00, 0x1])
        """
        data = [[address, 0] for address in addresses]
        request_packet = EDADCFGPacket(self._destination, EDACommand.READ_DCFG_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = EDADCFGPacket(self._destination, EDACommand.READ_DCFG_RES)
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
            application = sdk.get_eda_application()
            x = application.set_device_configuration([[0x0, 2], [0x1, 0x1]])
        """
        request_packet = EDADCFGPacket(self._destination, EDACommand.WRITE_DCFG_REQ)
        request_packet.set_payload("size", len(addresses_values))
        request_packet.set_payload("data", addresses_values)
        response_packet = EDADCFGPacket(self._destination, EDACommand.WRITE_DCFG_RES)
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
            application = sdk.get_eda_application()
            x = application.load_device_configuration()
        """
        request_packet = CommandPacket(self._destination, EDACommand.LOAD_DCFG_REQ)
        response_packet = CommandPacket(self._destination, EDACommand.LOAD_DCFG_RES)
        return self._send_packet(request_packet, response_packet)

    def set_power_mode(self, power_mode: EDAPowerMode) -> Dict:
        """
        Control the AD5940 ICs power state: to make it enter Hibernate or wakeup state.
        EPHY_LDO turn On needs to be done prior to this.

        :param power_mode: power mode, use get_supported_power_modes() to get all supported power modes.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_eda_application()
            x = application.set_power_mode(application.POWER_SLEEP)
        """
        request_packet = EDASleepWakeupPacket(self._destination, EDACommand.CONTROL_AD5940_SLEEP_WAKEUP_REQ)
        request_packet.set_payload("power_mode", power_mode)
        response_packet = EDASleepWakeupPacket(self._destination, EDACommand.CONTROL_AD5940_SLEEP_WAKEUP_RES)
        return self._send_packet(request_packet, response_packet)
