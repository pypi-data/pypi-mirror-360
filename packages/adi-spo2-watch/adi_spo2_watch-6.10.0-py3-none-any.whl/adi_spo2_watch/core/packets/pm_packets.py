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

from ..data_types.array import Array
from ..data_types.enums import Enums
from ..data_types.integer import Int
from ..data_types.binary import Binary
from ..data_types.string import String
from .command_packet import CommandPacket
from ..enums.common_enums import Application
from ..enums.pm_enums import MCUType, ElectrodeSwitch, LDO, ChipID, PowerMode, ControlStatus


class AppsHealthPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x16',
                'checksum': '0x0'
            },
            'payload': {
                'command': <PMCommand.GET_APPS_HEALTH_RES: ['0x91']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'ad5940_isr_count': 202,
                'adpd_isr_count': 3350,
                'adxl_isr_count': 1187
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["ad5940_isr_count"] = Int(4)
        self._config["payload"]["adpd_isr_count"] = Int(4)
        self._config["payload"]["adxl_isr_count"] = Int(4)


class ChipIDPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xD',
                'checksum': '0x0'
            },
            'payload': {
                'command': <PMCommand.CHIP_ID_RES: ['0x7D']>,
                'status': <PMStatus.OK: ['0x41']>,
                'chip_name': <ChipID.ADPD4K: ['0x02']>,
                'chip_id': 192
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["chip_name"] = Enums(1, enum_class=ChipID)
        self._config["payload"]["chip_id"] = Int(2)


class SwitchControlPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <PMCommand.SW_CONTROL_RES: ['0x79']>,
                'status': <PMStatus.OK: ['0x41']>,
                'switch_name': <ElectrodeSwitch.ADPD4000: ['0x02']>,
                'enabled': False
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["switch_name"] = Enums(1, enum_class=ElectrodeSwitch)
        self._config["payload"]["enabled"] = Binary(1)


class LDOControlPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <PMCommand.LDO_CONTROL_RES: ['0x7B']>,
                'status': <PMStatus.OK: ['0x41']>,
                'ldo_name': <LDO.OPTICAL: ['0x02']>,
                'enabled': False
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["ldo_name"] = Enums(1, enum_class=LDO)
        self._config["payload"]["enabled"] = Binary(1)


class ControlPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xB',
                'checksum': '0x0'
            },
            'payload': {
                'command': <PMCommand.CAP_SENSE_TEST_RES: ['0x7F']>,
                'status': <PMStatus.OK: ['0x41']>,
                'enabled': False
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["enabled"] = Binary(1)


class DateTimePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x15',
                'checksum': '0x0'
            },
            'payload': {
                'command': <PMCommand.GET_DATE_TIME_RES: ['0x53']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'year': 2021,
                'month': 3,
                'day': 12,
                'hour': 16,
                'minute': 33,
                'second': 12,
                'tz_sec': 19800
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["year"] = Int(2)
        self._config["payload"]["month"] = Int(1)
        self._config["payload"]["day"] = Int(1)
        self._config["payload"]["hour"] = Int(1)
        self._config["payload"]["minute"] = Int(1)
        self._config["payload"]["second"] = Int(1)
        self._config["payload"]["tz_sec"] = Int(4, sign=True)


class DCBStatusPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x1A',
                'checksum': '0x0'
            },
            'payload': {
                'command': <DCBCommand.QUERY_STATUS_RES: ['0x9E']>,
                'status': <PMStatus.OK: ['0x41']>,
                'general_block': 0,
                'ad5940_block': 0,
                'adpd_block': 0,
                'adxl_block': 0,
                'ppg_block': 0,
                'ecg_block': 0,
                'eda_block': 0,
                'ad7156_block': 1,
                'pedometer_block': 0,
                'temperature_block': 0,
                'low_touch_block': 0,
                'ui_config_block': 0,
                'user0_block': 0,
                'user1_block': 0,
                'user2_block': 0,
                'user3_block': 0,
                'bia_lcfg_block': 0,
                'bia_dcfg_block': 0,
                'eda_dcfg_block': 0,
                'adp5360_block': 0,
                'session_config_block': 0,
                'temperature_correction_block': 0,
                'sh_max86178_block': 0,
                'sh_adxl367_block': 0,
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["general_block"] = Binary(1)
        self._config["payload"]["ad5940_block"] = Binary(1)
        self._config["payload"]["adpd_block"] = Binary(1)
        self._config["payload"]["adxl_block"] = Binary(1)
        self._config["payload"]["ppg_block"] = Binary(1)
        self._config["payload"]["ecg_block"] = Binary(1)
        self._config["payload"]["eda_lcfg_block"] = Binary(1)
        self._config["payload"]["ad7156_block"] = Binary(1)
        self._config["payload"]["pedometer_block"] = Binary(1)
        self._config["payload"]["temperature_block"] = Binary(1)
        self._config["payload"]["low_touch_block"] = Binary(1)
        self._config["payload"]["ui_config_block"] = Binary(1)
        self._config["payload"]["user0_block"] = Binary(1)
        self._config["payload"]["user1_block"] = Binary(1)
        self._config["payload"]["user2_block"] = Binary(1)
        self._config["payload"]["user3_block"] = Binary(1)
        self._config["payload"]["bia_lcfg_block"] = Binary(1)
        self._config["payload"]["bia_dcfg_block"] = Binary(1)
        self._config["payload"]["eda_dcfg_block"] = Binary(1)
        self._config["payload"]["adp5360_block"] = Binary(1)
        self._config["payload"]["session_config_block"] = Binary(1)
        self._config["payload"]["temperature_correction_block"] = Binary(1)
        self._config["payload"]["sh_max86178_block"] = Binary(1)
        self._config["payload"]["sh_adxl367_block"] = Binary(1)


class MCUVersionPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xB',
                'checksum': '0x0'
            },
            'payload': {
                'command': <PMCommand.GET_MCU_VERSION_RES: ['0x59']>,
                'status': <PMStatus.OK: ['0x41']>,
                'mcu': <MCUType.MCU_M4: ['0x02']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["mcu"] = Enums(1, enum_class=MCUType)


class PingPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x49',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.PING_RES: ['0x1B']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_num': 1,
                'data': [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ... , 0, 0, 0, 0 ],
                'elapsed_time': 0.016231060028076172
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["sequence_num"] = Int(4)
        self._config["payload"]["data"] = Array(-1, data_types=[Int(1)])


class PowerStatePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xB',
                'checksum': '0x0'
            },
            'payload': {
                'command': <PMCommand.SET_POWER_STATE_RES: ['0x49']>,
                'status': <PMStatus.OK: ['0x41']>,
                'power_state': <PowerMode.ACTIVE: ['0x00']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["power_state"] = Enums(1, enum_class=PowerMode)


class SystemInfoPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x24',
                'checksum': '0x0'
            },
            'payload': {
                'command': <PMCommand.SYS_INFO_RES: ['0x4B']>,
                'status': <PMStatus.OK: ['0x41']>,
                'version': 0,
                'mac_address': 'C5-05-CA-F1-67-D5',
                'device_id': 0,
                'model_number': 0,
                'hw_id': 0,
                'bom_id': 0,
                'batch_id': 0,
                'date': 0,
                'board_type': 0
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["version"] = Int(2)
        self._config["payload"]["mac_address"] = Array(6, data_types=[Int(1)])
        self._config["payload"]["device_id"] = Int(4)
        self._config["payload"]["model_number"] = Int(4)
        self._config["payload"]["hw_id"] = Int(2)
        self._config["payload"]["bom_id"] = Int(2)
        self._config["payload"]["batch_id"] = Int(1)
        self._config["payload"]["date"] = Int(4)
        self._config["payload"]["board_type"] = Int(1)

    def get_dict(self, last_timestamp=None):
        packet = super().get_dict(last_timestamp)
        packet["payload"]["mac_address"] = ''.join(
            '{:02X}-'.format(x) for x in packet["payload"]["mac_address"])[:-1]
        return packet

class DisplayDCBPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC1', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 112,
                'checksum': 0
            },
            'payload': {
                'command': <DCBCommand.READ_CONFIG_RES: ['0x98']>,
                'status': <DCBStatus.OK: ['0x97']>,
                'size': 15,
                'data': [
                    [ '0x00', '0x0' ]
                    ...
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(-1,
                                                dimension=2,
                                                data_types=[
                                                    Int(1, to_hex=True),
                                                    Int(3, value_limit=[0x00, 0x05], to_hex=True)
                                                ], reverse_inner_array=True)


class EEPROMPacket(CommandPacket):
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(16, data_types=[Int(1, to_hex=True)])


class UICRCustomerRegistersPacket(CommandPacket):
    """
    Packet Structure:
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["manufacturer_name"] = String(4)
        self._config["payload"]["model_number"] = String(16)
        self._config["payload"]["hw_revision"] = String(8)
        self._config["payload"]["serial_number"] = String(12)
        self._config["payload"]["manufacture_date"] = String(12)
        self._config["payload"]["crc_8"] = Int(4)


class SyncTimerPacket(CommandPacket):
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["enabled"] = Binary(4)


class TopTouchControlPacket(CommandPacket):
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["enabled"] = Binary(1)


class HibernateModePacket(CommandPacket):
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["hibernate_mode"] = Binary(1)
        self._config["payload"]["seconds_to_trigger"] = Int(2)


class BootloaderVersionPacket(CommandPacket):
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config['payload']['bootloader_version'] = Int(4)


class ToolAddressPacket(CommandPacket):
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config['payload']['tool_address'] = Enums(2, enum_class=Application, reverse=True)


class LDOStatusPacket(CommandPacket):
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config['payload']['ldo_num'] = Enums(1, enum_class=LDO)
        self._config['payload']['ldo_status'] = Int(1)


class DG2502SWStatusPacket(CommandPacket):
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config['payload']['sw_name'] = Enums(1, enum_class=ElectrodeSwitch)
        self._config['payload']['sw_status'] = Enums(1, enum_class=ControlStatus)


class BLEStatusPacket(CommandPacket):
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config['payload']['ble_status'] = Int(1)
