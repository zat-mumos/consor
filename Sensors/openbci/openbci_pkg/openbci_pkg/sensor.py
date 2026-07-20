
import argparse
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

class OpenbciSensor():
    """Connect and acquire data from the OpenBCI sensor using BrainFlow"""
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        
    def init_parser(self, port: str):
        self.port = port
        self.parser.add_argument('--serial-port', type=str, help='serial port', required=False, default=self.port)
    
    def init_board(self):
        params = BrainFlowInputParams()
        params.serial_port = self.port
        self.board_ids = BoardIds.GANGLION_BOARD
        self.board = BoardShim(self.board_ids, params)

    def enable_accel(self):
        self.board.config_board('n')

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

    def get_board_description(self) -> dict:
        board_desc = BoardShim.get_board_descr(self.board_ids)
        return board_desc

    def get_board_data(self):
        data = self.board.get_board_data()
        return data
    