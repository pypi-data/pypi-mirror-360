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

from enum import Enum, unique

from .. import utils


@unique
class FSCommand(Enum):
    """
    FSCommand Enum
    """
    LOWEST = [0x40]
    MOUNT_REQ = [0x42]
    MOUNT_RES = [0x43]
    FORMAT_REQ = [0x46]
    FORMAT_RES = [0x47]
    LS_REQ = [0x48]
    LS_RES = [0x49]
    VOL_INFO_REQ = [0x4E]
    VOL_INFO_RES = [0x4F]
    GET_STATUS_REQ = [0x50]
    GET_STATUS_RES = [0x51]
    GET_STREAM_SUB_STATUS_REQ = [0x52]
    GET_STREAM_SUB_STATUS_RES = [0x53]
    STREAM_DEBUG_INFO_REQ = [0x56]
    STREAM_DEBUG_INFO_RES = [0x57]
    TEST_LOG_REQ = [0x58]
    TEST_LOG_RES = [0x59]
    FORCE_STOP_LOG_REQ = [0x5A]
    FORCE_STOP_LOG_RES = [0x5B]
    SET_KEY_VALUE_PAIR_REQ = [0x64]
    SET_KEY_VALUE_PAIR_RES = [0x65]
    DCFG_START_LOG_REQ = [0x66]
    DCFG_START_LOG_RES = [0x67]
    DCFG_STOP_LOG_REQ = [0x68]
    DCFG_STOP_LOG_RES = [0x69]
    LOG_USER_CONFIG_DATA_REQ = [0x6A]
    LOG_USER_CONFIG_DATA_RES = [0x6B]
    DELETE_CONFIG_FILE_REQ = [0x6E]
    DELETE_CONFIG_FILE_RES = [0x6F]
    GET_NUMBER_OF_FILE_REQ = [0x70]
    GET_NUMBER_OF_FILE_RES = [0x71]
    START_STREAM_LOGGING_REQ = [0x72]
    START_STREAM_LOGGING_RES = [0x73]
    STOP_STREAM_LOGGING_REQ = [0x74]
    STOP_STREAM_LOGGING_RES = [0x75]
    START_LOGGING_REQ = [0x76]
    START_LOGGING_RES = [0x77]
    STOP_LOGGING_REQ = [0x78]
    STOP_LOGGING_RES = [0x79]
    DOWNLOAD_LOG_REQ = [0x7A]
    DOWNLOAD_LOG_RES = [0x7B]
    GET_BAD_BLOCKS_REQ = [0x7E]
    GET_BAD_BLOCKS_RES = [0x7F]
    CHUNK_RETRANSMIT_REQ = [0x84]
    CHUNK_RETRANSMIT_RES = [0x85]
    GET_DEBUG_INFO_REQ = [0x88]
    GET_DEBUG_INFO_RES = [0x89]
    PATTERN_WRITE_REQ = [0x8A]
    PATTERN_WRITE_RES = [0x8B]
    GET_FILE_INFO_REQ = [0x8C]
    GET_FILE_INFO_RES = [0x8D]
    PAGE_READ_TEST_REQ = [0x8E]
    PAGE_READ_TEST_RES = [0x8F]
    APPEND_FILE_REQ = [0xA0]
    APPEND_FILE_RES = [0xA1]
    DOWNLOAD_LOG_BLE_REQ = [0xA4]
    DOWNLOAD_LOG_BLE_RES = [0xA5]
    DOWNLOAD_LOG_CONTINUE_REQ = [0xAE]
    DOWNLOAD_LOG_CONTINUE_RES = [0xAF]
    DOWNLOAD_LOG_CONTINUE_BLE_REQ = [0xB0]
    DOWNLOAD_LOG_CONTINUE_BLE_RES = [0xB1]
    STREAM_CONTINUE_DEBUG_REQ = [0xB2]
    STREAM_CONTINUE_DEBUG_RES = [0xB3]
    STREAM_CONTINUE_RESET_REQ = [0xB4]
    STREAM_CONTINUE_RESET_RES = [0xB5]
    DEVELOPER_TEST_REQ = [0xB8]
    DEVELOPER_TEST_RES = [0xB9]
    DEVELOPER_BAD_BLOCK_CREATE_REQ = [0xBA]
    DEVELOPER_BAD_BLOCK_CREATE_RES = [0xBB]
    DEVELOPER_GOOD_BLOCK_CREATE_REQ = [0xBE]
    DEVELOPER_GOOD_BLOCK_CREATE_RES = [0xBF]
    PATTERN_CONFIG_WRITE_REQ = [0xC0]
    PATTERN_CONFIG_WRITE_RES = [0xC1]
    GET_APP_DEBUG_INFO_REQ = [0xC2]
    GET_APP_DEBUG_INFO_RES = [0xC3]
    FS_USB_APP_DEBUG_INFO_REQ = [0xC4]
    FS_USB_APP_DEBUG_INFO_RES = [0xC5]
    FS_CLOSE_STREAM_FILE_REQ = [0xC6]
    FS_CLOSE_STREAM_FILE_RESP = [0xc7]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class FSStatus(Enum):
    """
    FSStatus Enum
    """
    LOWEST = [0x40]
    OK = [0x41]
    ERROR = [0x42]
    END_OF_FILE = [0x43]
    END_OF_DIR = [0x44]
    ERR_INVALID = [0x45]
    ERR_ARGS = [0x46]
    ERR_FORMAT = [0x47]
    ERR_MEMORY_FULL = [0x48]
    ERR_LOG_FORCE_STOPPED = [0x49]
    ERR_MAX_FILE_COUNT = [0x4A]
    CONFIG_FILE_FOUND = [0x4B]
    CONFIG_FILE_NOT_FOUND = [0x4C]
    LOGGING_STOPPED = [0x4D]
    LOGGING_IN_PROGRESS = [0x4E]
    LOGGING_ERROR = [0x4F]
    LOGGING_NOT_STARTED = [0x50]
    ERR_BATTERY_LOW = [0x51]
    ERR_POWER_STATE_SHUTDOWN = [0x52]
    ERR_CONFIG_FILE_POSITION = [0x53]
    BLOCKS_WRITE_ERROR = [0x54]
    NO_FILE_TO_APPEND = [0x55]
    ERR_STREAM_ONGOING = [0x56]
    ERR_STREAM_INVALID_TOOL = [0x57]
    SUB_FAILED_BATTERY_LOW = [0x58]
    SUBSCRIBER_ADDED = [0x59]
    SUBSCRIBER_REMOVED = [0x5A]
    SUBSCRIBER_COUNT_DECREMENT = [0x5B]
    ERR_NOT_CHKD = [0xFF]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class FileType(Enum):
    """
    FileType Enum
    """
    CONFIG_FILE = [0x0]
    DATA_FILE = [0x1]
    INVALID_TYPE = [0x2]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class FSLogging(Enum):
    """
    FSLogging Enum
    """
    STOP_LOGGING = [0x0]
    MEMORY_FULL = [0x1]
    BATTERY_LOW = [0x2]
    POWER_STATE_SHUTDOWN = [0x3]
    STREAMS_NOT_UNSUBSCRIBED = [0x16]
    STOP_LOGGING_INVALID = [0xFF]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))


@unique
class FSSubState(Enum):
    """
    FSSubState Enum
    """
    UNSUBSCRIBED = [0x0]
    SUBSCRIBED = [0x1]
    INVALID = [0xFF]

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, utils.convert_int_array_to_hex(self._value_))
