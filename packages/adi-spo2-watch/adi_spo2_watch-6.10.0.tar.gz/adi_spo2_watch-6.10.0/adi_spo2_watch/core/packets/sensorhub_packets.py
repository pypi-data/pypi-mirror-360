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

from .command_packet import CommandPacket
from ..data_types.integer import Int
from ..data_types.decimal import Decimal
from ..data_types.array import Array
from ..data_types.enums import Enums
from ..data_types.binary import Binary
from ..data_types.string import String
from ..enums.sensorhub_enums import SHMode, SHConfigID, ADXL367MeasRange, SHDevice, MAX86178Device,  \
                                    ADXL367Device, ALGODevice, LowPowerSelfTestResult, Spo2Coeff
from ..enums.dcb_enums import DCBConfigBlockIndex


class SetBootLoaderModePacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.BL_SET_MODE_REQ: ['0x46']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'mode':  True
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["mode"] = Binary(1)


class GetPageSizePacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.BL_GET_PAGE_SZ_REQ: ['0x4E']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'size':  '0x02', '0x00'
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["page_size"] = Int(2)


class SetPageNumberPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.BL_SET_NUM_PAGE_REQ: ['0x48']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'page_number':  '0x02', '0x00'
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["page_number"] = Int(2)


class SetIVPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.BL_SET_IV_REQ: ['0x4A']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'nonce':  []
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["nonce"] = Array(-1,
                                                dimension=1,
                                                data_types=[
                                                    Int(1),
                                                ])


class SetAuthorizationPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.BL_SET_AUTH_REQ: ['0x05']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'auth':  []
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["auth"] = Array(16,size_limit=16 ,dimension=1, data_types=[Int(1, to_hex=True)],default=0)


class EraseFlashPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.BL_ERASE_FLASH_REQ: ['0x50']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'auth':  []
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)


class SetFrequencyPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xB',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.SH_COMMAND_SET_FS_REQ: ['0x60']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'odr':  25
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["device"] = Enums(1, enum_class=SHDevice, default=SHDevice.SENSORHUB_DEVICE)
        self._config["payload"]["odr"] = Int(2)


class BootloaderExitModePacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.BL_EXIT_MODE_REQ: ['0x58']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'auth':  []
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["sensorhub_status"] = Int(1)


class BootloaderGetOperationModePacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.BL_GET_OP_MODE_REQ: ['0x05']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'mode':
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["mode"] = Enums(1, enum_class=SHMode,
                                                           default=SHMode.SENSORHUB_ERROR_MODE)


class BootloaderTestDataPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.MAX86178_SET_FS_REQ: ['0x05']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'mode':
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["test_data"] = Array(-1, dimension=1,
                                                data_types=[
                                                    Int(1, to_hex=True)
                                                ],size_limit = 26)


class DownloadSensorHubPagePacket(CommandPacket):
    """
          Packet Structure:

          .. code-block::

              {
                  'header': {
                      'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                      'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                      'length': '0xC',
                      'checksum': '0x0'
                  },
                  'payload': {
                      'command': <SHCommand.MAX86178_SET_FS_REQ: ['0x05']>,
                      'status': <CommonStatus.OK: ['0x00']>,
                      'mode':
                  }
              }
          """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["packet_number"] = Int(1)
        self._config["payload"]["page_number"] = Int(1)
        self._config["payload"]["page_part_size"] = Int(2)
        self._config["payload"]["page_part"] = Array(-1, dimension=1,
                                                data_types=[
                                                    Int(1, to_hex=True)
                                                ],size_limit = 128)


class GenericEnablePacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.MAX86178_SET_FS_REQ: ['0x05']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'enable':  True
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["enable"] = Binary(1)

class SetOpModePacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.MAX86178_SET_FS_REQ: ['0x05']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'mode':  SHConfigID.SENSORHUB_RAW_MODE
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["mode"] = Enums(1, enum_class=SHConfigID,
                                                           default=SHConfigID.SENSORHUB_RAW_MODE)


class Adxl367SelfTestRequestPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.ADXL367_SELF_TEST_REQ: ['0x5C']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'meas_range':  ADXL367MeasRange.MEAS_RANGE_8G
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["meas_range"] = Enums(1, enum_class=ADXL367MeasRange,
                                                           default=ADXL367MeasRange.MEAS_RANGE_8G)


class Adxl367SelfTestResponsePacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.ADXL367_SELF_TEST_RESP: ['0x5D']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'sh_status':  '0x0',
                   'result':    '0x0'
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["sh_status"] = Int(1)
        self._config["payload"]["result"] = Int(1)


class FirmwareVersionPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.FIRMWARE_VERSION_RESP: ['0x5F']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'major':  '0x33',
                   'minor':  '0x0',
                   'patch':  '0x0'
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["major"] = Int(1)
        self._config["payload"]["minor"] = Int(1)
        self._config["payload"]["patch"] = Int(1)
        self._config["payload"]["sha"] = String(10)


class AlgoVersionPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.ALGO_VERSION_RESP: ['0x79']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'major':  '0x33',
                   'minor':  '0x0',
                   'patch':  '0x0'
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["major"] = Int(1)
        self._config["payload"]["minor"] = Int(1)
        self._config["payload"]["patch"] = Int(1)


class RegOpPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.MAX86178_READ_REG_REQ: ['0x60']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'address':  '0x20',
                   'value':  '0x07'
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
                                                    Int(1, to_hex=True)
                                                ])


class MAX86178ConfigPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <SHCommand.LOAD_MAX86178_CFG_REQ: ['0x68']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'device_id': <MAX86178Device.DEVICE_G_R_IR: ['0x30']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["device_id"] = Enums(1, enum_class=MAX86178Device)


class WASConfigPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <SHCommand.SET_LCFG_RES: ['0x15']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'device_id': <ALGODevice.DEVICE_WAS: ['0x70']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["device_id"] = Enums(1, enum_class=ALGODevice)


class ADXL367ConfigPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <SHCommand.LOAD_ADXL367_CFG_REQ: ['0x6A']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'device_id': <ADXL367Device.DEVICE_367: ['0x6F', '0x01']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["device_id"] = Enums(2, enum_class=ADXL367Device)


class MAX86178DCBPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <SHCommand.READ_MAX86178_DCB_REQ: ['0x6']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'size': 15,
                'data': [
                    [ '0x20', '0x0' ],
                    [ '0x21', '0x0' ],
                    ...
                    [ '0x2D', '0x10' ],
                    [ '0x2E', '0x0' ]
                ]
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["packet_count"] = Int(1)
        self._config["payload"]["data"] = Array(-1,
                                                dimension=2,
                                                data_types=[
                                                    Int(1, to_hex=True),
                                                    Int(3, value_limit=[0x10, 0xC9], to_hex=True)
                                                ], reverse_inner_array=True)


class MAX86178DCBCommandPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <DCBCommand.READ_CONFIG_RES: ['0x98']>,
                'status': <DCBStatus.OK: ['0x97']>,
                'dcb_block_index': 1,
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["dcb_block_index"] = Enums(1, enum_class=DCBConfigBlockIndex,
                                                           default=DCBConfigBlockIndex.SH_MAX86178_BLOCK)


class SHDCFGPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        [
            {
                'header': {
                    'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                    'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                    'length': 242,
                    'checksum': 0
                },
                'payload': {
                    'command': <SHCommand.GET_MAX86178_DCFG_RESP: ['0x13']>,
                    'status': <CommonStatus.OK: ['0x00']>,
                    'size': 57,
                    'packet_count': 2,
                    'data': [
                        [ '0x9', '0x97' ],
                        [ '0xB', '0x6E2' ],
                        ...
                        [ '0x1A5', '0x5' ],
                        [ '0x1A6', '0x0' ]
                    ]
                }
            },
            {
                'header': {
                    'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                    'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                    'length': 242,
                    'checksum': 0
                },
                'payload': {
                    'command': <SHCommand.GET_MAX86178_DCFG_RESP: ['0x13']>,
                    'status': <CommonStatus.OK: ['0x00']>,
                    'size': 10,
                    'packet_count': 2,
                    'data': [
                        [ '0x1A7', '0x120' ],
                        [ '0x1A8', '0x0' ],
                        ...
                        [ '0x1AF', '0x0' ],
                        [ '0x1B0', '0x4' ]
                    ]
                }
            }
        ]
    """
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["packet_count"] = Int(1)
        self._config["payload"]["data"] = Array(-1, dimension=2,
                                                data_types=[
                                                    Int(1, value_limit=[0x0, 0x815], to_hex=True),
                                                    Int(1, to_hex=True)
                                                ])


class ADXL367DCBPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <SHCommand.READ_ADXL367_DCB_REQ: ['0x6']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'size': 15,
                'data': [
                    [ '0x20', '0x0' ],
                    [ '0x21', '0x0' ],
                    ...
                    [ '0x2D', '0x10' ],
                    [ '0x2E', '0x0' ]
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
                                                    Int(3, value_limit=[0x20, 0x2E], to_hex=True)
                                                ], reverse_inner_array=True)


class ADXL367DCBCommandPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <DCBCommand.READ_CONFIG_RES: ['0x98']>,
                'status': <DCBStatus.OK: ['0x97']>,
                'dcb_block_index': 1,
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["dcb_block_index"] = Enums(1, enum_class=DCBConfigBlockIndex,
                                                           default=DCBConfigBlockIndex.SH_ADXL367_BLOCK)

class ADXL367CalibrationConfigCommandPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <DCBCommand.READ_CONFIG_RES: ['0x98']>,
                'status': <DCBStatus.OK: ['0x97']>,
                'cal_en': True,
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["gain"] = Array(12,
                                                dimension=1,
                                                data_types=[
                                                    Int(4, sign=True),
                                                    Int(4, sign=True),
                                                    Int(4, sign=True)
                                                ])
        self._config["payload"]["offset"] = Array(12,
                                                dimension=1,
                                                data_types=[
                                                    Int(4, sign=True),
                                                    Int(4, sign=True),
                                                    Int(4, sign=True)
                                                ])


class WASLCFGPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        [
            {
                'header': {
                    'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                    'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                    'length': 242,
                    'checksum': 0
                },
                'payload': {
                    'command': <CommonCommand.GET_LCFG_RES: ['0x13']>,
                    'status': <CommonStatus.OK: ['0x00']>,
                    'size': 57,
                    'packet_count': 2,
                    'data': [
                        [ '0x9', '0x97' ],
                        [ '0xB', '0x6E2' ],
                        ...
                        [ '0x1A5', '0x5' ],
                        [ '0x1A6', '0x0' ]
                    ]
                }
            },
            {
                'header': {
                    'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                    'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                    'length': 242,
                    'checksum': 0
                },
                'payload': {
                    'command': <CommonCommand.GET_LCFG_RES: ['0x13']>,
                    'status': <CommonStatus.OK: ['0x00']>,
                    'size': 10,
                    'packet_count': 2,
                    'data': [
                        [ '0x1A7', '0x120' ],
                        [ '0x1A8', '0x0' ],
                        ...
                        [ '0x1AF', '0x0' ],
                        [ '0x1B0', '0x4' ]
                    ]
                }
            }
        ]
    """
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["packet_count"] = Int(1)
        self._config["payload"]["deviceid"] = Enums(1, enum_class=ALGODevice)
        self._config["payload"]["data"] = Array(-1, dimension=2,
                                                data_types=[
                                                    Int(2, value_limit=[0x0, 0x815], to_hex=True),
                                                    Int(2, to_hex=True)
                                                ])


class WASLibraryConfigPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 235,
                'checksum': 0
            },
            'payload': {
                'command': <CommonCommand.READ_LCFG_RES: ['0x17']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'size': 56,
                'data': [ '0xC0', '0x20', ... ] }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(1)
        self._config["payload"]["data"] = Array(-1, dimension=2,
                                                data_types=[
                                                    Int(2, value_limit=[0x00, 0x81E], to_hex=True),
                                                    Int(2, to_hex=True)
                                                ])


class SHHardResetAPPModePacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.HARD_RESET_REQ: ['0x82']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'wakeupmode':
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["wakeupmode"] = Int(1)


class RegdumpRequestPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.SH_REG_DUMP_REQ: ['0x82']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'device_id': SHDevice
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["device_id"] = Enums(1, enum_class=SHDevice)


class RegdumpResponsePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        [
            {
                'header': {
                    'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                    'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                    'length': 242,
                    'checksum': 0
                },
                'payload': {
                    'command': <CommonCommand.SH_REG_DUMP_RESP: ['0x85']>,
                    'status': <CommonStatus.OK: ['0x00']>,
                    'device_id': '0x01'
                    'num_ops': 62,
                    'packet_count': 2,
                    'ops': [
                        [ '0x01', '0x97' ],
                        [ '0x02', '0x6E' ],
                        ...
                        [ '0x09', '0x5' ],
                        [ '0x0A', '0x0' ]
                    ]
                }
            },
            {
                'header': {
                    'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                    'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                    'length': 242,
                    'checksum': 0
                },
                'payload': {
                    'command': <CommonCommand.SH_REG_DUMP_RESP: ['0x85']>,
                    'status': <CommonStatus.OK: ['0x00']>,
                    'device_id': '0x01'
                    'num_ops': 62,
                    'packet_count': 2,
                    'ops': [
                        [ '0x1A', '0x12' ],
                        [ '0x1B', '0x0' ],
                        ...
                        [ '0x1E', '0x0' ],
                        [ '0x1F', '0x4' ]
                    ]
                }
            }
        ]
    """
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["device_id"] = Enums(1, enum_class=SHDevice, default=SHDevice.MAX86178_DEVICE)
        self._config["payload"]["num_ops"] = Int(1)
        self._config["payload"]["packet_count"] = Int(1)
        self._config["payload"]["ops"] = Array(-1, dimension=2,
                                                data_types=[
                                                    Int(1, value_limit=[0x0, 0xFF], to_hex=True),
                                                    Int(1, value_limit=[0x0, 0xFF], to_hex=True)
                                                ])


class LPSelfTestPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.LP_SELF_TEST_RESP: ['0x8B']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'result': LowPowerSelfTestResult.OK
               }
           }
       """
    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["result"] = Enums(size=1, enum_class=LowPowerSelfTestResult,
                                                  default=LowPowerSelfTestResult.LP_NOT_DETECTED)


class DecimationRatePacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.SET_DECIMATION_REQ: ['0x8E']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'en_decimation':  '0xF'
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["en_decimation"] = Int(1)

class Spo2CoeffPacket(CommandPacket):
    """
       Packet Structure:

       .. code-block::

           {
               'header': {
                   'source': <Application.SENSORHUB: ['0xC8', '0x24']>,
                   'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                   'length': '0xC',
                   'checksum': '0x0'
               },
               'payload': {
                   'command': <SHCommand.SET_SPO2_COEFF_REQ: ['0x92']>,
                   'status': <CommonStatus.OK: ['0x00']>,
                   'type':  <Spo2Coeff.SPO2_COEFF_MLP: ['0x00']>
               }
           }
       """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["type"] = Enums(1, enum_class=Spo2Coeff, default=Spo2Coeff.SPO2_COEFF_MLP)
        self._config["payload"]["spo2_coeff"] = Array(-1, dimension=1, data_types=[Decimal(4)])
