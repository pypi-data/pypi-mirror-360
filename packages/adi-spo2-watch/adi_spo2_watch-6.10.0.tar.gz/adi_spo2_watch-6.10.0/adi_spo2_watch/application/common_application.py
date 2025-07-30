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

import re
import time
import logging
from queue import Queue

from ..core import utils
from ..core.enums.common_enums import CommonCommand

logger = logging.getLogger(__name__)


class CommonApplication:
    """
    A Common Application class.
    """

    def __init__(self, destination, packet_manager):
        """
        Initialize the common application class.

        :param destination: Address of the application.
        :param packet_manager: PacketManager Object.
        """
        self._timeout = 10
        self._packet_queues = {}
        self._destination = destination
        self._packet_manager = packet_manager
        is_dst = time.daylight and time.localtime().tm_isdst > 0
        self.tz_sec = - (time.altzone if is_dst else time.timezone)

    def _get_packet_id(self, response_command, destination=None):
        """
        Generates a unique packet ID.
        """
        destination = destination if destination else self._destination
        packet_id = utils.join_multi_length_packets(destination.value + response_command.value)
        return packet_id

    def _get_queue(self, packet_id):
        """
        Returns specified queue for packet ID.
        """
        queue = self._packet_queues.get(packet_id, None)
        if not queue:
            self._packet_queues[packet_id] = Queue()
        return self._packet_queues[packet_id]

    def _send_packet(self, request_packet, response_packet=None, callback=None, get_bytes=False, timeout=None):
        """
        Sends the specified packet to the packet manager, subscribe the callback for the packet id,
        retrieves the packet response from queue and unsubscribe from the packet id.
        """
        callback = callback if callback else self._callback_command
        command = response_packet.get_payload("command")
        destination = response_packet.get_header("destination")
        packet_id = self._get_packet_id(command, destination)
        self._packet_manager.subscribe(packet_id, callback)
        queue = self._get_queue(packet_id)
        self._packet_manager.send_packet(request_packet)
        source_address = response_packet.get_header("destination")
        response_byte = self._get_queue_data(queue, sourceAddress=source_address.value ,commandName=command, timeout=timeout)
        response_packet.decode_packet(response_byte)
        self._packet_manager.unsubscribe(packet_id, callback)
        response_dict = response_packet.get_dict()
        logger.debug(f"Packet decoded : {response_dict}")
        if get_bytes:
            return response_dict, response_byte
        return response_dict

    def _send_packet_no_response(self, request_packet, ):
        """
        Sends the specified packet to the packet manager, subscribe the callback for the packet id,
        retrieves the packet response from queue and unsubscribe from the packet id.
        """
        self._packet_manager.send_packet(request_packet)
        return {}

    def _send_packet_multi_response(self, request_packet, response_packet=None, packet_limit=None, timeout=None):
        result = []
        packet_count = 1
        command = response_packet.get_payload("command")
        destination = response_packet.get_header("destination")
        packet_id = self._get_packet_id(command, destination)
        self._packet_manager.subscribe(packet_id, self._callback_command)
        queue = self._get_queue(packet_id)
        self._packet_manager.send_packet(request_packet)
        while True:
            data = self._get_queue_data(queue, timeout=timeout)
            temp_packet = response_packet.__class__()
            temp_packet.decode_packet(data)
            packet_dict = temp_packet.get_dict()
            result.append(packet_dict)
            if packet_limit:
                if packet_limit <= packet_count:
                    break
            else:
                number_of_packets = packet_dict["payload"]["packet_count"]
                if number_of_packets == packet_count or number_of_packets == 0:
                    break
            packet_count += 1
        self._packet_manager.unsubscribe(packet_id, self._callback_command)
        return result

    def _get_queue_data(self, queue, sourceAddress = [0,0], commandName=CommonCommand.NO_RESPONSE, throw_exception=False, timeout=None):
        response_byte = [0, 0, 0, 0, 0, 10, 0, 0, commandName.value[0], -1] + [0] * 255
        response_byte[:2] = sourceAddress
        try:
            timeout = timeout if timeout else self._timeout
            response_byte = queue.get(timeout=timeout)
        except Exception as e:
            logger.debug(f"No data received, reason :: {e}.")
            if throw_exception:
                raise Exception("Timeout from Serial Port.")
        return response_byte

    def _callback_command(self, data, packet_id):
        """
        Receives the command response packet and store it in its respective packet id queue.
        """
        self._get_queue(packet_id).put(data)

    def set_timeout(self, timeout_value: float):
        """
        Sets the time out for queue to wait for command packet response.

        :param timeout_value: queue timeout value.
        :type timeout_value: int
        """
        self._timeout = timeout_value

    @staticmethod
    def _parse_single_dcb_line(dcb_line):
        str_val = dcb_line.split('#')
        str_val[0] = re.sub(r'[ ]+', " ", str_val[0], 0, re.MULTILINE)
        dcb = str_val[0].replace('\t', '').replace('\n', '').split(" ")
        return dcb

    @staticmethod
    def device_configuration_file_to_list(dcfg_file: str, address: bool = True):
        """
        This API parse DCB file to python List.

        :param dcfg_file: DCB file.
        :param address: If address is true, it will return a 2D list else 1D list.
        :return: List
        """
        try:
            file = open(dcfg_file, 'r')
            result = []
            for line in file:
                if line[0] != '#' and line[0] != '<' and line[0] != '\n' and line[0] != ' ' and line[0] != '\t':
                    dcb = CommonApplication._parse_single_dcb_line(line)
                    if address:
                        result.append([int(dcb[0], 16), int(dcb[1], 16)])
                    else:
                        result.append(int(dcb[0], 16))
            file.close()
            return result
        except Exception as e:
            logger.error(f"Can't parse {dcfg_file} file, make sure it's a single app dcfg file. Error :: {e}.",
                         exc_info=True)
