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

import rclpy
from rclpy.logging import LoggingSeverity
from rclpy.node import Node
from zat_ros2_msgs.msg import EmotibitMsg, EmotibitData
from builtin_interfaces.msg import Time
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
import pandas as pd
import numpy as np
import time

class SensorDataEmotibitWithSdk(Node):
    """
    Acquire and publish sensor data from EmotiBit using BrainFlow SDK.
    """

    def __init__(self,
                 batch_time: float = 1e-5, # the frequency at which the data should be collected
                 type_stream: list  = ["default_stream"],
                 sensor_topic: list = ["deafault_topic"]
                 ):
        """
        Initialise the SensorDataEmotibitWithSdk class.
        """
        super().__init__('sensor_data_emotibit_with_sdk')

        # self.get_logger().set_level(LoggingSeverity.DEBUG) # Uncomment this line to print debug statements within the code.

        self.i = 0 # counter

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

        # Declare parameters
        self.declare_parameter('topic_names', sensor_topic)
        self.declare_parameter('stream_names', type_stream)
        self.declare_parameter('emotibit_timer', batch_time)
        
        # Get parameter values
        batch_time = self.get_parameter('emotibit_timer').value
        self.get_logger().debug(f'Emotibit_timer: {batch_time} ')
        type_stream = self.get_parameter('stream_names').value
        self.get_logger().debug(f'Stream_names: {type_stream} ')
        sensor_topic = self.get_parameter('topic_names').value
        self.get_logger().debug(f'Topic_names: {sensor_topic} ')

        self.topics = sensor_topic
        self.batch_time = batch_time
        self.stream_type = type_stream
        self.get_logger().debug(f'Beginning code ... ')
        self.get_logger().info(f'Starting node for EmotiBit sensor (publishing frequency: {batch_time})')
        self.get_logger().debug(f'Stream type: \n{type_stream}\n\nTopic: \n{sensor_topic})')

        self.constants = {
            'Accelerometer': 1, 'Gyroscope': 2, 'Magnetometer': 3, 'PPG': 4, 'EDA': 5, 'Temperature': 6
        }
            
        self.publisher = {} # Keep track of publishers

        for stream, topic in zip(self.stream_type, self.topics):
            self.get_logger().debug(f'Creating publisher for EmotiBit sensor (Stream type: {stream} & Topic: {topic})')
            self.publisher[stream] = self.create_publisher(EmotibitMsg, topic, 10)

    def run(self):
        """
        A callback function which connects to the sensor, acquires data from it and then publishes this information to a ROS topic at regular intervals.
        """
        try:
            while rclpy.ok():
                if self.i == 0:
                    params = BrainFlowInputParams()
                    board_ids = BoardIds.EMOTIBIT_BOARD    
                    board = BoardShim(board_ids, params)
                    self.get_logger().debug(f"Board: {board}")
                    if not board.is_prepared():
                        board.prepare_session()
                    self.i += 1
                board.start_stream ()
                time.sleep(self.batch_time)
                data_def = board.get_board_data(preset=BrainFlowPresets.DEFAULT_PRESET)
                data_aux = board.get_board_data(preset=BrainFlowPresets.AUXILIARY_PRESET)
                data_anc = board.get_board_data(preset=BrainFlowPresets.ANCILLARY_PRESET)  # get all data and remove it from internal buffer
                board.stop_stream()
                board_descr_def = BoardShim.get_board_descr(board_ids, preset=BrainFlowPresets.DEFAULT_PRESET)
                board_descr_aux = BoardShim.get_board_descr(board_ids, preset=BrainFlowPresets.AUXILIARY_PRESET)
                board_descr_anc = BoardShim.get_board_descr(board_ids, preset=BrainFlowPresets.ANCILLARY_PRESET)
                data_def_to_publish = pd.DataFrame(np.transpose(data_def)) 
                data_aux_to_publish = pd.DataFrame(np.transpose(data_aux)) 
                data_anc_to_publish = pd.DataFrame(np.transpose(data_anc)) 
                timestamp_channel_def = board_descr_def['timestamp_channel']
                timestamp_channel_aux = board_descr_aux['timestamp_channel']
                timestamp_channel_anc = board_descr_anc['timestamp_channel']
                srate_def = board_descr_def['sampling_rate']
                srate_aux = board_descr_aux['sampling_rate']
                srate_anc = board_descr_anc['sampling_rate']
                self.t0_n_samples['def']['srate'] = srate_def
                self.t0_n_samples['aux']['srate'] = srate_aux
                self.t0_n_samples['anc']['srate'] = srate_anc
                streams_ = []
                # for each stream, publish data
                for stream in self.stream_type:
                    streams_.append(stream)
                    curr_publisher = self.publisher[stream]
                    curr_const = self.constants.get(stream)
                    channels = []
                    if stream in ["Accelerometer", "Gyroscope", "Magnetometer"]: # DEFAULT PRESET
                        timestamp = data_def_to_publish.iloc[:, timestamp_channel_def].to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
                        var_preset = 'def'
                        if stream == 'Accelerometer':
                            channels = board_descr_def['accel_channels']
                        elif stream == 'Gyroscope':
                            channels = board_descr_def['gyro_channels']
                        elif stream == 'Magnetometer':
                            channels = board_descr_def['magnetometer_channels']
                        sensor_data = data_def_to_publish.iloc[:, channels]
                    elif stream in ['PPG']: #AUXILIARY PRESET
                        timestamp = data_aux_to_publish.iloc[:, timestamp_channel_aux].to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
                        var_preset = 'aux'
                        channels = board_descr_aux['ppg_channels']
                        sensor_data = data_aux_to_publish.iloc[:, channels]
                    elif stream in ["EDA", "Temperature"]: # ANCILLARY PRESET
                        timestamp = data_anc_to_publish.iloc[:, timestamp_channel_anc].to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
                        var_preset = 'anc'
                        if stream == 'EDA':
                            channels = board_descr_anc['eda_channels']
                        elif stream == 'Temperature':
                            channels = board_descr_anc['temperature_channels']
                        sensor_data = data_anc_to_publish.iloc[:, channels]
                    else:
                        self.get_logger().info(f"Current stream ({stream}) does not belong to any preset\nContinuing ...")
                        continue
                    rows_zero = (sensor_data==0).all(axis=1)
                    sensor_data = sensor_data[~rows_zero]
                    if self.t0_n_samples[var_preset][stream]['t0'] == None:
                        self.t0_n_samples[var_preset][stream]['t0'] = timestamp[0]
                    n_samples = sensor_data.shape[0]
                    timestamp = []
                    for i in range(n_samples):
                        new_ts = self.t0_n_samples[var_preset][stream]['t0'] + (self.t0_n_samples[var_preset][stream]['n_samples'] + i)/ self.t0_n_samples[var_preset]['srate']
                        timestamp.append(new_ts)
                    self.get_logger().debug(f"New timestamps:\t{timestamp}")
                    self.t0_n_samples[var_preset][stream]['n_samples'] += n_samples
                    self.t0_n_samples[var_preset][stream]['n'].append(n_samples)

                    main_msg = EmotibitMsg()
                    main_msg.timestamp = [self.convert_time(t) for t in timestamp]
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
                self.get_logger().info(f"Message Published for {streams_}!", throttle_duration_sec=1.0)
        except KeyboardInterrupt:
            self.get_logger().debug('Session in keyboard interrupt')
            self.get_logger().debug(f"self.t0_n_samples: {self.t0_n_samples}")
            board.stop_stream()
            self.get_logger().debug('Session stopped')
            board.release_session()
            self.get_logger().debug('Session released & initiating rclpy shutdown')
            rclpy.shutdown()
        except Exception as e:
            self.get_logger().debug(f'Session in exception: {e}')
            board.stop_stream()
            self.get_logger().debug('Session stopped')
            board.release_session()
            self.get_logger().debug('Session released & initiating rclpy shutdown')
            rclpy.shutdown()

    def convert_time(self, timestamp: float):
        """
        Converts a float timestamp to seconds and nanoseconds.

        Arguments:
        float timestamp: timestamp in float

        Returns:
        builtin_interfaces.msg.Time : timestamp in seconds and nanoseconds
        """
        time = Time()
        time.sec = int(timestamp)
        time.nanosec = int((timestamp%1)*1e9)
        return time


def main():
    """
    Run the SensorDataEmotibitWithSdk Node.
    """
    rclpy.init()
    sensor_node=SensorDataEmotibitWithSdk()
    sensor_node.get_logger().debug("Node has been initialised")
    sensor_node.get_logger().debug(f"Node: {sensor_node}\nType: {type(rclpy.spin)}")
    try:
        sensor_node.run()
    except KeyboardInterrupt:
        sensor_node.get_logger().debug(f"KeyBoard Interrupt")
    finally:
        sensor_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
