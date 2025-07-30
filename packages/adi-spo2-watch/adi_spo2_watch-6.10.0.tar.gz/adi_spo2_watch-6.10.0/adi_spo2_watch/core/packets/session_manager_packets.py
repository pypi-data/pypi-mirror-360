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

from ..data_types.array import Array
from ..data_types.binary import Binary
from ..data_types.enums import Enums
from ..data_types.integer import Int
from .command_packet import CommandPacket
from ..enums.dcb_enums import DCBConfigBlockIndex
from ..enums.session_manager_enums import SessionManagerState, SessionManagerEvent
from ..enums.user0_enums import User0State, User0ID, User0OperationMode, User0Event, User0BatteryDrain, User0SubState, \
    User0WatchResetReason


class SessionManagerLibraryConfigPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.SESSION_MANAGER_APP: ['0xC8', '0x24']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 16,
                'checksum': 0
            },
            'payload': {
                'command': <CommonCommand.READ_LCFG_RES: ['0x17']>,
                'status': <CommonStatus.OK: ['0x41']>,
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
                                                    Int(1, to_hex=True),
                                                    Int(4, to_hex=True)
                                                ])


class SessionManagerStatePacket(CommandPacket):
    """
        Packet Structure:

        .. code-block::

            {
                'header': {
                    'source': <Application.SESSION_MANAGER_APP: ['0xC8', '0x24']>,
                    'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                    'length': 16,
                    'checksum': 0
                },
                'payload': {
                    'command': <CommonCommand.SET_STATE_RES: ['0x42']>,
                    'status': <CommonStatus.OK: ['0x41']>,
                    'state': <SessionManagerState.STANDBY: ['0x0'],
                }
            }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["state"] = Enums(1, enum_class=SessionManagerState)


class SessionManagerPrevStateEventPacket(CommandPacket):
    """
            Packet Structure:

            .. code-block::

                {
                    'header': {
                        'source': <Application.SESSION_MANAGER_APP: ['0xC8', '0x24']>,
                        'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                        'length': 16,
                        'checksum': 0
                    },
                    'payload': {
                        'command': <CommonCommand.READ_LCFG_RES: ['0x17']>,
                        'status': <CommonStatus.OK: ['0x41']>,
                        'prev_state': <SessionManagerState.STANDBY: ['0x0'],
                        'prev_event': <SessionManagerEvent.INVALID: ['0x0'],
                        'timestamp': 1633229664514.8113
                    }
                }
            """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["state"] = Enums(1, enum_class=SessionManagerState)
        self._config["payload"]["event"] = Enums(1, enum_class=SessionManagerEvent)
        self._config["payload"]["timestamp"] = Int(4)


class SessionManagerDCBPacket(CommandPacket):
    """
            Packet Structure:

            .. code-block::

                {
                    'header': {
                        'source': <Application.SESSION_MANAGER_APP: ['0xC8', '0x24']>,
                        'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                        'length': 16,
                        'checksum': 0
                    },
                    'payload': {
                        'command': <CommonCommand.READ_LCFG_RES: ['0x17']>,
                        'status': <CommonStatus.OK: ['0x41']>,
                        'dcb_block_index': <DCBConfigBlockIndex.SESSION_CONFIG_BLOCK: ['0x14']>,
                        'size': 1,
                        'data': [
                            [ '0x0', '0x8' ]
                        ]
                    }
                }
            """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["dcb_blk_index"] = Enums(1, enum_class=DCBConfigBlockIndex,
                                                         default=DCBConfigBlockIndex.SESSION_CONFIG_BLOCK)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(-1, dimension=1, data_types=[Int(4, to_hex=True)], size_limit=26)
