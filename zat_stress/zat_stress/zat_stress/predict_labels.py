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
A ROS node that infers labels (stressed or not stressed) from the extracted features and publishes it to a ROS topic.

Subscribers:
    /processing/extract_features: Subscriber for extracted features

Publishers:
    /processing/labels: Publishes inferred labels

Parameters:
    feature_topic (str, default: /processing/extract_features)
    process_topic  (str, default: /processing/labels)
    rel_loc_scaler (str, default: vendor/models/RF/rf_scaler.save)
    rel_loc_model (str, default: vendor/models/RF/rf_uq_model_60.pkl)
    use_cpu (bool, default: True)
    use_cnn (bool, default: False)
    input_dim (int, default: 16)

Description:
    This code subscribes to extracted features, infers labels based on the extracted features and publishes to the ROS topic.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>

NOTE: Some parts of the code are from the files stress_inference_node.py & stress_inference_rf.py within the vendor repository (https://github.com/prachi0711/Stress-Management-using-Physiological-Signals-and-conversational-agents/blob/main/ros_node).
"""
import datetime
from decimal import Decimal
from ament_index_python.packages import get_package_share_directory
import os
import joblib
import torch
import rclpy
from rclpy.node import Node
from builtin_interfaces.msg import Time 
import rclpy.time
from std_msgs.msg import Float32MultiArray, String
import threading
from vendor.CNN_UQ import Enhanced1DCNN, mc_dropout_predict # can delete Enhanced1DCNN if saved_model contains the entire model not just the state_dict()
from scipy.stats import entropy
import rclpy.executors
import numpy as np
import pandas as pd
from rclpy.logging import LoggingSeverity
from queue import Queue, Empty
from collections import deque
import logging

class InferenceNode(Node):
    """
    Infer labels and publish to a ROS node.
    """
    def __init__(
            self,
            package_name: str = 'zat_stress',
            rel_loc_scaler: str = 'vendor/models/RF/rf_scaler.save', #cnn_scaler.save',
            rel_loc_model: str = 'vendor/models/RF/rf_uq_model_60.pkl', #cnn_uq_model_60.pt',
            feature_topic: str = '/processing/extract_features',
            use_cnn: bool = False, # True
            use_cpu: bool = True,
            process_topic: str = '/processing/labels',
            input_dim: int = 16):
        """
        Initialize the InferenceNode class.

        Arguments:
        str package_name: Name of the package
        str rel_loc_scaler: Relative location of the scalar
        str rel_loc_model: Relative location of the model
        str feature_topic: ROS topic that publishes extracted features
        str process_topic: ROS topic to which the labels will be published
        bool use_cnn: If True, then CNN is used (there are steps within code that is specific to CNNs)
        bool use_cpu: If True, the device used is CPU else CUDA is used
        int input_dim: Input features for Enhanced1DCNN.  This is added as a parameter here since input_features is an argument in vendor/CNN_UQ.py.
        """
        super().__init__('inference_node')

        self.i = 0 # counter
        self.queue = deque()
        self.declare_parameters(
               namespace = '',
               parameters = [
                   ('process_topic', process_topic),
                   ('feature_topic', feature_topic),
                   ('rel_loc_scaler', rel_loc_scaler),
                   ('rel_loc_model', rel_loc_model),
                   ('use_cpu', use_cpu),
                   ('use_cnn', use_cnn),
                   ('input_dim', input_dim)
               ])
        # Get parameter values
        feature_topic = self.get_parameter('feature_topic').value
        process_topic = self.get_parameter('process_topic').value
        rel_loc_scaler = self.get_parameter('rel_loc_scaler').value
        path_saved_model = self.get_parameter('rel_loc_model').value
        use_cpu = self.get_parameter('use_cpu').value
        use_cnn = self.get_parameter('use_cnn').value
        input_dim = self.get_parameter('input_dim').value

        path_scaler = os.path.join(get_package_share_directory(package_name), rel_loc_scaler)
        self.get_logger().info(f"path scaler: {path_scaler}")
        path_saved_model = os.path.join(get_package_share_directory(package_name), rel_loc_model)
        self.get_logger().info(f"path model: {path_saved_model}")

        self._extracted_features_subscriber = self.create_subscription(Float32MultiArray, feature_topic, self._feature_subscriber_callback, 10)
        self._label_publisher = self.create_publisher(String, process_topic, 10)
        
        self.set_queue_timestamps = set()
        self.lock = threading.Lock()
        self.scaler = None
        self.model = None
        self.use_cnn = use_cnn
        device = torch.device('cpu' if use_cpu else 'cuda') 

        self.get_logger().debug(f"Check scaler path: {path_scaler}\t{os.path.exists(path_scaler)}\t{os.path.getsize(path_scaler)}")
        self.get_logger().debug(f"Check model path: {path_saved_model}\t{os.path.exists(path_saved_model)}\t{os.path.getsize(path_saved_model)}")       
        self.scaler = joblib.load(path_scaler)
        if self.scaler is not None:
            if self.use_cnn:
                self.model = Enhanced1DCNN(input_features = input_dim)
                self.model.load_state_dict(torch.load(path_saved_model, map_location = device))
                self.model.eval()
            else:
                self.model = joblib.load(path_saved_model)
        # self.cols = ['eda_mean', 'eda_std', 'eda_min', 'eda_max', 'eda_range', 'eda_skewness', 'eda_kurtosis', 'SCR_Peaks_N', 'SCR_Peaks_Amplitude_Mean', 
        #              'EDA_Tonic_SD']
        timer_period = 1.0
        self.get_logger().info("Starting node for label prediction")
        timer = self.create_timer(timer_period, self._timer_callback)
        
    def _feature_subscriber_callback(self, msg: Float32MultiArray):
        """
        A callback function for extracted features that is executed each time a new message is received.

        Arguments:
        Float32MultiArray msg: The message received from /processing/extract_features
        """
        self.get_logger().debug("In subscriber")
        try:
            with self.lock:
                self.queue.append(msg)
                self.get_logger().info("Msg added to queue")
                self.get_logger().debug(f"msg: {msg}\n")
        except Exception as e:
            self.get_logger().warn(f"Warning: {e}\nQueue full & dropping message: {msg}")

    def _timer_callback(self):
        """
        A callback function that subscribes to the extracted features and publishes inferred labels (1: stressed; 0: not stressed) to a ROS topic at regular intervals.
        """
        self.get_logger().debug(f"In Timer callback")
        with self.lock:
            while len(self.queue) > 0:
                self.get_logger().debug(f"Queue is not empty. Length of queue: {len(self.queue)}")
                msg = self.queue.popleft()
                data = np.array(msg.data)
                self.get_logger().debug(f"Shape of msg.data received: {data.shape}")
                # Parts of code adapted from vendor repository - stress_inference_node.py & stress_inference_rf.py
                features = data.reshape(1, -1)
                self.get_logger().debug(f"Shape of features after reshaping: {features.shape}")
                features_scaled = self.scaler.transform(features)
                if self.use_cnn:
                    input_tensor = torch.tensor(features_scaled, dtype = torch.float32).unsqueeze(1)
                    # MC dropout prediction
                    mean_probs, entropies = mc_dropout_predict(self.model, input_tensor, num_samples=50)
                    pred_label = mean_probs.argmax(axis = 1).item()
                    entropy_val = entropies[0]
                else:
                    probs = self.model.predict_proba(features_scaled)[0]
                    pred_label = np.argmax(probs)
                    entropy_val = entropy(probs)
                ros_time = self.get_clock().now().to_msg()
                timestamp = datetime.datetime.fromtimestamp(ros_time.sec + ros_time.nanosec + 1e-9)
                msg_out = String()
                msg_out.data = f"Predicted label: {pred_label},\tEntropy: {entropy_val:.4f}"
                self.get_logger().debug(f"Message: {msg_out}")
                self._label_publisher.publish(msg_out)
                self.get_logger().info("Message Published \n")

    def convert_time(self, timestamp: Time, bool_to_s: bool = True):
        """
        Converts timestamp from builtin_interfaces.Time to Decimal datatype.

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
    

def main():
    """
    Run the InferenceNode Node.
    """
    rclpy.init(args = None)
    dataProcessNode =  InferenceNode()
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

    