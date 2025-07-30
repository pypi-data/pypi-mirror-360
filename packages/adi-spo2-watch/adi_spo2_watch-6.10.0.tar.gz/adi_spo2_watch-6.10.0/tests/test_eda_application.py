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

from . import common_test
from ..adi_spo2_watch import SDK
from ..adi_spo2_watch.core.enums.common_enums import CommonStatus


def callback(data):
    print(data)


class TestEDAApplication(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.application = SDK("COM4", debug=True).get_eda_application()
        cls.application.set_callback(callback)
        cls.application.set_timeout(30)

    def test_calibrate_resistor_tia(self):
        x = self.application.calibrate_resistor_tia(self.application.SCALE_RESISTOR_100K,
                                                    self.application.SCALE_RESISTOR_128K,
                                                    self.application.SCALE_RESISTOR_100K)
        assert (x["payload"]["status"] == CommonStatus.OK)

    def test_dynamic_scaling(self):
        x = self.application.enable_dynamic_scaling(self.application.SCALE_RESISTOR_100K,
                                                    self.application.SCALE_RESISTOR_128K,
                                                    self.application.SCALE_RESISTOR_100K)
        assert (x["payload"]["status"] == CommonStatus.OK)
        x = self.application.disable_dynamic_scaling()
        assert (x["payload"]["status"] == CommonStatus.OK)

    def test_set_discrete_fourier_transformation(self):
        x = self.application.set_discrete_fourier_transformation(self.application.DFT_WINDOW_16)
        assert (x["payload"]["dft_window"] == self.application.DFT_WINDOW_16)

    def test_library_configuration(self):
        x = self.application.read_library_configuration([0x00])
        assert (x["payload"]["size"] == 1)
        x = self.application.write_library_configuration([[0x00, 0x1]])
        assert (x["payload"]["size"] == 1)

    def test_device_configuration_block(self):
        x = self.application.write_device_configuration_block([[0x0, 2]])
        assert (x["payload"]["size"] == 0)
        x = self.application.read_device_configuration_block()
        assert (x["payload"]["data"] == [['0x0', '0x2']])
        x = self.application.delete_device_configuration_block()
        assert (x["payload"]["size"] == 0)

    def test_decimation_factor(self):
        x = self.application.set_decimation_factor(2)
        assert (x["payload"]["decimation_factor"] == 2)
        x = self.application.get_decimation_factor()
        assert (type(x["payload"]["decimation_factor"]) == int)

    def test_get_sensor_status(self):
        x = self.application.get_sensor_status()
        assert (type(x["payload"]["num_subscribers"]) == int)
        assert (type(x["payload"]["num_start_registered"]) == int)

    def test_get_version(self):
        x = self.application.get_version()
        assert (type(x["payload"]["major_version"]) == int)

    def test_stream(self):
        common_test.test_stream(self.application)

    def test_stream_combined(self):
        common_test.test_stream_combined(self.application)

    def test_write_dcb_to_lcfg(self):
        x = self.application.write_dcb_to_lcfg()
        assert (x["payload"]["status"] == CommonStatus.ERROR)
