import pytest
from emotibit_sdk.custom_exceptions import InvalidPresetError, InvalidChannelNameError

"""
# Code tested: sensor.py
# Test overview: This scripts tests sensor-specific functions.
"""

def test_exception_raised_for_invalid_preset_name_1(mocksensorEmotibit):
    preset_name = "default_preset"
    with pytest.raises(Exception) as preset_value:
        mocksensorEmotibit.get_preset(preset_name)
    assert preset_value.type is InvalidPresetError


def test_exception_raised_for_invalid_preset_name_2(mocksensorEmotibit):
    channel_name = "temperature_channels"
    preset_name = "default_preset"
    with pytest.raises(Exception) as preset_value:
        mocksensorEmotibit.get_channels(preset_name, channel_name)
    assert preset_value.type is InvalidPresetError


def test_exception_raised_for_invalid_channel_name(mocksensorEmotibit):
    channel_name = "invalid_channel_name"
    preset_name = 'default'
    with pytest.raises(Exception) as value_returned:
        mocksensorEmotibit.get_channels(preset_name, channel_name)
    assert value_returned.type is InvalidChannelNameError


def test_function_get_preset(mocksensorEmotibit):
    preset_name = "default"
    assert mocksensorEmotibit.get_preset(preset_name) == 0


def test_function_get_channels(mocksensorEmotibit):
    channel_name = "accel_channels"
    preset_name = "default"
    assert mocksensorEmotibit.get_channels(preset_name, channel_name)[0] == [1, 2, 3]


# Functions get_board_data and get_board_description already tested implicitly in test_node_functions.py