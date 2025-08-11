import argparse
import time
import os
from ament_index_python.packages import get_package_share_directory

import pandas as pd
import numpy as np

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

import rclpy
from rclpy.logging import LoggingSeverity
from rclpy.node import Node

from zat_ros2_msgs.msg import Bci, BciData
from builtin_interfaces.msg import Time


class SensorDataOpenbci(Node):
    def __init__(self,
                 modality: str = 'default_modality',
                 port: str = 'no_port',
                 timer: float = 1.0):
        super().__init__('sensor_data_openbci')

        # self.get_logger().set_level(LoggingSeverity.DEBUG) # Uncomment this line to print the lines in DEBUG mode

        self.i = 0 # counter

        # Declare parameters
        self.declare_parameter('modality_name', 'default_modality')
        self.declare_parameter('port_name', 'no_port')
        self.declare_parameter('openbci_timer', 1.0)    

        # Get parameter values
        modality = self.get_parameter('modality_name').value
        port = self.get_parameter('port_name').value
        timer = self.get_parameter('openbci_timer').value

        self.modality = modality
        self.topics = f"/bci/{str.lower(self.modality)}" # i.e., if modality='eeg' then topic='/bci/eeg'
        self.port = port
        self.timer = timer

        # Print all launch values
        self.get_logger().debug(f"Modality: {self.modality}\nTopics: {self.topics}\nPort: {self.port}\nTimer: {self.timer}")

        # Create publisher
        self.publish_data = self.create_publisher(BciData, self.topics, 10)

        self.get_logger().debug("Creating publsher")


        # Create a timer
        self.timer_call = self.create_timer(timer, self.timer_callback)
        self.get_logger().debug("Creating timer")

    
    def timer_callback(self):
        try:
            self.get_logger().debug("In timer_callback")
            while rclpy.ok():
                self.get_logger().debug("In timer_callback 2")

                parser = argparse.ArgumentParser()
                self.get_logger().debug("In timer_callback 3")
                parser.add_argument('--serial-port', type=str, help='serial port', required=False, default=self.port)
                self.get_logger().debug("In timer_callback 4")

                self.get_logger().debug(f"Modality2: {self.modality}\nTopics: {self.topics}\nPort: {self.port}\nTimer: {self.timer}")

                params = BrainFlowInputParams()
                params.serial_port = self.port

                self.get_logger().debug(f"Params.serial_port: {params.serial_port}")

                board_ids = BoardIds.GANGLION_BOARD    
                board = BoardShim(board_ids, params)
                self.get_logger().debug(f"Board: {board}")

                board.prepare_session()
                board.start_stream ()
                time.sleep(5)

                data = board.get_board_data()  # get all data and remove it from internal buffer
                
                board.stop_stream()
                board.release_session()

                self.get_logger().debug(f"Data (shape): {pd.DataFrame(np.transpose(data)).shape}")
                self.get_logger().debug(f"Board Description: {BoardShim.get_board_descr(board_ids)}")

                data_to_publish = pd.DataFrame(np.transpose(data))
                board_descr = BoardShim.get_board_descr(board_ids)

                self.get_logger().debug(f"Timestamp Channel: {board_descr['timestamp_channel']}")

                main_msg = BciData()
                main_msg.timestamp = data_to_publish.iloc[:, board_descr['timestamp_channel']].to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
                main_msg.modality = self.modality
                main_msg.srate = board_descr['sampling_rate']

                mod_channel_name = f"{str.lower(self.modality)}_channels"
                msg = Bci()
                temp_msg = []
                for ch in board_descr[mod_channel_name]:
                    self.get_logger().debug(f"Modality: {self.modality}\nChannel name: {mod_channel_name}\nChannel No: {ch}")
                    msg.channel = f"ch_{ch}"
                    msg.data = data_to_publish.iloc[:, ch].to_numpy(dtype=np.float64).tolist()
                    temp_msg.append(msg)
                main_msg.openbci_data = temp_msg

                self.publish_data.publish(main_msg)
                self.get_logger().info(f'msg:\n{main_msg}\n--------**************---------\n')
        except KeyboardInterrupt:
            board.stop_stream()
            board.release_session()
            rclpy.shutdown()




def main():
    rclpy.init()
    node = SensorDataOpenbci()

    node.get_logger().debug("Node has been initialised")
    try:
        rclpy.spin(node)
        node.get_logger().debug("rclpy.spin() called ................")
    except KeyboardInterrupt:
        node.get_logger().debug(f"KeyBoard Interrupt")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
