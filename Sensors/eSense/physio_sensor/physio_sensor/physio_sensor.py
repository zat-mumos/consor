#!/usr/bin/python3.10

import rclpy
import rclpy.duration
from rclpy.node import Node

import sys
from zat_ros2_msgs.msg import PhysioSensor, Esense
import subprocess
import os
from ament_index_python.packages import get_package_share_directory

class SensorDataEsense(Node):
    def __init__(self, 
                 bash_script_path=None, 
                 sensor_topic: str = '/sensor/esense/data', # ROS topic
                 sample_no: int = 0,
                 sample_data: float = 1e-5,
                 buffer: float = 1.0
                 ):
        super().__init__('sensor_data_esense') # ROS node
        

        if bash_script_path==None:
            package_name = 'physio_sensor'
            bash_script_path = os.path.join(get_package_share_directory(package_name), 'scripts', 'main.sh')

        self.bash_script_path = bash_script_path
        self.get_logger().info(f'Bash script path: {self.bash_script_path}')

        self.i = 0 # counter

        self.declare_parameter('esense_topic', sensor_topic)
        self.declare_parameter('esense_bash_script_path', bash_script_path)
        self.declare_parameter('esense_timer', buffer)
        
        self.batch_time = buffer

        self.sample_no = sample_no
        self.sample_data = sample_data

        self.publish_sensor_data_ = self.create_publisher(PhysioSensor, sensor_topic, 10)
        
        # https://stackoverflow.com/questions/13332268/how-to-use-subprocess-command-with-pipes
        # Start a subprocess to run the bash script
        self.process = subprocess.Popen(
            self.bash_script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        self.get_logger().info('Starting node for eSense sensor data')

        self.timer = self.create_timer(buffer, self.timer_callback)
        

    def timer_callback(self):
        try:
            start_time=self.get_clock().now()
            total_duration = rclpy.duration.Duration(nanoseconds=int(self.batch_time)*1e9)

            batch_msg = PhysioSensor()
            batch_data = []

            self.i = 0
            while self.get_clock().now() - start_time < total_duration:
                msg = Esense()
                lines = self.process.stdout.readline().strip()
                # lines = sys.stdin.readline().strip()
                dataValue = str(lines)
                self.get_logger().info(f'Log: {lines}')
                print(lines)
                self.sample_no = dataValue.split(",")[0]
                # print('sno: ', self.sample_no)
                if self.sample_no.isnumeric():
                    self.sample_no = int(self.sample_no)
                    print('Sample no: ', self.sample_no)
                    self.sample_data = dataValue.split(",")[1]
                    self.sample_data = float(self.sample_data)
                    print('Sample data: ', self.sample_data)
                    # msg.sample_no = self.sample_no
                    msg.sample_data = self.sample_data
                    msg.header.stamp = self.get_clock().now().to_msg()
                    # self.publish_sensor_data_.publish(msg)
                    self.get_logger().info(f'{self.i}: Data: {msg}')
                    
                    batch_data.append(msg)
                    self.i += 1
            batch_msg.header.stamp = self.get_clock().now().to_msg()
            batch_msg.data = batch_data
            self.publish_sensor_data_.publish(batch_msg)
            self.get_logger().info(f'BATCH PUBLISHED-------------')

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
