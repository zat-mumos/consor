import rclpy
from rclpy.node import Node

from std_msgs.msg import String

file_path = "/home/user/<path to consor>/consor/datafile.txt"

class PublishData(Node):

    def __init__(self):
        super().__init__('publish_data')
        self.pub_=self.create_publisher(String, 'sensor_data', 10)
        timer_=0.5
        self.timer=self.create_timer(timer_, self.timer_callback)
        self.i=0.0

    def timer_callback(self):
        msg=String()
        file_ = open(file_path, 'r')
        output = file_.read()
        dataValue = str(output)
        msg.data = dataValue
        self.pub_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        self.i += 1
        file_.close()


def main(args=None):
    rclpy.init(args=args)
    publish_data=PublishData()
    rclpy.spin(publish_data)

    publish_data.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
