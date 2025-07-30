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
import os
import time
import logging
from typing import List
from datetime import datetime, timezone, timedelta

import serial
from tqdm import tqdm
from serial.tools import list_ports

from .application.max30208_application import MAX30208Application
from .core import utils
from .core.ble_manager import BLEManager
from .core.enums.board_enums import Board
from .core.enums.fs_enums import FSCommand
from .core.enums.pm_enums import PMCommand
from .core.enums.ecg_enums import ECGCommand
from .core.enums.sensorhub_enums import SHCommand
from .core.packet_manager import PacketManager
from .application.pm_application import PMApplication
from .application.fs_application import FSApplication
from .core.packets.sensorhub_packets import FirmwareVersionPacket, AlgoVersionPacket, SHDCFGPacket, WASLCFGPacket
from .application.eda_application import EDAApplication
from .application.ecg_application import ECGApplication
from .application.bia_application import BIAApplication
from .application.sensorhub_application import SensorHubApplication
from .application.test_application import TestApplication
from .application.user0_application import User0Application
from .application.session_manager_application import SessionManagerApplication
from .core.packets.ecg_packets import ECGLibraryConfigPacket
from .application.ad7156_application import AD7156Application
from .application.adp5360_application import ADP5360Application
from .core.packets.fs_packets import KeyValuePairResponsePacket
from .application.lt_mode4_application import LTMode4Application
from .application.vsm_mb_sb.pm_application import VSMPMApplication
from .application.low_touch_application import LowTouchApplication
from .core.packets.common_packets import VersionPacket, AlarmPacket
from .core.packets.pm_packets import DateTimePacket, SystemInfoPacket
from .core.enums.common_enums import Application, CommonCommand, CommonStatus

logger = logging.getLogger(__name__)


class ConnectionAlreadyExistError(Exception):
    pass


class DongleNotFoundError(Exception):
    pass


class SDK:
    """
    SDK class
    """

    READING_LOG = 0
    JOINING_CSV = 1

    STUDY_WATCH = Board.STUDY_WATCH
    VSM_MB_SB = Board.VSM_MB_SB
    SPO2_WATCH = Board.SPO2_WATCH
    FW_VERSION = "6.10.0"
    __version__ = "6.10a0"

    def __init__(self, serial_port_address: str, mac_address: str = None, baud_rate: int = 921600,
                 board=Board.STUDY_WATCH, logging_filename: str = None, debug: bool = False,
                 sync_date_time=True, check_version=True, ble_vendor_id: int = 0x0456, ble_product_id: int = 0x2CFE,
                 ble_serial_number: str = None, ble_timeout: int = 10, **kwargs):
        """
        Creates a SDK object

        :param serial_port_address: serial port of the device connected.
        :param mac_address: MAC address of the device.
        :param baud_rate: baud rate.
        :param board: board to connect (STUDY_WATCH, VSM_MB_SB).
        :param logging_filename: log file name.
        :param debug: control for debug mode.
        :param sync_date_time: Sync current system date and time with firmware (Default=True).
        :param check_version: Check for SDK and firmware compatibility (Default=True).
        :param ble_vendor_id: BLE Vendor ID for ADI dongle (Default=0x0456).
        :param ble_product_id: BLE Product ID for ADI dongle (Default=0x2CFE).
        :param ble_serial_number: BLE Serial Number ID for ADI dongle, if none then it will choose first device
         with given vendor and product ID (Default=None).
        :param ble_timeout: BLE connection timeout (Default=10).
        """
        self._board = None
        self._mac_address = None
        self._ble_manager = None
        self._alarms_args = None
        self._serial_object = None
        self._packet_manager = None
        self._alarms_callback_function = None
        self.reconnect(serial_port_address, mac_address, baud_rate, board, logging_filename, debug,
                       sync_date_time, check_version, ble_vendor_id, ble_product_id, ble_serial_number, ble_timeout,
                       **kwargs)

    def reconnect(self, serial_port_address: str, mac_address: str = None, baud_rate: int = 921600,
                  board=Board.STUDY_WATCH, logging_filename: str = None, debug: bool = False,
                  sync_date_time=False, check_version=False, ble_vendor_id: int = 0x0456, ble_product_id: int = 0x2CFE,
                  ble_serial_number: str = None, ble_timeout: int = 10, **kwargs):
        """
        reconnect method allows you to reconnect to SDK; you must call disconnect before using connect.

        :param serial_port_address: serial port of the device connected.
        :param mac_address: MAC address of the device.
        :param baud_rate: baud rate.
        :param board: board to connect (STUDY_WATCH, VSM_MB_SB).
        :param logging_filename: log file name.
        :param debug: control for debug mode.
        :param sync_date_time: Sync current system date and time with firmware (Default=False).
        :param check_version: Check for SDK and firmware compatibility (Default=False).
        :param ble_vendor_id: BLE Vendor ID for ADI dongle (Default=0x0456).
        :param ble_product_id: BLE Product ID for ADI dongle (Default=0x2CFE).
        :param ble_serial_number: BLE Serial Number ID for ADI dongle, if none then it will choose first device
         with given vendor and product ID (Default=None).
        :param ble_timeout: BLE connection timeout (Default=10).
        """

        log_format = '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        if logging_filename:
            logging.basicConfig(filename=logging_filename, filemode='a', format=log_format, datefmt=date_format,
                                level=logging.DEBUG)
        else:
            if debug:
                logging.basicConfig(format=log_format, datefmt=date_format, level=logging.DEBUG)
            else:
                logging.basicConfig(format=log_format, datefmt=date_format)
        logger.debug("----- Study Watch SDK Started -----")
        self._mac_address = mac_address
        self._board = board
        version = None
        for _ in range(3):
            if self._mac_address:
                candidates = list(list_ports.grep(serial_port_address))
                if len(candidates) == 0:
                    raise DongleNotFoundError("Can't find the BLE dongle.")
                if ble_serial_number is None:
                    ble_serial_number = candidates[0].serial_number
                self._ble_manager = BLEManager(ble_vendor_id, ble_product_id, ble_timeout, ble_serial_number)
                self._ble_manager.disconnect()
                self._ble_manager.connect(self._mac_address)
            self._serial_object = serial.Serial(serial_port_address, baud_rate, **kwargs)
            self._packet_manager = PacketManager(self._serial_object)
            self._subscribe_alarms()
            if self._mac_address:
                self._packet_manager.set_ble_source()
            else:
                self._packet_manager.set_usb_source()

            self._packet_manager.start_receive_and_process_threads()
            pm_app = self.get_pm_application()
            sh_app = self.get_sensorhub_application()
            tool_address = pm_app.get_existing_connection()["payload"]["tool_address"]
            if not tool_address == Application.NULL:
                raise ConnectionAlreadyExistError(f"Connection Address: {tool_address}")
            if sync_date_time:
                pm_app.set_datetime(datetime.now())
            version = pm_app.get_version()
            if not version["payload"]["status"] == CommonStatus.NO_RESPONSE:
                sh_mode = sh_app.get_operation_mode()
                if sh_mode["payload"]["status"] == CommonStatus.OK:
                    if sh_mode["payload"]["mode"] != sh_app.SH_APPLICATION_MODE:
                        logger.warning(f"SensorHub is not in application mode!\n"
                                       f"Please update the SensorHub firmware before continuing\n")
                break
            self.disconnect()

        if check_version:
            self._check_version(version)

    @staticmethod
    def _check_version(version):
        if version["payload"]["status"] == CommonStatus.NO_RESPONSE:
            raise Exception("Can't establish connection to the study watch.")

        supported_version = f"{version['payload']['major_version']}.{version['payload']['minor_version']}." \
                            f"{version['payload']['patch_version']}"
        if not supported_version == SDK.FW_VERSION:
            logger.warning(f"Current firmware is not fully compatible with this SDK Version.\n"
                           f"Supported Firmware Version :: {SDK.FW_VERSION}\n"
                           f"Current Firmware Version :: {supported_version}\n"
                           f"SDK Version :: {SDK.__version__}\n")

    def _subscribe_alarms(self):
        for app in [Application.ADP5360, Application.FS, Application.LT_APP, Application.USER0_APP,
                    Application.SENSORHUB, Application.PM, Application.ECG]:
            packet_id = self._get_packet_id(CommonCommand.ALARM_NOTIFICATION, app)
            self._packet_manager.subscribe(packet_id, self._alarms_callback)

    # noinspection PyUnusedLocal
    def _alarms_callback(self, data, packet_id):
        response_packet = AlarmPacket()
        response_packet.decode_packet(data)
        response_packet = response_packet.get_dict()
        if self._alarms_callback_function:
            self._alarms_callback_function(response_packet)
        else:
            logger.warning(f"ALARM - {response_packet['header']['source']} - {response_packet['payload']['status']}")

    def set_alarms_callback(self, callback_function, args=()):
        self._alarms_args = args
        self._alarms_callback_function = callback_function


    def get_adp5360_application(self):
        """
        Creates an adp5360 application object

        :returns: an ADP5360 Application
        :rtype: ADP5360Application
        """
        return ADP5360Application(self._packet_manager)

    def get_ecg_application(self):
        """
        Creates an ecg application object

        :returns: an ecg Application
        :rtype: ECGApplication
        """
        return ECGApplication(self._packet_manager)

    def get_eda_application(self):
        """
        Creates an eda application object

        :returns: an eda Application
        :rtype: EDAApplication
        """
        return EDAApplication(self._packet_manager)

    def get_fs_application(self):
        """
        Creates an fs application object

        :returns: an fs Application
        :rtype: FSApplication
        """
        return FSApplication(self._packet_manager)

    def get_pm_application(self):
        """
        Creates an pm application object

        :returns: an pm Application
        :rtype: VSMPMApplication
        """
        if self._board == Board.VSM_MB_SB:
            return VSMPMApplication(self._packet_manager)
        else:
            return PMApplication(self._packet_manager)

    def get_bia_application(self):
        """
        Creates a bia application object

        :returns: a BIA Application
        :rtype: BIAApplication
        """
        return BIAApplication(self._packet_manager)

    def get_ad7156_application(self):
        """
        Creates a ad7156 application object

        :returns: a AD7156 Application
        :rtype: AD7156Application
        """
        return AD7156Application(self._packet_manager)

    def get_sensorhub_application(self):
        """
        Creates a Sensor Hub application object

        :returns: a Sensor Hub Application
        :rtype: SensorHubApplication
        """
        return SensorHubApplication(self._packet_manager)

    def get_max30208_application(self):
        """
        Creates a Max30208 application object

        :returns: a Max30208 Application
        :rtype: MAX30208Application
        """
        return MAX30208Application(self._packet_manager)

    def get_lt_mode4_application(self):
        """
        Creates a lt_mode4 application object

        :returns: a lt_mode4 Application
        :rtype: LTMode4Application
        """
        return LTMode4Application(self._packet_manager)

    def get_low_touch_application(self):
        """
        Creates a low touch application object

        :returns: a LowTouch Application
        :rtype: LowTouchApplication
        """
        return LowTouchApplication(self._packet_manager)

    def get_test_application(self, key_test_callback=None, cap_sense_callback=None):
        """
        Creates a test application object, used for internal firmware testing.

        :returns: a Test Application
        :rtype: TestApplication
        """
        return TestApplication(key_test_callback, cap_sense_callback, self._packet_manager)

    def get_user0_application(self):
        """
        Creates a User0 application object

        :returns: a User Application
        :rtype: User0Application
        """
        return User0Application(self._packet_manager)

    def unsubscribe_all_streams(self):
        """
        Unsubscribe from all application streams
        """
        result = [self.get_bia_application().unsubscribe_stream(),
                  self.get_ecg_application().unsubscribe_stream(), 
                  self.get_eda_application().unsubscribe_stream()]
        fs_app = self.get_fs_application()
        for stream in fs_app.get_supported_streams():
            result.append(fs_app.unsubscribe_stream(stream))
        return result

    @staticmethod
    def _get_packet_id(response_command, destination):
        return utils.join_multi_length_packets(destination.value + response_command.value)

    @staticmethod
    def get_supported_boards():
        return [SDK.STUDY_WATCH, SDK.VSM_MB_SB, SDK.SPO2_WATCH]

    @staticmethod
    def get_available_ports() -> List:
        """
        returns the list of tuple (port, description, hardware_id) of available ports.
        """
        result = []
        for port, desc, hardware_id in sorted(list_ports.comports()):
            result.append((port, desc, hardware_id))
        return result

    @staticmethod
    def join_csv(*args, output_filename="combined.csv", display_progress=True, progress_callback=None):
        """
        Joins multiple data stream csv file into single csv file.
        """
        file_size = os.path.getsize(args[0])
        current_size = 0
        progress_bar = None
        if display_progress:
            progress_bar = tqdm(total=file_size)
            progress_bar.set_description("ADPD csv join")
        space = {}
        header = []
        all_csv = {}
        first_iter = {}
        result_file = open(output_filename, 'w')

        for file in args:
            csv_file = open(file, 'r')
            header = [csv_file.readline(), csv_file.readline()]
            all_csv[file] = csv_file
            first_iter[file] = True
            space[file] = 0

        # write header
        result_file.write(header[0])
        result_file.write(header[1])

        while True:
            result_line = ""
            empty_file_count = 0
            for file in args:
                line = all_csv[file].readline().strip()
                # checking for empty file condition
                if len(line) == 0:
                    empty_file_count += 1
                    result_line += "," * space[file]
                    continue
                # saving number of elements in a row
                if first_iter[file]:
                    space[file] = len(line.split(","))
                    first_iter[file] = False
                # concat row
                result_line += line + ","
                # progress bar
                if file == args[0]:
                    line_size = len(line.encode('utf-8'))
                    current_size += line_size
                    if display_progress:
                        progress_bar.update(line_size)
                    if progress_callback:
                        progress_callback(SDK.JOINING_CSV, file_size, current_size)
            # break condition
            if empty_file_count == len(args):
                break
            result_file.write(result_line + "\n")

        # cleanup
        result_file.close()
        if display_progress:
            progress_bar.update(file_size - current_size)
            progress_bar.close()
        if progress_callback:
            progress_callback(SDK.JOINING_CSV, file_size, file_size)
        for file in args:
            all_csv[file].close()

    @staticmethod
    def _csv_write_config(file, config, header):
        file.write(f"Address, Value, {header}\n")
        if not type(config) == list:
            config = [config]
        for data in config:
            for value in data["payload"]["data"]:
                if header == "#PPG_LCFG":
                    file.write(f"{value}\n")
                else:
                    file.write(f"{value[0]}, {value[1]}\n")
        file.write(f"\n")

    @staticmethod
    def _csv_write_version(file, config, header):
        file.write(f"Module, {header}\n")
        if (header == "Sensorhub Firmware Version") or  (header == "Wearable Algo Version"):
            if config['payload']['status'] == CommonStatus.OK:
                file.write(f"Major version, {config['payload']['major']}\n")
                file.write(f"Minor version, {config['payload']['minor']}\n")
                file.write(f"Patch version, {config['payload']['patch']}\n")
                if (header == "Sensorhub Firmware Version"):
                    file.write(f"SHA, {config['payload']['sha']}\n")
        else:    
            file.write(f"Major version, {config['payload']['major_version']}\n")
            file.write(f"Minor version, {config['payload']['minor_version']}\n")
            file.write(f"Patch version, {config['payload']['patch_version']}\n")
            file.write(f"Version string, {config['payload']['version_string']}\n")
            file.write(f"Build version, {config['payload']['build_version']}\n")
        file.write(f"\n")

    @staticmethod
    def _packet_loss(file, msg, packet_count):
        if packet_count:
            file.write(f"{msg}, {packet_count}\n")
        else:
            file.write(f"{msg}, 0\n")

    # noinspection PyProtectedMember,PyTypeChecker,PyUnresolvedReferences
    @staticmethod
    def convert_log_to_csv(filename, display_progress=True, progress_callback=None):
        """
        Converts M2M2 log file into csv.
        """
        if not os.path.exists(filename):
            raise Exception("File not Found.")

        info_result = {
            "key_value_pair": None, "datetime": None, "system_info": None, "version": None, "sensorhub_fw_version" : None, 
            "was_version" : None, "max86178_ppg_dcfg": None, "adxl367_dcfg": None, "was_lcfg": None,
        }
        folder_name = filename.split(".")[0]
        try:
            os.mkdir(folder_name)
        except Exception as e:
            logger.debug(e)

        # creating all applications
        packet_manager = PacketManager(None, filename=filename)
        packet_manager.set_usb_source()
        ad7156_app = AD7156Application(packet_manager)
        ecg_app = ECGApplication(packet_manager)
        eda_app = EDAApplication(packet_manager)
        bia_app = BIAApplication(packet_manager)
        pm_app = PMApplication(packet_manager)
        adp5360_app = ADP5360Application(packet_manager)
        sensorhub_app = SensorHubApplication(packet_manager)
        max30208_app = MAX30208Application(packet_manager)

        # enabling csv logging
        ecg_app.enable_csv_logging(f"{folder_name}/ecg.csv")
        eda_app.enable_csv_logging(f"{folder_name}/eda.csv")
        bia_app.enable_csv_logging(f"{folder_name}/bia.csv", stream=bia_app.STREAM_BIA)
        bia_app.enable_csv_logging(f"{folder_name}/bcm.csv", stream=bia_app.STREAM_BCM)
        adp5360_app.enable_csv_logging(f"{folder_name}/adp.csv")
        ad7156_app.enable_csv_logging(f"{folder_name}/ad7156.csv")
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_stream1.csv", stream=sensorhub_app.SH_MAX86178_STREAM1)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_stream2.csv", stream=sensorhub_app.SH_MAX86178_STREAM2)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_stream3.csv", stream=sensorhub_app.SH_MAX86178_STREAM3)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_stream4.csv", stream=sensorhub_app.SH_MAX86178_STREAM4)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_stream5.csv", stream=sensorhub_app.SH_MAX86178_STREAM5)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_stream6.csv", stream=sensorhub_app.SH_MAX86178_STREAM6)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_ecg.csv", stream=sensorhub_app.SH_MAX86178_ECG_STREAM)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_adxl.csv", stream=sensorhub_app.SH_ADXL_STREAM)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_hrm.csv", stream=sensorhub_app.SH_HRM_STREAM)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_spo2.csv", stream=sensorhub_app.SH_SPO2_STREAM)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_spo2_debug.csv", stream=sensorhub_app.SH_SPO2_DEBUG_STREAM)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_reg_conf.csv", stream=sensorhub_app.SH_REG_CONF_STREAM)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_debug_reg_conf.csv", stream=sensorhub_app.SH_DEBUG_REG_CONF_STREAM)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_rr.csv", stream=sensorhub_app.SH_RR_STREAM)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_pr.csv", stream=sensorhub_app.SH_PR_STREAM)
        sensorhub_app.enable_csv_logging(f"{folder_name}/sh_ama.csv", stream=sensorhub_app.SH_AMA_STREAM)
        max30208_app.enable_csv_logging(f"{folder_name}/max30208_temperature.csv")

        # subscribing
        apps = [ecg_app, eda_app, ad7156_app, max30208_app]
        for app in apps:
            app._subscribe_stream_data()
        adp5360_app._subscribe_stream_data(adp5360_app.STREAM_BATTERY)
        bia_app._subscribe_stream_data(bia_app.STREAM_BIA)
        bia_app._subscribe_stream_data(bia_app.STREAM_BCM)
        for stream in sensorhub_app.get_supported_streams():
            sensorhub_app._subscribe_stream_data(stream)

        def update_info_dict(packet, response_byte, key):
            packet.decode_packet(response_byte)
            if info_result.get(key) is None:
                info_result[key] = packet.get_dict()
            else:
                if type(info_result[key]) == list:
                    info_result[key] = info_result[key] + [packet.get_dict()]
                else:
                    info_result[key] = [info_result[key], packet.get_dict()]

        # noinspection PyShadowingNames,PyProtectedMember
        def callback(response_byte, packet_id):
            if SDK._get_packet_id(FSCommand.SET_KEY_VALUE_PAIR_RES, Application.FS) == packet_id:
                packet = KeyValuePairResponsePacket()
                update_info_dict(packet, response_byte, "key_value_pair")
            elif SDK._get_packet_id(PMCommand.GET_DATE_TIME_RES, Application.PM) == packet_id:
                packet = DateTimePacket()
                update_info_dict(packet, response_byte, "datetime")
                response_packet = info_result["datetime"]
                tz_sec = response_packet["payload"]["tz_sec"]
                offset = timezone(timedelta(seconds=tz_sec))
                dt = datetime(response_packet['payload']['year'], response_packet['payload']['month'],
                              response_packet['payload']['day'], response_packet['payload']['hour'],
                              response_packet['payload']['minute'], response_packet['payload']['second'],
                              tzinfo=offset)
                for _app in apps:
                    _app._update_timestamp(dt, generate_ts=True, tz_sec=tz_sec)
                bia_app._update_timestamp(dt, bia_app.STREAM_BIA, generate_ts=True, tz_sec=tz_sec)
                bia_app._update_timestamp(dt, bia_app.STREAM_BCM, generate_ts=True, tz_sec=tz_sec)
                adp5360_app._update_timestamp(dt, adp5360_app.STREAM_BATTERY, generate_ts=True, tz_sec=tz_sec)
                for _stream in sensorhub_app.get_supported_streams():
                    sensorhub_app._update_timestamp(dt, _stream, generate_ts=True, tz_sec=tz_sec)
            elif SDK._get_packet_id(PMCommand.SYS_INFO_RES, Application.PM) == packet_id:
                packet = SystemInfoPacket()
                update_info_dict(packet, response_byte, "system_info")
            elif SDK._get_packet_id(CommonCommand.GET_VERSION_RES, Application.PM) == packet_id:
                packet = VersionPacket()
                update_info_dict(packet, response_byte, "version")
            elif SDK._get_packet_id(SHCommand.FIRMWARE_VERSION_RESP, Application.SENSORHUB) == packet_id:
                packet = FirmwareVersionPacket()
                update_info_dict(packet, response_byte, "sensorhub_fw_version")
            elif SDK._get_packet_id(SHCommand.ALGO_VERSION_RESP, Application.SENSORHUB) == packet_id:
                packet = AlgoVersionPacket()
                update_info_dict(packet, response_byte, "was_version")
            elif SDK._get_packet_id(SHCommand.GET_MAX86178_DCFG_RESP, Application.SENSORHUB) == packet_id:
                packet = SHDCFGPacket()
                update_info_dict(packet, response_byte, "max86178_ppg_dcfg")
            elif SDK._get_packet_id(SHCommand.GET_ADXL367_DCFG_RESP, Application.SENSORHUB) == packet_id:
                packet = SHDCFGPacket()
                update_info_dict(packet, response_byte, "adxl367_dcfg")
            elif SDK._get_packet_id(CommonCommand.GET_LCFG_RES, Application.SENSORHUB) == packet_id:
                packet = WASLCFGPacket()
                update_info_dict(packet, response_byte, "was_lcfg")

        initial_packets = [
            [FSCommand.SET_KEY_VALUE_PAIR_RES, Application.FS],
            [PMCommand.GET_DATE_TIME_RES, Application.PM],
            [PMCommand.SYS_INFO_RES, Application.PM],
            [CommonCommand.GET_VERSION_RES, Application.PM],
            [SHCommand.FIRMWARE_VERSION_RESP, Application.SENSORHUB],
            [SHCommand.ALGO_VERSION_RESP, Application.SENSORHUB],
            [SHCommand.GET_MAX86178_DCFG_RESP, Application.SENSORHUB],
            [SHCommand.GET_ADXL367_DCFG_RESP, Application.SENSORHUB],
            [CommonCommand.GET_LCFG_RES, Application.SENSORHUB]
        ]
        for initial_packet in initial_packets:
            packet_id = SDK._get_packet_id(initial_packet[0], initial_packet[1])
            packet_manager.subscribe(packet_id, callback)

        # process file
        packet_manager.process_file(display_progress, progress_callback)

        # disabling csv logging.
        for app in apps:
            app.disable_csv_logging()
        bia_app.disable_csv_logging(stream=bia_app.STREAM_BIA)
        bia_app.disable_csv_logging(stream=bia_app.STREAM_BCM)
        adp5360_app.disable_csv_logging()
        for stream in sensorhub_app.get_supported_streams():
            sensorhub_app.disable_csv_logging(stream=stream)

        # unsubscribing
        for app in apps:
            app._unsubscribe_stream_data()
        bia_app._unsubscribe_stream_data(bia_app.STREAM_BIA)
        bia_app._unsubscribe_stream_data(bia_app.STREAM_BCM)
        adp5360_app._unsubscribe_stream_data(adp5360_app.STREAM_BATTERY)
        for stream in sensorhub_app.get_supported_streams():
            sensorhub_app._unsubscribe_stream_data(stream)

        with open(f"{folder_name}/Summary.csv", 'w') as f:
            if info_result['key_value_pair']:
                f.write(f"Participant Information, {info_result['key_value_pair']['payload']['value_id']}" + "\n")

                SDK._packet_loss(f, "AD7156 Packet loss", ad7156_app.get_packet_lost_count())
                SDK._packet_loss(f, "ECG Packet loss", ecg_app.get_packet_lost_count())
                SDK._packet_loss(f, "EDA Packet loss", eda_app.get_packet_lost_count())
                SDK._packet_loss(f, "BIA Packet loss", bia_app.get_packet_lost_count(bia_app.STREAM_BIA))
                SDK._packet_loss(f, "BCM Packet loss", bia_app.get_packet_lost_count(bia_app.STREAM_BCM))
                for i, stream in enumerate(sensorhub_app.get_supported_streams()):
                    if stream == sensorhub_app.SH_ADXL_STREAM:
                        SDK._packet_loss(f, "SH ADXL Packet loss", sensorhub_app.get_packet_lost_count(sensorhub_app.SH_ADXL_STREAM))
                    elif stream == sensorhub_app.SH_HRM_STREAM:
                        SDK._packet_loss(f, "SH HRM Packet loss", sensorhub_app.get_packet_lost_count(sensorhub_app.SH_HRM_STREAM))
                    elif stream == sensorhub_app.SH_SPO2_STREAM:
                        SDK._packet_loss(f, "SH SPO2 Packet loss", sensorhub_app.get_packet_lost_count(sensorhub_app.SH_SPO2_STREAM))
                    elif stream == sensorhub_app.SH_SPO2_DEBUG_STREAM:
                        SDK._packet_loss(f, "SH SPO2 Debug Packet loss", sensorhub_app.get_packet_lost_count(sensorhub_app.SH_SPO2_DEBUG_STREAM))
                    elif stream == sensorhub_app.SH_REG_CONF_STREAM:
                        SDK._packet_loss(f, "SH REG CONF Packet loss", sensorhub_app.get_packet_lost_count(sensorhub_app.SH_REG_CONF_STREAM))
                    elif stream == sensorhub_app.SH_DEBUG_REG_CONF_STREAM:
                        SDK._packet_loss(f, "SH DEBUG REG CONF Packet loss", sensorhub_app.get_packet_lost_count(sensorhub_app.SH_DEBUG_REG_CONF_STREAM))
                    elif stream == sensorhub_app.SH_RR_STREAM:
                        SDK._packet_loss(f, "SH RR Packet loss", sensorhub_app.get_packet_lost_count(sensorhub_app.SH_RR_STREAM))
                    elif stream == sensorhub_app.SH_PR_STREAM:
                        SDK._packet_loss(f, "SH PR Packet loss", sensorhub_app.get_packet_lost_count(sensorhub_app.SH_PR_STREAM))
                    elif stream == sensorhub_app.SH_AMA_STREAM:
                        SDK._packet_loss(f, "SH AMA Packet loss", sensorhub_app.get_packet_lost_count(sensorhub_app.SH_AMA_STREAM))
                    else:
                        sensorhub_lost_packets = sensorhub_app.get_packet_lost_count(stream)
                        if sensorhub_lost_packets:
                            SDK._packet_loss(f, f"SH_STREAM{i + 1} CH1 Packet loss", sensorhub_lost_packets[0])
                            SDK._packet_loss(f, f"SH_STREAM{i + 1} CH2 Packet loss", sensorhub_lost_packets[1])
                        else:
                            SDK._packet_loss(f, f"SH_STREAM{i + 1} CH1 Packet loss", 0)
                            SDK._packet_loss(f, f"SH_STREAM{i + 1} CH2 Packet loss", 0)
                SDK._packet_loss(f, "MAX30208 TEMPERATURE Packet loss", max30208_app.get_packet_lost_count(max30208_app.MAX30208_TEMPERATURE_STREAM))


        with open(f"{folder_name}/Configuration.csv", 'w') as f:
            if info_result["max86178_ppg_dcfg"]:
                SDK._csv_write_config(f, info_result["max86178_ppg_dcfg"], "#MAX86178_PPG_DCFG")
            if info_result["adxl367_dcfg"]:
                SDK._csv_write_config(f, info_result["adxl367_dcfg"], "#ADXL367_DCFG")
            if info_result["was_lcfg"]:
                SDK._csv_write_config(f, info_result["was_lcfg"], "#WAS_LCFG")

        with open(f"{folder_name}/FirmwareVersion.csv", 'w') as f:
            if info_result["version"]:
                SDK._csv_write_version(f, info_result["version"], "PM Firmware Version")
            if info_result["sensorhub_fw_version"]:
                SDK._csv_write_version(f, info_result["sensorhub_fw_version"], "Sensorhub Firmware Version")
            if info_result["was_version"]:
                SDK._csv_write_version(f, info_result["was_version"], "Wearable Algo Version")

        with open(f"{folder_name}/PSBoardInfo.csv", 'w') as f:
            if info_result["system_info"]:
                config = info_result["system_info"]
                f.write(f"Module, PS Board Info\n")
                f.write(f"Version, {config['payload']['version']}\n")
                f.write(f"MAC address, {config['payload']['mac_address']}\n")
                f.write(f"Device ID, {config['payload']['device_id']}\n")
                f.write(f"Model number, {config['payload']['model_number']}\n")
                f.write(f"Hardware ID, {config['payload']['hw_id']}\n")
                f.write(f"BOM ID, {config['payload']['bom_id']}\n")
                f.write(f"Batch ID, {config['payload']['batch_id']}\n")
                f.write(f"Board Type, {config['payload']['board_type']}\n")

        # cleanup
        for _ in apps:
            del _
        del pm_app
        del adp5360_app
        del sensorhub_app
        del packet_manager

    def convert_ticks_to_timestamp(self, ticks: int):
        """
        Converts firmware ticks to unix timestamp.
        """
        date_time_packet = self.get_pm_application().get_datetime()
        offset = timezone(timedelta(seconds=date_time_packet["payload"]["tz_sec"]))
        date_time = datetime(date_time_packet['payload']['year'], date_time_packet['payload']['month'],
                             date_time_packet['payload']['day'], date_time_packet['payload']['hour'],
                             date_time_packet['payload']['minute'], date_time_packet['payload']['second'],
                             tzinfo=offset)
        ts = (32000.0 * ((date_time.hour * 3600) + (date_time.minute * 60) + date_time.second))
        ref_time = date_time.timestamp()
        change = ts - ticks
        change = change / 32000.0
        return (ref_time - change) * 1000

    def disconnect(self):
        """disconnect SDK"""
        logger.debug("----- Study Watch SDK Stopped -----")
        if self._mac_address:
            self._ble_manager.disconnect()
        self._packet_manager.close()
        time.sleep(1)
