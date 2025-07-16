import os
from ament_index_python.packages import get_package_share_directory

import rclpy
from rclpy.logging import LoggingSeverity
from rclpy.node import Node

from zat_ros2_msgs.msg import EmotibitStream
from builtin_interfaces.msg import Time

from pylsl import resolve_byprop, StreamInlet

import threading
from threading import Thread

import time


class SensorDataEmotibit(Node):
    def __init__(self):
        super().__init__('sensor_data_emotibit')

        self.get_logger().set_level(LoggingSeverity.DEBUG)

        self.i = 0 # counter
        
        # Declare parameters
        self.declare_parameter('topic_names', ["default_topic"])
        self.declare_parameter('stream_names', ["default_stream"])
        self.declare_parameter('emotibit_timer', 1.0)
        self.declare_parameter('stream_timeout', 0.5)
        
        # Get parameter values
        buffer = self.get_parameter('emotibit_timer').value
        type_stream = self.get_parameter('stream_names').value
        sensor_topic = self.get_parameter('topic_names').value
        timeout = self.get_parameter('stream_timeout').value

        self.topics = sensor_topic
        self.batch_time = buffer
        self.stream_type = type_stream
        self.stream_timeout = timeout
        self.get_logger().debug(f'Beginning code ... ')
        self.get_logger().info(f'Starting node for EmotiBit sensor (timeout: {timeout}\nbuffer: {buffer}\nStream type: \n{type_stream}\n\nTopic: \n{sensor_topic})')
            
        self.publisher = {} # Keep track of publishers
        self.current_threads = [] # keep track of threads

        for stream, topic in zip(self.stream_type, self.topics):
            self.get_logger().info(f'Creating publisher for EmotiBit sensor (Stream type: {stream} & Topic: {topic})')
            self.publisher[stream] = self.create_publisher(EmotibitStream, topic, 10)

        # Create threads in the background
        try:
            background_thread = Thread(target=self.threads_fnc, daemon=True)
            self.get_logger().debug(f"{background_thread.name} initialised")
            background_thread.start()
            self.get_logger().debug(f"{background_thread.name} started")
        except Exception as e:
            self.get_logger().debug(f"Exception: {e}")


    def threads_fnc(self):
        self.get_logger().debug(f"In Function: threads_fnc()")
        self.create_threads()

        # time.sleep(0.1) # buffer time for thread to start

        # # On completing the execution, wait for all threads to finish
        # self.get_logger().info(f"Joining {len(self.current_threads)} threads")
        # for threads in self.current_threads:
        #     self.get_logger().debug(f"Joining thread: {threads.name}")
        #     threads.join()
        #     self.get_logger().debug(f"Thread joined: {threads.name}")
        # self.get_logger().info("All threads completed.")


    def create_threads(self):
        self.get_logger().debug(f"In Function: create_threads()")
        self.current_threads = [] # refresh list of current_threads
        k = 2 # Thread 1 is background thread
        for stream in self.stream_type:
            self.get_logger().debug(f"Thread initialised")
            thread = Thread(target=self.get_sensor_data, args=(stream, k,), daemon=True)
            self.get_logger().debug(f"Starting thread")
            thread.start()
            self.get_logger().debug(f"Thread appended")
            self.current_threads.append(thread)
            k += 1
        self.get_logger().info(f"{len(self.current_threads)} threads created & appended")

    
    def get_sensor_data(self, stream_type, id):
        try:
            curr_stream_pub = self.publisher[stream_type]
            self.get_logger().debug(f"Current publisher for stream type: {curr_stream_pub} | {stream_type}")
            while rclpy.ok():
                stream = resolve_byprop("type", stream_type)
                if not stream:
                    self.get_logger().error(f"No streams found of type: {stream_type}")
                    exit()
                    rclpy.shutdown()
                self.get_logger().info(f'Stream found: {stream_type}')

                inlet = StreamInlet(stream[0])
                sample, timestamp = inlet.pull_chunk(timeout=self.batch_time)
                if sample:
                    msg = EmotibitStream()
                    msg.stream_name = stream_type
                    var = [s[0] for s in sample]
                    msg.sensor_data = var
                    msg.timestamp = [self.convert_time(t) for t in timestamp]
                    msg.header.stamp = self.get_clock().now().to_msg()
                    
                    curr_stream_pub.publish(msg)
                    self.get_logger().info(f'msg:\n{msg}\n--------**************---------\n')

                else:
                    self.get_logger().info(f"Stream: {stream_type} | No data received")  
        except Exception as e:
            self.get_logger().error(f"Error (Thread {id}): {e}")      
        except KeyboardInterrupt:
            rclpy.shutdown()
            

    def convert_time(self, timestamp):
        time = Time()
        time.sec = int(timestamp)
        time.nanosec = int((timestamp%1)*1e9)
        return time


def main():
    rclpy.init()
    sensor_node=SensorDataEmotibit()
    sensor_node.get_logger().debug("Node has been initialised")
    print(f"Node: {sensor_node}\nType: {type(rclpy.spin)}")
    try:
        rclpy.spin(sensor_node)
        sensor_node.get_logger().debug("rclpy.spin() called ................")
    except KeyboardInterrupt:
        sensor_node.get_logger().debug(f"KeyBoard Interrupt")
    finally:
        sensor_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
