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
A Python script that facilitates communication between EmotiBit sensor and the system via BrainFlow.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
from emotibit_sdk.custom_exceptions import *

class EmotibitSensor():
    """Connect and acquire data from the EmotiBit sensor using BrainFlow"""
    def __init__(self):
        """Initialise BrainFlow parameters"""
        params = BrainFlowInputParams()
        self.board_ids = BoardIds.EMOTIBIT_BOARD    
        self.board = BoardShim(self.board_ids, params)

    def prepare(self):
        """Initiate BrainFlow's streaming session"""
        self.board.prepare_session()

    def is_board_prepared(self) -> bool:
        """Returns if the board is ready to stream data"""
        return self.board.is_prepared()
    
    def start_streaming(self):
        """Initiate or begin streaming the data"""
        self.board.start_stream()

    def stop_streaming(self):
        """Stop streaming the data"""
        self.board.stop_stream()
    
    def release_session(self):
        """Release the streaming session"""
        self.board.release_session()

    def get_board_description(self, preset_name: str) -> dict:
        """Get the description of the EmotiBit board

        Arguments:
        str preset_name: Name of the preset for which the data is to be acquired

        Returns:
        dict board_desc: Board description
        """
        preset = self.get_preset(preset_name)
        board_desc = BoardShim.get_board_descr(self.board_ids, preset)
        return board_desc

    def get_board_data(self, preset_name: str) -> np.ndarray:
        """Get the sensor data from the EmotiBit sensor
        
        Arguments:
        str preset_name: Name of the preset for which the data is to be acquired

        Returns:
        np.ndarray data: Sensor data for the preset specified by 'preset_name'
        """
        preset = self.get_preset(preset_name)
        data = self.board.get_board_data(preset=preset)
        return data
    
    def get_channels(self, preset_name: str, channel_name: str) -> tuple[int, dict]:
        """Get the channel name and the board description. If the channel name is invalid, an InvalidChannelNameError exception is raised.
        
        Arguments:
        str preset_name:  Name of the preset for which the data is to be acquired
        str channel_name: Name of the channel for which data is to be acquired

        Returns:
        int channel_data: Channel number for the channel specified by 'channel_name'
        dict board_desc: Board description
        """
        board_descr = self.get_board_description(preset_name)
        if channel_name not in board_descr.keys():
            raise InvalidChannelNameError(f"Channel ({channel_name}) is invalid for preset ({preset_name}).")
        else:
            channel_data = board_descr[channel_name]
            return channel_data, board_descr
    
    def get_preset(self, preset_name: str) -> int:
        """Returns the preset for the EmotiBit sensor

        Arguments:
        str preset_name: Name of the preset for which the data is to be acquired

        Returns:
        int preset: The integer value for the corresponding preset specified by 'preset_name'. This value will be provided to BrainFlow for communicating with the EmotiBit sensor.
        """
        if preset_name == 'auxiliary':
            preset = BrainFlowPresets.AUXILIARY_PRESET
        elif preset_name == 'ancillary':
            preset = BrainFlowPresets.ANCILLARY_PRESET
        elif preset_name == 'default':
            preset = BrainFlowPresets.DEFAULT_PRESET
        else:
            raise InvalidPresetError(f"{preset_name} preset is invalid and not recognised by BrainFlow. Possible preset values: auxiliary, ancillary or default")
        return preset
