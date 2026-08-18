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
A Python script that facilitates communication between OpenBCI sensor and the system via BrainFlow.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""

import numpy as np
import argparse
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

class OpenbciSensor():
    """Connect and acquire data from the OpenBCI sensor using BrainFlow"""
    def __init__(self):
        """Initialise BrainFlow parser"""
        self.parser = argparse.ArgumentParser()
        
    def init_parser(self, port: str):
        """Configure parameters (serial port) required to connect to the OpenBCI sensor
        
        Arguments:
        str port: Specify the port to connect to the sensor
        """
        self.port = port
        self.parser.add_argument('--serial-port', type=str, help='serial port', required=False, default=self.port)
    
    def init_board(self):
        """Initialise BrainFlow parameters."""
        params = BrainFlowInputParams()
        params.serial_port = self.port
        self.board_ids = BoardIds.GANGLION_BOARD
        self.board = BoardShim(self.board_ids, params)

    def enable_accel(self):
        """Enable accelerometer data. If this function is called, accelerometer data is obtained from the sensor."""
        self.board.config_board('n')

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

    def get_board_description(self) -> dict:
        """Get the description of the OpenBCI board
        
        Returns:
        dict board_desc: Board description
        """
        board_desc = BoardShim.get_board_descr(self.board_ids)
        return board_desc

    def get_board_data(self) -> np.ndarray:
        """
        Get the sensor data from OpenBCI sensor.

        Returns:
        np.ndarray data: Sensor data for the preset specified by 'preset_name'
        """
        data = self.board.get_board_data()
        return data
    