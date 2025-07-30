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

from .. import utils
from ..data_types.enums import Enums
from ..data_types.integer import Int
from ..enums import common_enums
from ..enums.common_enums import Application, CommonCommand, CommonStatus, Stream

logger = logging.getLogger(__name__)


class CommandPacket:
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
            }
        }
    """

    def __init__(self, destination=None, command=None):
        self._config = dict(header={}, payload={})
        self._config["header"]["source"] = Enums(2, Application)
        self._config["header"]["destination"] = Enums(2, Application, default=destination)
        self._config["header"]["length"] = Int(2, reverse=True)
        self._config["header"]["checksum"] = Int(2, reverse=True)
        self._config["payload"]["command"] = Enums(1, CommonCommand, default=command)
        self._config["payload"]["status"] = Enums(1, CommonStatus, default=CommonStatus.OK)

    def __str__(self):
        return str(self.get_dict())

    def set_header(self, key, value):
        self._config["header"][key].set_value(value)

    def set_payload(self, key, value):
        self._config["payload"][key].set_value(value)

    def get_header(self, key):
        return self._config["header"][key].get_value()

    def get_payload(self, key):
        return self._config["payload"][key].get_value()

    @staticmethod
    def decode(data, config, start_index):
        if config.get_size() == -1:
            data_slice = data[start_index:]
        else:
            data_slice = data[start_index: start_index + config.get_size()]
        config.decode(data_slice)

    def decode_packet(self, data):
        command = data[8:9]
        source = data[0:2]
        # change source config for stream.
        if command == CommonCommand.STREAM_DATA.value or source == Stream.FS.value:
            self._config["header"]["source"] = Enums(2, Stream)

        start_index = 0
        for key in self._config["header"]:
            self.decode(data, self._config["header"][key], start_index)
            start_index += self._config["header"][key].get_size()

        for key in self._config["payload"]:
            if key == "command":
                # change in command config.
                source = self.get_header("source")
                self._config["payload"]["command"] = Enums(1, common_enums.get_command(command, source))
            elif key == "status":
                # change in status config.
                status = data[9:10]
                source = self.get_header("source")
                self._config["payload"]["status"] = Enums(1, common_enums.get_status(status, source, command))
            self.decode(data, self._config["payload"][key], start_index)
            start_index += self._config["payload"][key].get_size()
        # if not len(data) == start_index:
        #     print(data)
        #     logger.warning(f"There is still some data left to parse. {self.get_dict()}")

    def get_id(self):
        subscribe_id = []
        subscribe_id += self._config["header"]["source"].encode()
        subscribe_id += self._config["payload"]["command"].encode()
        return utils.join_multi_length_packets(subscribe_id)

    def _generate_dict(self):
        packet = dict(header={}, payload={})
        for key in self._config["header"]:
            packet["header"][key] = self._config["header"][key].get_value()
        for key in self._config["payload"]:
            packet["payload"][key] = self._config["payload"][key].get_value()
        return packet

    @staticmethod
    def _trim_data_array(packet):
        size_present = packet["payload"].get("size", None)
        data_present = packet["payload"].get("data", None)
        if size_present is not None and data_present is not None:
            if packet["payload"]["size"] == 0:
                packet["payload"]["data"] = []
            else:
                packet["payload"]["data"] = packet["payload"]["data"][:packet["payload"]["size"]]
        return packet

    def get_dict(self, last_timestamp=None):
        packet = self._generate_dict()
        return self._trim_data_array(packet)

    def to_list(self):
        packet_list = []
        for key in self._config["header"]:
            packet_list += self._config["header"][key].encode()
        for key in self._config["payload"]:
            packet_list += self._config["payload"][key].encode()
        self.set_header("length", len(packet_list))
        packet_list[4:6] = self._config["header"]["length"].encode()
        return packet_list
