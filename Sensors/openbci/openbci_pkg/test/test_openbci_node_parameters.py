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
This Script tests if the exceptions/errors are raised when parameter/argument conditions are not met. The code in openbci.py is tested with this script.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
import pytest
from openbci_pkg.openbci import SensorDataOpenbci


def test_exception_raised_for_incorrect_parameter_value_1(mocksensorOpenbci):
    """Test that an incorrect type for the 'modality_name' ROS parameter raises a TypeError. In the ROS node, this is the  'modality' argument."""
    modality_arg = 0
    with pytest.raises(Exception) as value_returned:
        SensorDataOpenbci(sensor= mocksensorOpenbci, modality=modality_arg)
    assert value_returned.type is TypeError


def test_exception_raised_for_incorrect_parameter_value_2(mocksensorOpenbci):
    """Test that an incorrect 'port_name' ROS parameter raises a TypeError. In the ROS node, this is the  'port' argument."""
    modality_arg = 'eeg'
    port_arg = 0
    with pytest.raises(Exception) as value_returned:
        SensorDataOpenbci(sensor= mocksensorOpenbci, modality=modality_arg, port=port_arg)
    assert value_returned.type is TypeError


def test_exception_raised_for_incorrect_parameter_value_3(mocksensorOpenbci):
    """Test that an incorrect 'get_accel' ROS parameter raises a TypeError. In the ROS node, this is the  'get_accel' argument."""
    modality_arg = 'eeg'
    port_arg = '/dev/ttyACM0'
    get_accel = '0'
    with pytest.raises(Exception) as value_returned:
        SensorDataOpenbci(sensor= mocksensorOpenbci, modality=modality_arg, port=port_arg, get_accel=get_accel)
    assert value_returned.type is TypeError


def test_exception_raised_for_incorrect_parameter_value_4(mocksensorOpenbci):
    """Test that an incorrect value for the 'modality_name' ROS parameter raises a ValueError."""
    modality_arg = 'accelerometer'
    with pytest.raises(Exception) as value_returned:
        SensorDataOpenbci(sensor= mocksensorOpenbci, modality=modality_arg)
    assert value_returned.type is ValueError


def test_exception_raised_for_incorrect_parameter_value_5(mocksensorOpenbci):
    modality_arg = 'eeg'
    port_arg = 'no_port'
    with pytest.raises(Exception) as value_returned:
        SensorDataOpenbci(sensor= mocksensorOpenbci, modality=modality_arg, port=port_arg)
    assert value_returned.type is ValueError


def test_exception_raised_for_incorrect_parameter_value_6(mocksensorOpenbci):
    """Test that an incorrect 'get_accel' ROS parameter raises a TypeError. In the ROS node, this is the  'get_accel' argument."""
    modality_arg = 'eeg'
    port_arg = '/dev/ttyACM0'
    get_accel = 2
    with pytest.raises(Exception) as value_returned:
        SensorDataOpenbci(sensor= mocksensorOpenbci, modality=modality_arg, port=port_arg, get_accel=get_accel)
    assert value_returned.type is ValueError


def test_correct_parameter_value_1(mocksensorOpenbci):
    """Tests the node initialisation with correct parameter value. self.i is initialised only after all parameter 
    exceptions are checked. Hence, any issues with the parameter will raise an error before initialising self.i."""
    modality_arg = 'eeg'
    port_arg = '/dev/ttyACM0'
    node =  SensorDataOpenbci(sensor= mocksensorOpenbci, modality=modality_arg, port=port_arg)
    assert node.i == 0 


def test_correct_parameter_value_2(mocksensorOpenbci):
    """Tests the node initialisation with correct parameter value. self.i is initialised only after all parameter 
    exceptions are checked. Hence, any issues with the parameter will raise an error before initialising self.i."""
    modality_arg = 'eeg'
    port_arg = '/dev/ttyACM0'
    get_accel = 1
    node =  SensorDataOpenbci(sensor= mocksensorOpenbci, modality=modality_arg, port=port_arg, get_accel=get_accel)
    assert node.i == 0 
