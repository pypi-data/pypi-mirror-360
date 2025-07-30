import csv
import math
import logging
import time
from datetime import datetime, timezone, timedelta

from ..core.enums.common_enums import Stream

logger = logging.getLogger(__name__)


class CSVLogger:
    def __init__(self, filename, header, write_header=True):
        self.ch1_ppg = []
        self.ch2_ppg = []
        self.ch1_timestamp = []
        self.ch2_timestamp = []
        self.file = None
        self.writer = None
        self.header = header
        self.filename = filename
        self.logging_started = None
        self.write_header = write_header

    def write_row(self, row):
        if self.writer:
            self.writer.writerow(row)

    def start_logging(self, last_timestamp, tz_sec):
        try:
            self.file = open(self.filename, 'w', newline="")
            self.writer = csv.writer(self.file, quoting=csv.QUOTE_NONE)
            offset = timezone(timedelta(seconds=tz_sec))
            dt_object = datetime.fromtimestamp(last_timestamp, tz=offset)
            self.write_row(["Local: ", dt_object, "tz_sec ", tz_sec])
            self.write_row(["Linux Epoch (ms):", last_timestamp * 1000])
            if self.write_header:
                self.write_row(self.header)
        except Exception as e:
            logger.error(f"Error while opening the {self.filename} file, reason :: {e}.", exc_info=True)

    def stop_logging(self):
        data_len = max(len(self.ch1_timestamp), len(self.ch2_timestamp))
        if len(self.ch1_timestamp) > 0 and len(self.ch2_timestamp) > 0:
            if not len(self.ch1_timestamp) == len(self.ch2_timestamp):
                data_len = min(len(self.ch1_timestamp), len(self.ch2_timestamp))
                logger.warning(f"Issue with PPG CSV logging. Recommended sequence unsubscribe_stream "
                               f"then disable_csv_logging.")
        for i in range(data_len):
            if len(self.ch2_ppg) == 0:
                self.sh_ppg_add_row([self.ch1_timestamp[i], self.ch1_ppg[i]], 1)
            elif len(self.ch1_ppg) == 0:
                self.sh_ppg_add_row([self.ch2_timestamp[i], self.ch2_ppg[i]], 2)
            else:
                self.sh_ppg_add_row(
                    [self.ch1_timestamp[i], self.ch1_ppg[i], self.ch2_ppg[i]], 0)

        if self.file:
            self.file.close()

    def add_row(self, result, last_timestamp, tz_sec):
        stream = result["header"]["source"]
        if self.logging_started is None:
            self.logging_started = True
            self.start_logging(last_timestamp, tz_sec)
        if stream == Stream.ECG:
            self._ecg_callback(result)
        elif stream == Stream.EDA:
            self._eda_callback(result)
        elif stream == Stream.BIA:
            self._bia_callback(result)
        elif stream == Stream.BCM:
            self._bcm_callback(result)
        elif stream == Stream.BATTERY:
            self._battery_callback(result)
        elif stream == Stream.AD7156:
            self._ad7156_callback(result)
        elif stream == Stream.SENSORHUB_ADXL367_STREAM:
            self._sh_adxl_callback(result)
        elif stream == Stream.SENSORHUB_HRM_STREAM:
            self._sh_hrm_callback(result)
        elif stream == Stream.SENSORHUB_SPO2_STREAM:
            self._sh_spo2_callback(result)
        elif stream == Stream.SENSORHUB_SPO2_DEBUG_STREAM:
            self._sh_spo2_debug_callback(result)
        elif stream == Stream.SENSORHUB_RR_STREAM:
            self._sh_rr_callback(result)
        elif stream == Stream.SENSORHUB_PR_STREAM:
            self._sh_pr_callback(result)
        elif stream == Stream.SENSORHUB_AMA_STREAM:
            self._sh_ama_callback(result)
        elif stream == Stream.SENSORHUB_REG_CONF_STREAM:
            self._sh_reg_conf_callback(result)
        elif stream == Stream.SENSORHUB_DEBUG_REG_CONF_STREAM:
            self._sh_debug_reg_conf_callback(result)
        elif stream in [Stream.SENSORHUB_MAX86178_STREAM1, Stream.SENSORHUB_MAX86178_STREAM2, Stream.SENSORHUB_MAX86178_STREAM3,
                        Stream.SENSORHUB_MAX86178_STREAM4, Stream.SENSORHUB_MAX86178_STREAM5, Stream.SENSORHUB_MAX86178_STREAM6]:
            self._sh_ppg_callback(result)
        elif stream == Stream.SENSORHUB_MAX86178_ECG_STREAM:
            self._sh_ecg_callback(result)
        elif stream == Stream.SENSORHUB_MAX86178_BIOZ_STREAM:
            self._sh_bioz_callback(result)
        elif stream == Stream.MAX30208_TEMPERATURE_STREAM:
            self._max30208_temp_callback(result)

    def sh_ppg_add_row(self, row, header_format):
        if not self.write_header:
            self.write_header = True
            self.write_row([" ", self.header[0], "", "", "", ""])
            row2 = []
            if header_format == 0:
                row2 = [" ", " ", "CH1", "CH2"]
            elif header_format == 1:
                row2 = [" ", " ", "CH1"]
            elif header_format == 2:
                row2 = [" ", " ", "CH2"]
            self.write_row(row2)
            row3 = []
            if header_format == 0:
                row3 = [" ", "Timestamp", "ppg1", "ppg2"]
            elif header_format == 1:
                row3 = [" ", "Timestamp", "ppg1"]
            elif header_format == 2:
                row3 = [" ", "Timestamp", "ppg2"]
            self.write_row(row3)
        self.write_row([" "] + row)

    def _ecg_callback(self, data):
        for value in data["payload"]["stream_data"]:
            self.write_row([value["timestamp"], data["payload"]["sequence_number"], value["ecg_data"]])

    def _eda_callback(self, data):
        for value in data["payload"]["stream_data"]:
            eda_real = value["real"]
            eda_imaginary = value["imaginary"]
            if eda_real == 0:
                eda_real = 1
            impedance_img = eda_imaginary * 1000
            impedance_real = eda_real * 1000
            real_and_img = float(impedance_real * impedance_real + impedance_img * impedance_img)
            impedance_module = math.sqrt(real_and_img)
            impedance_phase = math.atan2(impedance_img, impedance_real)
            admittance_real = float(impedance_real /
                                    float(impedance_real * impedance_real + impedance_img * impedance_img))
            admittance_img = -float(impedance_img /
                                    float(impedance_real * impedance_real + impedance_img * impedance_img))
            admittance_module = 1 / impedance_module
            admittance_phase = math.atan2(admittance_img, admittance_real)

            self.write_row([
                value["timestamp"], impedance_real, impedance_img, impedance_module, impedance_phase, admittance_real,
                admittance_img, admittance_module, admittance_phase, data["payload"]["sequence_number"]
            ])

    def _bia_callback(self, data):
        for value in data["payload"]["stream_data"]:
            bcm_real = value["real"]
            bcm_imaginary = value["imaginary"]
            if bcm_real == 0:
                bcm_real = 1
            if bcm_imaginary == 0:
                bcm_imaginary = 1
            impedance_img = bcm_imaginary / 1000
            impedance_real = bcm_real / 1000
            real_and_img = float(impedance_real * impedance_real + impedance_img * impedance_img)
            impedance_module = math.sqrt(real_and_img)
            impedance_phase = math.atan2(impedance_img, impedance_real)
            admittance_real = float(impedance_real /
                                    float(impedance_real * impedance_real + impedance_img * impedance_img))
            admittance_img = -float(impedance_img /
                                    float(impedance_real * impedance_real + impedance_img * impedance_img))
            admittance_module = 1 / impedance_module
            admittance_phase = math.atan2(admittance_img, admittance_real)
            self.write_row([
                value["timestamp"], impedance_real, impedance_img, impedance_module, impedance_phase,
                admittance_real, admittance_img, admittance_module, admittance_phase,
                data["payload"]["sequence_number"], value["frequency_index"]
            ])

    def _bcm_callback(self, data):
        self.write_row([data["payload"]["timestamp"], data["payload"]["ffm_estimated"],
                        data["payload"]["bmi"], data["payload"]["fat_percent"], data["payload"]["sequence_num"]])

    def _battery_callback(self, data):
        self.write_row([data["payload"]["timestamp"], data["payload"]["battery_status"],
                        data["payload"]["adp5360_battery_level"], data["payload"]["custom_battery_level"], data["payload"]["battery_mv"]])

    def _ad7156_callback(self, data):
        for value in data["payload"]["stream_data"]:
            self.write_row([value["timestamp"], value["ch1_cap"], value["ch2_cap"], value["ch1_ADCCode"],
                            value["ch2_ADCCode"], value["OUT1_val"], value["OUT2_val"]])

    def _sh_adxl_callback(self, data):
        for value in data["payload"]["stream_data"]:
            self.write_row([value["timestamp"], value["x"], value["y"], value["z"]])

    def _sh_hrm_callback(self, data):
        for value in data["payload"]["stream_data"]:
            self.write_row([value["timestamp"], value["hr"], value["hr_conf"], value["activity_class"]])

    def _sh_spo2_callback(self, data):
        for value in data["payload"]["stream_data"]:
            self.write_row([value["timestamp"], value["r"], value["spo2"], value["spo2_ptr"], value["spo2_conf"], value["is_spo2_cal"], value["percentComplete"], value["lowQualitySignalFlag"], value["lowPiFlag"], value["unreliableRFlag"], value["spo2_state"], value["motionFlag"], value["orientationFlag"], value["redPi"], value["irPi"], value["ptr"], value["ptr_quality"]])

    def _sh_spo2_debug_callback(self, data):
        row = [data["payload"]["timestamp"]]
        for feature in data["payload"]["feature"]:
            row.append(feature)
        row.append(data["payload"]["feature_calculated"])
        self.write_row(row)

    def _sh_rr_callback(self, data):
        for value in data["payload"]["stream_data"]:
            self.write_row([value["timestamp"], value["irCardiacRespRmsRatio"], value["irRangeRmsRatio"], value["irGreenCorrCoefficient"], value["greenRrFromIbi"], value["irBaselineRr"], value["avgHrBpm"], value["stdIbiMSec"], value["greenRrFromIbiQuality"], value["irBaselineHighRr"], value["irBaselineSqi"], value["signalProcessingRr"], value["signalProcessingSqi"], value["rr_mlp"], value["motionFlag"]])

    def _sh_pr_callback(self, data):
        for value in data["payload"]["stream_data"]:
            self.write_row([value["timestamp"], value["ppgIirHeartBeatFidIndex"], value["ppgFirIirHeartBeatPeakIndex"], value["ppgIbiRaw"], value["ppgIbiCorrectedFloat"], value["greenHr"], value["ppgIbiQualityFlag"], value["peakIndex"]])

    def _sh_ama_callback(self, data):
        for value in data["payload"]["stream_data"]:
            self.write_row([value["timestamp"], value["activity_class"], value["total_activity_time"], value["total_walk_steps"], value["total_distance"]])

    def _sh_reg_conf_callback(self, data):
        reg_conf_data_length = len(data["payload"]["reg_conf"])
        led_curr = [] * reg_conf_data_length
        tint = [] * reg_conf_data_length
        avg_smpl = [] * reg_conf_data_length
        dac_offset1 = [] * reg_conf_data_length
        dac_offset2 = [] * reg_conf_data_length

        for i in range(1, reg_conf_data_length):
            for value in data["payload"]["reg_conf"]:
                led_curr.append(value["led_curr"])
                tint.append(value["tint"])
                avg_smpl.append(value["avg_smpl"])
                dac_offset1.append(value["dac_offset1"])
                dac_offset2.append(value["dac_offset2"])
        smpl_ave = data["payload"]["reg_sample_average"]
        self.write_row([data["payload"]["timestamp"],led_curr[0],tint[0],avg_smpl[0],dac_offset1[0],dac_offset2[0], 
                        led_curr[1], tint[1],avg_smpl[1],dac_offset1[1],dac_offset2[1], 
                        led_curr[2],tint[2],avg_smpl[2],dac_offset1[2],dac_offset2[2], smpl_ave])

    def _sh_debug_reg_conf_callback(self, data):
        row = [data["payload"]["timestamp"]]
        for feature in data["payload"]["reg_val"]:
            row.append(feature)
        self.write_row(row)

    def _max30208_temp_callback(self, data):
        self.write_row([data["payload"]["timestamp"], data["payload"]["temperature"]])

    def _sh_ecg_callback(self, data):
        for i in range(len(data["payload"]["ecg_data"])):
            self.write_row([data["payload"]["timestamp"], data["payload"]["lead_status"], data["payload"]["ecg_data"][i]])

    def _sh_bioz_callback(self, data):
        self.write_row([data["payload"]["timestamp"], data["payload"]["bioz_data"]])

    def _sh_ppg_callback(self,data):
        if len(self.ch1_timestamp) > 200 or len(self.ch2_timestamp) > 200:
            sh_ppg_data_length = len(data["payload"]["sh_data"])
            for i in range(sh_ppg_data_length):
                if len(self.ch2_ppg) == 0:
                    self.sh_ppg_add_row([self.ch1_timestamp[i], self.ch1_ppg[i]], 1)
                elif len(self.ch1_ppg) == 0:
                    self.sh_ppg_add_row([self.ch2_timestamp[i], self.ch2_ppg[i]], 2)
                else:
                    self.sh_ppg_add_row(
                        [self.ch1_timestamp[i], self.ch1_ppg[i], self.ch2_ppg[i]], 0)

            del self.ch1_ppg[:sh_ppg_data_length]
            del self.ch2_ppg[:sh_ppg_data_length]
            del self.ch1_timestamp[:sh_ppg_data_length]
            del self.ch2_timestamp[:sh_ppg_data_length]

        if data["payload"]["channel_num"] == 1:
            for sh_data in data["payload"]["sh_data"]:
                self.ch1_timestamp.append(data["payload"]["timestamp"])
                self.ch1_ppg.append(sh_data)

        elif data["payload"]["channel_num"] == 2:
            for sh_data in data["payload"]["sh_data"]:
                self.ch2_timestamp.append(data["payload"]["timestamp"])
                self.ch2_ppg.append(sh_data)
