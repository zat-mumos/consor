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
from unittest.mock import create_autospec
import rclpy
from openbci_pkg.sensor import OpenbciSensor
from openbci_constants import board_data, board_description


@pytest.fixture
def mocksensorOpenbci(monkeypatch):
    obj_sensor_class = OpenbciSensor()
    patches = { # for methods without arguments
        'init_board': None,
        'enable_accel': None,
        'prepare': None,
        'is_board_prepared': True, 
        'start_streaming': None,
        'stop_streaming': None,
        'release_session': None,
        'get_board_data': board_data,
        'get_board_description': board_description
    }

    for method_name, method_implementation in patches.items():
        method_instance = getattr(obj_sensor_class, method_name)
        mock_method = create_autospec(method_instance)
        mock_method.return_value = method_implementation
        monkeypatch.setattr(obj_sensor_class, method_name, mock_method)

    def init_parser(port: str):
        return port
    mock_method = create_autospec(obj_sensor_class.init_parser, side_effect = init_parser)
    monkeypatch.setattr(obj_sensor_class, "init_parser", mock_method)

    return obj_sensor_class


@pytest.fixture(scope='module', autouse=True)
def rclpy_init_shutdown():
    """Mock ROS node init and shutdown"""
    rclpy.init()
    yield
    rclpy.shutdown()
