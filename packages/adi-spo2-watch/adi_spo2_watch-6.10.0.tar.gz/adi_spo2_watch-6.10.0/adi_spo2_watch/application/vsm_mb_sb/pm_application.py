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
from typing import Dict, List

from ...core.enums.pm_enums import PMCommand
from ...core.packets.pm_packets import EEPROMPacket
from ...application.pm_application import PMApplication

logger = logging.getLogger(__name__)


class VSMPMApplication(PMApplication):
    """
    PM Application class.

    .. code-block:: python3
        :emphasize-lines: 4

        from adi_study_watch import SDK

        sdk = SDK("COM4", board=SDK.VSM_MB_SB)
        application = sdk.get_pm_application()

    """

    def __init__(self, packet_manager):
        super().__init__(packet_manager)

    def read_eeprom(self) -> Dict:
        """
        Reads EEPROM.

        .. code-block:: python3
            :emphasize-lines: 4

            from adi_study_watch import SDK

            sdk = SDK("COM4", board=SDK.VSM_MB_SB)
            application = sdk.get_pm_application()
            application.read_eeprom()
        """
        request_packet = EEPROMPacket(self._destination, PMCommand.READ_EEPROM_REQ)
        response_packet = EEPROMPacket(self._destination, PMCommand.READ_EEPROM_RES)
        return self._send_packet(request_packet, response_packet)

    def write_eeprom(self, message: List[int]) -> Dict:
        """
        writes EEPROM.

        .. code-block:: python3
            :emphasize-lines: 4

            from adi_study_watch import SDK

            sdk = SDK("COM4", board=SDK.VSM_MB_SB)
            application = sdk.get_pm_application()
            application.write_eeprom([0x01, 0x02, 0x03])
        """
        request_packet = EEPROMPacket(self._destination, PMCommand.WRITE_EEPROM_REQ)
        request_packet.set_payload("data", message)
        response_packet = EEPROMPacket(self._destination, PMCommand.WRITE_EEPROM_RES)
        return self._send_packet(request_packet, response_packet)
