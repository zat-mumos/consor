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
This script tests functions within esense_lsl.py

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
from src.consor.Sensors.esense.esense_lsl.esense_pkg.esense_pkg.esense_lsl import EsenseLslReceiver
from src.consor.tests.test_esense.esense_constants import *

def test_get_stream_info(mock_streaminlet):
    obj_sensor_class = EsenseLslReceiver(inlet = mock_streaminlet)
    info = obj_sensor_class.get_stream_info()
    
    assert info.desc().child('Metadata').child_value("Android_API_Level") == stream_info_android_api_level
    assert info.desc().child('Metadata').child_value("Device_Name") == stream_info_device_name
    assert info.desc().child('Metadata').child_value("Manufacturer_Name") == stream_info_manufacturer_name
    assert info.desc().child('Metadata').child_value("Sensor_Type") == stream_info_sensor_type
    assert info.desc().child('Metadata').child_value("Sampling_rate") == stream_info_sampling_rate
    assert info.desc().child('Metadata').child_value("Units") == stream_info_units
    

def test_get_metadata_value(mock_streaminlet):
    obj_sensor_class = EsenseLslReceiver(inlet = mock_streaminlet)
    output = obj_sensor_class.get_metadata_value()
    assert output == metadata


def test_ascii_to_string(mock_streaminlet):
    ascii_input = str('[103, 116, 115, 57, 119, 105, 102, 105]')
    expected_output = 'gts9wifi'
    obj_sensor_class = EsenseLslReceiver(inlet = mock_streaminlet)
    assert obj_sensor_class.ascii_to_string(ascii_input) == expected_output


def test_get_sample(mock_streaminlet):
    obj_sensor_class = EsenseLslReceiver(inlet = mock_streaminlet)
    output = obj_sensor_class.get_sample()
    assert output == sample[0]
