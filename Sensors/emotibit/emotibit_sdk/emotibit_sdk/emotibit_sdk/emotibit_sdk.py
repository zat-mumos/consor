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
    def __init__(self,
                 batch_time: float = 1e-5, # the frequency at which the data should be collected
                 callback_timer: float = 1e-5, # timer for the callback function
                 type_stream  = ["default_stream"],
                 sensor_topic = ["deafault_topic"]
                 ):
        super().__init__('sensor_data_emotibit_with_sdk')

        # self.get_logger().set_level(LoggingSeverity.DEBUG) # Uncomment this line to debug the code.

        self.i = 0 # counter
        
        # Declare parameters
        self.declare_parameter('topic_names', sensor_topic)
        self.declare_parameter('stream_names', type_stream)
        self.declare_parameter('callback_timer', callback_timer)
        self.declare_parameter('emotibit_timer', batch_time)
        
        # Get parameter values
        callback_timer = self.get_parameter('callback_timer').value
        self.get_logger().debug(f'callback_timer: {callback_timer} ')
        batch_time = self.get_parameter('emotibit_timer').value
        self.get_logger().debug(f'Emotibit_timer: {batch_time} ')
        type_stream = self.get_parameter('stream_names').value
        self.get_logger().debug(f'Stream_names: {type_stream} ')
        sensor_topic = self.get_parameter('topic_names').value
        self.get_logger().debug(f'Topic_names: {sensor_topic} ')

        self.topics = sensor_topic
        self.batch_time = batch_time
        self.stream_type = type_stream
        self.callback_timer = callback_timer
        self.get_logger().debug(f'Beginning code ... ')
        self.get_logger().info(f'Starting node for EmotiBit sensor (publishing frequency: {batch_time})')
        self.get_logger().debug(f'Stream type: \n{type_stream}\n\nTopic: \n{sensor_topic})')

        self.constants = {
            'Accelerometer': 1, 'Gyroscope': 2, 'Magnetometer': 3, 'PPG': 4, 'EDA': 5, 'Temperature': 6
        }
            
        self.publisher = {} # Keep track of publishers
        self.current_threads = [] # keep track of threads

        for stream, topic in zip(self.stream_type, self.topics):
            self.get_logger().debug(f'Creating publisher for EmotiBit sensor (Stream type: {stream} & Topic: {topic})')
            self.publisher[stream] = self.create_publisher(EmotibitMsg, topic, 10)

        
        self.timer_call = self.create_timer(self.callback_timer, self.timer_callback)

    def timer_callback(self):
        try:
            self.get_logger().debug("In timer_callback")
            while rclpy.ok():
                self.get_logger().debug("In timer_callback 2")

                params = BrainFlowInputParams()
                # current_preset = BrainFlowPresets.DEFAULT_PRESET
                # params.preset = current_preset

                board_ids = BoardIds.EMOTIBIT_BOARD    
                board = BoardShim(board_ids, params)
                self.get_logger().debug(f"Board: {board}")

                if not board.is_prepared():
                    self.get_logger().debug("In timer_callback 3")
                    board.prepare_session()
                
                if board.is_prepared():
                    self.get_logger().debug("In timer_callback 4")
                    board.start_stream ()
                    self.get_logger().debug(f"Streaming started")
                    time.sleep(self.batch_time)

                    data_def = board.get_board_data(preset=BrainFlowPresets.DEFAULT_PRESET)
                    data_aux = board.get_board_data(preset=BrainFlowPresets.AUXILIARY_PRESET)
                    data_anc = board.get_board_data(preset=BrainFlowPresets.ANCILLARY_PRESET)  # get all data and remove it from internal buffer
                    
                    self.get_logger().debug(f"Data received")
                    board.stop_stream()
                    self.get_logger().debug(f"Streaming stopped")
                    board.release_session()
                    self.get_logger().debug(f"Session released")


                    board_descr_def = BoardShim.get_board_descr(board_ids, preset=BrainFlowPresets.DEFAULT_PRESET)
                    board_descr_aux = BoardShim.get_board_descr(board_ids, preset=BrainFlowPresets.AUXILIARY_PRESET)
                    board_descr_anc = BoardShim.get_board_descr(board_ids, preset=BrainFlowPresets.ANCILLARY_PRESET)

                    self.get_logger().debug(f"DEFAULT PRESET")
                    self.get_logger().debug(f"Data (shape): {pd.DataFrame(np.transpose(data_def)).shape}")
                    self.get_logger().debug(f"Board Description: {board_descr_def}\n")

                    self.get_logger().debug(f"AUXILIARY PRESET")
                    self.get_logger().debug(f"Data (shape): {pd.DataFrame(np.transpose(data_aux)).shape}")
                    self.get_logger().debug(f"Board Description: {board_descr_aux}\n")

                    self.get_logger().debug(f"ANCILIARY PRESET")
                    self.get_logger().debug(f"Data (shape): {pd.DataFrame(np.transpose(data_anc)).shape}")
                    self.get_logger().debug(f"Board Description: {board_descr_anc}\n")

                    data_def_to_publish = pd.DataFrame(np.transpose(data_def)) 
                    data_aux_to_publish = pd.DataFrame(np.transpose(data_aux)) 
                    data_anc_to_publish = pd.DataFrame(np.transpose(data_anc)) 

                    timestamp_channel_def = board_descr_def['timestamp_channel']
                    timestamp_channel_aux = board_descr_aux['timestamp_channel']
                    timestamp_channel_anc = board_descr_anc['timestamp_channel']

                    self.get_logger().debug(f"Timestamp Channel: \nDefault {timestamp_channel_def}\nAuxiliary {timestamp_channel_aux}\nAncillary {timestamp_channel_anc}")

                    # for each stream, publish data
                    for stream in self.stream_type:
                        curr_publisher = self.publisher[stream]
                        curr_const = self.constants.get(stream)
                        channels = []
                        if stream in ["Accelerometer", "Gyroscope", "Magnetometer"]: # DEFAULT PRESET
                            timestamp = data_def_to_publish.iloc[:, timestamp_channel_def].to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
                            if stream == 'Accelerometer':
                                channels = board_descr_def['accel_channels']
                            elif stream == 'Gyroscope':
                                channels = board_descr_def['gyro_channels']
                            elif stream == 'Magnetometer':
                                channels = board_descr_def['magnetometer_channels']
                            sensor_data = data_def_to_publish.iloc[:, channels]

                        elif stream in ['PPG']: #AUXILIARY PRESET
                            timestamp = data_aux_to_publish.iloc[:, timestamp_channel_aux].to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
                            channels = board_descr_aux['ppg_channels']
                            sensor_data = data_aux_to_publish.iloc[:, channels]

                        elif stream in ["EDA", "Temperature"]: # ANCILLARY PRESET
                            timestamp = data_anc_to_publish.iloc[:, timestamp_channel_anc].to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
                            if stream == 'EDA':
                                channels = board_descr_anc['eda_channels']
                            elif stream == 'Temperature':
                                channels = board_descr_anc['temperature_channels']
                            sensor_data = data_anc_to_publish.iloc[:, channels]
                        else:
                            self.get_logger().info(f"Current stream ({stream}) does not belong to any preset\nContinuing ...")
                            continue

                        main_msg = EmotibitMsg()
                        main_msg.timestamp = [self.convert_time(t) for t in timestamp]
                        curr_const = self.constants.get(stream)
                        main_msg.stream = curr_const

                        temp_msg_data = []
                        for k, ch in enumerate(channels):
                            msg = EmotibitData()
                            if stream in ['EDA', 'Temperature']:
                                self.get_logger().info(f"if: Stream name: {stream}\nChannel No: {k+1}\nk: {k}\nch: {ch}")
                                msg.channel = 0
                            else:
                                self.get_logger().info(f"else: Stream name: {stream}\nChannel No: {k+1}\nk: {k}\nch: {ch}")
                                # self.get_logger().debug(f"\nData:\n{temp_data}\n")
                                msg.channel = k+1
                            temp_data = sensor_data.iloc[:, k] # columns range from 0 - no_channels-1
                            temp_data = temp_data.to_numpy(dtype=np.float64).tolist() # Pandas series -> Numpy array -> list
                            self.get_logger().debug(f"Stream name: {stream}\nChannel No: {channels[k]}\nk: {k}\nch: {ch}\nData:\n{temp_data}\n")
                            msg.data = temp_data
                            self.get_logger().debug(f"\nCurrent Msg: {msg}\nTemp_msg_data: {temp_msg_data}\n")
                            temp_msg_data.append(msg) # One list per channel

                        main_msg.data = temp_msg_data
                        curr_publisher.publish(main_msg) # One message per modality i.e. Accelerometer, Gyroscope, Magnetometer, ...
                        self.get_logger().info(f'msg:\n{main_msg}\n--------**************---------\n')
        except KeyboardInterrupt:
            self.get_logger().debug('Session in keyboard interrupt')
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


    def convert_time(self, timestamp):
        time = Time()
        time.sec = int(timestamp)
        time.nanosec = int((timestamp%1)*1e9)
        return time


def main():
    rclpy.init()
    sensor_node=SensorDataEmotibitWithSdk()

    sensor_node.get_logger().debug("Node has been initialised")
    sensor_node.get_logger().debug(f"Node: {sensor_node}\nType: {type(rclpy.spin)}")
    try:
        rclpy.spin(sensor_node)
        sensor_node.get_logger().debug("rclpy.spin() called ................")
    except KeyboardInterrupt:
        sensor_node.get_logger().debug(f"KeyBoard Interrupt")
    finally:
        sensor_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
