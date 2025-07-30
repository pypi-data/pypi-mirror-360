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

from unittest import TestCase

from ..adi_spo2_watch import SDK
from ..adi_spo2_watch.core.enums.fs_enums import FSStatus
from ..adi_spo2_watch.core.enums.pm_enums import PMStatus
from ..adi_spo2_watch.core.enums.common_enums import CommonStatus


def callback(data):
    print(data)


class TestTemperatureApplication(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.application = SDK("COM4", debug=True).get_test_application(callback, callback)

    def test_ping(self):
        x = self.application.ping(3, 70)
        assert (x[0]["payload"]["status"] == CommonStatus.OK)

    def test_set_battery_threshold(self):
        x = self.application.set_battery_threshold(5, 3, 20)
        print(x)
        assert (x["payload"]["status"] == PMStatus.OK)

    def test_set_power_mode(self):
        x = self.application.set_power_mode(self.application.POWER_MODE_ACTIVE)
        assert (x["payload"]["status"] == PMStatus.OK)

    def test_get_apps_health_status(self):
        x = self.application.get_apps_health_status()
        assert (x["payload"]["status"] == CommonStatus.OK)

    def test_flash_reset(self):
        x = self.application.flash_reset()
        assert (x["payload"]["status"] == PMStatus.OK)

    def test_get_states(self):
        x = self.application.get_ppg_states()
        print(x)

    def test_electrode_switch(self):
        x = self.application.disable_electrode_switch(self.application.SWITCH_ADPD4000)
        assert (x["payload"]["status"] == PMStatus.OK)
        x = self.application.enable_electrode_switch(self.application.SWITCH_ADPD4000)
        assert (x["payload"]["status"] == PMStatus.OK)

    def test_ldo(self):
        x = self.application.disable_ldo(self.application.LDO_OPTICAL)
        assert (x["payload"]["status"] == PMStatus.OK)
        x = self.application.enable_ldo(self.application.LDO_OPTICAL)
        assert (x["payload"]["status"] == PMStatus.OK)

    def test_get_bad_blocks(self):
        x = self.application.get_bad_blocks()
        assert (x["payload"]["status"] == CommonStatus.OK)

    def test_get_debug_info(self):
        x = self.application.get_debug_info()
        assert (x["payload"]["status"] == CommonStatus.OK)

    def test_get_stream_debug_info(self):
        x = self.application.get_stream_debug_info(self.application.STREAM_ADXL)
        assert (x["payload"]["status"] == FSStatus.OK)

    def test_fds_status(self):
        self.application.get_fds_status()

    def test_get_agc_info(self):
        x = self.application.get_agc_info(self.application.LED_GREEN)
        assert (x["payload"]["led_index"] == self.application.LED_GREEN)

    def test_adxl_self_test(self):
        x = self.application.adxl_self_test()
        assert (x["payload"]["status"] == CommonStatus.OK)

    def test_file_read_test(self):
        x = self.application.file_read_test("03124671.LOG")
        assert (x["payload"]["status"] == FSStatus.OK)

    def test_page_read_test(self):
        x = self.application.page_read_test(517, 5)
        assert (x["payload"]["status"] == FSStatus.OK)

    def test_get_file_info(self):
        x = self.application.get_file_info(3)
        assert (x["payload"]["status"] == FSStatus.OK)

    def test_get_fds_status(self):
        x = self.application.get_fds_status()
        print(x)

    def test_read_device_configuration_block_info(self):
        x = self.application.read_device_configuration_block_info()
        print(x)

    def test_command1(self):
        x = self.application.test_command1(5)
        print(x)
