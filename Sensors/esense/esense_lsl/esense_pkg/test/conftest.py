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
This file has functions that are called in multiple tests.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
import pytest
from unittest.mock import MagicMock, patch
import rclpy
import pylsl
from esense_constants import *


@pytest.fixture(scope='module', autouse=True)
def rclpy_init_shutdown():
    """Mock ROS node init and shutdown"""
    rclpy.init()
    yield
    rclpy.shutdown()

@pytest.fixture(autouse=True)
def mock_streaminlet(monkeypatch):
    info = pylsl.StreamInfo(name="eSense", type="sensor_data", channel_count=4, 
                        channel_format="string", source_id="lsl_esense_sensor_12345",
                        nominal_srate=1.000000000000000)
    
    desc = info.desc()
    desc.append_child('Metadata').append_child_value("Android_API_Level", stream_info_android_api_level)\
        .append_child_value("Device_Name", stream_info_device_name)\
        .append_child_value("Manufacturer_Name", stream_info_manufacturer_name)\
        .append_child_value("Sensor_Type", stream_info_sensor_type)\
        .append_child_value("Sampling_rate", stream_info_sampling_rate)\
        .append_child_value("Units", stream_info_units)

    mock_stream_inlet = MagicMock()
    mock_stream_inlet.info.return_value = info
    mock_stream_inlet.pull_sample.return_value = sample
    
    monkeypatch.setattr('esense_pkg.esense_lsl.StreamInlet',
                    MagicMock(return_value=mock_stream_inlet))

    return mock_stream_inlet
    
@pytest.fixture(autouse=True)
def mock_resolve_byprop():
    with patch('esense_pkg.esense_lsl.resolve_byprop') as mock_property:
        yield mock_property