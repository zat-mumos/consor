#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from zat_ros2_msgs.msg import Imu
from std_msgs.msg import String
import json
from threading import Lock

class ImuBatchNode(Node):
    def __init__(self):
        super().__init__('imu_batch_node')

        # Discover all topics of type Imu
        all_topics = self.get_topic_names_and_types()
        self.imu_topics = [
            name for name, types in all_topics
            if 'zat_ros2_msgs/msg/Imu' in types
        ]
        if not self.imu_topics:
            self.get_logger().error('No IMU topics found—run MovellaNode first.')
            return

        self.get_logger().info(f"Subscribing to: {self.imu_topics}")

        # Thread‐safe buffer: topic → list of dicts
        self._lock = Lock()
        self._buffer = {topic: [] for topic in self.imu_topics}

        # Create one subscriber per sensor‐topic
        for topic in self.imu_topics:
            self.create_subscription(
                Imu,
                topic,
                lambda msg, t=topic: self._imu_callback(msg, t),
                10
            )

        # Publisher for the 3-second batch
        self._batch_pub = self.create_publisher(String, 'imu_batch', 10)

        # Timer: every 3 s, publish & clear buffer
        self.create_timer(3.0, self._timer_callback)

    def _imu_callback(self, msg: Imu, topic: str):
        """
        Called on each incoming Imu. Timestamp it here,
        then stash roll/pitch/yaw into our buffer.
        """
        now = self.get_clock().now().to_msg()
        entry = {
            'timestamp': {
                'sec':  now.sec,
                'nsec': now.nanosec
            },
            'roll':  msg.roll,
            'pitch': msg.pitch,
            'yaw':   msg.yaw,
            # if your Imu msg has accel/mag/etc, add those too
        }
        with self._lock:
            self._buffer[topic].append(entry)

    def _timer_callback(self):
        """Every 3 s, dump and clear the buffer as one JSON message."""
        with self._lock:
            total = sum(len(v) for v in self._buffer.values())
            if total == 0:
                self.get_logger().debug('No samples this window; skipping.')
                return

            batch = {
                'window_end': {
                    'sec':  self.get_clock().now().to_msg().sec,
                    'nsec': self.get_clock().now().to_msg().nanosec
                },
                'data': self._buffer.copy()
            }

            # reset for next period
            self._buffer = {topic: [] for topic in self.imu_topics}

        msg = String()
        msg.data = json.dumps(batch)
        self._batch_pub.publish(msg)
        self.get_logger().info(
            f'Published batch with {total} samples '
            f'across {len(self.imu_topics)} topics.'
        )

def main():
    rclpy.init()
    node = ImuBatchNode()
    if not node.imu_topics:
        return
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
