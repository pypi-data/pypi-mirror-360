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
from ..data_types.decimal import Decimal
from .command_packet import CommandPacket
from ..enums.dcb_enums import DCBConfigBlockIndex
from ..enums.eda_enums import ScaleResistor, EDADFTWindow, EDAPowerMode


class DynamicScalingPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.EDA: ['0xC3', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x11',
                'checksum': '0x0'
            },
            'payload': {
                'command': <EDACommand.DYNAMIC_SCALE_RES: ['0x43']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'enabled': True,
                'min_scale': <ScaleResistor.SCALE_RESISTOR_100K: ['0x14', '0x00']>,
                'max_scale': <ScaleResistor.SCALE_RESISTOR_128K: ['0x16', '0x00']>,
                'lp_resistor_tia': <ScaleResistor.SCALE_RESISTOR_100K: ['0x14', '0x00']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["enabled"] = Binary(1)
        self._config["payload"]["min_scale"] = Enums(2, enum_class=ScaleResistor)
        self._config["payload"]["max_scale"] = Enums(2, enum_class=ScaleResistor)
        self._config["payload"]["lp_resistor_tia"] = Enums(2, enum_class=ScaleResistor)


class ResistorTIACalibratePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.EDA: ['0xC3', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x2A',
                'checksum': '0x0'
            },
            'payload': {
                'command': <EDACommand.RESISTOR_TIA_CAL_RES: ['0x4B']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'min_scale': <ScaleResistor.SCALE_RESISTOR_100K: ['0x14', '0x00']>,
                'max_scale': <ScaleResistor.SCALE_RESISTOR_128K: ['0x16', '0x00']>,
                'lp_resistor_tia': <ScaleResistor.SCALE_RESISTOR_100K: ['0x14', '0x00']>,
                'calibrated_values_count': 3,
                'calibrated_values': [
                    [ 106299, 100000 ],
                    [ 127514, 120000 ],
                    [ 136008, 128000 ]
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["min_scale"] = Enums(2, enum_class=ScaleResistor)
        self._config["payload"]["max_scale"] = Enums(2, enum_class=ScaleResistor)
        self._config["payload"]["lp_resistor_tia"] = Enums(2, enum_class=ScaleResistor)
        self._config["payload"]["size"] = Int(2)
        self._config["payload"]["data"] = Array(-1,
                                                dimension=2,
                                                data_types=[
                                                    Int(4, to_hex=True),
                                                    Int(4, to_hex=True)
                                                ])


class EDADFTPacket(CommandPacket):
    """
        Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.EDA: ['0xC3', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 11,
                'checksum': 0
            },
            'payload': {
                'command': <EDACommand.SET_DFT_NUM_RES: ['0x47']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'dft_window': <EDADFTWindow.DFT_WINDOW_8: ['0x01']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["dft_window"] = Enums(1, enum_class=EDADFTWindow)


class EDALibraryConfigPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.EDA: ['0xC3', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 21,
                'checksum': 0
            },
            'payload': {
                'command': <CommonCommand.READ_LCFG_RES: ['0x17']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'size': 2,
                'data': [
                    [ '0x1', '0x0' ],
                    [ '0x0', '0x0' ]
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
                                                    Int(4, to_hex=True)
                                                ])


class EDADCBLCFGPacket(CommandPacket):
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
        self._config["payload"]["data"] = Array(12,
                                                dimension=2,
                                                data_types=[
                                                    Int(2, to_hex=True),
                                                    Int(2, to_hex=True)
                                                ], reverse_inner_array=True)


class EDADCBDCFGPacket(CommandPacket):
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
        self._config["payload"]["data"] = Array(72,
                                                dimension=2,
                                                data_types=[
                                                    Int(4, to_hex=True),
                                                    Int(4, to_hex=True)
                                                ], reverse_inner_array=True)


class EDADCBCommandPacket(CommandPacket):
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


class EDARegisterReadPacket(CommandPacket):
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
                                                    Int(2, to_hex=True),
                                                    Int(4, to_hex=True)
                                                ])


class EDARegisterWritePacket(CommandPacket):
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
                                                    Int(2, to_hex=True),
                                                    Int(4, to_hex=True)
                                                ])


class EDADCFGPacket(CommandPacket):
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


class EDABaselineImpedancePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.EDA: ['0xC3', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 30,
                'checksum': 0
            },
            'payload': {
                'command': <EDACommand.BASELINE_IMP_SET_RES: ['0x4D']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'real_dft16': 25000.5,
                'imaginary_dft16': 25000.5,
                'real_dft8': 25000.5,
                'imaginary_dft8': 25000.5,
                'resistor_baseline': 19900
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["real_dft16"] = Decimal(4)
        self._config["payload"]["imaginary_dft16"] = Decimal(4)
        self._config["payload"]["real_dft8"] = Decimal(4)
        self._config["payload"]["imaginary_dft8"] = Decimal(4)
        self._config["payload"]["resistor_baseline"] = Int(4)


class EDAGetBaselineImpedancePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.EDA: ['0xC3', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 30,
                'checksum': 0
            },
            'payload': {
                'command': <EDACommand.BASELINE_IMP_SET_RES: ['0x4D']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'real_dft16': 25000.5,
                'imaginary_dft16': 25000.5,
                'real_dft8': 25000.5,
                'imaginary_dft8': 25000.5,
                'resistor_baseline': 19900
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["baseline_imp_set"] = Int(2)
        self._config["payload"]["real_dft16"] = Decimal(4)
        self._config["payload"]["imaginary_dft16"] = Decimal(4)
        self._config["payload"]["real_dft8"] = Decimal(4)
        self._config["payload"]["imaginary_dft8"] = Decimal(4)
        self._config["payload"]["resistor_baseline"] = Int(4)


class EDASleepWakeupPacket(CommandPacket):
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
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["power_mode"] = Enums(1, enum_class=EDAPowerMode)
