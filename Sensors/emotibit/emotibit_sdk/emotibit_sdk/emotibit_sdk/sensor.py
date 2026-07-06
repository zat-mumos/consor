
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
from emotibit_sdk.custom_exceptions import *

class EmotibitSensor():
    """Connect and acquire data from the EmotiBit sensor using BrainFlow"""
    def __init__(self):
        params = BrainFlowInputParams()
        self.board_ids = BoardIds.EMOTIBIT_BOARD    
        self.board = BoardShim(self.board_ids, params)

    def prepare(self):
        self.board.prepare_session()

    def is_board_prepared(self) -> bool:
        return self.board.is_prepared()
    
    def start_streaming(self):
        self.board.start_stream()

    def stop_streaming(self):
        self.board.stop_stream()
    
    def release_session(self):
        self.board.release_session()

    def get_board_description(self, preset_name: str) -> dict:
        preset = self.get_preset(preset_name)
        board_desc = BoardShim.get_board_descr(self.board_ids, preset)
        return board_desc

    def get_board_data(self, preset_name: str) -> np.ndarray:
        preset = self.get_preset(preset_name)
        data = self.board.get_board_data(preset=preset)
        return data
    
    def get_channels(self, preset_name: str, channel_name: str) -> tuple[int, dict]:
        board_descr = self.get_board_description(preset_name)
        if channel_name not in board_descr.keys():
            raise InvalidChannelNameError(f"Channel ({channel_name}) is invalid for preset ({preset_name}).")
        else:
            channel_data = board_descr[channel_name]
            return channel_data, board_descr
    
    def get_preset(self, preset_name: str) -> int:
        if preset_name == 'auxiliary':
            preset = BrainFlowPresets.AUXILIARY_PRESET
        elif preset_name == 'ancillary':
            preset = BrainFlowPresets.ANCILLARY_PRESET
        elif preset_name == 'default':
            preset = BrainFlowPresets.DEFAULT_PRESET
        else:
            raise InvalidPresetError(f"{preset_name} preset is invalid and not recognised by BrainFlow. Possible preset values: auxiliary, ancillary or default")
        return preset
