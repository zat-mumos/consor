import rclpy
from rclpy.node import Node

from std_msgs.msg import String
import subprocess
from subprocess import run
import os
import sys

class PublishData(Node):

    def __init__(self):
        super().__init__('publish_data')
        self.pub_=self.create_publisher(String, 'sensor_data', 10)
        timer_=0.5
        self.timer=self.create_timer(timer_, self.timer_callback)
        self.i=0.0

    def timer_callback(self):
        msg=String()
        output = sys.stdout.readlines()
        dataValue = str(output)
        msg.data = dataValue#'Hello %d'
        self.pub_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        self.i += 1
    
def main(args=None):
    rclpy.init(args=args)
    publish_data=PublishData()
    rclpy.spin(publish_data)

    publish_data.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
