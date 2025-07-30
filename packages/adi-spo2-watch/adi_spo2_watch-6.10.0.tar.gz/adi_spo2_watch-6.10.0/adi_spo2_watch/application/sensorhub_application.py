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
import math
from typing import Dict, List, Tuple, Callable
from .common_stream import CommonStream

from .csv_logging import CSVLogger
from ..core.packets.common_packets import StreamStatusPacket
from ..core.enums.common_enums import Application, Stream, CommonCommand
from ..core.enums.sensorhub_enums import SHCommand, SHMode, SHConfigID, ADXL367MeasRange, SHDevice, ADXL367Device, MAX86178Device, ALGODevice, AlgoDecimation, Spo2Coeff
from ..core.packets.sensorhub_packets import SetBootLoaderModePacket, GetPageSizePacket, SetPageNumberPacket, \
    SetIVPacket, BootloaderExitModePacket, BootloaderGetOperationModePacket, BootloaderTestDataPacket, \
    DownloadSensorHubPagePacket, SetOpModePacket, SetAuthorizationPacket, EraseFlashPacket, SetFrequencyPacket, \
    Adxl367SelfTestRequestPacket, Adxl367SelfTestResponsePacket, FirmwareVersionPacket, AlgoVersionPacket, RegOpPacket, ADXL367ConfigPacket, \
    MAX86178ConfigPacket, MAX86178DCBCommandPacket, MAX86178DCBPacket, ADXL367DCBCommandPacket, ADXL367DCBPacket, \
    ADXL367CalibrationConfigCommandPacket, WASConfigPacket, WASLCFGPacket, WASLibraryConfigPacket, SHHardResetAPPModePacket, \
    RegdumpRequestPacket, RegdumpResponsePacket, LPSelfTestPacket, DecimationRatePacket, GenericEnablePacket, Spo2CoeffPacket

from ..core.packets.stream_data_packets import SHMAX86178DataPacket, SHMAX86178ECGDataPacket, SHMAX86178BIOZDataPacket, SHADXLDataPacket, SHHRMDataPacket, SHSPO2DataPacket, \
    SHSPO2DebugDataPacket, SHRegConfPacket, SHDebugRegConfPacket, SHRRDataPacket, SHPRDataPacket, SHAMADataPacket

logger = logging.getLogger(__name__)
class SensorHubApplication(CommonStream):
    """
       Sensor Hub Application class.

       .. code-block:: python3
           :emphasize-lines: 4

           from adi_spo2_watch import SDK

           sdk = SDK("COM4")
           application = sdk.get_sensorhub_application()

       """

    SH_MAX86178_STREAM1 = Stream.SENSORHUB_MAX86178_STREAM1
    SH_MAX86178_STREAM2 = Stream.SENSORHUB_MAX86178_STREAM2
    SH_MAX86178_STREAM3 = Stream.SENSORHUB_MAX86178_STREAM3
    SH_MAX86178_STREAM4 = Stream.SENSORHUB_MAX86178_STREAM4
    SH_MAX86178_STREAM5 = Stream.SENSORHUB_MAX86178_STREAM5
    SH_MAX86178_STREAM6 = Stream.SENSORHUB_MAX86178_STREAM6
    SH_MAX86178_ECG_STREAM = Stream.SENSORHUB_MAX86178_ECG_STREAM
    SH_MAX86178_BIOZ_STREAM = Stream.SENSORHUB_MAX86178_BIOZ_STREAM
    SH_ADXL_STREAM = Stream.SENSORHUB_ADXL367_STREAM
    SH_HRM_STREAM = Stream.SENSORHUB_HRM_STREAM
    SH_SPO2_STREAM = Stream.SENSORHUB_SPO2_STREAM
    SH_SPO2_DEBUG_STREAM = Stream.SENSORHUB_SPO2_DEBUG_STREAM
    SH_REG_CONF_STREAM = Stream.SENSORHUB_REG_CONF_STREAM
    SH_DEBUG_REG_CONF_STREAM = Stream.SENSORHUB_DEBUG_REG_CONF_STREAM
    SH_RR_STREAM = Stream.SENSORHUB_RR_STREAM
    SH_PR_STREAM = Stream.SENSORHUB_PR_STREAM
    SH_AMA_STREAM = Stream.SENSORHUB_AMA_STREAM

    SH_APPLICATION_MODE = SHMode.SENSORHUB_APPLICATION_MODE
    SH_BOOTLOADER_MODE = SHMode.SENSORHUB_BOOTLOADER_MODE

    SH_CONFIG_RAW_MODE = SHConfigID.SENSORHUB_RAW_MODE
    SH_CONFIG_ALGO_MODE = SHConfigID.SENSORHUB_ALGO_MODE
    SH_CONFIG_PPG_MODE = SHConfigID.SENSORHUB_PPG_MODE
    SH_CONFIG_ADXL_MODE = SHConfigID.SENSORHUB_ADXL_MODE
    SH_CONFIG_ECG_MODE = SHConfigID.SENSORHUB_ECG_MODE
    SH_CONFIG_BIOZ_MODE = SHConfigID.SENSORHUB_BIOZ_MODE
    SH_CONFIG_AMA_MODE = SHConfigID.SENSORHUB_AMA_MODE

    SH_ADXL367_MEAS_RANGE_2G = ADXL367MeasRange.MEAS_RANGE_2G
    SH_ADXL367_MEAS_RANGE_4G = ADXL367MeasRange.MEAS_RANGE_4G
    SH_ADXL367_MEAS_RANGE_8G = ADXL367MeasRange.MEAS_RANGE_8G

    DEVICE_G_R_IR = MAX86178Device.DEVICE_G_R_IR
    DEVICE_ECG = MAX86178Device.DEVICE_ECG
    DEVICE_BIOZ = MAX86178Device.DEVICE_BIOZ

    DEVICE_367 = ADXL367Device.DEVICE_367

    DEVICE_WAS = ALGODevice.DEVICE_WAS
    DEVICE_AMA = ALGODevice.DEVICE_AMA

    MAX86178_DEVICE = SHDevice.MAX86178_DEVICE
    ADXL367_DEVICE = SHDevice.ADXL367_DEVICE
    SENSORHUB_DEVICE = SHDevice.SENSORHUB_DEVICE
    MAX86178_ECG_DEVICE = SHDevice.MAX86178_ECG_DEVICE

    SPO2_COEFF_MLP = Spo2Coeff.SPO2_COEFF_MLP
    SPO2_COEFF_PTR = Spo2Coeff.SPO2_COEFF_PTR

    def __init__(self, packet_manager):
        super().__init__(Application.SENSORHUB, Stream.SENSORHUB_MAX86178_STREAM1, packet_manager)
        self._lcfg_size = 56
        self._max86178_dcb_size = 55

    def _sensorhub_stream_helper(self, stream: Stream) -> Stream:
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
        List all supported streams for Sensorhub.

        :return: Array of stream ID enums.
        :rtype: List[Stream]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_streams()
            print(x)
            # [<Stream.SENSORHUB_MAX86178_STREAM1: ['0xC8', '0x27']>, ... , <Stream.SENSORHUB_HRM_STREAM: ['0xC8', 0x2B']>]
        """
        return [SensorHubApplication.SH_MAX86178_STREAM1, SensorHubApplication.SH_MAX86178_STREAM2, SensorHubApplication.SH_MAX86178_STREAM3,
                SensorHubApplication.SH_MAX86178_STREAM4, SensorHubApplication.SH_MAX86178_STREAM5, SensorHubApplication.SH_MAX86178_STREAM6,
                SensorHubApplication.SH_MAX86178_ECG_STREAM, SensorHubApplication.SH_MAX86178_BIOZ_STREAM, SensorHubApplication.SH_ADXL_STREAM, 
                SensorHubApplication.SH_AMA_STREAM, SensorHubApplication.SH_HRM_STREAM, SensorHubApplication.SH_SPO2_STREAM, 
                SensorHubApplication.SH_SPO2_DEBUG_STREAM, SensorHubApplication.SH_RR_STREAM, SensorHubApplication.SH_PR_STREAM, 
                SensorHubApplication.SH_REG_CONF_STREAM, SensorHubApplication.SH_DEBUG_REG_CONF_STREAM]

    @staticmethod
    def get_supported_config_ids() -> List[SHConfigID]:
        """
        List all supported Sensorhub configurations

        :return: Array of config ID enums.
        :rtype: List[SHConfigID]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_config_ids()
            print(x)
            # [<SHConfigID.SENSORHUB_RAW_MODE: ['0x00']>, ... , <SHConfigID.SENSORHUB_ADXL_MODE: ['0x05']>]
        """
        return [SensorHubApplication.SH_CONFIG_RAW_MODE, SensorHubApplication.SH_CONFIG_ALGO_MODE, SensorHubApplication.SH_CONFIG_PPG_MODE,
                SensorHubApplication.SH_CONFIG_ADXL_MODE, SensorHubApplication.SH_CONFIG_ECG_MODE, SensorHubApplication.SH_CONFIG_BIOZ_MODE, 
                SensorHubApplication.SH_CONFIG_AMA_MODE]

    @staticmethod
    def get_supported_devices() -> List[SHDevice]:
        """
        List all supported devices.

        :return: Array of device ID enums.
        :rtype: List[SHDevice]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_devices()
            print(x)
            # [<SensorHubApplication.MAX81678_DEVICE: ['0x1']>, ...]
        """
        return [SensorHubApplication.MAX86178_DEVICE, SensorHubApplication.ADXL367_DEVICE, SensorHubApplication.SENSORHUB_DEVICE, SensorHubApplication.MAX86178_ECG_DEVICE]

    @staticmethod
    def get_supported_adxl367_devices() -> List[ADXL367Device]:
        """
        List all supported device ID for adxl367.

        :return: Array of device ID enums.
        :rtype: List[ADXL367Device]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_adxl367_devices()
            print(x)
            # [<SensorHubApplication.DEVICE_367: ['0x6F', '0x1']>]
        """
        return [SensorHubApplication.DEVICE_367]

    @staticmethod
    def get_supported_was_devices() -> List[ALGODevice]:
        """
        List all supported device ID.

        :return: Array of device ID enums.
        :rtype: List[ALGODevice]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_was_devices()
            print(x)
            # [<SensorHubApplication.DEVICE_WAS: ['0x46']>]
        """
        return [SensorHubApplication.DEVICE_WAS, SensorHubApplication.DEVICE_AMA]

    @staticmethod
    def get_supported_max86178_devices() -> List[MAX86178Device]:
        """
        List all supported device ID for max86178.

        :return: Array of device ID enums.
        :rtype: List[MAX86178Device]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_max86178_devices()
            print(x)
            # [<SensorHubApplication.DEVICE_G_R_IR: ['0x30']>]
        """
        return [SensorHubApplication.DEVICE_G_R_IR, SensorHubApplication.DEVICE_ECG, SensorHubApplication.DEVICE_BIOZ]

    @staticmethod
    def get_supported_adxl367_meas_range() -> List[ADXL367MeasRange]:
        """
        List all supported measurement range for ADXL367

        :return: Array of measurement range enums.
        :rtype: List[ADXL367MeasRange]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_adxl367_meas_range()
            print(x)
            # [<SensorHubApplication.SH_ADXL367_MEAS_RANGE_2G: ['0x00']>,...]
        """
        return [SensorHubApplication.SH_ADXL367_MEAS_RANGE_2G, SensorHubApplication.SH_ADXL367_MEAS_RANGE_4G,
                SensorHubApplication.SH_ADXL367_MEAS_RANGE_8G]
    
    @staticmethod
    def get_supported_spo2coeffs() -> List[Spo2Coeff]:
        """
        List all supported Spo2 Coefficients

        :return: Array of Spo2 coefficient enums.
        :rtype: List[Spo2Coeff]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_spo2coeffs()
            print(x)
            # [<SensorHubApplication.SPO2_COEFF_MLP: ['0x00']>, <SensorHubApplication.SPO2_COEFF_PTR: ['0x01']>]
        """
        return [SensorHubApplication.SPO2_COEFF_MLP, SensorHubApplication.SPO2_COEFF_PTR]

    def get_sensor_status(self, stream: Stream = SH_MAX86178_STREAM1) -> Dict:
        """
        Returns packet with number of subscribers and number of sensor start request registered.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_sensor_status(application.SH_MAX86178_STREAM1)
            print(x["payload"]["num_subscribers"], x["payload"]["num_start_registered"])
            # 0 0
        """
        stream = self._sensorhub_stream_helper(stream)
        request_packet = StreamStatusPacket(self._destination, CommonCommand.GET_SENSOR_STATUS_REQ)
        request_packet.set_payload("stream_address", stream)
        response_packet = StreamStatusPacket(self._destination, CommonCommand.GET_SENSOR_STATUS_RES)
        return self._send_packet(request_packet, response_packet)

    def start_and_subscribe_stream(self, stream: Stream = SH_MAX86178_STREAM1) -> Tuple[Dict, Dict]:
        """
        Starts sensorhub and also subscribes to the specified stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :type stream: Stream
        :return: A response packet as dictionary.
        :rtype: Tuple[Dict, Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_streams()
            # [<Stream.SENSORHUB_MAX86178_STREAM1: [0xC8, 0x27]>, ... , <Stream.SENSORHUB_ADXL367_STREAM: [0xC8, 0x2C]>]
            start_sensor, subs_stream = application.start_and_subscribe_stream()
            print(start_sensor["payload"]["status"], subs_stream["payload"]["status"])
            # CommonStatus.STREAM_STARTED CommonStatus.SUBSCRIBER_ADDED
        """
        stream = self._sensorhub_stream_helper(stream)
        return super().start_and_subscribe_stream(stream)

    def stop_and_unsubscribe_stream(self, stream: Stream = SH_MAX86178_STREAM1) -> Tuple[Dict, Dict]:
        """
        Stops sensorhub and also unsubscribes from specified stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :type stream: Stream
        :return: A response packet as dictionary.
        :rtype: Tuple[Dict, Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_streams()
            # [<Stream.SENSORHUB_MAX86178_STREAM1: [0xC8, 0x27]>, ... , <Stream.SENSORHUB_ADXL367_STREAM: [0xC8, 0x2C]>]
            stop_sensor, unsubscribe_stream = application.stop_and_unsubscribe_stream()
            print(stop_sensor["payload"]["status"], unsubscribe_stream["payload"]["status"])
            # CommonStatus.STREAM_STOPPED CommonStatus.SUBSCRIBER_REMOVED
        """
        stream = self._sensorhub_stream_helper(stream)
        return super().stop_and_unsubscribe_stream(stream)

    def subscribe_stream(self, stream: Stream = SH_MAX86178_STREAM1) -> Dict:
        """
        Subscribe to the specified stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :type stream: Stream
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_streams()
            # [<Stream.SENSORHUB_MAX86178_STREAM1: [0xC8, 0x27]>, ... , <Stream.SENSORHUB_ADXL367_STREAM: [0xC8, 0x2C]>]
            subs_stream = application.subscribe_stream()
            print(subs_stream["payload"]["status"])
            # CommonStatus.SUBSCRIBER_ADDED
        """
        stream = self._sensorhub_stream_helper(stream)
        return super().subscribe_stream(stream)

    def unsubscribe_stream(self, stream: Stream = SH_MAX86178_STREAM1) -> Dict:
        """
        Unsubscribe the specified stream.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :type stream: Stream
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_streams()
            # [<Stream.SENSORHUB_MAX86178_STREAM1: [0xC8, 0x27]>, ... , <Stream.SENSORHUB_ADXL367_STREAM: [0xC8, 0x2C]>]
            unsubscribe_stream = application.unsubscribe_stream()
            print(unsubscribe_stream["payload"]["status"])
            # CommonStatus.SUBSCRIBER_REMOVED
        """
        stream = self._sensorhub_stream_helper(stream)
        return super().unsubscribe_stream(stream)

    def set_callback(self, callback_function: Callable, args: Tuple = (), stream: Stream = SH_MAX86178_STREAM1) -> None:
        """
        Sets the callback for the stream data.

        :param callback_function: callback function for specified sensorhub stream.
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
            application = sdk.get_sensorhub_application()
            # these optional arguments can be used to pass file, matplotlib or other objects to manipulate data.
            optional_arg1 = "1"
            optional_arg2 = "2"
            application.set_callback(callback, args=(optional_arg1, optional_arg2), stream=application.PPG)
        """
        stream = self._sensorhub_stream_helper(stream)
        self._callback_function[stream] = callback_function
        self._args[stream] = args

    def _callback_data(self, packet, packet_id, callback_function=None, args=None):
        """
        PPG Callback.
        """
        stream = Stream(packet[:2])
        response_packet = SHMAX86178DataPacket()
        if stream == self.SH_ADXL_STREAM:
            response_packet = SHADXLDataPacket()
        elif stream == self.SH_MAX86178_ECG_STREAM:
            response_packet = SHMAX86178ECGDataPacket()
        elif stream == self.SH_MAX86178_BIOZ_STREAM:
            response_packet = SHMAX86178BIOZDataPacket()
        elif stream == self.SH_HRM_STREAM:
            response_packet = SHHRMDataPacket()
        elif stream == self.SH_SPO2_STREAM:
            response_packet = SHSPO2DataPacket()
        elif stream == self.SH_SPO2_DEBUG_STREAM:
            response_packet = SHSPO2DebugDataPacket()
        elif stream == self.SH_REG_CONF_STREAM:
            response_packet = SHRegConfPacket()
        elif stream == self.SH_DEBUG_REG_CONF_STREAM:
            response_packet = SHDebugRegConfPacket()
        elif stream == self.SH_RR_STREAM:
            response_packet = SHRRDataPacket()
        elif stream == self.SH_PR_STREAM:
            response_packet = SHPRDataPacket()
        elif stream == self.SH_AMA_STREAM:
            response_packet = SHAMADataPacket()
        else:
            response_packet = SHMAX86178DataPacket()
        self._callback_data_helper(packet, response_packet, stream)

    def enable_csv_logging(self, filename: str, header: List = None, stream: Stream = SH_MAX86178_STREAM1) -> None:
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
            application = sdk.get_sensorhub_application()
            x = application.enable_csv_logging("ppg.csv", stream = application.SH_MAX86178_STREAM1)
        """
        stream = self._sensorhub_stream_helper(stream)
        if header is None:
            if stream == self.SH_ADXL_STREAM:
                header = ["Timestamp","X", "Y", "Z"]
            elif stream == self.SH_HRM_STREAM:
                header = ["Timestamp", "HR", "HR Confidence", "Activity Class"]
            elif stream == self.SH_SPO2_STREAM:
                header = ["Timestamp", "R", "SpO2", "pTR_SpO2", "SpO2Conf", "IsSpo2Cal", "PercentComplete", "LowSignalQualityFlag", "LowPiFlag", "UnreliableRFlag", "SpO2State", "MotionFlag", "OrientationFlag", "RedPi", "IrPi", "PTR", "PtrQuality"]
            elif stream == self.SH_SPO2_DEBUG_STREAM:
                header = ["Timestamp"]
                for i in range(0, 37):
                    header.append(f"Feature {i}")
                header.append("AreFeaturesCalculated")
            elif stream == self.SH_MAX86178_STREAM1:
                header = ["MEAS 1","Timestamp", "PPG1", "PPG2"]
            elif stream == self.SH_MAX86178_STREAM2:
                header = ["MEAS 2","Timestamp", "PPG1", "PPG2"]
            elif stream == self.SH_MAX86178_STREAM3:
                header = ["MEAS 3","Timestamp", "PPG1", "PPG2"]
            elif stream == self.SH_MAX86178_STREAM4:
                header = ["MEAS 4","Timestamp", "PPG1", "PPG2"]
            elif stream == self.SH_MAX86178_STREAM5:
                header = ["MEAS 5","Timestamp", "PPG1", "PPG2"]
            elif stream == self.SH_MAX86178_STREAM6:
                header = ["MEAS 6","Timestamp", "PPG1", "PPG2"]
            elif stream == self.SH_MAX86178_ECG_STREAM:
                header = ["Timestamp", "Lead Status", "ECG"]
            elif stream == self.SH_MAX86178_BIOZ_STREAM:
                header = ["Timestamp", "Impedance(ohms)"]
            elif stream == self.SH_REG_CONF_STREAM:
                header = ["Timestamp", "M1_LED_I(mA)", "M1_INT_T(us)", "M1_AVG_SMP(pulses)", "M1_DAC_Offset1(uA)", "M1_DAC_Offset2(uA)", "M2_LED_I(mA)", "M2_INT_T(us)", "M2_AVG_SMP(pulses)", "M2_DAC_Offset1(uA)", "M2_DAC_Offset2(uA)", "M3_LED_I(mA)", "M3_INT_T(us)", "M3_AVG_SMP(pulses)", "M3_DAC_Offset1(uA)", "M3_DAC_Offset2(uA)", "PPG_CNF3_SMP_AVE"]
            elif stream == self.SH_DEBUG_REG_CONF_STREAM:
                header = ["Timestamp"]
                header.extend(["0x20", "0x21", "0x22", "0x23", "0x24"])
                header.extend(["0x28", "0x29"])
                header.extend([f"0x{hex_val:02X}" for hex_val in range(0x30, 0x60)])
                header.extend(["0x70", "0x71", "0x71", "0x73", "0x74", "0x75"])
            elif stream == self.SH_RR_STREAM:
                header = ["Timestamp", "IR Cardiac Resp RMS Ratio", "IR Range RMS Ratio", "IR Green Corr Coefficient", "Green RR from IBI", "IR Baseline RR", "Avg HR BPM", "Std IBI MSec", "Green RR IBI quality", "IR Baseline High RR", "IR Baseline SQI", "Signal Processing RR", "Signal Processing SQI", "RR", "Motion Flag"]
            elif stream == self.SH_PR_STREAM:
                header = ["Timestamp", "PPG IIR Heart Beat", "PPG FIR IIR Heart Beat", "PPG IBI", "PPG IBI Corrected", "Green HR", "PPG IBI Quality flag", "Peak Index"]
            elif stream == self.SH_AMA_STREAM:
                header = ["Timestamp", "Activity Class", "Total Activity Time", "Total Walk Steps", "Total Distance"]
        if stream in [self.SH_MAX86178_STREAM1, self.SH_MAX86178_STREAM2, self.SH_MAX86178_STREAM3, self.SH_MAX86178_STREAM4, self.SH_MAX86178_STREAM5, self.SH_MAX86178_STREAM6]:
            self._csv_logger[stream] = CSVLogger(filename, header, write_header=False)
        else:
            self._csv_logger[stream] = CSVLogger(filename, header)

    def disable_csv_logging(self, stream: Stream = SH_MAX86178_STREAM1) -> None:
        """
        Stops logging stream data into CSV.

        :param stream: stream name, use get_supported_streams() to list all supported streams.
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.disable_csv_logging(stream = application.SH_MAX86178_STREAM1)
        """
        stream = self._sensorhub_stream_helper(stream)
        if self._csv_logger.get(stream):
            self._csv_logger[stream].stop_logging()
        self._csv_logger[stream] = None

    def enter_sh_boot_loader_mode(self, mode : bool) -> Dict:
        """
        Sets the Sensor Hub device to boot loader mode.

        :param mode: True for bootloader mode, False for application mode
        :type mode: bool
        :return: A empty dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.enter_boot_loader_mode(True)
            print(x)
        """
        request_packet = SetBootLoaderModePacket(self._destination, SHCommand.BL_SET_MODE_REQ)
        request_packet.set_payload("mode", mode)
        response_packet = SetBootLoaderModePacket(self._destination, SHCommand.BL_SET_MODE_RESP)
        return self._send_packet(request_packet, response_packet)

    def get_sh_page_size(self) -> Dict:
        """
        Fetch the page size (if any) that's set in the sensorhub.
        If page size read out is '0' this means that no page size has been configured at sensorhub.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_sh_page_size()
            print(x)
        """
        request_packet = GetPageSizePacket(self._destination, SHCommand.BL_GET_PAGE_SZ_REQ)
        response_packet = GetPageSizePacket(self._destination, SHCommand.BL_GET_PAGE_SZ_RESP)
        return self._send_packet(request_packet, response_packet)

    def set_sh_page_num(self, page_num : int) -> Dict:
        """
        Set the page size in the sensorhub.

        :param page_num: Page size in bytes
        :type page_num: int
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.set_sh_page_num(8196)
            print(x)
        """
        request_packet = SetPageNumberPacket(self._destination, SHCommand.BL_SET_NUM_PAGE_REQ)
        request_packet.set_payload("page_number", page_num)
        response_packet = SetPageNumberPacket(self._destination, SHCommand.BL_SET_NUM_PAGE_RESP)
        return self._send_packet(request_packet, response_packet)

    def set_sh_iv(self, nonce : List[int]) -> Dict:
        """
        Fetch the page size (if any) that's set in the sensorhub.
        If page size read out is '0' this means that no page size has been configured at sensorhub.

        :param nonce: IV
        :type nonce: List[int]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.set_sh_iv([415, 67])
            print(x["payload"]["status"])
        """
        data = [iv for iv in nonce]
        request_packet = SetIVPacket(self._destination, SHCommand.BL_SET_IV_REQ)
        request_packet.set_payload("nonce", data)
        response_packet = SetIVPacket(self._destination, SHCommand.BL_SET_IV_RESP)
        return self._send_packet(request_packet, response_packet)

    def set_sh_authorization(self, auth: List[int]) -> Dict:
        """
        Fetch the page size (if any) that's set in the sensorhub.
        If page size read out is '0' this means that no page size has been configured at sensorhub.

        :param nonce: auth
        :type nonce: List[int]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.set_sh_authorization([97, 67])
            print(x)
        """
        data = [authorization for authorization in auth]
        request_packet = SetAuthorizationPacket(self._destination, SHCommand.BL_SET_AUTH_REQ)
        request_packet.set_payload("auth", data)
        response_packet = SetAuthorizationPacket(self._destination, SHCommand.BL_SET_AUTH_RESP)
        return self._send_packet(request_packet, response_packet)

    def sh_exit_bootloader(self) -> Dict:
        """
        Fetch the page size (if any) that's set in the Sensorhub.
        If page size read out is '0' this means that no page size has been configured at sensorhub.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.sh_exit_bootloader()
            print(x)
        """
        request_packet = BootloaderExitModePacket(self._destination, SHCommand.BL_EXIT_MODE_REQ)
        response_packet = BootloaderExitModePacket(self._destination, SHCommand.BL_EXIT_MODE_RESP)
        return self._send_packet(request_packet, response_packet)

    def sh_erase_flash(self) -> Dict:
        """
        Fetch the page size (if any) that's set in the Sensorhub.
        If page size read out is '0' this means that no page size has been configured at sensorhub.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.sh_erase_flash()
            print(x)
        """
        request_packet = EraseFlashPacket(self._destination, SHCommand.BL_ERASE_FLASH_REQ)
        response_packet = EraseFlashPacket(self._destination, SHCommand.BL_ERASE_FLASH_RESP)
        return self._send_packet(request_packet, response_packet)

    def sh_start_download_page(self, packet_num: int,  page_num: int, page_part_sz: int, page: List[int]) -> Dict:
        """
        Fetch the page size (if any) that's set in the Sensorhub.
        If page size read out is '0' this means that no page size has been configured at sensorhub.

        :param packet_num: Packet number
        :type packet_num: int
        :param page_num: Page number
        :type page_num: int
        :param page_part_sz: Page part size
        :type page_part_sz: int
        :param page: Page
        :type page: List[int]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.sh_start_download_page(0, 0, 1024, [0xFF, 0xFF...])
            print(x)
        """
        data = [page_part for page_part in page]
        request_packet = DownloadSensorHubPagePacket(self._destination, SHCommand.DOWNLOAD_PAGE_START_REQ)
        request_packet.set_payload("packet_number",packet_num)
        request_packet.set_payload("page_number",page_num)
        request_packet.set_payload("page_part_size",page_part_sz)
        request_packet.set_payload("page_part",data)
        response_packet = DownloadSensorHubPagePacket(self._destination, SHCommand.DOWNLOAD_PAGE_START_RESP)
        return self._send_packet(request_packet, response_packet)

    def sh_init_download_page(self) -> Dict:
        """
        Fetch the page size (if any) that's set in the Sensorhub.
        If page size read out is '0' this means that no page size has been configured at sensorhub.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.sh_init_download_page()
            print(x)
        """
        data = [0]*128
        request_packet = DownloadSensorHubPagePacket(self._destination, SHCommand.DOWNLOAD_PAGE_INIT_REQ)
        request_packet.set_payload("packet_number", 0)
        request_packet.set_payload("page_number", 0)
        request_packet.set_payload("page_part_size", 0)
        request_packet.set_payload("page_part", data)
        response_packet = DownloadSensorHubPagePacket(self._destination, SHCommand.DOWNLOAD_PAGE_INIT_RESP)
        return self._send_packet(request_packet, response_packet)

    def bootloader_test_data(self) -> Dict:
        """
        Fetch the page size (if any) that's set in the Sensorhub.
        If page size read out is '0' this means that no page size has been configured at sensorhub.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.bootloader_test_data()
            print(x)
        """
        request_packet = BootloaderTestDataPacket(self._destination, SHCommand.BL_GET_TEST_DATA_REQ)
        response_packet = BootloaderTestDataPacket(self._destination, SHCommand.BL_GET_TEST_DATA_RESP)
        return self._send_packet(request_packet, response_packet)

    def get_operation_mode(self) -> Dict:
        """
        Fetch sensorhub's current operation mode

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_operation_mode()
            print(x)
        """
        request_packet = BootloaderGetOperationModePacket(self._destination, SHCommand.BL_GET_OP_MODE_REQ)
        response_packet = BootloaderGetOperationModePacket(self._destination, SHCommand.BL_GET_OP_MODE_RESP)
        return self._send_packet(request_packet, response_packet)

    def set_operation_mode(self , sh_mode : SHConfigID) -> Dict:
        """
        Set sensorhub operation mode.

        :param sh_mode: Operation mode, use get_supported_config_ids() to get supported operation modes
        :type sh_mode: SHConfigID
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.set_operation_mode(application.SH_CONFIG_RAW_MODE)
            print(x["payload"]["status"])
        """
        request_packet = SetOpModePacket(self._destination, SHCommand.CONFIG_OP_MODE_REQ)
        request_packet.set_payload("mode", sh_mode)
        response_packet = SetOpModePacket(self._destination, SHCommand.CONFIG_OP_MODE_RESP)
        return self._send_packet(request_packet, response_packet)

    def set_sh_frequency(self, odr : int, device : SHDevice = SENSORHUB_DEVICE) -> Dict:
        """
        Command to set the sampling frequency (in Hz) for the sensors at sensorhub
        Supported frequencies: 25Hz, 50Hz, 100Hz

        :param odr: Sampling frequency in hz
        :type odr: int
        :param device: Device for which ODR is to be set, use get_supported_devices() to fetch supported devices
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.set_sh_frequency(25, application.SENSORHUB_DEVICE)
            print(x["payload"]["odr"])
        """
        request_packet = SetFrequencyPacket(self._destination, SHCommand.SET_FS_REQ)
        request_packet.set_payload("odr", odr)
        request_packet.set_payload("device", device)
        response_packet = SetFrequencyPacket(self._destination, SHCommand.SET_FS_RESP)
        return self._send_packet(request_packet, response_packet)

    def get_sh_frequency(self, device : SHDevice = SENSORHUB_DEVICE) -> Dict:
        """
        Command to get the sampling frequency (in Hz) for the sensors at sensorhub

        :param odr: Sampling frequency in hz
        :param device: Device for which ODR is to be set, use get_supported_devices() to fetch supported devices
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_sh_frequency(application.SENSORHUB_DEVICE)
            print(x["payload"]["odr"])
        """
        request_packet = SetFrequencyPacket(self._destination, SHCommand.GET_FS_REQ)
        request_packet.set_payload("device", device)
        response_packet = SetFrequencyPacket(self._destination, SHCommand.GET_FS_RESP)
        return self._send_packet(request_packet, response_packet)

    def adxl367_self_test(self, meas_range : ADXL367MeasRange) -> Dict:
        """
        Command to run ADXL367 self test through the sensorhub

        :param meas_range: Measure range to be used, use get_supported_adxl367_meas_range() to get supported measurement range
        :type meas_range: ADXL367MeasRange
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.adxl367_self_test(application.SH_ADXL367_MEAS_RANGE_8G)
            print(x["payload"]["result"])
        """
        request_packet = Adxl367SelfTestRequestPacket(self._destination, SHCommand.ADXL367_SELF_TEST_REQ)
        request_packet.set_payload("meas_range", meas_range)
        response_packet = Adxl367SelfTestResponsePacket(self._destination, SHCommand.ADXL367_SELF_TEST_RESP)
        return self._send_packet(request_packet, response_packet)

    def get_sh_firmware_version(self) -> Dict:
        """
        Command to fetch the sensorhub firmware version

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_sh_firmware_version()
            print(f'{x["payload"]["major"]}.{x["payload"]["minor"]}.{x["payload"]["patch"]}')
        """
        request_packet = FirmwareVersionPacket(self._destination, SHCommand.FIRMWARE_VERSION_REQ)
        response_packet = FirmwareVersionPacket(self._destination, SHCommand.FIRMWARE_VERSION_RESP)
        return self._send_packet(request_packet, response_packet)

    def get_sh_algo_version(self) -> Dict:
        """
        Command fetch the sensorhub algorithm version

        :return: A empty dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_sh_algo_version()
            print(f'{x["payload"]["major"]}.{x["payload"]["minor"]}.{x["payload"]["patch"]}')
        """
        request_packet = AlgoVersionPacket(self._destination, SHCommand.ALGO_VERSION_REQ)
        response_packet = AlgoVersionPacket(self._destination, SHCommand.ALGO_VERSION_RESP)
        return self._send_packet(request_packet, response_packet)
    
    def get_sh_aec_version(self) -> Dict:
        """
        Command fetch the sensorhub AEC version

        :return: A empty dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_sh_aec_version()
            print(f'{x["payload"]["major"]}.{x["payload"]["minor"]}.{x["payload"]["patch"]}')
        """
        request_packet = AlgoVersionPacket(self._destination, SHCommand.AEC_VERSION_REQ)
        response_packet = AlgoVersionPacket(self._destination, SHCommand.AEC_VERSION_RESP)
        return self._send_packet(request_packet, response_packet)
    
    def max86178_read_register(self, addresses: List[int]) -> Dict:
        """
        Read the register value of specified address.

        :param addresses: List of register addresses to read.
        :type addresses: List[int]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x00
             - 0xC9

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.max86178_read_register([0x20, 0x21])
            print(x["payload"]["data"]
            # [['0x20', '0x07'] [0x21, 0x00]]

        """
        data = [[address, 0] for address in addresses]
        request_packet = RegOpPacket(self._destination, SHCommand.MAX86178_READ_REG_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = RegOpPacket(self._destination, SHCommand.MAX86178_READ_REG_RESP)
        return self._send_packet(request_packet, response_packet)

    def max86178_write_register(self, addresses_values: List[List[int]]) -> Dict:
        """
        Writes the register value of specified address.

        :param addresses_values: List of register addresses and values to write.
        :type addresses_values: List[List[int]]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x00
             - 0xC9

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.max86178_write_register([[0x20, 0x1], [0x21, 0x2]])
            print(x["payload"]["data"])
            # [['0x20', '0x1'], ['0x21', '0x2']]

        """
        request_packet = RegOpPacket(self._destination, SHCommand.MAX86178_WRITE_REG_REQ)
        request_packet.set_payload("size", len(addresses_values))
        request_packet.set_payload("data", addresses_values)
        response_packet = RegOpPacket(self._destination, SHCommand.MAX86178_WRITE_REG_RESP)
        return self._send_packet(request_packet, response_packet)

    def adxl367_read_register(self, addresses: List[int]) -> Dict:
        """
        Read the register value of specified address.

        :param addresses: List of register addresses to read.
        :type addresses: List[int]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x00
             - 0x45

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.adxl367_read_register([0x20, 0x21])
            print(x["payload"]["data"])
            # [['0x20', '0x07'] [0x21, 0x00]]

        """
        data = [[address, 0] for address in addresses]
        request_packet = RegOpPacket(self._destination, SHCommand.ADXL367_READ_REG_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = RegOpPacket(self._destination, SHCommand.ADXL367_READ_REG_RESP)
        return self._send_packet(request_packet, response_packet)

    def adxl367_write_register(self, addresses_values: List[List[int]]) -> Dict:
        """
        Writes the register value of specified address.

        :param addresses_values: List of register addresses and values to write.
        :type addresses_values: List[List[int]]
        :return: A response packet as dictionary.
        :rtype: Dict

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x00
             - 0x45

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.adxl367_write_register([[0x20, 0x1], [0x21, 0x2]])
            print(x["payload"]["data"])
            # [['0x20', '0x1'], ['0x21', '0x2']]

        """
        request_packet = RegOpPacket(self._destination, SHCommand.ADXL367_WRITE_REG_REQ)
        request_packet.set_payload("size", len(addresses_values))
        request_packet.set_payload("data", addresses_values)
        response_packet = RegOpPacket(self._destination, SHCommand.ADXL367_WRITE_REG_RESP)
        return self._send_packet(request_packet, response_packet)

    def load_max86178_configuration(self, device_id: MAX86178Device) -> Dict:
        """
        Loads specified device id configuration.

        :param device_id: Device ID to load, use get_supported_max86178_devices() to list all supported devices.
        :type device_id: MAX86178Device
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5,8

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_max86178_devices()
            print(x)
            # [<MAX86178Device.DEVICE_G_R_IR: ['0x30']>]
            x = application.load_max86178_configuration(application.DEVICE_G_R_IR)
            print(x["payload"]["device_id"])
            # <MAX86178Device.DEVICE_G_R_IR: ['0x30']>

        """
        request_packet = MAX86178ConfigPacket(self._destination, SHCommand.LOAD_MAX86178_CFG_REQ)
        request_packet.set_payload("device_id", device_id)
        response_packet = MAX86178ConfigPacket(self._destination, SHCommand.LOAD_MAX86178_CFG_RESP)
        return self._send_packet(request_packet, response_packet)

    def load_adxl367_configuration(self, device_id: ADXL367Device) -> Dict:
        """
        Loads specified device id configuration.

        :param device_id: Device ID to load, use get_supported_adxl367_devices() to list all supported adxl367 devices.
        :type device_id: ADXL367Device
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5,8

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_adxl367_devices()
            print(x)
            # [<ADXL367Device.DEVICE_367: ['0x6F', '0x1']>]
            x = application.load_adxl367_configuration(application.DEVICE_367)
            print(x["payload"]["device_id"])
            # <ADXL367Device.DEVICE_367: ['0x6F', '0x1']>

        """
        request_packet = ADXL367ConfigPacket(self._destination, SHCommand.LOAD_ADXL367_CFG_REQ)
        request_packet.set_payload("device_id", device_id)
        response_packet = ADXL367ConfigPacket(self._destination, SHCommand.LOAD_ADXL367_CFG_RESP)
        return self._send_packet(request_packet, response_packet)

    def read_max86178_device_configuration_block(self) -> List[Dict]:
        """
        Returns entire device configuration block.

        :return: A response packet as dictionary.
        :rtype: [Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.read_max86178_device_configuration_block()
            print(x["payload"]["data"])

        """
        request_packet = MAX86178DCBCommandPacket(self._destination, SHCommand.READ_MAX86178_DCB_REQ)
        response_packet = MAX86178DCBPacket(self._destination, SHCommand.READ_MAX86178_DCB_RESP)
        return self._send_packet_multi_response(request_packet, response_packet)

    def write_max86178_device_configuration_block(self, addresses_values: List[List[int]]) -> List[Dict]:
        """
        Writes the device configuration block values of specified addresses.
        This function takes a list of addresses and values to write, and returns a response packet as
        dictionary containing addresses and values.

        :param addresses_values: List of addresses and values to write.
        :type addresses_values: List[List[int]]
        :return: A response packet as dictionary.
        :rtype: [Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.write_max86178_device_configuration_block([[0x20, 2], [0x21, 0x1]])
            print(x["payload"]["size"])
            # 2

        """
        result = []
        packets = math.ceil(len(addresses_values) / self._max86178_dcb_size)
        for packet in range(packets):
            addresses_value = addresses_values[packet * self._max86178_dcb_size:(packet + 1) * self._max86178_dcb_size]
            request_packet = MAX86178DCBPacket(self._destination, SHCommand.WRITE_MAX86178_DCB_REQ)
            request_packet.set_payload("size", len(addresses_value))
            request_packet.set_payload("packet_count", packets)
            request_packet.set_payload("data", addresses_value)
            response_packet = MAX86178DCBCommandPacket(self._destination, SHCommand.WRITE_MAX86178_DCB_RESP)
            result.append(self._send_packet(request_packet, response_packet))
        return result

    def write_max86178_device_configuration_block_from_file(self, filename: str) -> List[Dict]:
        """
        Writes the device configuration block values of specified addresses from file.

        :param filename: dcb filename
        :return: A response packet as dictionary.
        :rtype: [Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.write_max86178_device_configuration_block_from_file("max86178_dcb.dcfg")

        """
        result = self.device_configuration_file_to_list(filename)
        if result:
            return self.write_max86178_device_configuration_block(result)

    def delete_max86178_device_configuration_block(self) -> Dict:
        """
        Deletes MAX86178 Device configuration block.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.delete_max86178_device_configuration_block()
        """
        request_packet = MAX86178DCBCommandPacket(self._destination, SHCommand.ERASE_MAX86178_DCB_REQ)
        response_packet = MAX86178DCBCommandPacket(self._destination, SHCommand.ERASE_MAX86178_DCB_RESP)
        return self._send_packet(request_packet, response_packet)

    def read_adxl367_device_configuration_block(self) -> Dict:
        """
        Returns the entire adxl367 device configuration block.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.read_adxl367_device_configuration_block()
            print(x["payload"]["data"])
            # []

        """
        request_packet = ADXL367DCBCommandPacket(self._destination, SHCommand.READ_ADXL367_DCB_REQ)
        response_packet = ADXL367DCBPacket(self._destination, SHCommand.READ_ADXL367_DCB_RESP)
        return self._send_packet(request_packet, response_packet)

    def write_adxl367_device_configuration_block(self, addresses_values: List[List[int]]) -> Dict:
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
            application = sdk.get_sensorhub_application()
            x = application.write_adxl367_device_configuration_block([[0x20, 2], [0x21, 0x1]])
            print(x["payload"]["size"])
            # 2

        """
        request_packet = ADXL367DCBPacket(self._destination, SHCommand.WRITE_ADXL367_DCB_REQ)
        request_packet.set_payload("size", len(addresses_values))
        request_packet.set_payload("data", addresses_values)
        response_packet = ADXL367DCBCommandPacket(self._destination, SHCommand.WRITE_ADXL367_DCB_RESP)
        return self._send_packet(request_packet, response_packet)

    def write_adxl367_device_configuration_block_from_file(self, filename: str) -> Dict:
        """
        Writes the device configuration block values of specified addresses from file.

        :param filename: dcb filename
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.write_adxl367_device_configuration_block_from_file("adxl367_dcb.dcfg")

        """
        result = self.device_configuration_file_to_list(filename)
        if result:
            return self.write_adxl367_device_configuration_block(result)

    def delete_adxl367_device_configuration_block(self) -> Dict:
        """
        Deletes ADXL367 Device configuration block.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.delete_adxl367_device_configuration_block()
        """
        request_packet = ADXL367DCBCommandPacket(self._destination, SHCommand.ERASE_ADXL367_DCB_REQ)
        response_packet = ADXL367DCBCommandPacket(self._destination, SHCommand.ERASE_ADXL367_DCB_RESP)
        return self._send_packet(request_packet, response_packet)

    def get_adxl367_calibration_en(self) -> Dict:
        """
        Fetch ADXL367 calibration

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.get_adxl367_calibration_en()
        """
        request_packet = GenericEnablePacket(self._destination, SHCommand.GET_ADXL367_G_CALIBRATION_EN_REQ)
        response_packet = GenericEnablePacket(self._destination, SHCommand.GET_ADXL367_G_CALIBRATION_EN_RESP)
        return self._send_packet(request_packet, response_packet)

    def set_adxl367_calibration_en(self, cal_en: bool) -> Dict:
        """
        Enable/disable ADXL367 calibration

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.set_adxl367_calibration_en(True)
        """
        request_packet = GenericEnablePacket(self._destination, SHCommand.SET_ADXL367_G_CALIBRATION_EN_REQ)
        request_packet.set_payload("enable", cal_en)
        response_packet = GenericEnablePacket(self._destination, SHCommand.SET_ADXL367_G_CALIBRATION_EN_RESP)
        return self._send_packet(request_packet, response_packet)

    def get_adxl367_calibration_config(self) -> Dict:
        """
        Fetch ADXL367 calibration config

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.get_adxl367_calibration_config()
        """
        request_packet = ADXL367CalibrationConfigCommandPacket(self._destination, SHCommand.GET_ADXL367_G_CALIBRATION_REQ)
        response_packet = ADXL367CalibrationConfigCommandPacket(self._destination, SHCommand.GET_ADXL367_G_CALIBRATION_RESP)
        return self._send_packet(request_packet, response_packet)

    def set_adxl367_calibration_config(self, x_gain: int, y_gain: int, z_gain: int, x_offset: int, y_offset: int, z_offset: int) -> Dict:
        """
        Fetch ADXL367 calibration config

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.set_adxl367_calibration_config(10000, 10000, 10000, 0, 0, 0)
        """
        request_packet = ADXL367CalibrationConfigCommandPacket(self._destination, SHCommand.SET_ADXL367_G_CALIBRATION_REQ)
        gain = [x_gain, y_gain, z_gain]
        offset = [x_offset, y_offset, z_offset]
        request_packet.set_payload('gain', gain)
        request_packet.set_payload('offset', offset)
        response_packet = ADXL367CalibrationConfigCommandPacket(self._destination, SHCommand.SET_ADXL367_G_CALIBRATION_RESP)
        return self._send_packet(request_packet, response_packet)

    def load_was_configuration(self, device_id: ALGODevice) -> Dict:
        """
        Loads specified device id configuration.

        :param device_id: Device ID to load, use get_supported_was_devices() to list all supported devices.
        :type device_id: ALGODevice
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5,8

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_supported_was_devices()
            print(x)
            # [<MAX86178Device.DEVICE_WAS: ['0x46']>]
            x = application.load_was_configuration(application.DEVICE_WAS)
            print(x["payload"]["device_id"])
            # <MAX86178Device.DEVICE_WAS: ['0x46']>

        """
        request_packet = WASConfigPacket(self._destination, CommonCommand.SET_LCFG_REQ)
        request_packet.set_payload("device_id", device_id)
        response_packet = WASConfigPacket(self._destination, CommonCommand.SET_LCFG_RES)
        return self._send_packet(request_packet, response_packet)


    def write_library_configuration(self, fields_values: List[List[int]]) -> List[Dict]:
        """
        Writes the was configuration block values of specified fields.
        This function takes a list of fields and values to write, and returns a response packet as
        dictionary containing fields and values.

        :param fields_values: List of addresses and values to write.
        :type fields_values: List[List[int]]
        :return: A response packet as dictionary.
        :rtype: List[Dict]

        .. list-table::
           :widths: 50 50
           :header-rows: 1

           * - Address Lower Limit
             - Address Upper Limit
           * - 0x0000
             - 0x0277

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.write_library_configuration([[0x20, 2], [0x21, 0x1]])
            print(x["payload"]["size"])
            # 2
        """
        result = []
        packets = math.ceil(len(fields_values) / self._lcfg_size)
        for packet in range(packets):
            fields_value = fields_values[packet* self._lcfg_size:(packet+1) * self._lcfg_size]
            request_packet = WASLibraryConfigPacket(self._destination, CommonCommand.WRITE_LCFG_REQ)
            request_packet.set_payload("size", len(fields_value))
            request_packet.set_payload("data", fields_value)
            response_packet = WASLibraryConfigPacket(self._destination, CommonCommand.WRITE_LCFG_RES)
            result.append(self._send_packet(request_packet, response_packet))
        return result


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
             - 0x34

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.read_library_configuration([0x0000])
            print(x["payload"]["data"])
            # [['0x0', '0x0']]

        """
        data = [[field, 0] for field in fields]
        request_packet = WASLibraryConfigPacket(self._destination, CommonCommand.READ_LCFG_REQ)
        request_packet.set_payload("size", len(data))
        request_packet.set_payload("data", data)
        response_packet = WASLibraryConfigPacket(self._destination, CommonCommand.READ_LCFG_RES)
        return self._send_packet(request_packet, response_packet)

    def write_was_library_configuration_block_from_file(self, filename: str) -> Dict:
        """
        Writes the was configuration block values of specified addresses from file.

        :param filename: was filename
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.write_was_library_configuration_block_from_file("sh_was.lcfg")

        """
        result = self.device_configuration_file_to_list(filename)
        if result:
            return self.write_library_configuration(result)

    def read_was_library_configuration_block(self) -> List[Dict]:
        """
        Returns entire was device configuration block.

        :return: A response packet as dictionary.
        :rtype: [Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.read_was_library_configuration_block()
            print(x["payload"]["data"])
        """
        request_packet = WASLCFGPacket(self._destination, CommonCommand.GET_LCFG_REQ)
        response_packet = WASLCFGPacket(self._destination, CommonCommand.GET_LCFG_RES)
        return self._send_packet_multi_response(request_packet, response_packet)

    def sh_hard_reset(self) -> Dict:
        """
        Command to perform the hard reset to enter in application mode at sensorhub.

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.sh_hard_reset()
            print(x["payload"]["wakeupmode"])
        """
        request_packet = SHHardResetAPPModePacket(self._destination, SHCommand.HARD_RESET_REQ)
        response_packet = SHHardResetAPPModePacket(self._destination, SHCommand.HARD_RESET_RESP)
        return self._send_packet(request_packet, response_packet)

    def read_register_dump(self, device_id : SHDevice) -> List[Dict]:
        """
        Returns device configuration data.
        :param read : device enum
        :type fields: SHDevice, use get_supported_devices() to fetch supported devices
        :return: A response packet as dictionary.
        :rtype: List[Dict]

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
              sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.sh_read_reg_dump()
            print(x["payload"]["data"])
            # [['0x0', '0x12']]
        """
        request_packet = RegdumpRequestPacket(self._destination, SHCommand.SH_REG_DUMP_REQ)
        request_packet.set_payload("device_id", device_id)
        response_packet = RegdumpResponsePacket(self._destination, SHCommand.SH_REG_DUMP_RESP)
        return self._send_packet_multi_response(request_packet, response_packet, timeout=100)

    def max86178_enable_ecg_packetization(self, enable : bool) -> Dict:
        """
        Enable/Disable continuous stream from MAX86178 ECG based on lead status
        :param enable : True -> Continuous stream, False -> Stream only when Leads on is detected
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.max86178_enable_ecg_packetization(True)
            print(x["payload"]["status"])
            # CommonStatus.OK
        """
        request_packet = GenericEnablePacket(self._destination, SHCommand.ENABLE_MAX86178_ECG_PACKETIZATION_REQ)
        request_packet.set_payload("enable", enable)
        response_packet = GenericEnablePacket(self._destination, SHCommand.ENABLE_MAX86178_ECG_PACKETIZATION_RESP)
        return self._send_packet(request_packet, response_packet)
    
    def set_low_power_mode2_en(self, enable : bool) -> Dict:
        """
        Enable/Disable sensorhub's low power mode 2
        :param enable : True -> low power mode 2, False -> normal mode
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.set_low_power_mode2_en(True)
            print(x["payload"]["status"])
            # CommonStatus.OK
        """
        request_packet = GenericEnablePacket(self._destination, SHCommand.SET_LP_MODE2_REQ)
        request_packet.set_payload("enable", enable)
        response_packet = GenericEnablePacket(self._destination, SHCommand.SET_LP_MODE2_RESP)
        return self._send_packet(request_packet, response_packet)
    
    def get_low_power_mode2_en(self) -> Dict:
        """
        Fetch Sensorhub's low power mode 2 status
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            x = application.get_low_power_mode2_en()
            print(x["payload"]["enable"])
            # True
        """
        request_packet = GenericEnablePacket(self._destination, SHCommand.GET_LP_MODE2_REQ)
        response_packet = GenericEnablePacket(self._destination, SHCommand.GET_LP_MODE2_RESP)
        return self._send_packet(request_packet, response_packet)

    def lp_self_test(self) -> Dict:
        """
        Perform self test for Sensorhub's low power mode

            x = application.lp_self_test()
            print(x["payload"]["result"])
        """
        request_packet = LPSelfTestPacket(self._destination, SHCommand.LP_SELF_TEST_REQ)
        response_packet = LPSelfTestPacket(self._destination, SHCommand.LP_SELF_TEST_RESP)
        return self._send_packet(request_packet, response_packet)
    
    def set_algo_decimation(self, en_reg_decimation : bool, en_spo2_decimation : bool, en_hr_decimation : bool, en_rr_decimation : bool, en_pr_decimation : bool, en_ama_decimation : bool) -> Dict:
        """
        Set the decimation for algorithm data stream
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.set_algo_decimation(True, True, True, True)
        """
        request_packet = DecimationRatePacket(self._destination, SHCommand.SET_DECIMATION_REQ)
        en_decimation = 0
        en_decimation |= en_ama_decimation << AlgoDecimation.EN_AMA_DECIMATION.value
        en_decimation |= en_pr_decimation << AlgoDecimation.EN_PR_DECIMATION.value
        en_decimation |= en_reg_decimation << AlgoDecimation.EN_REG_DECIMATION.value
        en_decimation |= en_spo2_decimation << AlgoDecimation.EN_SPO2_DECIMATION.value
        en_decimation |= en_hr_decimation << AlgoDecimation.EN_HR_DECIMATION.value
        en_decimation |= en_rr_decimation
        en_decimation &= 0x3F
        request_packet.set_payload('en_decimation', en_decimation)
        response_packet = DecimationRatePacket(self._destination, SHCommand.SET_DECIMATION_RESP)
        return self._send_packet(request_packet, response_packet)
    
    def get_algo_decimation(self) -> Dict:
        """
        Get the decimation status for algorithm data stream
        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.get_algo_decimation()
        """
        request_packet = DecimationRatePacket(self._destination, SHCommand.GET_DECIMATION_REQ)
        response_packet = DecimationRatePacket(self._destination, SHCommand.GET_DECIMATION_RESP)
        return self._send_packet(request_packet, response_packet)
    
    def set_spo2_coefficient(self, type: Spo2Coeff, coeff_a: float, coeff_b: float, coeff_c: float) -> Dict:
        """
        Set Spo2 Coefficients
        :param type: Spo2 Coefficient type, use get_supported_spo2coeffs() to list all supported types.
        :param coeff_a: Coefficient A
        :param coeff_b: Coefficient B
        :param coeff_c: Coefficient C

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.set_spo2_coefficient(application.SPO2_COEFF_MLP, 0, 0, 0)
        """
        request_packet = Spo2CoeffPacket(self._destination, SHCommand.SET_SPO2_COEFF_REQ)
        request_packet.set_payload('type', type)
        request_packet.set_payload('spo2_coeff', [coeff_a, coeff_b, coeff_c])
        response_packet = Spo2CoeffPacket(self._destination, SHCommand.SET_SPO2_COEFF_RESP)
        return self._send_packet(request_packet, response_packet)
    
    def get_spo2_coefficient(self, type: Spo2Coeff) -> Dict:
        """
        Set Spo2 Coefficients
        :param type: Spo2 Coefficient type, use get_supported_spo2coeffs() to list all supported types.
        :return: A response packet as dictionary.

         .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.get_spo2_coefficient(application.SPO2_COEFF_MLP)
        """
        request_packet = Spo2CoeffPacket(self._destination, SHCommand.GET_SPO2_COEFF_REQ)
        request_packet.set_payload('type', type)
        response_packet = Spo2CoeffPacket(self._destination, SHCommand.GET_SPO2_COEFF_RESP)
        return self._send_packet(request_packet, response_packet)
    
    def motion_activated_wakeup_enable(self, enable: bool) -> Dict:
        """
        Enable/disable adxl367 based motion activated wakeup

        :return: A response packet as dictionary.
        :rtype: Dict
        
        .. code-block:: python3
            :emphasize-lines: 5
        
            from adi_spo2_watch import SDK
        
            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.motion_activated_wakeup_enable(True)
        """
        request_packet = GenericEnablePacket(self._destination, SHCommand.EN_MOTION_ACTIVATED_WAKEUP_REQ)
        request_packet.set_payload("enable", enable)
        response_packet = GenericEnablePacket(self._destination, SHCommand.EN_MOTION_ACTIVATED_WAKEUP_RESP)
        return self._send_packet(request_packet, response_packet)

    def enable_debug_register_stream(self, enable: bool) -> Dict:
        """
        Enable/disable debug register stream

        :return: A response packet as dictionary.
        :rtype: Dict

        .. code-block:: python3
            :emphasize-lines: 5

            from adi_spo2_watch import SDK

            sdk = SDK("COM4")
            application = sdk.get_sensorhub_application()
            application.enable_debug_register_stream(True)
        """
        request_packet = GenericEnablePacket(self._destination, SHCommand.EN_DEBUG_REG_CFG_REQ)
        request_packet.set_payload("enable", enable)
        response_packet = GenericEnablePacket(self._destination, SHCommand.EN_DEBUG_REG_CFG_RESP)
        return self._send_packet(request_packet, response_packet)