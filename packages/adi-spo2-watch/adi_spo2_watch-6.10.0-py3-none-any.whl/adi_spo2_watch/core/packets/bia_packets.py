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
from ..enums.bia_enums import HSResistorTIA, BIADFTWindow
from ..enums.dcb_enums import DCBConfigBlockIndex


class DCBTimingInfoPacket(CommandPacket):

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["clear_entries_time"] = Int(2)
        self._config["payload"]["check_entries_time"] = Int(2)
        self._config["payload"]["delete_record_time"] = Int(2)
        self._config["payload"]["read_entry_time"] = Int(2)
        self._config["payload"]["update_entry_time"] = Int(2)


class FDSStatusPacket(CommandPacket):

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["dirty_records"] = Int(2)
        self._config["payload"]["open_records"] = Int(2)
        self._config["payload"]["valid_records"] = Int(2)
        self._config["payload"]["pages_available"] = Int(2)
        self._config["payload"]["num_blocks"] = Int(2)
        self._config["payload"]["blocks_free"] = Int(2)


class HSRTIAPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.BIA: ['0xC3', '0x07']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <BIACommand.SET_HS_TRANS_IMPEDANCE_AMPLIFIER_CAL_RES: ['0x49']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'hs_resistor_tia': <HSResistorTIA.RESISTOR_1K: ['0x00', '0x01']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["hs_resistor_tia"] = Enums(2, enum_class=HSResistorTIA)


class BIADFTPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.BIA: ['0xC3', '0x07']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 12,
                'checksum': 0
            },
            'payload': {
                'command': <BIACommand.SET_DFT_NUM_RES: ['0x47']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'dft_window': <BIADFTWindow.DFT_WINDOW_16384: ['0x00', '0x12']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["dft_window"] = Enums(2, enum_class=BIADFTWindow)


class BIALibraryConfigPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.BIA: ['0xC3', '0x07']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 16,
                'checksum': 0
            },
            'payload': {
                'command': <CommonCommand.READ_LCFG_RES: ['0x17']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'size': 1,
                'data': [
                    [ '0x0', '0x0' ]
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(-1, dimension=2,
                                                data_types=[
                                                    Int(1, value_limit=[0x00, 0x1B], to_hex=True),
                                                    Int(4, to_hex=True)
                                                ])


class BIADCBLCFGPacket(CommandPacket):
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
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(108,
                                                dimension=1,
                                                data_types=[
                                                    Int(4, to_hex=True),
                                                ])


class BIADCBDCFGPacket(CommandPacket):
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
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(88,
                                                dimension=2,
                                                data_types=[
                                                    Int(4, to_hex=True),
                                                    Int(4, to_hex=True)
                                                ], reverse_inner_array=True)


class BIADCBCommandPacket(CommandPacket):
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


class BIADCFGPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.EDA: ['0xC3', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 23,
                'checksum': 0
            },
            'payload': {
                'command': <CommonCommand.REGISTER_READ_RES: ['0x22']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'size': 3,
                'data': [
                    [ '0x0', '0x1' ],
                    [ '0x1', '0x2' ],
                    [ '0x2', '0x3' ]
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
                                                    Int(4, to_hex=True),
                                                    Int(4, to_hex=True)
                                                ])
