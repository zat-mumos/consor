import os
from ament_index_python.packages import get_package_share_directory

import rclpy
import rclpy.duration
from rclpy.node import Node

from zat_ros2_msgs.msg import Emotibit, Temp, Eda
from builtin_interfaces.msg import Time

from pylsl import resolve_byprop, StreamInlet


class SensorDataEmotibit(Node):
    def __init__(self,
                 sensor_topic: str = '/sensor/emotibit/data',
                 type_stream: list = ["default1", "default2"],
                 buffer: float = 1.0
                 ):
        super().__init__('sensor_data_emotibit')

        self.i = 0 # counter
        
        # Declare parameters
        self.declare_parameter('emotibit_topic', sensor_topic)
        self.declare_parameter('emotibit_stream_type', type_stream)
        self.declare_parameter('emotibit_timer', buffer)
        
        # Get parameter values
        buffer = self.get_parameter('emotibit_timer').value
        type_stream = self.get_parameter('emotibit_stream_type').value
        sensor_topic = self.get_parameter('emotibit_topic').value

        self.batch_time = buffer
        self.stream_type = type_stream

        self.publish_emotibit_data_ = self.create_publisher(Emotibit, sensor_topic, 10)

        self.get_logger().info(f'Starting node for emotibit sensor data (Type: {type_stream})')
        self.timer = self.create_timer(buffer, self.timer_callback)

    
    def timer_callback(self):
        try:
            main_msg = Emotibit()
            dict_main_msg_vars = {"Temperature":"temp", "EDA":"eda"}

            for i in range(len(self.stream_type)):
                var_a = self.get_sensor_data(self.stream_type[i])
                self.get_logger().info(f"Var A: \n{var_a}\n Stream:{self.stream_type[i], type(dict_main_msg_vars[self.stream_type[i]])}")
                setattr(main_msg, f"data_{dict_main_msg_vars[self.stream_type[i]]}", [var_a])    

            main_msg.header.stamp = self.get_clock().now().to_msg()

            self.publish_emotibit_data_.publish(main_msg)
            self.get_logger().info(f"{self.i}. Data Published: \n{main_msg}\n---------------------------")
            
            self.i+=1

        except KeyboardInterrupt:
            rclpy.shutdown()


    def get_sensor_data(self, stream_type):
        try:
            stream_obj = {"Temperature":Temp(), "EDA":Eda()}
            msg = stream_obj[stream_type]

            # https://github.com/labstreaminglayer/pylsl/blob/main/src/pylsl/examples/ReceiveDataInChunks.py
            stream = resolve_byprop("type", stream_type)
            if not stream:
                self.get_logger().error(f"No streams found of type: {stream_type}")
                exit()
                rclpy.shutdown()
         
            self.get_logger().info(f'Stream found: {stream_type}')

            inlet = StreamInlet(stream[0])
            sample, timestamp = inlet.pull_chunk(timeout=self.batch_time)

            var = [s[0] for s in sample]
            msg.data = var
            # self._logger.info(f"Timestamps:\n{timestamp}\n")
            msg.timestamps = [self.convert_time(t) for t in timestamp]
            msg.header.stamp = self.get_clock().now().to_msg()
            return msg
        
        except KeyboardInterrupt:
            rclpy.shutdown()
        
            
    def convert_time(self, timestamp):
        time = Time()
        time.sec = int(timestamp)
        time.nanosec = int((timestamp%1)*1e9)
        return time

def main():
    rclpy.init()
    publish_data=SensorDataEmotibit()
    rclpy.spin(publish_data)

    publish_data.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
