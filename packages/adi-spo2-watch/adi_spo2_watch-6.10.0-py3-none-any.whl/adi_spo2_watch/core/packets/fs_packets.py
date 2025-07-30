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
from ..data_types.string import String
from ..enums.common_enums import Stream
from .command_packet import CommandPacket
from ..enums.fs_enums import FileType, FSLogging, FSSubState, FSStatus


class BadBlockPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xE',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.GET_BAD_BLOCKS_RES: ['0x7F']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'bad_blocks': 0
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["bad_blocks"] = Int(4)


class ConfigFilePacket(CommandPacket):

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["size"] = Int(2)
        self._config["payload"]["bytes"] = Array(70, data_types=[Int(1)])
        self._config["payload"]["status"] = Enums(1, enum_class=FSStatus)


class DebugInfoPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x2A',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.GET_DEBUG_INFO_RES: ['0x89']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'head_pointer': 374,
                'tail_pointer': 4,
                'usb_avg_tx_time': 0,
                'usb_avg_port_write_time': 0,
                'page_read_time': 0,
                'page_write_time': 1
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["head_pointer"] = Int(4)
        self._config["payload"]["tail_pointer"] = Int(4)
        self._config["payload"]["usb_avg_tx_time"] = Int(4)
        self._config["payload"]["usb_avg_port_write_time"] = Int(4)
        self._config["payload"]["page_read_time"] = Int(4)
        self._config["payload"]["init_circular_buffer_flag"] = Int(2)
        self._config["payload"]["mem_full_flag"] = Int(2)
        self._config["payload"]["data_offset"] = Int(2)
        self._config["payload"]["config_file_occupied"] = Int(2)
        self._config["payload"]["page_write_time"] = Int(4)
        self._config["payload"]["init_circular_buffer_flag"] = Int(2)
        self._config["payload"]["mem_full_flag"] = Int(2)
        self._config["payload"]["data_offset"] = Int(2)
        self._config["payload"]["config_file_occupied"] = Int(2)
        self._config["payload"]["page_write_time"] = Int(4)
        self._config["payload"]["fs_display_query_cnt"] = Int(2)
        self._config["payload"]["min_timer_cnt"] = Int(2)
        self._config["payload"]["block_lock_reg_val"] = Int(1)
        self._config["payload"]["config_reg_val"] = Int(1)
        self._config["payload"]["status_reg_val"] = Int(1)
        self._config["payload"]["die_select_reg_val"] = Int(1)
        self._config["payload"]["device_id"] = Int(1)
        self._config["payload"]["manufacture_id"] = Int(1)


class FileCountPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.GET_NUMBER_OF_FILE_RES: ['0x71']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'file_count': 2
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["file_count"] = Int(2)


class FileInfoRequestPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x26',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.GET_FILE_INFO_RES: ['0x8D']>,
                'status': <FSStatus.OK: ['0x41']>,
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["file_index"] = Int(1)


class FileInfoResponsePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x26',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.GET_FILE_INFO_RES: ['0x8D']>,
                'status': <FSStatus.OK: ['0x41']>,
                'filename': '03123EBD.LOG',
                'start_page': 375,
                'end_page': 375,
                'file_size': 426
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["filename"] = String(16)
        self._config["payload"]["start_page"] = Int(4)
        self._config["payload"]["end_page"] = Int(4)
        self._config["payload"]["file_size"] = Int(4)


class FSStreamStatusPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xD',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.GET_STREAM_SUB_STATUS_RES: ['0x53']>,
                'status': <FSStatus.OK: ['0x41']>,
                'stream_address': <Stream.ADXL: ['0xC2', '0x02']>,
                'sub_state': 0
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["stream_address"] = Enums(2, enum_class=Stream, reverse=True)
        self._config["payload"]["sub_state"] = Enums(1, enum_class=FSSubState, reverse=True)


class KeyValuePairPacket(CommandPacket):

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["value_id"] = String(16)


class KeyValuePairResponsePacket(CommandPacket):

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["key_id"] = Int(2)
        self._config["payload"]["value_id"] = String(16)
        self._config["payload"]["year"] = Int(2)
        self._config["payload"]["month"] = Int(1)
        self._config["payload"]["day"] = Int(1)
        self._config["payload"]["hour"] = Int(1)
        self._config["payload"]["minute"] = Int(1)
        self._config["payload"]["second"] = Int(1)
        self._config["payload"]["tz_sec"] = Int(4)


class LoggingPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xA',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.START_LOGGING_RES: ['0x77']>,
                'status': <FSStatus.OK: ['0x41']>
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["logging_type"] = Enums(1, enum_class=FSLogging)


class LSRequestPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x37',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.LS_RES: ['0x49']>,
                'status': <FSStatus.OK: ['0x41']>,
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["dir_path"] = Int(2, default=257)


class LSResponsePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x37',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.LS_RES: ['0x49']>,
                'status': <FSStatus.OK: ['0x41']>,
                'filename': '03043B06.LOG',
                'filetype': <FileType.DATA_FILE: ['0x01']>,
                'file_size': 160309
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["filename"] = String(40)
        self._config["payload"]["filetype"] = Enums(1, enum_class=FileType)
        self._config["payload"]["file_size"] = Int(4)


class PageInfoRequestPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x7A',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.PAGE_READ_TEST_RES: ['0x8F']>,
                'status': <FSStatus.OK: ['0x41']>,
                'page_num': 300,
                'num_bytes': 10
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["page_num"] = Int(4)
        self._config["payload"]["num_bytes"] = Int(1)


class PageInfoResponsePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x7A',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.PAGE_READ_TEST_RES: ['0x8F']>,
                'status': <FSStatus.OK: ['0x41']>,
                'page_num': 300,
                'ecc_zone_status': 0,
                'next_page': 301,
                'occupied': 1,
                'data_region_status': 0,
                'data': [ 4, 0, 74, 71, 104, 6, 75, 126, 4, 0 ],
                'num_bytes': 10
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["page_num"] = Int(4)
        self._config["payload"]["ecc_zone_status"] = Int(1)
        self._config["payload"]["next_page"] = Int(4)
        self._config["payload"]["occupied"] = Int(1)
        self._config["payload"]["data_region_status"] = Int(1)
        self._config["payload"]["data"] = Array(100, data_types=[Int(1)])
        self._config["payload"]["num_bytes"] = Int(1)

    def get_dict(self, last_timestamp=None):
        packet = super().get_dict(last_timestamp)
        packet["payload"]["data"] = packet["payload"]["data"][:packet["payload"]["num_bytes"]]
        return packet


class PatternWritePacket(CommandPacket):

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["file_size"] = Int(4)
        self._config["payload"]["scale_type"] = Int(1)
        self._config["payload"]["scale_factor"] = Int(2)
        self._config["payload"]["num_files_to_write"] = Int(2)


class StreamDebugInfoPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x26',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.STREAM_DEBUG_INFO_RES: ['0x57']>,
                'status': <FSStatus.OK: ['0x41']>,
                'stream_address': <Stream.ADXL: ['0xC2', '0x02']>,
                'packets_received': 0,
                'packets_missed': 0,
                'last_page_read': 0,
                'last_page_read_offset': 0,
                'last_page_read_status': 0,
                'num_bytes_transferred': 0,
                'bytes_read': 0,
                'usb_cdc_write_failed': 0
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["stream_address"] = Enums(2, enum_class=Stream, reverse=True)
        self._config["payload"]["packets_received"] = Int(4)
        self._config["payload"]["packets_missed"] = Int(4)
        self._config["payload"]["last_page_read"] = Int(4)
        self._config["payload"]["last_page_read_offset"] = Int(4)
        self._config["payload"]["last_page_read_status"] = Int(1)
        self._config["payload"]["num_bytes_transferred"] = Int(4)
        self._config["payload"]["bytes_read"] = Int(4)
        self._config["payload"]["usb_cdc_write_failed"] = Int(1)


class StreamFileChunkPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x20E',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.CHUNK_RETRANSMIT_RES: ['0x85']>,
                'status': <FSStatus.OK: ['0x41']>,
                'retransmit_type': 0,
                'page_roll_over': 1,
                'page_chunk_number': 0,
                'page_number': 2,
                'filename': 'FILENAME.LOG'
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["retransmit_type"] = Int(1)
        self._config["payload"]["page_roll_over"] = Int(1)
        self._config["payload"]["page_chunk_number"] = Int(1)
        self._config["payload"]["page_number"] = Int(2)
        self._config["payload"]["filename"] = String(-1)


class StreamFileRequestPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x20E',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.DOWNLOAD_LOG_RES: ['0x7B']>,
                'status': <FSStatus.OK: ['0x41']>,
                'filename': 'FILENAME.LOG'
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["filename"] = String(-1)


class StreamFileResponsePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x20E',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.DOWNLOAD_LOG_RES: ['0x7B']>,
                'status': <FSStatus.OK: ['0x41']>,
                'page_chunk_number': 1,
                'page_number': 0,
                'page_chunk_size': 512,
                'page_chunk_bytes': [ 0, 195, 0, ... , 0, 0, 0, 0, 0, 0, 0 ],
                'crc16': 4312
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["page_chunk_number"] = Int(1)
        self._config["payload"]["page_number"] = Int(2)
        self._config["payload"]["page_chunk_size"] = Int(2)
        self._config["payload"]["page_chunk_bytes"] = Array(512, data_types=[Int(1)])
        self._config["payload"]["crc16"] = Int(2)


class StreamBleFileResponsePacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x20E',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.DOWNLOAD_LOG_RES: ['0x7B']>,
                'status': <FSStatus.OK: ['0x41']>,
                'page_chunk_number': 1,
                'page_number': 0,
                'page_chunk_size': 512,
                'page_chunk_bytes': [ 0, 195, 0, ... , 0, 0, 0, 0, 0, 0, 0 ],
                'crc16': 4312
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["page_chunk_number"] = Int(1)
        self._config["payload"]["page_number"] = Int(2)
        self._config["payload"]["page_chunk_size"] = Int(2)
        self._config["payload"]["page_chunk_bytes"] = Array(150, data_types=[Int(1)])
        self._config["payload"]["crc16"] = Int(2)


class VolumeInfoPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.FS: ['0xC5', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x14',
                'checksum': '0x0'
            },
            'payload': {
                'command': <FSCommand.VOL_INFO_RES: ['0x4F']>,
                'status': <FSStatus.OK: ['0x41']>,
                'total_memory': 536870656,
                'used_memory': 487424,
                'available_memory': 99
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["total_memory"] = Int(4)
        self._config["payload"]["used_memory"] = Int(4)
        self._config["payload"]["available_memory"] = Int(2)


class SystemTestInfoRequestPacket(CommandPacket):
    """
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["skipped_test_list"] = Array(20, data_types=[Int(1)])


class SystemTestInfoResponsePacket(CommandPacket):
    """
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["num_test_passed"] = Int(1)
        self._config["payload"]["num_test_skipped"] = Int(1)
        self._config["payload"]["num_test_failed"] = Int(1)
