#!/usr/bin/python3.8

import rclpy
from rclpy.node import Node

import sys
from zat_ros2_msgs.msg import PhysioSensor

class SensorDataEsense(Node):
    def __init__(self, 
                 sensor_topic: str = '/sensor/esense_data', # ROS topic
                 sample_no_: int = 0,
                 sample_data_: float = 1e-5,
                 timer_: float = 0.5
                 ):
        super().__init__('sensor_data_esense') # ROS node
        
        self.get_logger().info('Starting node for eSense sensor data')
        self.i = 0 # counter

        self.declare_parameter('sample_no', sample_no_)
        self.declare_parameter('sample_data', sample_data_)
        self.declare_parameter('timer', timer_)

        self.sample_no_ = sample_no_
        self.sample_data_ = sample_data_

        self.publish_sensor_data_ = self.create_publisher(PhysioSensor, sensor_topic, 10)
        self.timer = self.create_timer(timer_, self.timer_callback)
        

    def timer_callback(self):
        try:
            msg=PhysioSensor()
            lines=sys.stdin.readline().strip()
            dataValue = str(lines)
            print(lines)
            self.sample_no_ = dataValue.split(",")[0]
            # print('sno: ', self.sample_no_)
            if self.sample_no_.isnumeric():
                self.sample_no_ = int(self.sample_no_)
                print('Sample no: ', self.sample_no_)
                self.sample_data_ = dataValue.split(",")[1]
                self.sample_data_ = float(self.sample_data_)
                print('Sample data: ', self.sample_data_)
                msg.sample_no = self.sample_no_
                msg.sample_data = self.sample_data_
                self.publish_sensor_data_.publish(msg)
                self.get_logger().info(f'Publishing: {msg}')
                self.i += 1


        except KeyboardInterrupt:
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    publish_data=SensorDataEsense()
    rclpy.spin(publish_data)

    publish_data.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
