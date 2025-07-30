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

from ..data_types.enums import Enums
from ..data_types.integer import Int
from ..data_types.string import String
from .command_packet import CommandPacket
from ..enums.common_enums import Stream, AlarmStatus


class DecimationFactorPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.ADPD: ['0xC1', '0x10']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xD',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.GET_STREAM_DEC_FACTOR_RES: ['0x2A']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'stream_address': <Stream.ADPD6: ['0xC2', '0x16']>,
                'decimation_factor': 1
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["stream_address"] = Enums(2, Stream, reverse=True)
        self._config["payload"]["decimation_factor"] = Int(1, value_limit=[1, 5])


class StreamPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.ADXL: ['0xC1', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.SUBSCRIBE_STREAM_RES: ['0x0D']>,
                'status': <CommonStatus.SUBSCRIBER_ADDED: ['0x09']>,
                'stream_address': <Stream.ADXL: ['0xC2', '0x02']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["stream_address"] = Enums(2, Stream, reverse=True, default=Stream.NULL)


class StreamStatusPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.ADXL: ['0xC1', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xE',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.GET_SENSOR_STATUS_RES: ['0x11']>,
                'status': <CommonStatus.STREAM_STOPPED: ['0x03']>,
                'stream_address': <Stream.ADXL: ['0xC2', '0x02']>,
                'num_subscribers': 0,
                'num_start_registered': 0
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["stream_address"] = Enums(2, Stream, reverse=True)
        self._config["payload"]["num_subscribers"] = Int(1)
        self._config["payload"]["num_start_registered"] = Int(1)


class VersionPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.ADPD: ['0xC1', '0x10']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x42',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.GET_VERSION_RES: ['0x01']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'major_version': 0,
                'minor_version': 3,
                'patch_version': 1,
                'version_string': 'ADPD_App',
                'build_version': 'TEST ADPD4000_VERSION STRING'
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["major_version"] = Int(2)
        self._config["payload"]["minor_version"] = Int(2)
        self._config["payload"]["patch_version"] = Int(2)
        self._config["payload"]["version_string"] = String(13)
        self._config["payload"]["build_version"] = String(43)


class AlarmPacket(CommandPacket):
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["status"] = Enums(1, enum_class=AlarmStatus)
