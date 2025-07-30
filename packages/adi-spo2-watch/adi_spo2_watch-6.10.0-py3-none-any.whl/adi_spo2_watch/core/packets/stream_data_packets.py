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

from .. import utils
from ..data_types.array import Array
from ..data_types.enums import Enums
from ..data_types.integer import Int
from ..data_types.decimal import Decimal
from .command_packet import CommandPacket
from ..enums.bia_enums import BIAAppInfo

class ECGDataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - Data Type
             - Depricated
             - Depricated
           * - ECG Info
             - bool
             - Leads off/Leads on
           * - HR
             - Not supported
             - Not supported
           * - ECG data
             - ADC count
             - --

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.ECG: ['0xC4', '0x01']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x3D',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 0,
                'data_type': 1,
                'ecg_info': 0,
                'hr': 0,
                'stream_data': [
                    {
                        'timestamp': 1771095376,
                        'ecg_data': 12351
                    },
                    {
                        'timestamp': 1771095703,
                        'ecg_data': 12353
                    },
                    {
                        'timestamp': 1771096030,
                        'ecg_data': 52470
                    },
                    {
                        'timestamp': 1771096357,
                        'ecg_data': 41129
                    },
                    {
                        'timestamp': 1771096676,
                        'ecg_data': 63838
                    },
                    {
                        'timestamp': 1771096995,
                        'ecg_data': 63848
                    },
                    {
                        'timestamp': 1771097314,
                        'ecg_data': 63848
                    },
                    {
                        'timestamp': 1771097633,
                        'ecg_data': 63848
                    },
                    {
                        'timestamp': 1771097954,
                        'ecg_data': 63833
                    },
                    {
                        'timestamp': 1771098273,
                        'ecg_data': 63846
                    },
                    {
                        'timestamp': 1771098592,
                        'ecg_data': 63846
                    }
                ]
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["data_type"] = Int(1)
        self._config["payload"]["timestamp1"] = Int(4)
        self._config["payload"]["ecg_info"] = Int(1)
        self._config["payload"]["hr"] = Int(1)
        self._config["payload"]["ecg_data1"] = Int(2)
        self._config["payload"]["timestamp2"] = Int(2)
        self._config["payload"]["ecg_data2"] = Int(2)
        self._config["payload"]["timestamp3"] = Int(2)
        self._config["payload"]["ecg_data3"] = Int(2)
        self._config["payload"]["timestamp4"] = Int(2)
        self._config["payload"]["ecg_data4"] = Int(2)
        self._config["payload"]["timestamp5"] = Int(2)
        self._config["payload"]["ecg_data5"] = Int(2)
        self._config["payload"]["timestamp6"] = Int(2)
        self._config["payload"]["ecg_data6"] = Int(2)
        self._config["payload"]["timestamp7"] = Int(2)
        self._config["payload"]["ecg_data7"] = Int(2)
        self._config["payload"]["timestamp8"] = Int(2)
        self._config["payload"]["ecg_data8"] = Int(2)
        self._config["payload"]["timestamp9"] = Int(2)
        self._config["payload"]["ecg_data9"] = Int(2)
        self._config["payload"]["timestamp10"] = Int(2)
        self._config["payload"]["ecg_data10"] = Int(2)
        self._config["payload"]["timestamp11"] = Int(2)
        self._config["payload"]["ecg_data11"] = Int(2)

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["stream_data"] = []
        timestamp = 0
        for i in range(1, 12):
            timestamp += packet["payload"][f"timestamp{i}"]
            data = {"timestamp": timestamp,
                    "ecg_data": packet["payload"][f"ecg_data{i}"]}
            [packet["payload"].pop(key) for key in [f"timestamp{i}", f"ecg_data{i}"]]
            packet["payload"]["stream_data"].append(data)
        utils.update_timestamp(packet, last_timestamp)
        return packet


class EDADataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - Data Type
             - N/A
             - N/A
           * - Real
             - Ohm
             - -32,768 to 32,767
           * - Imaginary
             - Ohm
             - -32,768 to 32,767

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.EDA: ['0xC4', '0x02']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x3D',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 0,
                'data_type': 0,
                'stream_data': [
                    {
                        'timestamp': 1774366622,
                        'real': 0,
                        'imaginary': 0
                    },
                    {
                        'timestamp': 1774374407,
                        'real': 0,
                        'imaginary': 16708
                    },
                    {
                        'timestamp': 1774382157,
                        'real': 16728,
                        'imaginary': 3257
                    },
                    {
                        'timestamp': 1774389924,
                        'real': 3277,
                        'imaginary': -20751
                    },
                    {
                        'timestamp': 1774397691,
                        'real': -20731,
                        'imaginary': -15161
                    },
                    {
                        'timestamp': 1774405458,
                        'real': -15141,
                        'imaginary': -30319
                    }
                ]
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["data_type"] = Int(1)
        self._config["payload"]["timestamp1"] = Int(4)
        self._config["payload"]["real1"] = Int(2, sign=True)
        self._config["payload"]["imaginary1"] = Int(2, sign=True)
        self._config["payload"]["timestamp2"] = Int(4)
        self._config["payload"]["real2"] = Int(2, sign=True)
        self._config["payload"]["imaginary2"] = Int(2, sign=True)
        self._config["payload"]["timestamp3"] = Int(4)
        self._config["payload"]["real3"] = Int(2, sign=True)
        self._config["payload"]["imaginary3"] = Int(2, sign=True)
        self._config["payload"]["timestamp4"] = Int(4)
        self._config["payload"]["real4"] = Int(2, sign=True)
        self._config["payload"]["imaginary4"] = Int(2, sign=True)
        self._config["payload"]["timestamp5"] = Int(4)
        self._config["payload"]["real5"] = Int(2, sign=True)
        self._config["payload"]["imaginary5"] = Int(2, sign=True)
        self._config["payload"]["timestamp6"] = Int(4)
        self._config["payload"]["real6"] = Int(2, sign=True)
        self._config["payload"]["imaginary6"] = Int(2, sign=True)

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["stream_data"] = []
        for i in range(1, 7):
            timestamp = packet["payload"][f"timestamp{i}"]
            data = {"timestamp": timestamp,
                    "real": packet["payload"][f"real{i}"],
                    "imaginary": packet["payload"][f"imaginary{i}"]}
            [packet["payload"].pop(key) for key in [f"timestamp{i}", f"real{i}", f"imaginary{i}"]]
            packet["payload"]["stream_data"].append(data)
        utils.update_timestamp(packet, last_timestamp)
        return packet


class TemperatureDataPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.TEMPERATURE: ['0xC4', '0x06']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x14',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 2,
                'timestamp': 1779692742,
                'skin_temperature': 30.1, # celsius
                'impedance': 79000 # ohm
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["timestamp"] = Int(4)
        self._config["payload"]["skin_temperature"] = Int(2)
        self._config["payload"]["impedance"] = Int(2)

    def get_dict(self, last_timestamp=None):
        """
        Postprocessing.
        """
        packet = super().get_dict()
        packet["payload"]["skin_temperature"] = packet["payload"]["skin_temperature"] / 1000.0
        packet["payload"]["impedance"] = packet["payload"]["impedance"] * 100
        utils.update_timestamp(packet, last_timestamp)
        return packet


class BIADataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - BIA info
             - bool
             - Leads off/Leads on
           * - Real
             - Ohm
             - --
           * - Imaginary
             - Ohm
             - --
           * - Frequency Index
             - Hz
             - 1 to 200,000Hz

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.BIA: ['0xC4', '0x07']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x41',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 1,
                'data_type': 0,
                'stream_data': [
                    {
                        'timestamp': 1788107093,
                        'real': 0,
                        'imaginary': 0,
                        'frequency_index': 82
                    },
                    {
                        'timestamp': 1788114863,
                        'real': 0,
                        'imaginary': 0,
                        'frequency_index': 5
                    },
                    {
                        'timestamp': 1788122630,
                        'real': 0,
                        'imaginary': 0,
                        'frequency_index': 8
                    },
                    {
                        'timestamp': 1788130399,
                        'real': 0,
                        'imaginary': 0,
                        'frequency_index': 54
                    }
                ]
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["data_type"] = Int(1)
        self._config["payload"]["bia_info"] = Enums(1, enum_class=BIAAppInfo)
        self._config["payload"]["timestamp1"] = Int(4)
        self._config["payload"]["real1"] = Int(4, sign=True)
        self._config["payload"]["imaginary1"] = Int(4, sign=True)
        self._config["payload"]["frequency_index1"] = Int(4)
        self._config["payload"]["timestamp2"] = Int(4)
        self._config["payload"]["real2"] = Int(4, sign=True)
        self._config["payload"]["imaginary2"] = Int(4, sign=True)
        self._config["payload"]["frequency_index2"] = Int(4)
        self._config["payload"]["timestamp3"] = Int(4)
        self._config["payload"]["real3"] = Int(4, sign=True)
        self._config["payload"]["imaginary3"] = Int(4, sign=True)
        self._config["payload"]["frequency_index3"] = Int(4)
        self._config["payload"]["timestamp4"] = Int(4)
        self._config["payload"]["real4"] = Int(4, sign=True)
        self._config["payload"]["imaginary4"] = Int(4, sign=True)
        self._config["payload"]["frequency_index4"] = Int(4)

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["stream_data"] = []
        for i in range(1, 5):
            timestamp = packet["payload"][f"timestamp{i}"]
            data = {"timestamp": timestamp,
                    "real": packet["payload"][f"real{i}"],
                    "imaginary": packet["payload"][f"imaginary{i}"],
                    "frequency_index": packet["payload"][f"frequency_index{i}"]}
            [packet["payload"].pop(key) for key in
             [f"timestamp{i}", f"real{i}", f"imaginary{i}", f"frequency_index{i}"]]
            packet["payload"]["stream_data"].append(data)
        utils.update_timestamp(packet, last_timestamp)
        return packet


class KeyStreamDataPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.DISPLAY: ['0xC5', '0x03']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xB',
                'checksum': '0x0'
            },
            'payload': {
                'command': <DisplayCommand.KEY_STREAM_DATA: ['0x48']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'key_code': 18
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["key_code"] = Int(1)


class CapSenseStreamDataPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Application.PM: ['0xC5', '0x00']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0xC',
                'checksum': '0x0'
            },
            'payload': {
                'command': <PMCommand.CAP_SENSE_STREAM_DATA: ['0x82']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'position': 1,
                'value': 0
            }
        }
    """

    def __init__(self, destination=None, command=None):
        super().__init__(destination, command)
        self._config["payload"]["position"] = Int(1)
        self._config["payload"]["value"] = Int(1)


class AD7156DataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - CH1 Cap
             - pF
             - 0 to 4pF
           * - CH2 Cap
             - pF
             - 0 to 4pF
           * - CH1 ADC Code
             - ADC Code
             - --
           * - CH2 ADC Code
             - ADC Code
             - --
           * - OUT1 Val
             - --
             - --
           * - OUT2 Val
             - --
             - --

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.AD7156: ['0xC8', '0x15']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x2C',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 0,
                'stream_data': [
                    {
                        'timestamp': 1751731879,
                        'ch1_cap': 102,
                        'ch2_cap': 1023,
                        'ch1_ADCCode': 1023,
                        'ch2_ADCCode': 1023,
                        'OUT1_val': 1023,
                        'OUT2_val': 1023,
                    }
                    {
                        'timestamp': 1751731879,
                        'ch1_cap': 102,
                        'ch2_cap': 1023,
                        'ch1_ADCCode': 1023,
                        'ch2_ADCCode': 1023,
                        'OUT1_val': 1023,
                        'OUT2_val': 1023,
                    }
                ]
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["timestamp1"] = Int(4)
        self._config["payload"]["ch1_cap1"] = Int(2)
        self._config["payload"]["ch2_cap1"] = Int(2)
        self._config["payload"]["ch1_ADCCode1"] = Int(2)
        self._config["payload"]["ch2_ADCCode1"] = Int(2)
        self._config["payload"]["OUT1_val1"] = Int(1)
        self._config["payload"]["OUT2_val1"] = Int(1)
        self._config["payload"]["timestamp2"] = Int(2)
        self._config["payload"]["ch1_cap2"] = Int(2)
        self._config["payload"]["ch2_cap2"] = Int(2)
        self._config["payload"]["ch1_ADCCode2"] = Int(2)
        self._config["payload"]["ch2_ADCCode2"] = Int(2)
        self._config["payload"]["OUT1_val2"] = Int(1)
        self._config["payload"]["OUT2_val2"] = Int(1)
        self._config["payload"]["timestamp3"] = Int(2)
        self._config["payload"]["ch1_cap3"] = Int(2)
        self._config["payload"]["ch2_cap3"] = Int(2)
        self._config["payload"]["ch1_ADCCode3"] = Int(2)
        self._config["payload"]["ch2_ADCCode3"] = Int(2)
        self._config["payload"]["OUT1_val3"] = Int(1)
        self._config["payload"]["OUT2_val3"] = Int(1)
        self._config["payload"]["timestamp4"] = Int(2)
        self._config["payload"]["ch1_cap4"] = Int(2)
        self._config["payload"]["ch2_cap4"] = Int(2)
        self._config["payload"]["ch1_ADCCode4"] = Int(2)
        self._config["payload"]["ch2_ADCCode4"] = Int(2)
        self._config["payload"]["OUT1_val4"] = Int(1)
        self._config["payload"]["OUT2_val4"] = Int(1)

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["stream_data"] = []
        timestamp = 0
        for i in range(1, 5):
            timestamp += packet["payload"][f"timestamp{i}"]
            data = {
                "timestamp": timestamp,
                "ch1_cap": packet["payload"][f"ch1_cap{i}"],
                "ch2_cap": packet["payload"][f"ch2_cap{i}"],
                "ch1_ADCCode": packet["payload"][f"ch1_ADCCode{i}"],
                "ch2_ADCCode": packet["payload"][f"ch2_ADCCode{i}"],
                "OUT1_val": packet["payload"][f"OUT1_val{i}"],
                "OUT2_val": packet["payload"][f"OUT2_val{i}"]
            }
            [packet["payload"].pop(key) for key in [f"timestamp{i}", f"ch1_cap{i}", f"ch2_cap{i}",
                                                    f"ch1_ADCCode{i}", f"ch2_ADCCode{i}",
                                                    f"OUT1_val{i}", f"OUT2_val{i}"]]
            packet["payload"]["stream_data"].append(data)
        utils.update_timestamp(packet, last_timestamp)
        return packet


class BCMDataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - FFM Estimated
             - --
             - --
           * - BMI
             - Kg/sq.m
             - 15 to 50
           * - Fat percent
             - Percentage
             - 0 to 100

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.BCM: ['0xC8', '0x14']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x2C',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 0,
                'ffm_estimated': 1,
                'bmi': 20.4,
                'fat_percent': 12,
                'timestamp': 1751731879,
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_num"] = Int(2)
        self._config["payload"]["ffm_estimated"] = Decimal(4)
        self._config["payload"]["bmi"] = Decimal(4)
        self._config["payload"]["fat_percent"] = Decimal(4)
        self._config["payload"]["timestamp"] = Int(4)

    def get_dict(self, last_timestamp=None):
        """
        Postprocessing.
        """
        packet = super().get_dict()
        utils.update_timestamp(packet, last_timestamp)
        return packet


class SHMAX86178DataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - SH data
             - ADC count
             - 0 to 524287

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.SENSORHUB_MAX86178_STREAM1: ['0xC8', '0x27']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x2C',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 0,
                'op_mode': 1,
                'channel_num': 2,
                'timestamp': 1751731879,
                'sample_num': 2,
                'sh_data': [ 351762, 351755 ],
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode"] = Int(1)
        self._config["payload"]["timestamp"] = Int(4)
        self._config["payload"]["channel_num"] = Int(1)
        self._config["payload"]["sample_num"] = Int(1)
        self._config["payload"]["data"] = Array(-1, dimension=1, data_types=[Int(1)])

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["sh_data"] = []
        data_size = 3
        sample_num = packet["payload"]["sample_num"]
        for i in range(0, sample_num * data_size, data_size):
            data = packet["payload"]["data"][i: i + data_size]
            sh_data = utils.join_multi_length_packets(data)
            packet["payload"]["sh_data"].append(sh_data)
        del packet["payload"]["data"]
        utils.update_timestamp(packet, last_timestamp)
        return packet

class SHMAX86178ECGDataPacket(CommandPacket):
    """
     .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - Lead status
             - bool
             - Leads off/ Leads on 
           * - ECG data
             - ADC count
             - -32,768 to 32,767

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.SENSORHUB_MAX86178_ECG_STREAM: ['0xC8', '0x32']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x2C',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 0,
                'op_mode': 1,
                'timestamp': 1751731879,
                'ecg_data': [ 35762, 35755, ... ],
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode"] = Int(1)
        self._config["payload"]["timestamp"] = Int(4)
        self._config["payload"]["lead_status"] = Int(1)
        self._config["payload"]["ecg_data"] = Array(-1, dimension=1, data_types=[Int(4)])

    def get_dict(self, last_timestamp=None):
        """
        Convert ECG data into signed values
        """
        packet = super().get_dict()
        for i in range(12):
            val = packet["payload"]["ecg_data"][i]
            packet["payload"]["ecg_data"][i] = (val & ((1<<17) - 1)) - (val & (1<<17))
        utils.update_timestamp(packet, last_timestamp)
        return packet
        
class SHMAX86178BIOZDataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - BioZ data
             - Ohms
             - 0 to 4,294,967,295 Ohms

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.SENSORHUB_MAX86178_BIOZ_STREAM: ['0xC8', '0x36']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x2C',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 0,
                'op_mode': 1,
                'timestamp': 1751731879,
                'bioz_data': [ 351762, 351755, ... ],
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode"] = Int(1)
        self._config["payload"]["timestamp"] = Int(4)
        self._config["payload"]["bioz_data"] = Int(4)

    def get_dict(self, last_timestamp=None):
        """
        Postprocess BIOZ data
        """
        packet = super().get_dict()
        utils.update_timestamp(packet, last_timestamp)
        return packet
    
class SHRegConfPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - LED Current
             - mA
             - 0 to 127.5mA
           * - Integration time
             - us
             - 0 to 117us
           * - Burst average
             - integer
             - 1 to 128
           * - Sample average
             - integer
             - 1 to 128
    
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.SENSORHUB_REG_CONF: ['0xC8', '0x2D']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x2C',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 0,
                'op_mode': 1,
                'timestamp': 1751731879,
                'led_curr': [ 3A, 1B, 1A, 1A ],
                'tint': ['3A']
                'avg_smpl': ['2A']
                'reg_sample_average' : ['1A']
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode_id"] = Int(1)
        self._config["payload"]["timestamp"] = Int(4)
        self._config["payload"]["led_curr1"] = Decimal(4)
        self._config["payload"]["tint1"] = Int(1)
        self._config["payload"]["avg_smpl1"] = Int(1)
        self._config["payload"]["dac_offset11"] = Int(1)
        self._config["payload"]["dac_offset12"] = Int(1)

        self._config["payload"]["led_curr2"] = Decimal(4)
        self._config["payload"]["tint2"] = Int(1)
        self._config["payload"]["avg_smpl2"] = Int(1)
        self._config["payload"]["dac_offset21"] = Int(1)
        self._config["payload"]["dac_offset22"] = Int(1)

        self._config["payload"]["led_curr3"] = Decimal(4)
        self._config["payload"]["tint3"] = Int(1)
        self._config["payload"]["avg_smpl3"] = Int(1)
        self._config["payload"]["dac_offset31"] = Int(1)
        self._config["payload"]["dac_offset32"] = Int(1)

        self._config["payload"]["reg_sample_average"] = Int(1)

    def get_dict(self, last_timestamp=None):
        """
        Postprocessing.
        """
        packet = super().get_dict()
        packet["payload"]["reg_conf"] = []
        for i in range(1, 4):
            data = {
                "led_curr": packet["payload"][f"led_curr{i}"],
                "tint": packet["payload"][f"tint{i}"],
                "avg_smpl": packet["payload"][f"avg_smpl{i}"],
                "dac_offset1": packet["payload"][f"dac_offset{i}1"],
                "dac_offset2": packet["payload"][f"dac_offset{i}2"],
            }
            [packet["payload"].pop(key) for key in [f"led_curr{i}", f"tint{i}", f"avg_smpl{i}", f"dac_offset{i}1", f"dac_offset{i}2"]]
            packet["payload"]["reg_conf"].append(data)
        utils.update_timestamp(packet, last_timestamp)
        return packet

class SHDebugRegConfPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.SENSORHUB_DEBUG_REG_CONF_STREAM: ['0xC8', '0x37']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x2C',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 0,
                'op_mode': 1,
                'timestamp': 1751731879,
                'reg_val': [ 0x31, 0x32, ... ],
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode"] = Int(1)
        self._config["payload"]["timestamp"] = Int(4)
        self._config["payload"]["reg_val"] = Array(-1, dimension=1, data_types=[Int(1, to_hex=True)])

    def get_dict(self, last_timestamp=None):
        """
        Post processing
        """
        packet = super().get_dict()
        utils.update_timestamp(packet, last_timestamp)
        return packet

class SHADXLDataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - X
             - mg
             - -32,768 to 32,767mg
           * - Y
             - mg
             - -32,768 to 32,767mg
           * - Z
             - mg
             - -32,768 to 32,767mg

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.ADXL: ['0xC8', '0x2C']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x37',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 395,
                'op_mode_id': 0,
                'stream_data': [
                    {
                        'timestamp': 1767361372,
                        'x': -85,
                        'y': 90,
                        'z': 55
                    },
                    {
                        'timestamp': 1767362027,
                        'x': -80,
                        'y': 88,
                        'z': 55
                    },
                    {
                        'timestamp': 1767362682,
                        'x': 40,
                        'y': 274,
                        'z': 79
                    },
                    {
                        'timestamp': 1767363337,
                        'x': 70,
                        'y': 273,
                        'z': 54
                    },
                    {
                        'timestamp': 1767363931,
                        'x': 57,
                        'y': 257,
                        'z': 48
                    }
                ]
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode_id"] = Int(1)
        self._config["payload"]["timestamp1"] = Int(4)
        self._config["payload"]["x1"] = Int(2, sign=True)
        self._config["payload"]["y1"] = Int(2, sign=True)
        self._config["payload"]["z1"] = Int(2, sign=True)
        self._config["payload"]["timestamp2"] = Int(2)
        self._config["payload"]["x2"] = Int(2, sign=True)
        self._config["payload"]["y2"] = Int(2, sign=True)
        self._config["payload"]["z2"] = Int(2, sign=True)
        self._config["payload"]["timestamp3"] = Int(2)
        self._config["payload"]["x3"] = Int(2, sign=True)
        self._config["payload"]["y3"] = Int(2, sign=True)
        self._config["payload"]["z3"] = Int(2, sign=True)
        self._config["payload"]["timestamp4"] = Int(2)
        self._config["payload"]["x4"] = Int(2, sign=True)
        self._config["payload"]["y4"] = Int(2, sign=True)
        self._config["payload"]["z4"] = Int(2, sign=True)
        self._config["payload"]["timestamp5"] = Int(2)
        self._config["payload"]["x5"] = Int(2, sign=True)
        self._config["payload"]["y5"] = Int(2, sign=True)
        self._config["payload"]["z5"] = Int(2, sign=True)

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["stream_data"] = []
        timestamp = 0
        for i in range(1, 6):
            timestamp += packet["payload"][f"timestamp{i}"]
            data = {
                "timestamp": timestamp,
                "x": packet["payload"][f"x{i}"],
                "y": packet["payload"][f"y{i}"],
                "z": packet["payload"][f"z{i}"]
            }
            [packet["payload"].pop(key) for key in [f"timestamp{i}", f"x{i}", f"y{i}", f"z{i}"]]
            packet["payload"]["stream_data"].append(data)
        utils.update_timestamp(packet, last_timestamp)
        return packet

class SHHRMDataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - HR
             - Beats per minute
             - 30 - 220 bpm
           * - HR confidence
             - Percent
             - 0-100
           * - Activity class
             - Enum (0-4)
             - No activity/activity/other activity

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.SENSORHUB_HRM_STREAM: ['0xC8', '0x2B']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 33,
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 395,
                'op_mode_id': 1,
                'stream_data': [
                    {
                        'timestamp': 1767361372,
                        'hr': 0,
                        'hr_conf': 0,
                        'activity_class': 0,
                    },
                    {
                        'timestamp': 1767361372,
                        'hr': 0,
                        'hr_conf': 0,
                        'activity_class': 0,
                    }
                ]
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode_id"] = Int(1)
        self._config["payload"]["timestamp1"] = Int(4)
        self._config["payload"]["hr1"] = Int(2, sign=True)
        self._config["payload"]["hr_conf1"] = Int(1, sign=False)
        self._config["payload"]["activity_class1"] = Int(1, sign=False)
        self._config["payload"]["timestamp2"] = Int(2)
        self._config["payload"]["hr2"] = Int(2, sign=True)
        self._config["payload"]["hr_conf2"] = Int(1, sign=False)
        self._config["payload"]["activity_class2"] = Int(1, sign=False)

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["stream_data"] = []
        timestamp = 0
        for i in range(1, 3):
            timestamp += packet["payload"][f"timestamp{i}"]
            data = {
                "timestamp": timestamp,
                "hr": packet["payload"][f"hr{i}"],
                "hr_conf": packet["payload"][f"hr_conf{i}"],
                "activity_class": packet["payload"][f"activity_class{i}"]
            }
            [packet["payload"].pop(key) for key in [f"timestamp{i}", f"hr{i}", f"hr_conf{i}", f"activity_class{i}"]]
            packet["payload"]["stream_data"].append(data)
        utils.update_timestamp(packet, last_timestamp)
        return packet

class SHSPO2DataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - r
             - Enum (0-4)
             - No activity/activity/other activity
           * - SpO2 confidence
             - Percent
             - 0-100
           * - SpO2
             - Percent
             - 0-100
           * - Percent complete
             - Percent
             - 0-100
           * - Low signal quality flag
             - bool
             - 0/1
           * - Motion flag
             - bool
             - 0/1
           * - Low PI flag
             - bool
             - 0/1
           * - Unreliable R flag
             - bool
             - 0/1
           * - SpO2 state
             - N/A
             - N/A
           * - SCD contact state
             - Enum (0-3)
             - No decision/On skin/Off skin/On object

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.SENSORHUB_SPO2_STREAM: ['0xC8', '0x30']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 43,
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 395,
                'op_mode_id': 1,
                'stream_data': [
                    {
                        'r': 0,
                        'spo2_conf': 0,
                        'spo2': 0,
                        'percentComplete': 0,
                        'lowQualitySignalFlag': 1,
                        'motionFlag': 1,
                        'lowPiFlag': 1,
                        'unreliableRFlag': 0,
                        'spo2_state': 0,
                        'scd_contact_state': 0
                    },
                    {
                       'r': 0,
                        'spo2_conf': 0,
                        'spo2': 0,
                        'percentComplete': 0,
                        'lowQualitySignalFlag': 1,
                        'motionFlag': 1,
                        'lowPiFlag': 1,
                        'unreliableRFlag': 0,
                        'spo2_state': 0,
                        'scd_contact_state': 0
                    }
                ]
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode_id"] = Int(1)
        self._config["payload"]["timestamp1"] = Int(4)
        self._config["payload"]["r1"] = Int(2, sign=True)
        self._config["payload"]["spo21"] = Int(2, sign=False)
        self._config["payload"]["spo2_ptr1"] = Int(2, sign=False)
        self._config["payload"]["spo2_conf1"] = Int(1, sign=False)
        self._config["payload"]["is_spo2_cal1"] = Int(1, sign=False)
        self._config["payload"]["percentComplete1"] = Int(1, sign=False)
        self._config["payload"]["lowQualitySignalFlag1"] = Int(1, sign=False)
        self._config["payload"]["lowPiFlag1"] = Int(1, sign=False)
        self._config["payload"]["unreliableRFlag1"] = Int(1, sign=False)
        self._config["payload"]["spo2_state1"] = Int(1, sign=False)
        self._config["payload"]["motionFlag1"] = Int(1, sign=False)
        self._config["payload"]["orientationFlag1"] = Int(1, sign=False)
        self._config["payload"]["redPi1"] = Int(2, sign=False)
        self._config["payload"]["irPi1"] = Int(2, sign=False)
        self._config["payload"]["ptr1"] = Int(2, sign=False)
        self._config["payload"]["ptr_quality1"] = Int(2, sign=False)
        self._config["payload"]["timestamp2"] = Int(2)
        self._config["payload"]["r2"] = Int(2, sign=True)
        self._config["payload"]["spo22"] = Int(2, sign=False)
        self._config["payload"]["spo2_ptr2"] = Int(2, sign=False)
        self._config["payload"]["spo2_conf2"] = Int(1, sign=False)
        self._config["payload"]["is_spo2_cal2"] = Int(1, sign=False)
        self._config["payload"]["percentComplete2"] = Int(1, sign=False)
        self._config["payload"]["lowQualitySignalFlag2"] = Int(1, sign=False)
        self._config["payload"]["lowPiFlag2"] = Int(1, sign=False)
        self._config["payload"]["unreliableRFlag2"] = Int(1, sign=False)
        self._config["payload"]["spo2_state2"] = Int(1, sign=False)
        self._config["payload"]["motionFlag2"] = Int(1, sign=False)
        self._config["payload"]["orientationFlag2"] = Int(1, sign=False)
        self._config["payload"]["redPi2"] = Int(2, sign=False)
        self._config["payload"]["irPi2"] = Int(2, sign=False)
        self._config["payload"]["ptr2"] = Int(2, sign=False)
        self._config["payload"]["ptr_quality2"] = Int(2, sign=False)

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["stream_data"] = []
        timestamp = 0
        for i in range(1, 3):
            timestamp += packet["payload"][f"timestamp{i}"]
            data = {
                "timestamp": timestamp,
                "r": packet["payload"][f"r{i}"] / 1000.0,
                "spo2": packet["payload"][f"spo2{i}"] / 10.0,
                "spo2_ptr": packet["payload"][f"spo2_ptr{i}"] / 10.0,
                "spo2_conf": packet["payload"][f"spo2_conf{i}"],
                "is_spo2_cal": packet["payload"][f"is_spo2_cal{i}"],
                "percentComplete": packet["payload"][f"percentComplete{i}"],
                "lowQualitySignalFlag": packet["payload"][f"lowQualitySignalFlag{i}"],
                "lowPiFlag": packet["payload"][f"lowPiFlag{i}"],
                "unreliableRFlag": packet["payload"][f"unreliableRFlag{i}"],
                "spo2_state": packet["payload"][f"spo2_state{i}"],
                "motionFlag": packet["payload"][f"motionFlag{i}"],
                "orientationFlag": packet["payload"][f"orientationFlag{i}"],
                "redPi": packet["payload"][f"redPi{i}"] / 1000.0,
                "irPi": packet["payload"][f"irPi{i}"] / 1000.0,
                "ptr": packet["payload"][f"ptr{i}"] / 1000.0,
                "ptr_quality": packet["payload"][f"ptr_quality{i}"] / 1000.0
            }
            [packet["payload"].pop(key) for key in [f"timestamp{i}", f"r{i}", f"spo2_conf{i}", f"spo2{i}", f"percentComplete{i}", f"lowQualitySignalFlag{i}",
                                                    f"motionFlag{i}", f"lowPiFlag{i}", f"unreliableRFlag{i}", f"spo2_state{i}", f"orientationFlag{i}",
                                                    f"redPi{i}", f"irPi{i}", f"ptr{i}", f"ptr_quality{i}", f"is_spo2_cal{i}", f"spo2_ptr{i}"]]
            packet["payload"]["stream_data"].append(data)
        utils.update_timestamp(packet, last_timestamp)
        return packet

class SHSPO2DebugDataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - SH data
             - ADC count
             - 0 to 524287

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.M2M2_ADDR_SENSORHUB_SPO2_DEBUG_STREAM: ['0xC8', '0x39']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x2C',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 0,
                'op_mode': 1,
                'timestamp': 1751731879,
                'feature': [ 27.78, 35.1755, .. ],
                'feature_calculated': 1,
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode"] = Int(1)
        self._config["payload"]["timestamp"] = Int(4)
        self._config["payload"]["data"] = Array(148, dimension=1, data_types=[Decimal(4)])
        self._config["payload"]["feature_calculated"] = Int(1)

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["feature"] = []
        for i in range(0, 37):
            feature = packet["payload"]["data"][i]
            packet["payload"]["feature"].append(feature)
        del packet["payload"]["data"]
        utils.update_timestamp(packet, last_timestamp)
        return packet

class SHRRDataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - IR Cardiac Resp RMS Ratio
             - --
             - --
           * - IR Range RMS Ratio
             - --
             - --
           * - IR Green Corr Coefficient
             - --
             - --
           * - Gree RR from IBI
             - --
             - --
           * - IR Baseline RR
             - --
             - --
           * - Std IBI MSec
             - --
             - --
           * - Avg HR BPM
             - Beats per minute
             - 30 to 220 bpm
           * - Green RR from IBI Quality
             - --
             - --
           * - RR MLP Output
             - Breaths per minute
             - 5 to 40 bpm / -1 when not available
           * - RR Median output
             - Depricated
             - Depricated
           * - RR Confience
             - Depricated
             - Depricated

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.SENSORHUB_RR_STREAM: ['0xC8', '0x2E']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 43,
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 395,
                'op_mode_id': 1,
                'stream_data': [
                    {
                        'timestamp': 15656161576
                        'irCardiacRespRmsRatio': 0,
                        'irRangeRmsRatio': 0,
                        'irGreenCorrCoefficient': 0,
                        'greenRrFromIbi': 0,
                        'irBaselineRr': 1,
                        'avgHrBpm': 1,
                        'greenRrFromIbiQuality': 0,
                        'irBaselineHighRr': 0,
                        'irBaselineSqi': 0,
                        'signalProcessingRr': 0,
                        'signalProcessingSqi': 0,
                        'rr_mlp': 0,
                    },
                    {
                        'timestamp': 15656161616
                        'irCardiacRespRmsRatio': 0,
                        'irRangeRmsRatio': 0,
                        'irGreenCorrCoefficient': 0,
                        'greenRrFromIbi': 0,
                        'irBaselineRr': 1,
                        'avgHrBpm': 1,
                        'greenRrFromIbiQuality': 0,
                        'irBaselineHighRr': 0,
                        'irBaselineSqi': 0,
                        'signalProcessingRr': 0,
                        'signalProcessingSqi': 0,
                        'rr_mlp': 0,
                    }
                ]
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode_id"] = Int(1)
        self._config["payload"]["timestamp1"] = Int(4)
        self._config["payload"]["irCardiacRespRmsRatio1"] = Int(2, sign=True)
        self._config["payload"]["irRangeRmsRatio1"] = Int(2, sign=True)
        self._config["payload"]["irGreenCorrCoefficient1"] = Int(2, sign=True)
        self._config["payload"]["greenRrFromIbi1"] = Int(2, sign=True)
        self._config["payload"]["irBaselineRr1"] = Int(2, sign=True)
        self._config["payload"]["avgHrBpm1"] = Int(2, sign=True)
        self._config["payload"]["stdIbiMSec1"] = Int(2, sign=True)
        self._config["payload"]["greenRrFromIbiQuality1"] = Int(2, sign=True)
        self._config["payload"]["irBaselineHighRr1"] = Int(2, sign=True)
        self._config["payload"]["irBaselineSqi1"] = Int(2, sign=True)
        self._config["payload"]["signalProcessingRr1"] = Int(2, sign=True)
        self._config["payload"]["signalProcessingSqi1"] = Int(2, sign=True)
        self._config["payload"]["rr_mlp1"] = Int(2, sign=True)
        self._config["payload"]["motionFlag1"] = Int(1, sign=False)
        self._config["payload"]["timestamp2"] = Int(2)
        self._config["payload"]["irCardiacRespRmsRatio2"] = Int(2, sign=True)
        self._config["payload"]["irRangeRmsRatio2"] = Int(2, sign=True)
        self._config["payload"]["irGreenCorrCoefficient2"] = Int(2, sign=True)
        self._config["payload"]["greenRrFromIbi2"] = Int(2, sign=True)
        self._config["payload"]["irBaselineRr2"] = Int(2, sign=True)
        self._config["payload"]["avgHrBpm2"] = Int(2, sign=True)
        self._config["payload"]["stdIbiMSec2"] = Int(2, sign=True)
        self._config["payload"]["greenRrFromIbiQuality2"] = Int(2, sign=True)
        self._config["payload"]["irBaselineHighRr2"] = Int(2, sign=True)
        self._config["payload"]["irBaselineSqi2"] = Int(2, sign=True)
        self._config["payload"]["signalProcessingRr2"] = Int(2, sign=True)
        self._config["payload"]["signalProcessingSqi2"] = Int(2, sign=True)
        self._config["payload"]["rr_mlp2"] = Int(2, sign=True)
        self._config["payload"]["motionFlag2"] = Int(1, sign=False)

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["stream_data"] = []
        timestamp = 0
        for i in range(1, 3):
            timestamp += packet["payload"][f"timestamp{i}"]
            data = {
                "timestamp": timestamp,
                "irCardiacRespRmsRatio": packet["payload"][f"irCardiacRespRmsRatio{i}"]/100.0,
                "irRangeRmsRatio": packet["payload"][f"irRangeRmsRatio{i}"]/100.0,
                "irGreenCorrCoefficient": packet["payload"][f"irGreenCorrCoefficient{i}"]/100.0,
                "greenRrFromIbi": packet["payload"][f"greenRrFromIbi{i}"]/100.0,
                "irBaselineRr": packet["payload"][f"irBaselineRr{i}"]/100.0,
                "avgHrBpm": packet["payload"][f"avgHrBpm{i}"]/100.0,
                "stdIbiMSec": packet["payload"][f"stdIbiMSec{i}"]/100.0,
                "greenRrFromIbiQuality": packet["payload"][f"greenRrFromIbiQuality{i}"]/100.0,
                "irBaselineHighRr": packet["payload"][f"irBaselineHighRr{i}"]/100.0,
                "irBaselineSqi": packet["payload"][f"irBaselineSqi{i}"]/100.0,
                "signalProcessingRr": packet["payload"][f"signalProcessingRr{i}"]/100.0,
                "signalProcessingSqi": packet["payload"][f"signalProcessingSqi{i}"]/100.0,
                "rr_mlp": packet["payload"][f"rr_mlp{i}"]/100.0,
                "motionFlag": packet["payload"][f"motionFlag{i}"]
            }
            [packet["payload"].pop(key) for key in [f"timestamp{i}", f"irCardiacRespRmsRatio{i}", f"irRangeRmsRatio{i}", f"irGreenCorrCoefficient{i}", f"greenRrFromIbi{i}", f"irBaselineRr{i}",
                                                    f"avgHrBpm{i}", f"stdIbiMSec{i}", f"greenRrFromIbiQuality{i}", f"irBaselineHighRr{i}", f"irBaselineSqi{i}", f"signalProcessingRr{i}", 
                                                    f"signalProcessingSqi{i}", f"rr_mlp{i}", f"motionFlag{i}"]]
            packet["payload"]["stream_data"].append(data)
        utils.update_timestamp(packet, last_timestamp)
        return packet
    
class SHPRDataPacket(CommandPacket):
    """
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.SENSORHUB_PR_STREAM: ['0xC8', '0x2E']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 43,
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 395,
                'op_mode_id': 1,
                'stream_data': [
                    {
                        'timestamp': 15656161576
                        'ppgIirHeartBeatFidIndex': 0,
                        'ppgFirIirHeartBeatPeakIndex': 0,
                        'ppgIbiRaw': 0,
                        'ppgIbiCorrectedFloat': 0,
                        'greenHr': 1,
                        'ppgIbiQualityFlag': 1,
                        'peakIndex': 1,
                    },
                    {
                        'timestamp': 15656161616
                        'ppgIirHeartBeatFidIndex': 0,
                        'ppgFirIirHeartBeatPeakIndex': 0,
                        'ppgIbiRaw': 0,
                        'ppgIbiCorrectedFloat': 0,
                        'greenHr': 1,
                        'ppgIbiQualityFlag': 1,
                        'peakIndex': 1,
                    }
                ]
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode_id"] = Int(1)
        self._config["payload"]["timestamp1"] = Int(4)
        self._config["payload"]["ppgIirHeartBeatFidIndex1"] = Int(2, sign=True)
        self._config["payload"]["ppgFirIirHeartBeatPeakIndex1"] = Int(2, sign=True)
        self._config["payload"]["ppgIbiRaw1"] = Int(2, sign=True)
        self._config["payload"]["ppgIbiCorrectedFloat1"] = Int(2, sign=True)
        self._config["payload"]["greenHr1"] = Int(2, sign=True)
        self._config["payload"]["ppgIbiQualityFlag1"] = Int(2, sign=True)
        self._config["payload"]["peakIndex1"] = Int(2, sign=True)
        self._config["payload"]["timestamp2"] = Int(2)
        self._config["payload"]["ppgIirHeartBeatFidIndex2"] = Int(2, sign=True)
        self._config["payload"]["ppgFirIirHeartBeatPeakIndex2"] = Int(2, sign=True)
        self._config["payload"]["ppgIbiRaw2"] = Int(2, sign=True)
        self._config["payload"]["ppgIbiCorrectedFloat2"] = Int(2, sign=True)
        self._config["payload"]["greenHr2"] = Int(2, sign=True)
        self._config["payload"]["ppgIbiQualityFlag2"] = Int(2, sign=True)
        self._config["payload"]["peakIndex2"] = Int(2, sign=True)

    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["stream_data"] = []
        timestamp = 0
        for i in range(1, 3):
            timestamp += packet["payload"][f"timestamp{i}"]
            data = {
                "timestamp": timestamp,
                "ppgIirHeartBeatFidIndex": packet["payload"][f"ppgIirHeartBeatFidIndex{i}"],
                "ppgFirIirHeartBeatPeakIndex": packet["payload"][f"ppgFirIirHeartBeatPeakIndex{i}"],
                "ppgIbiRaw": packet["payload"][f"ppgIbiRaw{i}"]/100.0,
                "ppgIbiCorrectedFloat": packet["payload"][f"ppgIbiCorrectedFloat{i}"]/100.0,
                "greenHr": packet["payload"][f"greenHr{i}"]/100.0,
                "ppgIbiQualityFlag": packet["payload"][f"ppgIbiQualityFlag{i}"]/100.0,
                "peakIndex": packet["payload"][f"peakIndex{i}"]/100.0,
            }
            [packet["payload"].pop(key) for key in [f"timestamp{i}", f"ppgIirHeartBeatFidIndex{i}", f"ppgFirIirHeartBeatPeakIndex{i}", f"ppgIbiRaw{i}",
                                                    f"ppgIbiCorrectedFloat{i}", f"greenHr{i}", f"ppgIbiQualityFlag{i}", f"peakIndex{i}"]]
            packet["payload"]["stream_data"].append(data)
        utils.update_timestamp(packet, last_timestamp)
        return packet


class SHAMADataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - Activity Class
             - Enum (0-4)
             - No activity/activity/other activity
           * - Total activity time
             - Seconds
             - 0 to 4,294,967,295
           * - Total walk steps
             - Steps
             - 0 to 4,294,967,295
           * - Total distance
             - Meters
             - 0 to 4,294,967,295
    
    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.SENSORHUB_AMA_STREAM: ['0xC8', '0x37']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': 43,
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 395,
                'op_mode_id': 1,
                'stream_data': [
                    {
                        'timestamp': 15656161576
                        'activity_class': 0,
                        'total_activity_time': 0,
                        'total_walk_steps': 0,
                        'total_distance': 0
                    },
                    {
                        'timestamp': 15656161576
                        'activity_class': 0,
                        'total_activity_time': 0,
                        'total_walk_steps': 0,
                        'total_distance': 0
                    }
                ]
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["op_mode_id"] = Int(1)
        self._config["payload"]["timestamp1"] = Int(4)
        self._config["payload"]["activity_class1"] = Int(1, sign=False)
        self._config["payload"]["total_activity_time1"] = Int(4, sign=False)
        self._config["payload"]["total_walk_steps1"] = Int(4, sign=False)
        self._config["payload"]["total_distance1"] = Int(4, sign=False)
        self._config["payload"]["timestamp2"] = Int(2)
        self._config["payload"]["activity_class2"] = Int(1, sign=False)
        self._config["payload"]["total_activity_time2"] = Int(4, sign=False)
        self._config["payload"]["total_walk_steps2"] = Int(4, sign=False)
        self._config["payload"]["total_distance2"] = Int(4, sign=False)
        
    def get_dict(self, last_timestamp=None):
        """
        Reorganising of stream data in stream_data key.
        """
        packet = super().get_dict()
        packet["payload"]["stream_data"] = []
        timestamp = 0
        for i in range(1, 3):
            timestamp += packet["payload"][f"timestamp{i}"]
            data = {
                "timestamp": timestamp,
                "activity_class": packet["payload"][f"activity_class{i}"],
                "total_activity_time": packet["payload"][f"total_activity_time{i}"],
                "total_walk_steps": packet["payload"][f"total_walk_steps{i}"],
                "total_distance": packet["payload"][f"total_distance{i}"]/10.0,
            }
            [packet["payload"].pop(key) for key in [f"timestamp{i}", f"activity_class{i}", f"total_activity_time{i}", f"total_walk_steps{i}", f"total_distance{i}"]]
            packet["payload"]["stream_data"].append(data)
        utils.update_timestamp(packet, last_timestamp)
        return packet
    
class MAX30208TemperatureDataPacket(CommandPacket):
    """
    .. list-table::
           :header-rows: 1

           * - Data
             - Unit
             - Range
           * - Temperature
             - Degree Celsius
             - +0°C to +70°C

    Packet Structure:

    .. code-block::

        {
            'header': {
                'source': <Stream.MAX30208_TEMPERATURE_STREAM: ['0xC4', '0x06']>,
                'destination': <Application.APP_USB: ['0xC7', '0x05']>,
                'length': '0x14',
                'checksum': '0x0'
            },
            'payload': {
                'command': <CommonCommand.STREAM_DATA: ['0x28']>,
                'status': <CommonStatus.OK: ['0x00']>,
                'sequence_number': 2,
                'timestamp': 1779692742,
                'temperature': 30.1,
            }
        }
    """

    def __init__(self):
        super().__init__()
        self._config["payload"]["sequence_number"] = Int(2)
        self._config["payload"]["timestamp"] = Int(4)
        self._config["payload"]["temperature"] = Int(2)

    def get_dict(self, last_timestamp=None):
        """
        Postprocessing.
        """
        packet = super().get_dict()
        packet["payload"]["temperature"] = packet["payload"]["temperature"] * 0.005
        utils.update_timestamp(packet, last_timestamp)
        return packet
