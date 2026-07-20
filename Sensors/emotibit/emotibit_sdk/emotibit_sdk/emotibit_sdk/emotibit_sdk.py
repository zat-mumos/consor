"""
A ROS node that gets data from the EmotiBit sensor and publishes it to a ROS topic

Subscribers:
    None

Publishers:
    One publisher per stream or topic as mentioned in the YAML config file. 
    For example, /emotibit/acc, /emotibit/gyro, /emotibit/mag, /emotibit/ppg, /emotibit/eda, /emotibit/temp 

Parameters:
    - topic_names (list, default: ["default_topic"])
    - stream_names (list, default: ["default_stream"])
    - callback_timer (float, default: 1e-5)
    - emotibit_timer (float, default: 1e-5)

Description:
    This code connects to the sensor using BrainFlow SDK.
    Depending on the streams, the preset (to know more about BrainFlow presets, visit http://brainflow.readthedocs.io/en/stable/DataFormatDesc.html#presets-label) is set and the sensor data is acquired. 
    The data received from the sensor is then published to the respective ROS2 topic.

Author: 
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""

import time
from typing import Literal
import rclpy
from rclpy.logging import LoggingSeverity
from rclpy.node import Node
import traceback
import rclpy.publisher
from zat_ros2_msgs.msg import EmotibitMsg, EmotibitData
from builtin_interfaces.msg import Time
import pandas as pd
import numpy as np
from emotibit_sdk.sensor import EmotibitSensor
from common_functions.common import convert_time

class SensorDataEmotibitWithSdk(Node):
    """
    Acquire and publish sensor data from EmotiBit using BrainFlow SDK.
    """

    def __init__(self,
                 sensor: EmotibitSensor,
                 batch_time: float = 1e-5, # the frequency at which the data should be collected
                 type_stream: list  = ["default_stream"],
                 sensor_topic: list = ["deafault_topic"]
                 ):
        """
        Initialise the SensorDataEmotibitWithSdk class.
        """
        super().__init__('sensor_data_emotibit_with_sdk')

        # self.get_logger().set_level(LoggingSeverity.DEBUG) # Uncomment this line to print debug statements within the code.
        
        # Declare parameters
        self.declare_parameter('topic_names', sensor_topic)
        self.declare_parameter('stream_names', type_stream)
        self.declare_parameter('emotibit_timer', batch_time)
        
        # Get parameter values
        batch_time = self.get_parameter('emotibit_timer').value
        type_stream = self.get_parameter('stream_names').value
        sensor_topic = self.get_parameter('topic_names').value

        self.get_logger().debug(f'Stream_names: {type_stream} ')
        self.get_logger().debug(f'Emotibit_timer: {batch_time} ')
        self.get_logger().debug(f'Topic_names: {sensor_topic} ')

        # Check conditions
        if not isinstance(type_stream, list):
            self.get_logger().error(f"Expected 'list' but received '{type(type_stream)}' for parameter type_stream")
            raise TypeError(f" Expected 'list' but received '{type(type_stream)}' for parameter type_stream")
        if not isinstance(sensor_topic, list):
            self.get_logger().error(f"Expected 'list' but received '{type(sensor_topic)}' for parameter sensor_topic")
            raise TypeError(f"Expected 'list' but received '{type(sensor_topic)}' for parameter sensor_topic")
        if len(type_stream) != len(sensor_topic):
            self.get_logger().error(f"Length mismatch: Number of streams ({len(type_stream)}) does not match the number of topics ({len(sensor_topic)}). Plese check the yaml file.")
            raise ValueError(f"Length mismatch: Number of streams ({len(type_stream)}) does not match the number of topics ({len(sensor_topic)}). Plese check the yaml file.")
        
        self.constants = {
            'Accelerometer': 1, 'Gyroscope': 2, 'Magnetometer': 3, 'PPG': 4, 'EDA': 5, 'Temperature': 6
        }
        
        if any(i not in self.constants.keys() for i in type_stream):
            self.get_logger().error(f"Value mismatch: At least one of the stream type is invalid ({type_stream}). Possible stream types are: Accelerometer, Gyroscope, Magnetometer, PPG, EDA, Temperature.")
            raise ValueError(f"Value mismatch: At least one of the stream type is invalid ({type_stream}). Possible stream types are: Accelerometer, Gyroscope, Magnetometer, PPG, EDA, Temperature.")
        
        self.i = 0 # counter
        self._emotibit = sensor

        self.t0_n_samples = {
            'def': {
                "Accelerometer": {'t0': None, 'n_samples': 0, 'n': []},
                "Gyroscope": {'t0': None, 'n_samples': 0, 'n': []},
                "Magnetometer": {'t0': None, 'n_samples': 0, 'n': []},
                },
            'aux': {    
                "PPG": {'t0': None, 'n_samples': 0, 'n': []}
                },
            'anc': {
                "EDA": {'t0': None, 'n_samples': 0, 'n': []},
                "Temperature": {'t0': None, 'n_samples': 0, 'n': []}
                }
            }

        self.topics = sensor_topic
        self.batch_time = batch_time
        self.stream_type = type_stream
        self.get_logger().info(f'Starting node for EmotiBit sensor (publishing frequency: {batch_time})')
        self.get_logger().debug(f'Stream type: \n{type_stream}\n\nTopic: \n{sensor_topic})')
            
        self.publisher = {} # Keep track of publishers
        for stream, topic in zip(self.stream_type, self.topics):
            self.get_logger().debug(f'Creating publisher for EmotiBit sensor (Stream type: {stream} & Topic: {topic})')
            self.publisher[stream] = self.create_publisher(EmotibitMsg, topic, 10)

    def check_sensor_prepared(self):
        """Connect to the sensor and prepare it for streaming. Raise an error if the sensor if not ready (is_board_prepared() returns False) after 5 tries."""
        for _ in range(5):
            self.i += 1
            self.get_logger().info("Preparing session")
            self._emotibit.prepare()
            if not self._emotibit.is_board_prepared():
                if self.i >= 5:
                    self.get_logger().error("Unable to prepare session. Exiting code after 5 tries.")
                    break
            else:
                self.get_logger().info("Session prepared")
                break

    def acquire_sensor_data(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get data from the sensor for all presets. For Emotibit sensor, there are 3 available presets (namely default, auxiliary and ancillary preset).
        
        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray] : data from default preset, data from auxiliary preset, data from ancillary preset
        """
        time.sleep(self.batch_time)
        data_def = self._emotibit.get_board_data(preset_name='default')
        data_aux = self._emotibit.get_board_data(preset_name='auxiliary')
        data_anc = self._emotibit.get_board_data(preset_name='ancillary')  # get all data and remove it from internal buffer
        return data_def, data_aux, data_anc
    
    def format_data_default_preset(self, data_def: np.ndarray, stream: Literal['Accelerometer', 'Gyroscope', 'Magnetometer']) -> tuple[pd.DataFrame, list, str, list]:
        """Get data for the stream in the default preset as specified by the 'stream' variable. Possible streams for 'default' preset are 'Accelerometer', 'Gyroscope' and 'Magnetometer'.
        Arguments:
            np.ndarray data_def : Data from sensor for default preset
            str stream : Stream name (either 'Accelerometer', 'Gyroscope' or 'Magnetometer')

        Returns:
            pd.DataFrame sensor_data : Data for specified stream
            list timestamp : Timestamp for 'sensor_data' provided by BrainFlow
            str var_preset : Variable for abbreviated preset name (i.e., 'def')
            list channels : List of channel names for the current preset
        """
        data_def_to_publish = pd.DataFrame(np.transpose(data_def)) 
        timestamp_channel_def, _ = self._emotibit.get_channels(preset_name='default', channel_name='timestamp_channel')
        timestamp = data_def_to_publish.iloc[:, timestamp_channel_def].to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
        var_preset = 'def'
        if stream == 'Accelerometer':
            channels, _ = self._emotibit.get_channels(preset_name='default', channel_name='accel_channels')
        elif stream == 'Gyroscope':
            channels, _ = self._emotibit.get_channels(preset_name='default', channel_name='gyro_channels')
        elif stream == 'Magnetometer':
            channels, _ = self._emotibit.get_channels(preset_name='default', channel_name='magnetometer_channels')
        sensor_data = data_def_to_publish.iloc[:, channels]
        return sensor_data, timestamp, var_preset, channels

    def format_data_auxiliary_preset(self, data_aux: np.ndarray) -> tuple[pd.DataFrame, list, str, list]:
        """Get data for PPG modality in the auxiliary preset.
        Arguments:
            np.ndarray data_aux : Data from sensor for auxiliary preset

        Returns:
            pd.DataFrame sensor_data : PPG data from the sensor
            list timestamp : Timestamp for 'sensor_data' provided by BrainFlow
            str var_preset : Variable for abbreviated preset name (i.e., 'aux')
            list channels : List of channel names for the current preset
        """
        data_aux_to_publish = pd.DataFrame(np.transpose(data_aux))
        timestamp_channel_aux, _ = self._emotibit.get_channels(preset_name='auxiliary', channel_name='timestamp_channel')
        timestamp = data_aux_to_publish.iloc[:, timestamp_channel_aux].to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
        var_preset = 'aux'
        channels, _ = self._emotibit.get_channels(preset_name='auxiliary', channel_name='ppg_channels')
        sensor_data = data_aux_to_publish.iloc[:, channels]
        return sensor_data, timestamp, var_preset, channels
    
    def format_data_ancillary_preset(self, data_anc: np.ndarray, stream: Literal['EDA', 'Temperature']) -> tuple[pd.DataFrame, list, str, list]:
        """Get data for the stream in the ancillary preset as specified by the 'stream' variable. Possible streams for 'ancillary' preset are 'EDA' and 'Temperature'.
        Arguments:
            np.ndarray data_anc : Data from sensor for ancillary preset
            str stream : Stream name (either EDA or Temperature)

        Returns:
            pd.DataFrame sensor_data : Data for specified stream
            list timestamp : Timestamp for 'sensor_data' provided by BrainFlow
            str var_preset : Variable for abbreviated preset name (i.e., 'anc')
            list channels : List of channel names for the current preset
        """
        data_anc_to_publish = pd.DataFrame(np.transpose(data_anc)) 
        timestamp_channel_anc, _ = self._emotibit.get_channels(preset_name='ancillary', channel_name='timestamp_channel')
        timestamp = data_anc_to_publish.iloc[:, timestamp_channel_anc].to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
        var_preset = 'anc'
        if stream == 'EDA':
            channels, _ = self._emotibit.get_channels(preset_name='ancillary', channel_name='eda_channels')
        elif stream == 'Temperature':
            channels, _ = self._emotibit.get_channels(preset_name='ancillary', channel_name='temperature_channels')
        sensor_data = data_anc_to_publish.iloc[:, channels]
        return sensor_data, timestamp, var_preset, channels
    
    def store_srate(self):
        """Get the sampling rate for each preset and store them in a class 'dict' variable."""
        srate_def, _ = self._emotibit.get_channels(preset_name='default', channel_name='sampling_rate') # 25
        srate_aux, _ = self._emotibit.get_channels(preset_name='auxiliary', channel_name='sampling_rate') # 25
        srate_anc, _ = self._emotibit.get_channels(preset_name='ancillary', channel_name='sampling_rate') # 15
        self.t0_n_samples['def']['srate'] = srate_def
        self.t0_n_samples['aux']['srate'] = srate_aux
        self.t0_n_samples['anc']['srate'] = srate_anc

    def modify_timestamp(self, var_preset: str, stream: Literal['Accelerometer', 'Gyroscope', 'Magnetometer', 'PPG', 'EDA', 'Temperature'], 
                        sensor_data: pd.DataFrame, timestamp_: list) -> list:
        """Modify timestamp to be evenly spaced as uneven timestamps are received from BrainFlow.
        Arguments:
            str var_preset : Variable for current preset
            str stream : Stream name (Possible streams are Accelerometer, Gyroscope, Magnetometer, PPG, EDA or Temperature)
            pd.DataFrame sensor_data : Data for specified stream
            list timestamp_ : Timestamp for 'sensor_data' provided by BrainFlow

        Returns:
            list timestamp : Evenly spaced timestamps
        """
        if self.t0_n_samples[var_preset][stream]['t0'] == None:
            self.t0_n_samples[var_preset][stream]['t0'] = timestamp_[0]
        n_samples = sensor_data.shape[0]
        if self.t0_n_samples[var_preset][stream]['n_samples'] == None:
            self.t0_n_samples[var_preset][stream]['n_samples'] = n_samples
        timestamp = []
        for i in range(n_samples):
            new_ts = self.t0_n_samples[var_preset][stream]['t0'] + (self.t0_n_samples[var_preset][stream]['n_samples'] + i)/ self.t0_n_samples[var_preset]['srate']
            timestamp.append(new_ts)
        self.t0_n_samples[var_preset][stream]['n_samples'] += n_samples
        self.t0_n_samples[var_preset][stream]['n'].append(n_samples)
        return timestamp

    def acquire_and_publish_data(self):
        """Communicate with the sensor, format the acquired data and publish the sensor data to ROS2 topic.
        If no data is received, then a warning is raised."""
        if self.i == 0:
            self.check_sensor_prepared()
            self._emotibit.start_streaming()
        all_data = self.acquire_sensor_data() 
        if all(i.shape[1] != 0 for i in all_data):
            data_def, data_aux, data_anc = all_data[0], all_data[1], all_data[2]
            self.store_srate()
            streams_ = []
            for stream in self.stream_type: # for each stream, publish data
                streams_.append(stream)
                curr_publisher = self.publisher[stream]
                channels = []
                if stream in ["Accelerometer", "Gyroscope", "Magnetometer"]: # DEFAULT PRESET
                    sensor_data, timestamp, var_preset, channels = self.format_data_default_preset(data_def, stream)
                elif stream in ['PPG']: #AUXILIARY PRESET
                    sensor_data, timestamp, var_preset, channels = self.format_data_auxiliary_preset(data_aux)
                elif stream in ["EDA", "Temperature"]: # ANCILLARY PRESET
                    sensor_data, timestamp, var_preset, channels = self.format_data_ancillary_preset(data_anc, stream)                
                else:
                    self.get_logger().error(f"Current stream ({stream}) does not belong to any preset.")
                rows_zero = (sensor_data==0).all(axis=1)
                sensor_data = sensor_data[~rows_zero]
                timestamp = self.modify_timestamp(var_preset, stream, sensor_data, timestamp)
                self.publish_data(timestamp, stream, channels, sensor_data, curr_publisher)
            self.get_logger().info(f"Message Published for {streams_}!", throttle_duration_sec=1.0) # self.get_logger().info(f"Publishing time: {end_time2 - start_time2}")
        else:
            self.get_logger().warning(f"Waiting to receive data from all presets. Shape of the data received: {[i.shape for i in all_data]}")

    def publish_data(self, timestamp: list, stream: Literal['Accelerometer', 'Gyroscope', 'Magnetometer', 'PPG', 'EDA', 'Temperature'], channels: list, 
                    sensor_data: pd.DataFrame, curr_publisher: rclpy.publisher.Publisher):
        """Publish data to ROS2 topic.
        Arguments:
            list timestamp : Timestamps for sensor data
            str stream : Stream name (Possible streams are Accelerometer, Gyroscope, Magnetometer, PPG, EDA or Temperature)
            list channels : List of channel names for current preset
            pd.DataFrame sensor_data : Data for specified stream
            rclpy.publisher.Publisher : ROS2 publisher object
        """
        main_msg = EmotibitMsg()
        main_msg.timestamp = [convert_time(t) for t in timestamp]
        curr_const = self.constants.get(stream)
        main_msg.stream = curr_const
        temp_msg_data = []
        for k, ch in enumerate(channels):
            msg = EmotibitData()
            if stream in ['EDA', 'Temperature']:
                msg.channel = 0
            else:
                msg.channel = k+1
            temp_data = sensor_data.iloc[:, k] # columns range from 0 - no_channels-1
            temp_data = temp_data.to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
            msg.data = temp_data
            temp_msg_data.append(msg) # One list per channel
        main_msg.data = temp_msg_data
        curr_publisher.publish(main_msg) # One message per modality i.e. Accelerometer, Gyroscope, Magnetometer, ...

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
            self._emotibit.stop_streaming()
            self.get_logger().info('Session stopped')
            self._emotibit.release_session()
            self.get_logger().info('Session released')


def main():
    """Run the SensorDataEmotibitWithSdk Node."""
    sensor = EmotibitSensor()
    rclpy.init()
    sensor_node=SensorDataEmotibitWithSdk(sensor=sensor)
    sensor_node.get_logger().debug("Node has been initialised")
    try:
        sensor_node.run()
    finally:
        sensor_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
