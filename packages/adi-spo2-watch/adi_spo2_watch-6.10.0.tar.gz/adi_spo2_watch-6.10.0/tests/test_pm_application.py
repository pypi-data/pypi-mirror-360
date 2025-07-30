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
import datetime
from unittest import TestCase

from ..adi_spo2_watch import SDK
from ..adi_spo2_watch.core.enums.common_enums import CommonStatus
from ..adi_spo2_watch.core.enums.pm_enums import PMStatus, PMCommand


class TestPMApplication(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.application = SDK("COM4", debug=True).get_pm_application()

    def test_touch_sensor(self):
        x = self.application.enable_touch_sensor()
        assert (x["payload"]["command"] == PMCommand.ACTIVATE_TOUCH_SENSOR_RES)
        x = self.application.disable_touch_sensor()
        assert (x["payload"]["command"] == PMCommand.DEACTIVATE_TOUCH_SENSOR_RES)

    def test_get_battery_info(self):
        x = self.application.get_battery_info()
        assert (x["payload"]["status"] == PMStatus.OK)

    def test_get_chip_id(self):
        x = self.application.get_chip_id(self.application.CHIP_ADPD4K)
        assert (x["payload"]["status"] == PMStatus.OK)

    def test_get_datetime(self):
        x = self.application.get_datetime()
        assert (x["payload"]["status"] == CommonStatus.OK)

    def test_get_low_touch_status(self):
        x = self.application.get_low_touch_status()
        assert (x["payload"]["status"] == PMStatus.LOW_TOUCH_LOGGING_NOT_STARTED)

    def test_get_mcu_version(self):
        x = self.application.get_mcu_version()
        assert (x["payload"]["status"] == PMStatus.OK)

    def test_get_system_info(self):
        x = self.application.get_system_info()
        print(x)
        # assert (x["payload"]["status"] == PMStatus.OK)

    def test_get_version(self):
        x = self.application.get_version()
        assert (x["payload"]["status"] == CommonStatus.OK)

    def test_device_configuration_block_status(self):
        x = self.application.device_configuration_block_status()
        assert (x["payload"]["status"] == PMStatus.OK)

    def test_set_datetime(self):
        x = self.application.set_datetime(datetime.datetime.now())
        assert (x["payload"]["status"] == CommonStatus.OK)

    def test_register(self):
        x = self.application.write_register([[0xa, 0x1], [0xb, 0x2]])
        assert (x["payload"]["size"] == 2)
        assert (x["payload"]["data"] == [['0xA', '0x1'], ['0xB', '0x2']])
        x = self.application.read_register([0xa, 0xb])
        assert (x["payload"]["size"] == 2)
        assert (x["payload"]["data"] == [['0xA', '0x1'], ['0xB', '0x2']])
