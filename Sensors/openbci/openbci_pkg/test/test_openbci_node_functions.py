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
This script tests functions within openbci.py

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
from unittest.mock import MagicMock
from openbci_pkg.openbci import SensorDataOpenbci
from openbci_constants import *
import numpy as np


test_modality_arg = 'eeg'
test_get_accel_arg = 1
test_port_arg = '/dev/ttyACM0'

def test_function_get_board_metadata(mocksensorOpenbci):
    node = SensorDataOpenbci(sensor = mocksensorOpenbci, modality = test_modality_arg, get_accel = test_get_accel_arg, port = test_port_arg)
    # initialise self variable
    node.metadata = {'eeg': {'srate': 0, 'channels': [], 'timestamp_channel': []}, 'accel': {'srate': 0, 'channels': [], 'timestamp_channel': []}}
    node.get_board_metadata()
    assert node.metadata == board_metadata


def test_function_acquire_sensor_data(mocksensorOpenbci):
    node = SensorDataOpenbci(sensor = mocksensorOpenbci, modality = test_modality_arg, get_accel = test_get_accel_arg, port = test_port_arg)
    assert (node.acquire_sensor_data() == board_data).all()


def test_function_format_data(mocksensorOpenbci):
    node = SensorDataOpenbci(sensor = mocksensorOpenbci, modality = test_modality_arg, get_accel = test_get_accel_arg, port = test_port_arg)
    bool_all_cols =  (node.format_data(data=board_data) == formatted_board_data).all()
    assert bool_all_cols.all()
    

def test_function_modify_timestamp(mocksensorOpenbci):
    channels = board_description[f"{test_modality_arg}_channels"]
    sensor_data = formatted_board_data[channels]
    node = SensorDataOpenbci(sensor = mocksensorOpenbci, modality = test_modality_arg, get_accel = test_get_accel_arg, port = test_port_arg)
    node.metadata[test_modality_arg]['srate'] = 200
    res = node.modify_timestamp(channel_name=test_modality_arg, sensor_data = sensor_data, timestamp_ = timestamp_brainflow)
    assert res == expected_timestamp


def test_function_publish_data(mocksensorOpenbci):
    list_channels = board_description[f"{test_modality_arg}_channels"]
    sensor_data = formatted_board_data[list_channels]
    msg = []
    node = SensorDataOpenbci(sensor = mocksensorOpenbci, modality = test_modality_arg, get_accel = test_get_accel_arg, port = test_port_arg)
    node.metadata[test_modality_arg]['srate'] = 200
    node.publisher[test_modality_arg].publish = lambda main_msg: msg.append(main_msg)
    node.publish_data(timestamp = expected_timestamp, channel_name = test_modality_arg, channels=list_channels, sensor_data = sensor_data, curr_publisher=node.publisher[test_modality_arg])
    assert main_msg == msg[0]

    
def test_function_check_sensor_prepared_1(mocksensorOpenbci, monkeypatch):# sensor not ready
    """Test that an error message is logged when method 'is_board_prepared()' returns False (i.e., sensor is not ready)."""
    monkeypatch.setattr(mocksensorOpenbci, "is_board_prepared", lambda: False)
    
    node = SensorDataOpenbci(sensor = mocksensorOpenbci, modality = test_modality_arg, get_accel = test_get_accel_arg, port = test_port_arg)
    node.get_logger = MagicMock()
    node.check_sensor_prepared()
    assert node.i == 5
    node.get_logger().error.assert_called_once()


def test_function_check_sensor_prepared_2(mocksensorOpenbci):
    """Test that a message is logged when method 'is_board_prepared()' returns True (i.e., sensor is ready)."""
    node = SensorDataOpenbci(sensor = mocksensorOpenbci, modality = test_modality_arg, get_accel = test_get_accel_arg, port = test_port_arg)
    node.get_logger = MagicMock()
    node.check_sensor_prepared()
    node.get_logger().info.assert_called_with("Session prepared")


def test_function_acquire_and_publish_data1(mocksensorOpenbci, monkeypatch):
    """Test that a warning is logged when empty data is received from the sensor. This can happen when there is no data in 
    the internal buffer. The data is emptied from buffer faster than the sensor has time to acquire data."""
    monkeypatch.setattr(mocksensorOpenbci, "is_board_prepared", lambda: False)
    monkeypatch.setattr(mocksensorOpenbci, "get_board_data", lambda: np.empty([15, 0]))
    
    node = SensorDataOpenbci(sensor = mocksensorOpenbci, modality = test_modality_arg, get_accel = test_get_accel_arg, port = test_port_arg)
    node.get_logger = MagicMock()
    node.acquire_and_publish_data()
    node.get_logger().warning.assert_called_once()


def test_function_acquire_and_publish_data2(mocksensorOpenbci):
    node = SensorDataOpenbci(sensor = mocksensorOpenbci, modality = test_modality_arg, get_accel = test_get_accel_arg, port = test_port_arg)
    node.get_logger = MagicMock()
    node.acquire_and_publish_data()
    print(f"list channels: {node.list_channel_names}")
    node.get_logger().info.assert_called_with(f"Message Published for {node.list_channel_names}!", throttle_duration_sec=1.0)

