from unittest.mock import patch
from src.consor.Sensors.esense.esense_lsl.esense_pkg.esense_pkg.esense_lsl import EsenseLslReceiver
from esense_pkg.esense_pkg import SensorDataEsense
from src.consor.tests.test_esense.esense_constants import *

"""
# Code tested: esense_pkg.py
# Test overview: This script tests functions within esense_pkg.py
"""

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
