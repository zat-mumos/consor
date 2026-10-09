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
A ROS node that publishes responses based on the inferred labels (0: not stressed; 1: stressed).

Subscribers:
    /processing/labels: Subscriber for inferred or predicted labels

Publishers:
    /processing/responses: Publishes responses

Parameters:
    process_topic (str, default: /processing/responses)
    feature_topic  (str, default: /processing/labels)

Description:
    This code subscribes to a ROS topic that publishes inferred labels.  Based on these labels, responses are publishes to another ROS topic.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>

NOTE: Some parts of the code are from the files stress_inference_node.py & stress_inference_rf.py within the vendor repository (https://github.com/prachi0711/Stress-Management-using-Physiological-Signals-and-conversational-agents/blob/main/ros_node)
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
import time
import pickle
from vendor.dialogue_manager import DialogueManager
from scipy.stats import entropy
import rclpy.executors
import numpy as np
import pandas as pd
from rclpy.logging import LoggingSeverity
from queue import Queue, Empty
from collections import deque
import logging

class FeedbackNode(Node):
    """
    Publish feedback or responses to a ROS topic.
    """
    def __init__(
            self,
            feature_topic: str = '/processing/labels',
            process_topic: str = '/processing/responses',):
        """
        Initialize the FeebackNode class.

        Arguments:
        str feature_topic: The topic that publishes the inferred labels
        str process_topic: The topic that will publish the feedback or responses
        """
        super().__init__('label_prediction_node')
        # self.get_logger().set_level(LoggingSeverity.DEBUG) # Uncomment this line to print debug statements within the code.

        self.i = 0 # counter
        self.queue = deque()
        self.declare_parameters(
               namespace = '',
               parameters = [
                   ('process_topic', process_topic),
                   ('feature_topic', feature_topic),
               ])
        # Get parameter values
        label_topic = self.get_parameter('feature_topic').value
        process_topic = self.get_parameter('process_topic').value
        self._labels_subscriber = self.create_subscription(String, label_topic, self._labels_subscriber_callback, 10)
        self._response_publisher = self.create_publisher(String, process_topic, 10)
        self.obj_DialogueManager = DialogueManager()
        self.set_queue_timestamps = set()
        self.lock = threading.Lock()
        timer_period = 1.0
        self.get_logger().info("Starting node for publishing responses")
        timer = self.create_timer(timer_period, self._timer_callback)
        
    def _labels_subscriber_callback(self, msg: String):
        """
        A callback function for inferred or predicted labels that is executed each time a new message is received.
        """
        try:
            with self.lock:
                self.queue.append(msg)
                self.get_logger().info("Msg added to queue")
                self.get_logger().debug(f"msg: {msg}\n")
        except Exception as e:
            self.get_logger().warn(f"Warning: {e}\nQueue full & dropping message: {msg}")

    def _timer_callback(self):
        """
        A callback function that subscribes to the inferred labels and publishes feedback or responses to a ROS topic at regular intervals.
        """
        self.get_logger().debug(f"In Timer callback")
        with self.lock:
            while len(self.queue) > 0:
                self.get_logger().debug(f"Queue is not empty. Length of queue: {len(self.queue)}")
                msg = self.queue.popleft()
                # Split msg into predicted label and entropy
                res = [string for string in msg.data.split(',\t')]
                self.get_logger().debug(f"res: {res}")
                # separate results of labels & entropy
                val_label = self.split_string_return_value(res[0], ":")
                val_entropy = self.split_string_return_value(res[1], ":")
                self.get_logger().debug(f"pred label: {val_label}\tentropy: {val_entropy}")
                # Parts of code adapted from vendor repositoy - stress_inference_node.py & stress_inference_rf.py
                response = self.obj_DialogueManager.get_response(user_id = 0, entropy_val = val_entropy, pred_label = val_label)                
                # self.get_logger().debug(f"response: {response}")
                msg_out = String()
                msg_out.data = f"response: {response}"
                self.get_logger().debug(f"Message: {msg_out}")
                self._response_publisher.publish(msg_out)
                self.get_logger().info("Message Published\n")

    def split_string_return_value(self, text: str, sep: str = ":"):
        """
        Returns value from text. The text variable includes information such as 'Predicted label: 0'. This function returns the value (i.e., 0).

        Arguments:
        str text: This text contains values that needs to be extracted
        str sep: Separator that helps split the text

        Returns:
        Union[int, float]: A float or integer value
        """
        list_text = text.split(sep)
        self.get_logger().debug(f"list_text: {list_text}")
        if list_text[0] == 'Predicted label':
            val = int(list_text[1])
        else:
            val = float(list_text[1])
        return val
        
    def convert_time(self, timestamp: Time, bool_to_s: bool = True):
        """
        Converts timestamp from builtin_interfaces.Time to Decimal.

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
    Run the FeedbackNode Node.
    """
    rclpy.init(args = None)
    dataProcessNode =  FeedbackNode()
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
