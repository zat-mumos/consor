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
A ROS node that gets data from the OpenBCI sensor and publishes it to a ROS topic

Subscribers:
    None

Publishers:
    One publisher per modality. For example, if modality = 'eeg' then publisher topic is '/bci/eeg'. 

Parameters:
    - modality_name (str, default: 'default_modality')
    - get_accel (Literal[0, 1], default: 0)
    - port_name (str, default: 'no_port')
    - openbci_timer (float, default: 1e-5)

Description:
    This code connects to the sensor using BrainFlow SDK. The data acquired from the sensor is published to a ROS2 topic.

Author: 
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""

import time
import traceback
from typing import Literal
import pandas as pd
import numpy as np
import rclpy
from rclpy.logging import LoggingSeverity
from rclpy.node import Node
from zat_ros2_msgs.msg import Bci, BciData
from builtin_interfaces.msg import Time
from openbci_pkg.sensor import OpenbciSensor
from common_functions.common import convert_time


class SensorDataOpenbci(Node):
    """
    Acquire and publish sensor data from OpenBCI using BrainFlow SDK.
    """
    def __init__(self,
                 sensor: OpenbciSensor,
                 modality: str = 'default_modality',
                 get_accel: Literal[0, 1] = 0,
                 port: str = 'no_port',
                 batch_time: float = 1e-5, 
                 ):
        """
        Initialise the SensorDataOpenbci class.

        Arguments:
        OpenbciSensor sensor: Object of the OpenbciSensor class
        str modality: Modality for which the data should be collected
        Literal get_acc: Enable accelerometer data. If 0, accelerometer data is not collected. If 1, accelerometer data will be collected.
        str port: Port for communicating with the sensor
        float batch_time: Duration for which data should be collected
        """
        super().__init__('sensor_data_openbci')

        # self.get_logger().set_level(LoggingSeverity.DEBUG) # Uncomment this line to print the lines in DEBUG mode

        # Declare parameters
        self.declare_parameter('modality_name', modality)
        self.declare_parameter('get_accel', get_accel)
        self.declare_parameter('port_name', port)
        self.declare_parameter('openbci_timer', batch_time)

        # Get parameter values
        modality = self.get_parameter('modality_name').value
        port = self.get_parameter('port_name').value
        batch_time = self.get_parameter('openbci_timer').value
        get_accel = self.get_parameter('get_accel').value
        
        if not isinstance(modality, str):
            raise TypeError(f"Parameter 'modality_name' of value {modality} and type {type(modality)} is not valid. It should be a string value.")
        if str.lower(modality) not in ['ecg', 'eeg', 'emg', 'eog']:
            raise ValueError(f"Modality ({modality}) is not valid.")
        if not isinstance(port, str):
            raise TypeError(f"Parameter 'port_name' of value {port} and type {type(port)} is not valid. It should be a string value.")
        if port == 'no_port':
            raise ValueError(f"Port ({port}) is not valid.")
        if not isinstance(get_accel, int):
            raise TypeError(f"Parameter 'get_accel' of value {get_accel} and type {type(get_accel)} is not valid. It should either be 0 or 1.")
        if get_accel not in [0, 1]:
            raise ValueError(f"Parameter 'get_accel' of value {get_accel} is not valid. It should either be 0 or 1.")
        
        self.i = 0 # counter
        self.list_channel_names = []

        self.modality = modality
        self.topics = f"/bci/{str.lower(self.modality)}" # i.e., if modality='eeg' then topic='/bci/eeg'
        self.port = port
        self.batch_time = batch_time
        self.bool_get_accel = bool(get_accel)

        sensor.init_parser(self.port)
        sensor.init_board()
        self._openbci = sensor
        
        # Print all launch values
        self.get_logger().debug(f"Modality: {self.modality}\nTopics: {self.topics}\nPort: {self.port}\nBatch Time: {self.batch_time}\nAccel: {self.bool_get_accel}\naccel_param: {get_accel}\nself._openbci:\t{self._openbci}")

        self.publisher = {} # keep track of publishers
        # Create publishers
        self.get_logger().debug("Creating publsher")
        self.publisher[f"{str.lower(self.modality)}"] = self.create_publisher(BciData, self.topics, 10) # topic for modality e.g. /bci/eeg
        self.list_channel_names.append(self.modality)
        if self.bool_get_accel:
            self.publisher["accel"] = self.create_publisher(BciData, "/bci/acc", 10)
            self.list_channel_names.append('accel')
        self.get_logger().debug(f"self.list_channel_name: \n{self.list_channel_names}")
        self.t0_n_samples = {}
        self.metadata = {}
        temp_var = {'t0': None, 'n_samples': 0, 'n': []}
        temp_var2 = {'srate': 0, 'channels': [], 'timestamp_channel': []}
        for i, channel_name in enumerate(self.list_channel_names):
            if channel_name not in list(self.t0_n_samples.keys()):
                self.t0_n_samples[channel_name] = temp_var.copy()
                self.metadata[channel_name] = temp_var2.copy()
    
    def check_sensor_prepared(self):
        """Connect to the sensor and prepare it for streaming. Raise an error if the sensor if not ready (is_board_prepared() returns False) after 5 tries."""
        for _ in range(5):
            self.i += 1
            self.get_logger().info("Preparing session")
            self._openbci.prepare()
            if not self._openbci.is_board_prepared():
                if self.i >= 5:
                    self.get_logger().error("Unable to prepare session. Exiting code after 5 tries.")
                    break
            else:
                if self.bool_get_accel:
                    self._openbci.enable_accel()
                self.get_logger().info("Session prepared")
                break

    def acquire_sensor_data(self) -> np.ndarray:
        """Get data from the sensor. 

        Returns:
            np.ndarray : data from sensor
        """
        time.sleep(self.batch_time)
        data = self._openbci.get_board_data()  # get all data and remove it from internal buffer
        return data
    
    def format_data(self, data: np.ndarray) -> pd.DataFrame:
        """Format data acquired from the sensor.
        Arguments:
            np.ndarray data : Data from sensor

        Returns:
            pd.DataFrame sensor_data : Data from the sensor
        """
        data_to_publish = pd.DataFrame(np.transpose(data))
        return data_to_publish
    
    def modify_timestamp(self, channel_name: str, sensor_data: pd.DataFrame, timestamp_: list) -> list:
        """Modify timestamp to be evenly spaced as uneven timestamps are received from BrainFlow.
        Arguments:
            str channel_name : Variable for current preset
            pd.DataFrame sensor_data : Data for specified stream
            list timestamp_ : Timestamp for 'sensor_data' provided by BrainFlow

        Returns:
            list timestamp : Evenly spaced timestamps
        """
        if self.t0_n_samples[channel_name]['t0'] == None:
            self.t0_n_samples[channel_name]['t0'] = timestamp_[0]
        n_samples = sensor_data.shape[0]
        if self.t0_n_samples[channel_name]['n_samples'] == None:
            self.t0_n_samples[channel_name]['n_samples'] = n_samples
        timestamp = []
        for i in range(n_samples):
            new_ts = self.t0_n_samples[channel_name]['t0'] + (self.t0_n_samples[channel_name]['n_samples'] + i)/ self.metadata[channel_name]['srate']
            timestamp.append(new_ts)
        self.t0_n_samples[channel_name]['n_samples'] += n_samples
        self.t0_n_samples[channel_name]['n'].append(n_samples)
        return timestamp
    
    def get_board_metadata(self):
        """Get OpenBCI board's descriotion and save it in a dict."""
        for channel_name in self.list_channel_names:
            board_descr = self._openbci.get_board_description()
            timestamp_channel = board_descr['timestamp_channel']
            srate = board_descr['sampling_rate']
            modality_channel_name = f"{str.lower(channel_name)}_channels"
            modality_channels = board_descr[modality_channel_name]
            self.metadata[channel_name]['timestamp_channel'] = timestamp_channel
            self.metadata[channel_name]['channels'] = modality_channels
            self.metadata[channel_name]['srate'] = srate

    def publish_data(self, timestamp: list, channel_name: str, channels: list, sensor_data: pd.DataFrame, curr_publisher: rclpy.publisher.Publisher):
        """Publish data to ROS2 topic.
        Arguments:
            list timestamp : Timestamps for sensor data
            str channel_name : Name of the channel
            list channels : List of channels
            pd.DataFrame sensor_data : Data acquired from the sensor
            rclpy.publisher.Publisher : ROS2 publisher object
        """
        main_msg = BciData()
        main_msg.timestamp = [convert_time(t) for t in timestamp]
        main_msg.srate = self.metadata[channel_name]['srate']
        temp_msg = []
        for k, ch in enumerate(channels):
            msg = Bci()
            self.get_logger().debug(f"Channel name: {channel_name}\nChannel No, channel: {k+1}, {ch}")
            msg.channel = k+1
            msg.data = sensor_data[ch].to_numpy(dtype=np.float64).tolist()
            temp_msg.append(msg)
        main_msg.data = temp_msg
        curr_publisher.publish(main_msg)

    def acquire_and_publish_data(self):
        """Communicate with the sensor, format the acquired data and publish the sensor data to ROS2 topic. 
        If no data is received, then a warning is raised."""
        if self.i == 0:
            self.check_sensor_prepared()
            self._openbci.start_streaming()
        self.get_board_metadata()
        all_data = self.acquire_sensor_data()
        all_data = self.format_data(all_data)
        if all_data.shape[0] != 0:
            rows_zero = (all_data==0).all(axis=1)
            all_data = all_data[~rows_zero]
            for i, channel_name in enumerate(self.list_channel_names):
                curr_publisher = self.publisher[channel_name]
                channels = self.metadata[channel_name]['channels']
                sensor_data = all_data[channels]
                timestamp_channel = self.metadata[channel_name]['timestamp_channel']
                timestamp_ = all_data[timestamp_channel]
                timestamp = self.modify_timestamp(channel_name, sensor_data, timestamp_)
                self.publish_data(timestamp, channel_name, channels, sensor_data, curr_publisher)
            self.get_logger().info(f"Message Published for {self.list_channel_names}!", throttle_duration_sec=1.0)
        else:
            self.get_logger().warning(f"Waiting to receive data. Shape of the data received: {all_data.shape}")

    def run(self):
        """Runs the node continuously in a while loop until manually exited or any exception occurs."""
        try:
            while rclpy.ok():
                self.acquire_and_publish_data()
        except KeyboardInterrupt:
            self.get_logger().info('Session in keyboard interrupt')
        except Exception as e:
            self.get_logger().info(f'Session in exception: {traceback.format_exc()}')
        finally:
            self._openbci.stop_streaming()
            self.get_logger().info('Session stopped')
            self._openbci.release_session()
            self.get_logger().info('Session released')


def main():
    """Run the SensorDataOpenbci Node."""
    sensor = OpenbciSensor()
    rclpy.init()
    sensor_node=SensorDataOpenbci(sensor=sensor)
    sensor_node.get_logger().debug("Node has been initialised")
    try:
        sensor_node.run()
    finally:
        sensor_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
