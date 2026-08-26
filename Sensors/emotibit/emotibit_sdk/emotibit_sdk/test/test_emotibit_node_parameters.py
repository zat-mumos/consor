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
This Script tests if the exceptions/errors are raised when parameter/argument conditions are not met. The code in emotibit_sdk.py is tested with this script.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
import pytest
from emotibit_sdk.emotibit_sdk import SensorDataEmotibitWithSdk


def test_exception_raised_for_incorrect_parameter_value_1(mocksensorEmotibit):
    """Test that an incorrect type for the 'stream_names' ROS parameter raises a TypeError. In the ROS node, this is the  'type_stream' argument."""
    stream_type_arg = 'Accelerometer'
    with pytest.raises(Exception) as value_returned:
        SensorDataEmotibitWithSdk(sensor=mocksensorEmotibit, type_stream=stream_type_arg)
    assert value_returned.type is TypeError


def test_exception_raised_for_incorrect_parameter_value_2(mocksensorEmotibit):
    """Test that an incorrect 'topic_names' ROS parameter raises a TypeError. In the ROS node, this is the  'sensor_topic' argument."""
    sensor_topic_arg = 'default_topic'
    with pytest.raises(Exception) as value_returned:
        SensorDataEmotibitWithSdk(sensor=mocksensorEmotibit, sensor_topic=sensor_topic_arg)
    assert value_returned.type is TypeError


def test_exception_raised_for_incorrect_parameter_value_3(mocksensorEmotibit):
    """Test that an incorrect case for the 'stream_names' ROS parameter raises a TypeError. This is because the 'stream_names' are provided to 
    the sensor and they are case sensitive. In the ROS node, this is the  'type_stream' argument."""
    stream_type_arg = ['Accelerometer', 'magnetometer']
    sensor_topic_arg = ['topic1', 'topic2']
    with pytest.raises(Exception) as value_returned:
        SensorDataEmotibitWithSdk(sensor=mocksensorEmotibit, type_stream=stream_type_arg, sensor_topic=sensor_topic_arg)
    assert value_returned.type is ValueError


def test_exception_raised_for_parameter_len_mismatch(mocksensorEmotibit):
    """Test that a ValueError is raised when the number of 'stream_names' parameter ('type_stream' argument) is not equal to the number of 
    'topic_names' parameter ('sensor_topic' argument). This is because the code expects each stream to have a separate ROS topic that the 
    data will be published to."""
    stream_type_arg = ['default_stream1', 'default_stream2']
    sensor_topic_arg = ['default_topic']
    with pytest.raises(Exception) as value_returned:
        SensorDataEmotibitWithSdk(sensor=mocksensorEmotibit, type_stream=stream_type_arg, sensor_topic=sensor_topic_arg)
    assert value_returned.type is ValueError


def test_correct_parameter_value_1(mocksensorEmotibit):
    """Tests the node initialisation with correct parameter value. self.i is initialised only after all parameter 
    exceptions are checked. Hence, any issues with the parameter will raise an error before initialising self.i."""
    stream_type_arg = ['Accelerometer']
    node = SensorDataEmotibitWithSdk(sensor=mocksensorEmotibit, type_stream=stream_type_arg)
    assert node.i == 0 


def test_correct_parameter_value_2(mocksensorEmotibit):
    """Tests the node initialisation with correct parameter value. self.i is initialised only after all parameter 
    exceptions are checked. Hence, any issues with the parameter will raise an error before initialising self.i."""
    stream_type_arg = ['Accelerometer']
    sensor_topic_arg = ['default_topic']
    node = SensorDataEmotibitWithSdk(sensor=mocksensorEmotibit, type_stream=stream_type_arg, sensor_topic=sensor_topic_arg)
    assert node.i == 0 
