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
A ROS2 node that gets data from the Esense sensor and publishes it to a ROS topic using Lab Streaming Layer (LSL).

Subscribers:
    None

Publishers:
    /sensor/esense/data: A ROS2 topic to publish acquired eSense data

Parameters:
    - esense_topic (str, default: '/sensor/esense/data')
    - esense_timer (float, default: 1.0)

Description:
    This code connects to the eSense android application using Lab Streaming Layer (LSL).  The data received from the sensor is published to the respective ROS2 topic

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
import rclpy
import rclpy.duration
from rclpy.logging import LoggingSeverity
from rclpy.node import Node
import rclpy.time
from zat_ros2_msgs.msg import Esense, EsenseStream
import traceback
from builtin_interfaces.msg import Time
from esense_pkg.esense_lsl import EsenseLslReceiver

class SensorDataEsense(Node):
    """
    Acquire and publish sensor data from Esense sensors using LSL.
    """
    def __init__(self,
                 sensor: EsenseLslReceiver,
                 sensor_topic: str = '/sensor/esense/data',
                 batch_time: float = 1.0
                 ):
        """
        Initialise the SensorDataEsense class.

        Arguments:
        EsenseLslReceiver sensor: Object of class EsenseLslReceiver
        str sensor_topic: ROS topic
        float batch_time: Determines the duration for which the data is collected before publishing
        """
        super().__init__('sensor_data_esense')

        self.get_logger().set_level(LoggingSeverity.DEBUG) # Uncomment this line to debug the code.

        self.i = 0 # counter

        # Declare parameters
        self.declare_parameter('esense_topic', sensor_topic)
        self.declare_parameter('esense_timer', batch_time)
        
        # Get parameter values
        batch_time = self.get_parameter('esense_timer').value
        sensor_topic = self.get_parameter('esense_topic').value

        self.batch_time = batch_time
        self._esense = sensor

        if not self._esense.stream:
            return
        else:
            self.get_logger().info(f"Stream found: {self._esense.stream[0].name()}")
            info = self._esense.get_stream_info()
            self.get_logger().info(f"Stream information (as xml): \n{info.as_xml()}\n")
            self.metadata = self._esense.get_metadata_value()
            self.get_logger().info(f"Sensor metadata: {type(self.metadata)}\n{self.metadata}")
            self.get_logger().info(f"info:\t{type(info)}\n{info}")
            self.get_logger().info(f"batch time:\t{self.batch_time}s")
            # Create publisher
            self.publish_sensor_data = self.create_publisher(EsenseStream, sensor_topic, 10)
            self.get_logger().info('Publisher created. \nStarting node for eSense sensor data')

    def acquire_and_publish_data(self, start_time: rclpy.time.Time, total_duration: rclpy.duration.Duration):
        """A callback function that connects to the sensor, acquires data from it and then publishes this information to a ROS topic at regular intervals.
        Arguments:
        rclpy.time.Time start_time: The time at which the data acquisition is started
        rclpy.duration.Duration total_duration:  The duration for which the data should be acquired
        """
        self.get_logger().debug(f"acquire_and_publish_data:\nstart_time:\t{type(start_time)}\t{start_time}\ntotal_duration:\t{type(total_duration)}\t{total_duration}")
        main_msg = EsenseStream()
        batch_data, timestamp = self.acquire_data_for_specific_duration(start_time, total_duration)
        main_msg.header.stamp = timestamp
        main_msg.data = batch_data
        main_msg.sensor_type = self.metadata['sensor_type']
        main_msg.sample_rate = self.metadata['sampling_rate']
        main_msg.unit_name = self.metadata['units']
        self.publish_sensor_data.publish(main_msg)
        self.get_logger().debug(f"--------------------\n{main_msg}\n------------------")
        self.get_logger().info(f'Batch Published\n')

    def acquire_data_for_specific_duration(self, start_time: rclpy.time.Time, total_duration: rclpy.duration.Duration) -> tuple[list, Time]:
        """Data is acquired for a duration specified by the argument 'total_duration' 
        Arguments:
        rclpy.time.Time start_time: The start time for data acquisition
        rclpy.duration.Duration total_duration: The duration for which the data should be acquired

        Returns:
        list batched_data: The data for the entire duration specified by 'total_duration'
        Time timestamp: The timestamp of the finally acquired data
        """
        batched_data = []
        self.i = 0
        while self.get_clock().now() - start_time < total_duration:
            batched_data, timestamp = self.acquire_data(batched_data)
            self.i += 1
        return batched_data, timestamp
    
    def acquire_data(self, data: list = []) -> tuple[list, Time]:
        """Acquire sensor data
        Arguments:
        list data: This is the data from previous batches. Default is an empty list.

        Returns:
        list data: The batched data (including data from previous batches and newly acquired)
        Time timestamp: The timestamp of the newly acquired data
        """
        self.get_logger().debug(f"acquire data:\ninitial batch_data:\n{data}")
        msg = Esense()
        sample_timestamp_array = self._esense.get_sample()
        self.get_logger().debug(f"Data received: {sample_timestamp_array}")
        seconds = int(sample_timestamp_array[0])
        nanoseconds = int(sample_timestamp_array[1])
        timestamp = self.convert_time(seconds, nanoseconds)
        self.get_logger().debug(f"\nSample no: {sample_timestamp_array[3]}: Sample data: {sample_timestamp_array[2]}\nTimestamp: {timestamp} ; {seconds} {nanoseconds}\n")
        sample = sample_timestamp_array[2]
        msg.sample_data = float(sample)
        msg.header.stamp = timestamp
        data.append(msg)
        self.get_logger().debug(f"batch_data:\n{data}\ntimestamp:\n{timestamp}\n")
        return data, timestamp
    
    def convert_time(self, seconds: int, nanos: int) -> Time:
        """
        Converts seconds and nanoseconds to builtin_interfaces.msg.Time.

        Arguments:
        int seconds: Seconds of a timestamp
        int nanos: Nanoseconds of a timestamp

        Returns:
        builtin_interfaces.msg.Time time: Timestamp as builtin_interfaces.msg.Time
        """
        self.get_logger().debug(f"convert_time:\nseconds:\n{seconds}\nnanosec:\n{nanos}")
        time = Time()
        time.sec = int(seconds)
        time.nanosec = int(nanos)
        self.get_logger().debug(f"time:\n{time}\n")
        return time
    
    def run(self):
        """Runs the node continuously in a while loop until manually exited or any exception occurs."""
        try:
            self.get_logger().debug("Starting run function")
            while rclpy.ok():
                start_time = self.get_clock().now()
                total_duration = rclpy.duration.Duration(nanoseconds = int(self.batch_time)*1e9)
                self.get_logger().debug(f"start time:\t{start_time}\ttotal duration:\t{total_duration}")
                self.acquire_and_publish_data(start_time, total_duration)
        except KeyboardInterrupt:
            self.get_logger().info('Session in keyboard interrupt')
        except Exception as e:
            self.get_logger().info(f'Session in exception: {traceback.format_exc()}')


def main(args = None):
    """Run the SensorDataEsense Node."""
    esense_lsl = EsenseLslReceiver()
    rclpy.init(args = args)
    sensor_node = SensorDataEsense(esense_lsl)
    sensor_node.get_logger().debug(f"Node has been initialised")
    try:
        sensor_node.run()
    finally:
        sensor_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
