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

import logging
import datetime

logger = logging.getLogger(__name__)


def add_index_to_array(array, one_index=False, to_hex=False):
    result = []
    update_index = 1 if one_index else 0
    for i, val in enumerate(array):
        ind = i + update_index
        ind = '0x%02X' % ind if to_hex else ind
        result.append([ind, val])
    return result


def missing_sequences(expected_seq_no, current_seq_no):
    if current_seq_no > expected_seq_no:
        return current_seq_no - expected_seq_no
    elif current_seq_no < expected_seq_no:
        return current_seq_no + 65536 - expected_seq_no
    return 0


def get_updated_timestamp(reference_time, last_ts, timestamp):
    base_datetime = datetime.datetime.fromtimestamp(reference_time)
    if last_ts > timestamp:
        base_datetime = base_datetime + datetime.timedelta(days=1)
        reference_time = base_datetime.timestamp()
    new_datetime = base_datetime + datetime.timedelta(seconds=timestamp / 32000.0)
    return new_datetime.timestamp(), reference_time


def update_timestamp(packet, last_timestamp, is_syncppg=False):
    single_timestamp = packet["payload"].get("timestamp", None)
    if single_timestamp is not None:
        reference_time, last_ts = last_timestamp
        timestamp = packet["payload"]["timestamp"]
        updated_timestamp, reference_time = get_updated_timestamp(reference_time, last_ts, timestamp)
        packet["payload"]["timestamp"] = updated_timestamp * 1000
        last_timestamp[0] = reference_time
        last_timestamp[1] = timestamp
    else:
        if is_syncppg:
            for i in range(len(packet["payload"]["stream_data"])):
                ppg_reference_time, ppg_last_ts, adxl_reference_time, adxl_last_ts = last_timestamp
                ppg_timestamp = packet["payload"]["stream_data"][i]["ppg_timestamp"]
                adxl_timestamp = packet["payload"]["stream_data"][i]["adxl_timestamp"]
                updated_ppg_timestamp, ppg_reference_time = get_updated_timestamp(
                    ppg_reference_time,
                    ppg_last_ts,
                    ppg_timestamp
                )
                packet["payload"]["stream_data"][i]["ppg_timestamp"] = updated_ppg_timestamp * 1000
                updated_adxl_timestamp, adxl_reference_time = get_updated_timestamp(
                    adxl_reference_time,
                    adxl_last_ts,
                    adxl_timestamp
                )
                packet["payload"]["stream_data"][i]["adxl_timestamp"] = updated_adxl_timestamp * 1000
                last_timestamp[0] = ppg_reference_time
                last_timestamp[1] = ppg_timestamp
                last_timestamp[2] = adxl_reference_time
                last_timestamp[3] = adxl_timestamp
        else:
            for i in range(len(packet["payload"]["stream_data"])):
                reference_time, last_ts = last_timestamp
                timestamp = packet["payload"]["stream_data"][i]["timestamp"]
                updated_timestamp, reference_time = get_updated_timestamp(reference_time, last_ts, timestamp)
                packet["payload"]["stream_data"][i]["timestamp"] = updated_timestamp * 1000
                last_timestamp[0] = reference_time
                last_timestamp[1] = timestamp


def join_multi_length_packets(packet, sign=False, reverse=False, convert_to_hex=False):
    """
    Joins array of bytes into integer.
    """
    ans = 0
    packet_len = len(packet)
    if packet_len == 0:
        return ans
    if reverse:
        packet = list(reversed(packet))
    for i, value in enumerate(packet):
        ans += (value << (8 * i))
    bits = packet_len * 8
    if sign and ans & (1 << (bits - 1)):
        ans -= 1 << bits
    if convert_to_hex:
        return "0x%X" % ans
    return ans


def split_int_in_bytes(value, length=None, reverse=False):
    """
    Breaks int into array of byte array of specified length.
    """
    result = []
    shift = 0
    base_value = 0
    if value < 0:
        base_value = 255
    while value >> shift and not (value < 0 and value >> shift == -1):
        result.append((value >> shift) & 0xff)
        shift += 8
    if length and not len(result) == length:
        result += [base_value] * abs(length - len(result))
    if reverse:
        result = list(reversed(result))
    return result


def convert_int_array_to_hex(arr):
    """
    Convert int to hex.
    """
    return ['0x%02X' % x for x in arr]


def pretty(value, tab_char='\t', next_line_char='\n', indent=0):
    """
    Print dict in clean format.
    """
    line = next_line_char + tab_char * (indent + 1)
    if type(value) is dict:
        items = [
            line + repr(key) + ': ' + pretty(value[key], tab_char, next_line_char, indent + 1)
            for key in value
        ]
        return '{%s}' % (','.join(items) + next_line_char + tab_char * indent)
    elif type(value) is list:
        items = []
        flag = " "
        for item in value:
            if type(item) is list:
                flag = line[:-1]
                items.append(line + pretty(item, tab_char, next_line_char, indent))
            elif type(item) is dict:
                flag = line[:-1]
                items.append(line + pretty(item, tab_char, next_line_char, indent + 1))
            else:
                items.append(" " + pretty(item, tab_char, " ", 0))
        return '[%s%s]' % (','.join(items), flag)
    elif type(value) is tuple:
        items = [
            line + pretty(item, tab_char, next_line_char, indent + 1)
            for item in value
        ]
        return '(%s)' % (','.join(items) + next_line_char + tab_char * indent)
    else:
        return repr(value)
