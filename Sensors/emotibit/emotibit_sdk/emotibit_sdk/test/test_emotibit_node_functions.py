# © 2026 Hochschule Bonn-Rhein-Sieg <https://www.h-brs.de/>
# 
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
# Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program. If not, see <https://www.gnu.org/licenses/>.

"""
This script tests functions within emotibit_sdk.py

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
from unittest.mock import MagicMock
from emotibit_sdk.emotibit_sdk import SensorDataEmotibitWithSdk
from emotibit_constants import *

test_stream = ['Accelerometer', 'PPG', 'Temperature']
test_topic = ['mock_emotibit/default_preset', 'mock_emotibit/auxiliary_preset', 'mock_emotibit/ancillary_preset']

def test_function_acquire_sensor_data(mocksensorEmotibit):
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    assert node.acquire_sensor_data() == (board_data_default, board_data_auxiliary, board_data_ancillary)


def test_function_format_data_default_preset(mocksensorEmotibit):
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    r1, r2, r3, r4 = node.format_data_default_preset(data_def = board_data_default, stream = test_stream[0]) 
    bool_all_rows_each_col = (r1 == sensor_data_default_preset).all() # for each col, if all rows are equal
    assert bool_all_rows_each_col.all() # checks if all colums are True
    assert r2 == timestamp_default_preset
    assert r3 == var_preset_default
    assert r4 == channels_default_preset


def test_function_format_data_auxiliary_preset(mocksensorEmotibit):
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    r1, r2, r3, r4 = node.format_data_auxiliary_preset(data_aux = board_data_auxiliary) 
    bool_all_rows_each_col = (r1 == sensor_data_auxiliary_preset).all() # for each col, if all rows are equal
    assert bool_all_rows_each_col.all() # checks if all colums are True
    assert r2 == timestamp_auxiliary_preset
    assert r3 == var_preset_auxiliary
    assert r4 == channels_auxiliary_preset


def test_function_format_data_anciliary_preset(mocksensorEmotibit):
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    r1, r2, r3, r4 = node.format_data_ancillary_preset(data_anc = board_data_ancillary, stream = test_stream[2]) 
    bool_all_rows_each_col = (r1 == sensor_data_anciliary_preset).all() # for each col, if all rows are equal
    assert bool_all_rows_each_col.all() # checks if all colums are True
    assert r2 == timestamp_anciliary_preset
    assert r3 == var_preset_anciliary
    assert r4 == channels_anciliary_preset


def test_function_modify_timestamp_for_default_preset(mocksensorEmotibit):
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    node.t0_n_samples[var_preset_default]['srate'] = 25
    res = node.modify_timestamp(var_preset = var_preset_default, stream = test_stream[0], sensor_data = sensor_data_final_default, timestamp_ = timestamp_default_preset)
    assert res == formatted_timestamp_default_preset


def test_function_modify_timestamp_for_auxiliary_preset(mocksensorEmotibit):
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    node.t0_n_samples[var_preset_auxiliary]['srate'] = 25
    res = node.modify_timestamp(var_preset = var_preset_auxiliary, stream = test_stream[1], sensor_data = sensor_data_final_auxiliary, timestamp_ = timestamp_auxiliary_preset)
    assert res == formatted_timestamp_auxiliary_preset


def test_function_modify_timestamp_for_anciliary_preset(mocksensorEmotibit):
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    node.t0_n_samples[var_preset_anciliary]['srate'] = 15
    res = node.modify_timestamp(var_preset = var_preset_anciliary, stream = test_stream[2], sensor_data = sensor_data_final_anciliary, timestamp_ = timestamp_anciliary_preset)
    assert res == formatted_timestamp_anciliary_preset


def test_function_publish_msg_for_default_preset(mocksensorEmotibit):
    msg = []
    curr_stream = test_stream[0]
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    node.publisher[curr_stream].publish = lambda main_msg: msg.append(main_msg)
    node.publish_data(timestamp = formatted_timestamp_default_preset, stream = curr_stream, channels=channels_default_preset, sensor_data = sensor_data_final_default, curr_publisher=node.publisher[curr_stream])
    assert main_msg_default_preset == msg[0]


def test_function_publish_msg_for_auxiliary_preset(mocksensorEmotibit):
    msg = []
    curr_stream = test_stream[1]
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    node.publisher[curr_stream].publish = lambda main_msg: msg.append(main_msg)
    node.publish_data(timestamp = formatted_timestamp_auxiliary_preset, stream = curr_stream, channels=channels_auxiliary_preset, sensor_data = sensor_data_final_auxiliary, curr_publisher=node.publisher[curr_stream])
    assert main_msg_auxiliary_preset == msg[0]


def test_function_publish_msg_for_anciliary_preset(mocksensorEmotibit):
    msg = []
    curr_stream = test_stream[2]
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    node.publisher[curr_stream].publish = lambda main_msg: msg.append(main_msg)
    node.publish_data(timestamp = formatted_timestamp_anciliary_preset, stream = curr_stream, channels=channels_anciliary_preset, sensor_data = sensor_data_final_anciliary, curr_publisher=node.publisher[curr_stream])
    assert main_msg_anciliary_preset == msg[0]

    
def test_function_check_sensor_prepared_1(mocksensorEmotibit, monkeypatch):# sensor not ready
    """Test that an error message is logged when method 'is_board_prepared()' returns False (i.e., sensor is not ready)."""
    monkeypatch.setattr(mocksensorEmotibit, "is_board_prepared", lambda: False)
    
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    node.get_logger = MagicMock()
    node.check_sensor_prepared()
    assert node.i == 5
    node.get_logger().error.assert_called_once()


def test_function_check_sensor_prepared_2(mocksensorEmotibit):
    """Test that a message is logged when method 'is_board_prepared()' returns True (i.e., sensor is ready)."""
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    node.get_logger = MagicMock()
    node.check_sensor_prepared()
    node.get_logger().info.assert_called_with("Session prepared")


def test_function_acquire_and_publish_data1(mocksensorEmotibit, monkeypatch):
    """Test that a warning is logged when empty data is received from the sensor. This can happen when there is no data in 
    the internal buffer. The data is emptied from buffer faster than the sensor has time to acquire data."""
    monkeypatch.setattr(mocksensorEmotibit, "is_board_prepared", lambda: False)
    monkeypatch.setattr(mocksensorEmotibit, "get_board_data", lambda preset_name: np.empty((10,0)))
    
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    node.get_logger = MagicMock()
    node.acquire_and_publish_data()
    node.get_logger().warning.assert_called_once()


def test_function_acquire_and_publish_data2(mocksensorEmotibit):
    node = SensorDataEmotibitWithSdk(sensor = mocksensorEmotibit, type_stream = test_stream, sensor_topic = test_topic)
    node.get_logger = MagicMock()
    node.acquire_and_publish_data()
    node.get_logger().info.assert_called_with(f"Message Published for {test_stream}!", throttle_duration_sec=1.0)

