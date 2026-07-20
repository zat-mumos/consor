import pytest
from unittest.mock import create_autospec
import rclpy
from emotibit_sdk.emotibit_sdk import EmotibitSensor
from openbci_pkg.sensor import OpenbciSensor
from emotibit_sdk.custom_exceptions import InvalidChannelNameError
from src.consor.tests.test_openbci.openbci_constants import board_data, board_description
from src.consor.tests.test_emotibit.emotibit_constants import board_data_default, board_data_auxiliary, board_data_ancillary, board_description_default, board_description_auxiliary, board_description_ancillary

"""This file has functions that are called in multiple tests."""

@pytest.fixture
def mocksensorEmotibit(monkeypatch):
    obj_sensor_class = EmotibitSensor()
    patches = {
        'prepare': None,
        'is_board_prepared': True, 
        'start_streaming': None,
        'stop_streaming': None,
        'release_session': None
    }

    for method_name, method_implementation in patches.items():
        method_instance = getattr(obj_sensor_class, method_name)
        mock_method = create_autospec(method_instance)
        mock_method.return_value = method_implementation
        monkeypatch.setattr(obj_sensor_class, method_name, mock_method)
    
    def get_board_data(preset_name: str):
        preset = obj_sensor_class.get_preset(preset_name)
        if preset == 1: # aux
            data =  board_data_auxiliary 
        elif preset == 2: # anc
            data = board_data_ancillary 
        else: # def
            data = board_data_default 
        return data
    mock_method = create_autospec(obj_sensor_class.get_board_data , side_effect = get_board_data)
    monkeypatch.setattr(obj_sensor_class, "get_board_data", mock_method)
    
    def get_channels(preset_name: str, channel_name: str):
        board_descr = obj_sensor_class.get_board_description(preset_name)
        if channel_name not in board_descr.keys():
            raise InvalidChannelNameError(f"Channel ({channel_name}) is invalid for preset ({preset_name}).")
        else:
            channel_data = board_descr[channel_name]
            return channel_data, board_descr
    mock_method = create_autospec(obj_sensor_class.get_channels, side_effect = get_channels)
    monkeypatch.setattr(obj_sensor_class, "get_channels", mock_method)

    def get_board_description(preset_name):
        preset = obj_sensor_class.get_preset(preset_name)
        if preset == 1: #auxiliary preset
            board_desc = board_description_auxiliary
        elif preset == 2: #ancillary preset
            board_desc = board_description_ancillary
        else: # 0: default preset
            board_desc = board_description_default
        return board_desc
    mock_method = create_autospec(obj_sensor_class.get_board_description, side_effect = get_board_description)
    monkeypatch.setattr(obj_sensor_class, "get_board_description", mock_method)

    return obj_sensor_class


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
