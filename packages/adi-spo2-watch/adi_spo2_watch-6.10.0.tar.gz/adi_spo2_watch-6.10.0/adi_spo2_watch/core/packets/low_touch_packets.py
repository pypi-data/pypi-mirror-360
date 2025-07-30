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
from .command_packet import CommandPacket
from ..enums.dcb_enums import DCBConfigBlockIndex
from ..enums.low_touch_enum import LTWristDetectStatus, LTWristDetectSensor
class WristDetectPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.LT_APP: ['0xC8', '0x0A']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <LTCommand.WRIST_DETECT_RES: ['0x49']>,
                'status': <LTStatus.OK: ['0x41']>,
                'wrist_detect_status': <LTWristDetectStatus.WRIST_DETECT_OFF: ['0x2']>,
                'wrist_detect_sensor_used': <LTWristDetectSensor.LT_SENSOR_EDA: ['0x1']>,
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["wrist_detect_status"] = Enums(1, enum_class=LTWristDetectStatus)
        self._config["payload"]["wrist_detect_sensor_used"] = Enums(1, enum_class=LTWristDetectSensor)

class ReadCH2CapPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.LT_APP: ['0xC8', '0x0A']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <LTCommand.READ_CH2_CAP_RES: ['0x47']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'cap_value': 1179
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["cap_value"] = Int(2)


class CommandLogPacket(CommandPacket):
    """
    CommandLogPacket
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["start_cmd_len"] = Int(2, default=0)
        self._config["payload"]["start_cmd_count"] = Int(2, default=0)
        self._config["payload"]["stop_cmd_len"] = Int(2, default=0)
        self._config["payload"]["stop_cmd_count"] = Int(2, default=0)
        self._config["payload"]["crc16"] = Int(2, default=0)
        self._config["payload"]["commands"] = Array(-1, data_types=[Int(1)], default=[])

    def add_start_command(self, command):
        start_cmd_len = self.get_payload("start_cmd_len")
        start_cmd_count = self.get_payload("start_cmd_count")
        commands = self.get_payload("commands")
        self.set_payload("start_cmd_count", start_cmd_count + 1)
        self.set_payload("start_cmd_len", start_cmd_len + len(command))
        self.set_payload("commands", commands + command)

    def add_stop_command(self, command):
        start_cmd_len = self.get_payload("stop_cmd_len")
        start_cmd_count = self.get_payload("stop_cmd_count")
        commands = self.get_payload("commands")
        self.set_payload("stop_cmd_count", start_cmd_count + 1)
        self.set_payload("stop_cmd_len", start_cmd_len + len(command))
        self.set_payload("commands", commands + command)


class LTDCBGENPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.LT_APP: ['0xC8', '0x0A']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 242,
                'checksum': 0
            },
            'payload': {
                'command': <DCBCommand.READ_CONFIG_RES: ['0x98']>,
                'status': <DCBStatus.ERROR_NO_DCB: ['0x98']>,
                'size': 0,
                'packet_count': 0,
                'data': [ ],
                'start_command_count': 0,
                'stop_command_count': 0
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["dcb_block_index"] = Enums(1, enum_class=DCBConfigBlockIndex)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["packet_count"] = Int(2)
        self._config["payload"]["data"] = Array(-1, dimension=1, data_types=[Int(1)])

    def get_dict(self, last_timestamp=None):
        return self._generate_dict()


class LTDCBLCFGPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 32,
                'checksum': 0
            },
            'payload': {
                'command': <DCBCommand.READ_CONFIG_RES: ['0x98']>,
                'status': <DCBStatus.OK: ['0x97']>,
                'size': 5,
                'data': [
                    [ '0x0', '0x1B58' ],
                    [ '0x1', '0x1388' ],
                    [ '0x2', '0x564' ],
                    [ '0x3', '0x53C' ],
                    [ '0x4', '0x3' ]
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["dcb_block_index"] = Enums(1, enum_class=DCBConfigBlockIndex)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(-1, dimension=2,
                                                data_types=[
                                                    Int(2, to_hex=True),
                                                    Int(2, to_hex=True)
                                                ], reverse_inner_array=True)


class LTDCBCommandPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.EDA: ['0xC3', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 20,
                'checksum': 0
            },
            'payload': {
                'command': <DCBCommand.READ_CONFIG_RES: ['0x98']>,
                'status': <DCBStatus.OK: ['0x97']>,
                'size': 1,
                'data': [
                    [ '0x0', '0x8' ]
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["dcb_block_index"] = Enums(1, enum_class=DCBConfigBlockIndex)


class LTLibraryConfigPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.LT_APP: ['0xC8', '0x0A']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 14,
                'checksum': 0
            },
            'payload': {
                'command': <CommonCommand.READ_LCFG_RES: ['0x17']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'size': 1,
                'data': [
                    [ '0x0', '0x1B58' ]
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(-1, dimension=2,
                                                data_types=[
                                                    Int(1, value_limit=[0x0, 0x5], to_hex=True),
                                                    Int(2, to_hex=True)
                                                ])
