from ..data_types.array import Array
from ..data_types.enums import Enums
from ..data_types.integer import Int
from .command_packet import CommandPacket
from ..enums.dcb_enums import DCBConfigBlockIndex


class AD7156RegisterReadPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.AD7156: ['0xC8', '0x0B']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 23,
                'checksum': 0
            },
            'payload': {
                'command': <CommonCommand.REGISTER_READ_RES: ['0x22']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'size': 3,
                'data': [
                    [ '0x10', '0x40' ],
                    [ '0x11', '0xC0' ],
                    [ '0x12', '0xC0' ]
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(-1, dimension=2,
                                                data_types=[
                                                    Int(2, value_limit=[0x00, 0x17], to_hex=True),
                                                    Int(2, to_hex=True)
                                                ])


class AD7156RegisterWritePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.AD7156: ['0xC8', '0x0B']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 15,
                'checksum': 0
            },
            'payload': {
                'command': <CommonCommand.REGISTER_WRITE_RES: ['0x24']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'size': 1,
                'data': [
                    [ '0x10', '0x11' ]
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(-1, dimension=2,
                                                data_types=[
                                                    Int(2, value_limit=[0x09, 0x12], to_hex=True),
                                                    Int(2, to_hex=True)
                                                ])


class AD7156DCBPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.AD7156: ['0xC8', '0x0B']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 92,
                'checksum': 0
            },
            'payload': {
                'command': <DCBCommand.READ_CONFIG_RES: ['0x98']>,
                'status': <DCBStatus.OK: ['0x97']>,
                'size': 7,
                'data': [
                    [ '0x9', '0x19' ],
                    [ '0xA', '0x66' ],
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
                                                    Int(3, value_limit=[0x09, 0x12], to_hex=True)
                                                ], reverse_inner_array=True)


class AD7156DCBCommandPacket(CommandPacket):
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
                                                           default=DCBConfigBlockIndex.AD7156_BLOCK)
