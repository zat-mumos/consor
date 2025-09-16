import rclpy
import rclpy.duration
from rclpy.logging import LoggingSeverity
from rclpy.node import Node

import sys
from zat_ros2_msgs.msg import EsenseData, EsenseStream
from pylsl import StreamInlet, resolve_byprop
from ament_index_python.packages import get_package_share_directory

import time
from builtin_interfaces.msg import Time

import pylsl

class SensorDataEsense(Node):
    def __init__(self,
                 sensor_topic: str = '/sensor/esense/data', # ROS topic
                 batch_time: float = 1.0
                 ):
        super().__init__('sensor_data_esense')

        # self.get_logger().set_level(LoggingSeverity.DEBUG) # Uncomment this line to debug the code.

        self.i = 0 # counter

        # Declare parameters
        self.declare_parameter('esense_topic', sensor_topic)
        self.declare_parameter('esense_timer', batch_time)
        
        # Get parameter values
        batch_time = self.get_parameter('esense_timer').value
        sensor_topic = self.get_parameter('esense_topic').value

        self.batch_time = batch_time

        # Initialise for LSL communication
        self.stream = resolve_byprop("name", "eSense")
        self.inlet = StreamInlet(self.stream[0])

        self.info = self.inlet.info()


        if not self.stream:
            return
        else:
            self.get_logger().info(f"Stream found: {self.stream[0].name()}")
            self.get_logger().info(f"Stream information (as xml): \n{self.info.as_xml()}\n")

            self.sampling_rate = int(
                self.info.desc().child('Metadata').child_value("Sampling_rate")
                )
            
            self.android_api_level = int(
                self.info.desc().child('Metadata').child_value("Android_API_Level")
                )
            
            self.device_name = self.ascii_to_string(
                self.info.desc().child('Metadata').child_value("Device_Name")
                )
            
            self.manufacturer_name = self.ascii_to_string(
                self.info.desc().child('Metadata').child_value("Manufacturer_Name")
                )
            
            self.unit = self.info.desc().child('Metadata').child_value("Units")
            self.sensor_type = self.info.desc().child('Metadata').child_value("Sensor_Type")

            self.get_logger().info(f"Sensor metadata: \nSamping rate: {self.sampling_rate}\n \
                                   Android API level: {self.android_api_level}\n \
                                    Device name: {self.device_name}\n Manufacturer name: \
                                    {self.manufacturer_name}\n Units: {self.unit}\n \
                                    Sensor type: {self.sensor_type}")

            # Create publisher
            self.publish_sensor_data = self.create_publisher(EsenseStream, sensor_topic, 10)
            
            self.get_logger().info('Publisher created. \nStarting node for eSense sensor data')

            self.timer = self.create_timer(self.batch_time, self.timer_callback)


        
    def timer_callback(self):
        try:
            start_time=self.get_clock().now()
            total_duration = rclpy.duration.Duration(nanoseconds=int(self.batch_time)*1e9)

            main_msg = EsenseStream()
            batch_data = []

            self.i = 0
            while self.get_clock().now() - start_time < total_duration:
                msg = EsenseData()
                sample, timestamp = self.inlet.pull_sample()
                timestamp = self.convert_time(timestamp)

                self.get_logger().debug(f"\nSample data: {sample[0]}\nTimestamp: {timestamp}\n")
                
                msg.sample_data = float(sample[0])
                msg.header.stamp = timestamp
                batch_data.append(msg)
                self.i += 1
            main_msg.header.stamp = timestamp #self.get_clock().now().to_msg()
            main_msg.data = batch_data
            main_msg.sensor_type = self.sensor_type
            main_msg.sample_rate = self.sampling_rate
            main_msg.unit_name = self.unit

            self.publish_sensor_data.publish(main_msg)
            self.get_logger().info(f"--------------------\n{main_msg}\n------------------")
            self.get_logger().info(f'BATCH PUBLISHED\n')

        except KeyboardInterrupt:
            rclpy.shutdown()           


    def convert_time(self, timestamp):
        time = Time()
        time.sec = int(timestamp)
        time.nanosec = int((timestamp%1)*1e9)
        return time

    def ascii_to_string(self, string_data:str):
        data = string_data.strip('[]').split(',')
        data = ''.join(chr(int(ch)) for ch in data)
        return data

def main(args=None):
    rclpy.init(args=args)
    publish_data=SensorDataEsense()
    rclpy.spin(publish_data)

    publish_data.destroy_node()
    rclpy.shutdown()



if __name__ == '__main__':
    main()
