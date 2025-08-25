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
                 get_accel: int = 0,
                 port: str = 'no_port',
                 batch_time: float = 1e-5, # the frequency at which the data should be collected
                 callback_time: float = 1e-5, # timer for the callback function
                 ):
        super().__init__('sensor_data_openbci')

        self.get_logger().set_level(LoggingSeverity.DEBUG) # Uncomment this line to print the lines in DEBUG mode

        self.i = 0 # counter

        # Declare parameters
        self.declare_parameter('modality_name', modality)
        self.declare_parameter('get_accel', get_accel)
        self.declare_parameter('port_name', port)
        self.declare_parameter('openbci_timer', batch_time)    
        self.declare_parameter('openbci_callback_timer', callback_time)    

        # Get parameter values
        modality = self.get_parameter('modality_name').value
        port = self.get_parameter('port_name').value
        batch_time = self.get_parameter('openbci_timer').value
        callback_time = self.get_parameter('openbci_callback_timer').value
        get_accel = self.get_parameter('get_accel').value
        get_accel = bool(get_accel)

        self.modality = modality
        self.topics = f"/bci/{str.lower(self.modality)}" # i.e., if modality='eeg' then topic='/bci/eeg'
        self.port = port
        self.batch_time = batch_time
        self.callback_time = callback_time
        self.bool_get_accel = get_accel

        # self.constants = {
        #     'eeg':1,
        #     'ecg':2,
        #     'emg':3,
        #     'eog':4,
        #     'resistance':5,
        #     'accel':6
        # }

        # Print all launch values
        self.get_logger().debug(f"Modality: {self.modality}\nTopics: {self.topics}\nPort: {self.port}\nBatch Time: {self.batch_time}\nCallback Timer: {self.callback_time}\nAccel: {self.bool_get_accel}\naccel_param: {get_accel}")

        self.publisher = {} # keep track of publishers

        # Create publishers
        self.publisher[f"{str.lower(self.modality)}"] = self.create_publisher(BciData, self.topics, 10) # topic for modality e.g. /bci/eeg
        self.publisher["resistance"] = self.create_publisher(BciData, "/bci/res", 10) # topic for resistance channel

        if self.bool_get_accel:
            self.publisher["accel"] = self.create_publisher(BciData, "/bci/acc", 10) # topic for resistance channel

        self.get_logger().debug("Creating publsher")


        # Create a timer
        self.timer_call = self.create_timer(self.callback_time, self.timer_callback)
        self.get_logger().debug("Creating timer")

    
    def timer_callback(self):
        try:
            self.get_logger().debug("In timer_callback")
            while rclpy.ok():
                self.get_logger().debug("In timer_callback 2")
                if self.i == 0:
                    parser = argparse.ArgumentParser()
                    self.get_logger().debug("In timer_callback 3")
                    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default=self.port)
                    self.get_logger().debug("In timer_callback 4")

                    self.get_logger().info(f"Modality2: {self.modality}\nTopics: {self.topics}\nPort: {self.port}\nBatch Time: {self.batch_time}\nCallback time: {self.callback_time}")
                    
                    params = BrainFlowInputParams()
                    params.serial_port = self.port

                    self.get_logger().debug(f"Params.serial_port: {params.serial_port}")

                    board_ids = BoardIds.GANGLION_BOARD    
                    board = BoardShim(board_ids, params)
                    self.get_logger().debug(f"Board: {board}")

                    board.prepare_session()
                    self.i +=1
                    self.get_logger().debug(f"i = {self.i}")

                board.start_stream ()
                time.sleep(self.batch_time)

                data = board.get_board_data()  # get all data and remove it from internal buffer
                
                board.stop_stream()
                # board.release_session()

                self.get_logger().debug(f"Data (transposed - shape): {pd.DataFrame(np.transpose(data)).shape}") #\ndata (shape): {pd.DataFrame(data).shape}\nData (w/o transposing):\n{pd.DataFrame(data)}")
                self.get_logger().debug(f"Board Description: {BoardShim.get_board_descr(board_ids)}")
                
                # pd.DataFrame(data).to_csv("/home/swathy/.ros/data.csv")

                data_to_publish = pd.DataFrame(np.transpose(data))
                board_descr = BoardShim.get_board_descr(board_ids)

                self.get_logger().debug(f"Timestamp Channel: {board_descr['timestamp_channel']}")


                list_channels = [f"{str.lower(self.modality)}", 'resistance']
                if self.bool_get_accel:
                    list_channels.append('accel')

                for mod in list_channels:
                    # get publisher corresponding to the 'mod'
                    curr_publisher = self.publisher[mod]

                    main_msg = BciData()
                    timestamp = data_to_publish.iloc[:, board_descr['timestamp_channel']].to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
                    main_msg.timestamp = [self.convert_time(t) for t in timestamp]
                    self.get_logger().debug(f"mod: {mod}")
                    # main_msg.modality = self.constants.get(mod)
                    main_msg.srate = board_descr['sampling_rate']

                    mod_channel_name = f"{str.lower(mod)}_channels"
                    temp_msg = []
                    no_channels = board_descr[mod_channel_name]
                    for k, ch in enumerate(no_channels):
                        msg = Bci()
                        self.get_logger().debug(f"Modality: {self.modality}\nChannel No: {k+1}, {ch}")
                        msg.channel = k+1 
                        msg.data = data_to_publish.iloc[:, ch].to_numpy(dtype=np.float64).tolist()
                        temp_msg.append(msg)
                    main_msg.data = temp_msg

                    curr_publisher.publish(main_msg)
                    self.get_logger().info(f'msg:\n{main_msg}\n--------**************---------\n')
        except KeyboardInterrupt:
            board.stop_stream()
            board.release_session()
            rclpy.shutdown()


    def convert_time(self, timestamp):
        time = Time()
        time.sec = int(timestamp)
        time.nanosec = int((timestamp%1)*1e9)
        return time



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
