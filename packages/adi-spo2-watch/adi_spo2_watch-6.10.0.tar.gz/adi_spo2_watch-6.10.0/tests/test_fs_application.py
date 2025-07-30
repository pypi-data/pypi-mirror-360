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
from ..adi_spo2_watch.core.enums.common_enums import CommonStatus
from ..adi_spo2_watch.core.enums.fs_enums import FSStatus


class TestFSApplication(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.application = SDK("COM4", debug=True).get_fs_application()

    def test_abort_logging(self):
        x = self.application.abort_logging()
        assert (x["payload"]["status"] == CommonStatus.STREAM_NOT_STARTED)

    def test_config_log(self):
        self.application.disable_config_log()
        self.application.enable_config_log()

    def test_delete_config_file(self):
        self.application.delete_config_file()

    def test_logging(self):
        self.application.start_logging()
        self.application.stop_logging()

    def test_get_file_count(self):
        x = self.application.get_file_count()
        assert (x["payload"]["status"] == CommonStatus.OK)

    def test_format(self):
        x = self.application.format()
        assert (x["payload"]["status"] == FSStatus.OK)

    def test_get_stream_status(self):
        x = self.application.get_stream_status(self.application.STREAM_ADXL)
        assert (x["payload"]["status"] == FSStatus.OK)

    def test_inject_key_value_pair(self):
        x = self.application.inject_key_value_pair(1234)
        assert (x["payload"]["status"] == FSStatus.OK)

    def test_ls(self):
        x = self.application.ls()
        assert (type(x) == list)

    def test_get_status(self):
        x = self.application.get_status()
        assert (x["payload"]["status"] == FSStatus.LOGGING_NOT_STARTED)

    def test_subscribe_stream(self):
        x = self.application.subscribe_stream(self.application.STREAM_ADXL)
        assert (x["payload"]["status"] == CommonStatus.SUBSCRIBER_ADDED)
        x = self.application.unsubscribe_stream(self.application.STREAM_ADXL)
        assert (x["payload"]["status"] == CommonStatus.SUBSCRIBER_REMOVED)

    def test_volume_info(self):
        x = self.application.volume_info()
        assert (x["payload"]["status"] == FSStatus.OK)
