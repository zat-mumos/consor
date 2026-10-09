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
A ROS node that extracts features from sensor data and publishes it to a ROS topic.

Subscribers:
    /sensor/synched/data: Subscriber for Synched data

Publishers:
    /processing/extract_features: Publishes extracted features

Parameters:
    window_size (int, default: 60)
    process_topic  (str, default: /processing/extract_features)
    sync_topic (str, default: /sensor/synched/data)

Description:
    This code subscribes to synched data.  If EDA data is available, the features are extracted and published to the ROS topic.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>

NOTE: Some parts of the code are used directly from vendor/eda_features.py.
"""
from decimal import Decimal
import rclpy
from rclpy.node import Node
from builtin_interfaces.msg import Time 
import rclpy.time
from std_msgs.msg import Float32MultiArray
import threading
import time
from vendor.eda_features import segment_windows, extract_manual_eda_features, extract_neurokit_eda_features
import rclpy.executors
import numpy as np
import pandas as pd
from rclpy.logging import LoggingSeverity
from zat_ros2_msgs.msg import SynchData
from queue import Queue, Empty
from collections import deque
import logging

class FeatureExtractionNode(Node):
    """
    Extract features and publish to a ROS node.
    """
    def __init__(
            self,
            sync_topic: str = '/sensor/synched/data',
            window_size: int = 60,
            process_topic: str = '/processing/extract_features'):
        """
        Initialize the FeatureExtractionNode class.

        Arguments:
        str sync_topic: ROS topic that synched data is being published
        str process_topic: ROS topic to publish extracted features
        window_size: Window size for sampling data for feature extraction
        """
        super().__init__('feature_extraction_node')
        # self.get_logger().set_level(LoggingSeverity.DEBUG) # Uncomment this line to print debug statements within the code.

        self.i = 0 # counter
        self.queue = deque()
        self.declare_parameters(
               namespace = '',
               parameters = [
                   ('window_size', window_size),
                   ('process_topic', process_topic),
                   ('sync_topic', sync_topic)
               ])
        # Get parameter values
        sync_topic = self.get_parameter('sync_topic').value
        process_topic = self.get_parameter('process_topic').value
        window_size = self.get_parameter('window_size').value

        self.window_size = window_size
        self._synched_data_subscriber = self.create_subscription(SynchData, sync_topic, self._sync_callback, 10)
        self._feature_publisher = self.create_publisher(Float32MultiArray, process_topic, 10)
        self.sync_period = None
        self.sampling_rate = None
        self.prev_ts_ = None
        self.prev_msg = None
        self.window_configs = None
        self.dfs = None
        self.max_buffer_len = None
        self.buffer = None
        self.bool_init = False
        self.set_queue_timestamps = set()
        self.lock = threading.Lock()
        self.temp_largest_window_key = None
        timer_period = 1.0
        self.get_logger().info("Starting node for feature extraction")
        timer = self.create_timer(timer_period, self._timer_callback)
        
    def _sync_callback(self, msg: SynchData):
        """
        A callback function for synched data that is executed each time a new message is received.

        Arguments:
        SyncData msg: The message received from /sensor/synched/data
        """
        list_timestamp = (msg.header.stamp.sec, msg.header.stamp.nanosec)
        if list_timestamp not in self.set_queue_timestamps:
            try:
                with self.lock:
                    self.queue.append(msg)
                    self.set_queue_timestamps.add(list_timestamp)
                    self.get_logger().info("Msg added to queue")
            except Exception as e:
                self.get_logger().warn(f"Warning: {e}\nQueue full & dropping message: {msg}")

    def _timer_callback(self):
        """
        A callback function that subscribes to the synched data ROS topic and publishes the extracted fatures to a ROS topic at regular intervals.
        """
        self.get_logger().debug(f"In Timer callback")
        with self.lock:
            while len(self.queue) > 0:
                msg_from_queue = self.queue.popleft()
                msg_timestamp = msg_from_queue.header.stamp
                ts_ = self.convert_time(msg_timestamp)                
                # This if-else conditions only run once in the beginning to set the sampling rate & window configs
                if self.prev_ts_ is None:
                    self.prev_ts_ = ts_
                    self.prev_msg = msg_from_queue
                    continue
                else:
                    if self.sync_period is None:
                        time_diff = abs(ts_ - self.prev_ts_)
                        self.sync_period = time_diff
                        self.get_logger().debug(f"\n\ntime difference/sync_period: {time_diff}\n\n")
                        self.sampling_rate = int(1 / self.sync_period)
                        # Parts of code adapted from vendor/eda_features.py
                        # !! different window sizes in seconds and steps (set steps for overlapping)
                        self.window_configs = {
                            self.window_size: {'size': self.window_size * self.sampling_rate, 'step': self.window_size * self.sampling_rate}
                        }
                        self.dfs = {size: [] for size in self.window_configs}
                        self.temp_largest_window_key = max(self.window_configs.keys())
                        self.max_buffer_len = self.window_configs[self.temp_largest_window_key]['size']
                        self.buffer = {} # eda_segment
                        self.buffer['eda'] = deque(maxlen = self.max_buffer_len)

                        # once all configs are set, add value from prev msg to buffer
                        for data in self.prev_msg.data:
                            if data.modality_name == 'eda':
                                self.buffer['eda'].append((self.prev_ts_, data.value))
                if self.bool_init:
                    self.dfs = {size: [] for size in self.window_configs}
                    self.buffer = {}
                    self.buffer['eda'] = deque(maxlen = self.max_buffer_len)
                    self.bool_init = False
                for data in msg_from_queue.data:
                    device_name = data.device_name
                    device_id = data.device_id
                    modality = data.modality_name
                    sensor_value = data.value
                    msg = Float32MultiArray()
                    if modality is not None and modality == 'eda':
                        self.buffer[modality].append((ts_, sensor_value)) # continue adding to self.buffer until the no of samples match the highest size of window
                        self.get_logger().debug(f"len(self.buffer['eda']): {len(self.buffer['eda'])}\t{self.max_buffer_len and len(self.buffer['eda']) % self.window_configs[self.temp_largest_window_key]['step']}")
                                    # f"buffer: {self.buffer}")
                        samples, timestamps = [], []
                        if len(self.buffer[modality]) == self.max_buffer_len and len(self.buffer['eda']) % self.window_configs[self.temp_largest_window_key]['step'] == 0:
                            win = list(self.buffer['eda'])
                            self.bool_init = True
                            self.get_logger().debug(f"check self.dfs: {self.dfs}")   
                            self.get_logger().info("Extracting features")
                            all_feats = self.process_eda(win)
                            data = all_feats[self.window_size]['feats'][0]
                            self.get_logger().debug(f"data: {data}")
                            data = [v for k, v in data.items()]
                            self.get_logger().debug(f"data: {data}")
                            msg.data = data
                            self._feature_publisher.publish(msg)
                            self.get_logger().info("Published extracted features\n")

    def convert_time(self, timestamp: Time, bool_to_s: bool = True):
        """
        Converts timestamp from builtin_interfaces.Time (https://docs.ros.org/en/humble/p/builtin_interfaces/msg/Time.html) to Decimal (https://docs.python.org/3/library/decimal.html) datatype.

        Arguments:
        Time timestamp: Timestamp 
        bool bool_to_s: If True, it converts timestamp from builtin_interfaces.Time to Decimal datatype

        Returns:
        Decimal time: The timestamp in seconds as a Decimal datatype
        """
        if bool_to_s:
            seconds = Decimal(timestamp.sec)
            nanosec = Decimal(timestamp.nanosec) / Decimal(1000000000) # 1e9
            time = seconds + nanosec
        return time
    
    def process_eda(self, win: list):
        """
        Processes the EDA signal to extract features (eda_mean, eda_std, eda_max, eda_range, eda_skewness, eda_kurtosis, SCR_Peaks, SCR_Peaks_Amplitude_Mean, EDA_Tonic_SD).

        Arguments:
        list win: A window of signal data

        Returns:
        dict temp_var: A dictionary of extracted features for the signal window specified by 'win'
        """
        self.get_logger().debug("In process_eda")
        # Parts of code is from vendor/eda_features.py
        timestamps = [ts for ts, v in win]
        samples = [[v] for ts, v in win]
        samples = np.array(samples)
        for k, v in self.window_configs.items():
                windows = segment_windows(samples, window_size = v['size'], step = v['step'])
                corresp_ts = segment_windows(timestamps, window_size = v['size'], step = v['step'])
                for i, window in enumerate(windows):                                
                    if len(window) < 10:
                        continue
                    feats_manual = extract_manual_eda_features(window)
                    feats_nk = extract_neurokit_eda_features(window, sampling_rate=self.sampling_rate)
                    all_feats = {}
                    all_feats['feats'] = {**feats_manual, **feats_nk}
                    all_feats['signal'] = window
                    all_feats['timestamp'] = corresp_ts
                    all_feats['window'] = i + 1
                    self.dfs[k].append(all_feats)
        self.get_logger().debug("Exiting process_eda")
        temp_var = {size: pd.DataFrame(feats) for size, feats in self.dfs.items()}
        for k, df in temp_var.items():
            self.get_logger().debug(f"df['feats'] = {df['feats'][0]}")
            df['feats'][0].pop("EDA_Sympathetic")
            df['feats'][0].pop("EDA_SympatheticN")
            df['feats'][0].pop("EDA_Autocorrelation")
            self.get_logger().debug(f"k: {k}\ttemp_var[k]: {temp_var[k]['feats'][0].keys()}")
        return temp_var
        

def main():
    """
    Run the FeatureExtractionNode Node.
    """
    rclpy.init(args = None)
    dataProcessNode =  FeatureExtractionNode(
            sync_topic = '/sensor/synched/data',
            window_size = 60,
            process_topic = '/processing/extract_features')    
    executor = rclpy.executors.SingleThreadedExecutor()
    executor.add_node(dataProcessNode)
    try:
        rclpy.spin(dataProcessNode)
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        dataProcessNode.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

    