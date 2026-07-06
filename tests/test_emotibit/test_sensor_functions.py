import pytest
from emotibit_sdk.custom_exceptions import InvalidPresetError, InvalidChannelNameError

"""
# Code tested: sensor.py
# Test overview: This scripts tests sensor-specific functions.
"""

def test_exception_raised_for_invalid_preset_name_1(mocksensor):
    preset_name = "default_preset"
    with pytest.raises(Exception) as preset_value:
        mocksensor.get_preset(preset_name)
    assert preset_value.type is InvalidPresetError


def test_exception_raised_for_invalid_preset_name_2(mocksensor):
    channel_name = "temperature_channels"
    preset_name = "default_preset"
    with pytest.raises(Exception) as preset_value:
        mocksensor.get_channels(preset_name, channel_name)
    assert preset_value.type is InvalidPresetError


def test_exception_raised_for_invalid_channel_name(mocksensor):
    channel_name = "invalid_channel_name"
    preset_name = 'default'
    with pytest.raises(Exception) as value_returned:
        mocksensor.get_channels(preset_name, channel_name)
    assert value_returned.type is InvalidChannelNameError


def test_function_get_preset(mocksensor):
    preset_name = "default"
    assert mocksensor.get_preset(preset_name) == 0


def test_function_get_channels(mocksensor):
    channel_name = "accel_channels"
    preset_name = "default"
    assert mocksensor.get_channels(preset_name, channel_name)[0] == [1, 2, 3]


# Functions get_board_data and get_board_description already tested implicitly in test_node_functions.py