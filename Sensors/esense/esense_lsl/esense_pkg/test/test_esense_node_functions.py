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
This script tests functions within esense_pkg.py

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
from unittest.mock import patch
from esense_pkg.esense_lsl import EsenseLslReceiver
from esense_pkg.esense_pkg import SensorDataEsense
from esense_constants import *

def test_acquire_data(mock_streaminlet):
    obj_sensor_class = EsenseLslReceiver(inlet=mock_streaminlet)
    node = SensorDataEsense(obj_sensor_class)
    output1, output2 = node.acquire_data([])
    assert output1 == batch_data
    assert output2 == timestamp

def test_acquire_and_publish_data(mock_streaminlet):
    msg = []
    obj_sensor_class = EsenseLslReceiver(inlet=mock_streaminlet)
    node = SensorDataEsense(obj_sensor_class)
    with patch.object(node, 'acquire_data_for_specific_duration', return_value=[batch_data, timestamp]):
        node.publish_sensor_data.publish = lambda main_msg: msg.append(main_msg)
        node.acquire_and_publish_data(start_time, duration)
    assert msg[0] == sample_msg

def test_convert_time(mock_streaminlet):
    obj_sensor_class = EsenseLslReceiver(inlet=mock_streaminlet)
    node = SensorDataEsense(obj_sensor_class)
    output = node.convert_time(seconds, nanoseconds)
    assert output == timestamp
