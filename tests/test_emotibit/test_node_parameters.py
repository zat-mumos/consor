import pytest
from emotibit_sdk.emotibit_sdk import SensorDataEmotibitWithSdk

"""
# Code tested: emotibit_sdk.py
# Tests overview: This Script tests if the exceptions/errors are raised when parameter/argument conditions are not met.
"""

def test_exception_raised_for_incorrect_parameter_value_1(mocksensor):
    """Test that an incorrect type for the 'stream_names' ROS parameter raises a TypeError. In the ROS node, this is the  'type_stream' argument."""
    stream_type_arg = 'Accelerometer'
    with pytest.raises(Exception) as value_returned:
        SensorDataEmotibitWithSdk(sensor=mocksensor, type_stream=stream_type_arg)
    assert value_returned.type is TypeError


def test_exception_raised_for_incorrect_parameter_value_2(mocksensor):
    """Test that an incorrect 'topic_names' ROS parameter raises a TypeError. In the ROS node, this is the  'sensor_topic' argument."""
    sensor_topic_arg = 'default_topic'
    with pytest.raises(Exception) as value_returned:
        SensorDataEmotibitWithSdk(sensor=mocksensor, sensor_topic=sensor_topic_arg)
    assert value_returned.type is TypeError


def test_exception_raised_for_incorrect_parameter_value_3(mocksensor):
    """Test that an incorrect case for the 'stream_names' ROS parameter raises a TypeError. This is because the 'stream_names' are provided to 
    the sensor and they are case sensitive. In the ROS node, this is the  'type_stream' argument."""
    stream_type_arg = ['Accelerometer', 'magnetometer']
    sensor_topic_arg = ['topic1', 'topic2']
    with pytest.raises(Exception) as value_returned:
        SensorDataEmotibitWithSdk(sensor=mocksensor, type_stream=stream_type_arg, sensor_topic=sensor_topic_arg)
    assert value_returned.type is ValueError


def test_exception_raised_for_parameter_len_mismatch(mocksensor):
    """Test that a ValueError is raised when the number of 'stream_names' parameter ('type_stream' argument) is not equal to the number of 
    'topic_names' parameter ('sensor_topic' argument). This is because the code expects each stream to have a separate ROS topic that the 
    data will be published to."""
    stream_type_arg = ['default_stream1', 'default_stream2']
    sensor_topic_arg = ['default_topic']
    with pytest.raises(Exception) as value_returned:
        SensorDataEmotibitWithSdk(sensor=mocksensor, type_stream=stream_type_arg, sensor_topic=sensor_topic_arg)
    assert value_returned.type is ValueError


def test_correct_parameter_value_1(mocksensor):
    """Tests the node initialisation with correct parameter value. self.i is initialised only after all parameter 
    exceptions are checked. Hence, any issues with the parameter will raise an error before initialising self.i."""
    stream_type_arg = ['Accelerometer']
    node = SensorDataEmotibitWithSdk(sensor=mocksensor, type_stream=stream_type_arg)
    assert node.i == 0 


def test_correct_parameter_value_2(mocksensor):
    """Tests the node initialisation with correct parameter value. self.i is initialised only after all parameter 
    exceptions are checked. Hence, any issues with the parameter will raise an error before initialising self.i."""
    stream_type_arg = ['Accelerometer']
    sensor_topic_arg = ['default_topic']
    node = SensorDataEmotibitWithSdk(sensor=mocksensor, type_stream=stream_type_arg, sensor_topic=sensor_topic_arg)
    assert node.i == 0 
