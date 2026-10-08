#!/usr/bin/env python3
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
A ROS node that combines different EmotiBit modalities into a single ROS2 topic.

Subscribers:
    One subscriber per stream or ROS2 topic.

Publishers:
    A single publisher that publishes EmotiBit data from all streams (sensor/emotibit/data).

Parameters:
    - timer_period (float, default: 0.8)
    - emotibit_accelerometer_topic (str, /emotibit/acc)
    - emotibit_gyroscope_topic (str, /emotibit/gyro)
    - emotibit_magnetometer_topic (str, /emotibit/mag)
    - emotibit_ppg_topic (str, /emotibit/ppg)
    - emotibit_eda_topic (str, /emotibit/eda)
    - emotibit_temperature_topic (str, /emotibit/temp)
    - emotibit_synch_topic (str, sensor/emotibit/data)

Descriptions:
    This code subscribes to EmotiBit ROS2 topics. Each EmotiBit stream data is published in a separate ROS2 topic.
    Once data from all EmotiBit streams are obtained, it is published to a single ROS2 topic.

Author:
    Oviya Rajavel <oviya.rajavel@smail.inf.h-brs.de>
    Michal Stolarz <michal.stolarz@h-brs.de>
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""

import rclpy
from rclpy.node import Node
from zat_ros2_msgs.msg import EmotibitMsg, EmotibitSynchData

class EmotibitStreamsCombine(Node):
    """
    Combine data from different modalities and publish to a ROS topic.
    """
    def __init__(
            self, 
            timer_period: float = 0.8,
            emotibit_accelerometer_topic: str = '/emotibit/acc',
            emotibit_gyroscope_topic: str = '/emotibit/gyro',
            emotibit_magnetometer_topic: str = '/emotibit/mag',
            emotibit_ppg_topic: str = '/emotibit/ppg',
            emotibit_eda_topic: str = '/emotibit/eda',
            emotibit_temperature_topic: str = '/emotibit/temp',
            emotibit_synch_topic: str = 'sensor/emotibit/data'):
        """
        Initialise the EmotibitStreamsCombine class.
        
        Arguments:
        float timer_period: Determines the intervals at which the callback function is called
        str emotibit_accelerometer_topic: Name of the ROS2 topic publishing accelerometer data
        str emotibit_gyroscope_topic: Name of the ROS2 topic publishing gyroscope data
        str emotibit_magnetometer_topic: Name of the ROS2 topic publishing magnetometer data
        str emotibit_ppg_topic: Name of the ROS2 topic publishing ppg data
        str emotibit_eda_topic: Name of the ROS2 topic publishing eda data
        str emotibit_temperature_topic: Name of the ROS2 topic publishing temperature data
        str emotibit_synch_topic: ROS2 topic for publishing combined EmotiBit data
        """
        super().__init__('emotibit_streams_combine')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('timer_period', timer_period),
                ('emotibit_accelerometer_topic', emotibit_accelerometer_topic),
                ('emotibit_gyroscope_topic', emotibit_gyroscope_topic),
                ('emotibit_magnetometer_topic', emotibit_magnetometer_topic),
                ('emotibit_ppg_topic', emotibit_ppg_topic),
                ('emotibit_eda_topic', emotibit_eda_topic),
                ('emotibit_temperature_topic', emotibit_temperature_topic),
                ('emotibit_synch_topic', emotibit_synch_topic)
            ])
        
        # Get parameter values
        timer_period = self.get_parameter('timer_period').value
        emotibit_accelerometer_topic = self.get_parameter('emotibit_accelerometer_topic').value
        emotibit_gyroscope_topic = self.get_parameter('emotibit_gyroscope_topic').value
        emotibit_magnetometer_topic = self.get_parameter('emotibit_magnetometer_topic').value
        emotibit_ppg_topic = self.get_parameter('emotibit_ppg_topic').value
        emotibit_eda_topic = self.get_parameter('emotibit_eda_topic').value
        emotibit_temperature_topic = self.get_parameter('emotibit_temperature_topic').value
        emotibit_synch_topic = self.get_parameter('emotibit_synch_topic').value
        
        self._timer_period = timer_period
        self._emotibit_streams = ["accelerometer", "gyroscope", "magnetometer", "ppg", "eda", "temperature"]

        self._emotibit_accelerometer_subscriber = self.create_subscription(EmotibitMsg, 
                                                                        emotibit_accelerometer_topic, 
                                                                        self._emotibit_accelerometer_callback, 
                                                                        10)

    
        self._emotibit_gyroscope_subscriber = self.create_subscription(EmotibitMsg,
                                                                    emotibit_gyroscope_topic, 
                                                                    self._emotibit_gyroscope_callback, 
                                                                    10)
    
        self._emotibit_magnetometer_subscriber = self.create_subscription(EmotibitMsg, 
                                                                    emotibit_magnetometer_topic, 
                                                                    self._emotibit_magnetometer_callback, 
                                                                    10)
    
        self._emotibit_ppg_subscriber = self.create_subscription(EmotibitMsg, 
                                                            emotibit_ppg_topic, 
                                                            self._emotibit_ppg_callback, 
                                                            10)
    
        self._emotibit_eda_subscriber = self.create_subscription(EmotibitMsg, 
                                                            emotibit_eda_topic, 
                                                            self._emotibit_eda_callback, 
                                                            10)
    
        self._emotibit_temperature_subscriber = self.create_subscription(EmotibitMsg, 
                                                                    emotibit_temperature_topic, 
                                                                    self._emotibit_temperature_callback, 
                                                                    10)
    
        self._emotibit_synch_publisher = self.create_publisher(EmotibitSynchData, emotibit_synch_topic, 10)

        self._emotibit_dict = {"accelerometer": None, "gyroscope": None, "magnetometer": None, "ppg": None, "eda": None, "temperature": None}

        self.timer1 = self.create_timer(self._timer_period, self._emotibit_synch_callback)

    # Since each modality in emotibit has its own ros2 topic, when new msgs are received emotibit_sync() is called
    def _emotibit_accelerometer_callback(self, msg: EmotibitMsg):
        """
        A callback function for EmotiBit sensor that is executed whenever a new msg from ROS2 topic publishing EmotiBit accelerometer data is received.
        
        Arguments:
        EmotibitMsg msg: The message received from /emotibit/acc topic.
        """
        self._emotibit_dict["accelerometer"] = msg

    def _emotibit_gyroscope_callback(self, msg: EmotibitMsg):
        """
        A callback function for EmotiBit sensor that is executed whenever a new msg from ROS2 topic publishing EmotiBit gyroscope data is received.
        
        Arguments:
        EmotibitMsg msg: The message received from /emotibit/gyro topic.
        """
        self._emotibit_dict["gyroscope"] = msg

    def _emotibit_magnetometer_callback(self, msg: EmotibitMsg):
        """
        A callback function for EmotiBit sensor that is executed whenever a new msg from ROS2 topic publishing EmotiBit magnetometer data is received.
        
        Arguments:
        EmotibitMsg msg: The message received from /emotibit/mag topic.
        """
        self._emotibit_dict["magnetometer"] = msg

    def _emotibit_ppg_callback(self, msg: EmotibitMsg):
        """
        A callback function for EmotiBit sensor that is executed whenever a new msg from ROS2 topic publishing EmotiBit PPG data is received.
        
        Arguments:
        EmotibitMsg msg: The message received from /emotibit/ppg topic.
        """
        self._emotibit_dict["ppg"] = msg  

    def _emotibit_eda_callback(self, msg: EmotibitMsg):
        """
        A callback function for EmotiBit sensor that is executed whenever a new msg from ROS2 topic publishing EmotiBit EDA data is received.
        
        Arguments:
        EmotibitMsg msg: The message received from /emotibit/eda topic.
        """
        self._emotibit_dict["eda"] = msg 

    def _emotibit_temperature_callback(self, msg: EmotibitMsg):
        """
        A callback function for EmotiBit sensor that is executed whenever a new msg from ROS2 topic publishing EmotiBit temperature data is received.
        
        Arguments:
        EmotibitMsg msg: The message received from /emotibit/temp topic.
        """
        self._emotibit_dict["temperature"] = msg      

    def _emotibit_synch_callback(self):
        """
        This function combines data from all modalities from emotibit that is published as separate topics into a single msg
        """
        emotibit_synch_data = EmotibitSynchData()

        for stream in self._emotibit_dict:
            if self._emotibit_dict[stream] is None:
                self.get_logger().warn("Emotibit data not received")
                return

            setattr(emotibit_synch_data, stream, [self._emotibit_dict[stream]])
        
        self.get_logger().debug(f"emotibit sync data: {emotibit_synch_data}\n\n\n")
        self._emotibit_synch_publisher.publish(emotibit_synch_data)

        self.get_logger().info("Emotibit data received")
        self._emotibit_dict = {"accelerometer": None, 
                               "gyroscope": None, 
                               "magnetometer": None, 
                               "ppg": None, 
                               "eda": None, 
                               "temperature": None}                            
    
def main():
    """Run the EmotibitStreamsCombine Node"""
    rclpy.init(args= None)
    emotibit_data =  EmotibitStreamsCombine(
        emotibit_accelerometer_topic = '/emotibit/acc',
        emotibit_gyroscope_topic= '/emotibit/gyro',
        emotibit_magnetometer_topic = '/emotibit/mag',
        emotibit_ppg_topic = '/emotibit/ppg',
        emotibit_eda_topic = '/emotibit/eda',
        emotibit_temperature_topic= '/emotibit/temp',
        emotibit_synch_topic = 'sensor/emotibit/data')
    rclpy.spin(emotibit_data)

    emotibit_data.destroy_node()
    rclpy.shutdown()
     
if __name__ == '__main__':
    main()