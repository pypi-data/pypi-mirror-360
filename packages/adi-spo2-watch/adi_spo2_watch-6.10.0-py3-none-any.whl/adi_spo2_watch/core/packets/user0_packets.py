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
from ..data_types.binary import Binary
from ..data_types.enums import Enums
from ..data_types.integer import Int
from .command_packet import CommandPacket
from ..enums.dcb_enums import DCBConfigBlockIndex
from ..enums.user0_enums import User0State, User0ID, User0OperationMode, User0Event, User0BatteryDrain, User0SubState, \
    User0WatchResetReason


class User0LibraryConfigPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.USER0_APP: ['0xC8', '0x0F']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 16,
                'checksum': 0
            },
            'payload': {
                'command': <CommonCommand.READ_LCFG_RES: ['0x17']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'size': 1,
                'data': [
                    [ '0x0', '0x42' ]
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(-1, dimension=2,
                                                data_types=[
                                                    Int(1, value_limit=[0x00, 0x12], to_hex=True),
                                                    Int(4, to_hex=True)
                                                ])


class User0StatePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.USER0_APP: ['0xC8', '0x0F']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 11,
                'checksum': 0
            },
            'payload': {
                'command': <User0Command.GET_STATE_RES: ['0x45']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'state': <User0State.END_MONITORING: ['0x06']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["state"] = Enums(1, enum_class=User0State)


class User0DCBPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.USER0_APP: ['0xC8', '0x0F']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 88,
                'checksum': 0
            },
            'payload': {
                'command': <DCBCommand.READ_CONFIG_RES: ['0x98']>,
                'status': <DCBStatus.OK: ['0x97']>,
                'size': 19,
                'data': [
                    [ '0x00', '0x42' ],
                    [ '0x01', '0x1' ],
                    ...
                    [ '0x11', '0xF' ],
                    [ '0x12', '0x249F0' ]
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(-1, dimension=1, data_types=[Int(4, to_hex=True)], size_limit=0x13)


class User0DCBCommandPacket(CommandPacket):
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
        self._config["payload"]["dcb_block_index"] = Enums(1, enum_class=DCBConfigBlockIndex,
                                                           default=DCBConfigBlockIndex.USER0_BLOCK)


class User0HardwareIDPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.USER0_APP: ['0xC8', '0x0F']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 14,
                'checksum': 0
            },
            'payload': {
                'command': <User0Command.ID_OP_RES: ['0x47']>,
                'status': <User0Status.OK: ['0x41']>,
                'id': <User0ID.HW_ID: ['0x00']>,
                'operation': <User0OperationMode.READ: ['0x00']>,
                'value': 34
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["id"] = Enums(1, enum_class=User0ID, default=User0ID.HW_ID)
        self._config["payload"]["operation"] = Enums(1, enum_class=User0OperationMode)
        self._config["payload"]["value"] = Int(2, value_limit=[1, 99])


class BypassUser0TimingPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.USER0_APP: ['0xC8', '0x0F']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 14,
                'checksum': 0
            },
            'payload': {
                'command': <User0Command.ID_OP_RES: ['0x47']>,
                'status': <User0Status.OK: ['0x41']>,
                'enabled': false
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["enabled"] = Binary(1)


class User0ExperimentIDPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.USER0_APP: ['0xC8', '0x0F']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 14,
                'checksum': 0
            },
            'payload': {
                'command': <User0Command.ID_OP_RES: ['0x47']>,
                'status': <User0Status.OK: ['0x41']>,
                'id': <User0ID.EXP_ID: ['0x01']>,
                'operation': <User0OperationMode.READ: ['0x00']>,
                'value': 9999
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["id"] = Enums(1, enum_class=User0ID, default=User0ID.EXP_ID)
        self._config["payload"]["operation"] = Enums(1, enum_class=User0OperationMode)
        self._config["payload"]["value"] = Int(2, value_limit=[1, 9999])


class User0PrevStateEventPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.USER0_APP: ['0xC8', '0x0F']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 36,
                'checksum': 0
            },
            'payload': {
                'command': <User0Command.GET_PREV_ST_EVT_RES: ['0x4B']>,
                'status': <User0Status.OK: ['0x41']>,
                'intermittent_count': 1,
                'stream_data': [
                    {
                        'state': <User0State.END_MONITORING: ['0x06']>,
                        'event': <User0Event.WATCH_ON_CRADLE_NAV_BUTTON_RESET: ['0x02']>,
                        'timestamp': 1633154418511.9675
                    },
                    {
                        'state': <User0State.END_MONITORING: ['0x06']>,
                        'event': <User0Event.FINISH_LOG_TRANSFER: ['0x0B']>,
                        'timestamp': 1633154737959.6863
                    },
                    {
                        'state': <User0State.END_MONITORING: ['0x06']>,
                        'event': <User0Event.WATCH_ON_CRADLE_NAV_BUTTON_RESET: ['0x02']>,
                        'timestamp': 1633161548514.8425
                    },
                    {
                        'state': <User0State.END_MONITORING: ['0x06']>,
                        'event': <User0Event.WATCH_ON_CRADLE_NAV_BUTTON_RESET: ['0x02']>,
                        'timestamp': 1633229664514.8113
                    }
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["prev_state_1"] = Enums(1, enum_class=User0State)
        self._config["payload"]["prev_event_1"] = Enums(1, enum_class=User0Event)
        self._config["payload"]["prev_timestamp_1"] = Int(4)
        self._config["payload"]["prev_state_2"] = Enums(1, enum_class=User0State)
        self._config["payload"]["prev_event_2"] = Enums(1, enum_class=User0Event)
        self._config["payload"]["prev_timestamp_2"] = Int(4)
        self._config["payload"]["prev_state_3"] = Enums(1, enum_class=User0State)
        self._config["payload"]["prev_event_3"] = Enums(1, enum_class=User0Event)
        self._config["payload"]["prev_timestamp_3"] = Int(4)
        self._config["payload"]["prev_state_4"] = Enums(1, enum_class=User0State)
        self._config["payload"]["prev_event_4"] = Enums(1, enum_class=User0Event)
        self._config["payload"]["prev_timestamp_4"] = Int(4)
        self._config["payload"]["prev_state_5"] = Enums(1, enum_class=User0State)
        self._config["payload"]["prev_event_5"] = Enums(1, enum_class=User0Event)
        self._config["payload"]["prev_timestamp_5"] = Int(4)
        self._config["payload"]["intermittent_count"] = Int(2)
        self._config["payload"]["intermittent_count"] = Int(2)
        self._config["payload"]["battery_drain_state"] = Enums(1, enum_class=User0BatteryDrain)
        self._config["payload"]["sub_state"] = Enums(1, enum_class=User0SubState)
        self._config["payload"]["rtc_compare_int_count"] = Int(1)
        self._config["payload"]["rtc_compare_val_ticks"] = Int(4)
        self._config["payload"]["watch_reset_reason"] = Enums(1, enum_class=User0WatchResetReason)

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of data.
        """
        packet = super().get_dict()
        packet["payload"]["stream_data"] = []
        for i in range(1, 6):
            data = {
                "state": packet["payload"][f"prev_state_{i}"],
                "event": packet["payload"][f"prev_event_{i}"],
                "timestamp": packet["payload"][f"prev_timestamp_{i}"],
            }
            [packet["payload"].pop(key) for key in [f"prev_timestamp_{i}", f"prev_event_{i}", f"prev_state_{i}"]]
            packet["payload"]["stream_data"].append(data)
        return packet
