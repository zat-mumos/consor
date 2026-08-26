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
This scripts tests sensor-specific functions within sensor.py

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
import pytest
from emotibit_sdk.custom_exceptions import InvalidPresetError, InvalidChannelNameError

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