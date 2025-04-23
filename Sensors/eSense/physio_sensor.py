#!/usr/bin/python3.8

import rclpy
from rclpy.node import Node

import sys
from zat_ros2_msgs.msg import PhysioSensor
import subprocess

class SensorDataEsense(Node):
    def __init__(self, 
                 bash_script_path="/home/user/<path to consor>/consor/Sensors/eSense/main.sh", 
                 sensor_topic: str = '/sensor/esense_data', # ROS topic
                 sample_no: int = 0,
                 sample_data: float = 1e-5,
                 timer: float = 0.5
                 ):
        super().__init__('sensor_data_esense') # ROS node
        
        self.i = 0 # counter

        self.declare_parameter('bash_script_path', bash_script_path)
        self.declare_parameter('timer', timer)

        self.sample_no = sample_no
        self.sample_data = sample_data
        self.bash_script_path = bash_script_path

        self.publish_sensor_data_ = self.create_publisher(PhysioSensor, sensor_topic, 10)
        self.get_logger().info('Starting node for eSense sensor data')
        
        # https://stackoverflow.com/questions/13332268/how-to-use-subprocess-command-with-pipes
        # Start a subprocess to run the bash script
        self.process = subprocess.Popen(
            self.bash_script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        self.timer = self.create_timer(timer, self.timer_callback)
        

    def timer_callback(self):
        try:
            msg = PhysioSensor()
            lines = self.process.stdout.readline().strip()
            dataValue = str(lines)
            print(lines)
            self.sample_no = dataValue.split(",")[0]
            # print('sno: ', self.sample_no_)
            if self.sample_no.isnumeric():
                self.sample_no = int(self.sample_no)
                print('Sample no: ', self.sample_no)
                self.sample_data = dataValue.split(",")[1]
                self.sample_data = float(self.sample_data)
                print('Sample data: ', self.sample_data)
                msg.sample_no = self.sample_no
                msg.sample_data = self.sample_data
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
