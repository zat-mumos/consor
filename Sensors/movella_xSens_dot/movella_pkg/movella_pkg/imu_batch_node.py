import sys
import os
import rclpy
from rclpy.node import Node
from rclpy.logging import get_logger
from std_msgs.msg import String  # Publish JSON as String messages
from zat_ros2_msgs.msg import MovellaData, MovellaImu, MovellaSensor
from builtin_interfaces.msg import Time

# sys.path.append(os.path.expanduser('~/ros2_movella/src/movella_pkg/movella_pkg/examples/xdpcsdk/python'))




import movelladot_pc_sdk  # Movella SDK
from movella_pkg.xdpchandler import XdpcHandler

class MovellabatchNode(Node):
    def __init__(self):
        super().__init__('movella_batch_node')

        self.logger = get_logger(self.get_name())
        self.xdpcHandler = XdpcHandler()

        # Xpdchandler check initialization

        if not self.xdpcHandler.initialize():
            self.xdpcHandler.cleanup()
            self.get_logger().error('Failed to initialize the XdpcHandler. Exiting...')
            rclpy.shutdown()
            return

        # Movella DOT device scanning and connection

        self.xdpcHandler.scanForDots()

        if len(self.xdpcHandler.detectedDots()) == 0:
            self.get_logger().error("No Movella DOT device(s) found. Aborting.")
            self.xdpcHandler.cleanup()
            rclpy.shutdown()
            return
        
        # BLE connection

        self.xdpcHandler.connectDots()

        self.declare_parameter('output_rate', 10.0)

        output_rate = int(self.get_parameter('output_rate').get_parameter_value().double_value)

        # change the streaming rate to 10 hz
        for device in self.xdpcHandler.connectedDots():

            # if device.setOutputRate(10):
        
        # according to the launch file

            if device.setOutputRate(output_rate):
                self.get_logger().info("Successfully set onboard recording rate")
            else:
                self.get_logger().error("Setting onboard recording rate failed!")

        if len(self.xdpcHandler.connectedDots()) == 0:
            self.get_logger().error("Could not connect to any Movella DOT device(s). Aborting.")
            self.xdpcHandler.cleanup()
            rclpy.shutdown()
            return
        
        else:
            self.get_logger().info(f"Connected to {len(self.xdpcHandler.connectedDots())} devices ")

        # setting up a single publisher for sending data from the buffer

        for dev in self.xdpcHandler.connectedDots():
            mac = dev.portInfo().bluetoothAddress()

            for prof in dev.getAvailableFilterProfiles():
                self.get_logger().info(f"Profile: {prof.label()}")

            if not dev.setOnboardFilterProfile("General"):
                self.get_logger().error("Could not set filter profile")

            if not dev.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedEuler):
                self.get_logger().error("Could not start measurement mode")

        
        # buffer batch publisher
        # self.buffer_pub = self.create_publisher(MovellaData, '/movella/data', 100000)

        # imu data publisher topic through launch file

        buffer_topic = self.get_parameter('buffer_topic').get_parameter_value().string_value

        self.buffer_pub = self.create_publisher(MovellaData, buffer_topic, 100000)



        self.buffer = { dev.portInfo().bluetoothAddress(): [] for dev in self.xdpcHandler.connectedDots() }

        # printing the buffer
        self.get_logger().info(f"Buffer: {self.buffer}")



        buffer_duration_ms = self.get_parameter('buffer_duration').get_parameter_value().integer_value

        # self.buffer_duration_ms = 
        
        self.buffer_duration_ms = buffer_duration_ms

        # self.start_time = self.get_clock().now().to_msg()
        # self.logger.info(f"data collection from {self.start_time} for {self.buffer_duration} sec")

        self.record__batch_data()

    def record__batch_data(self):
        orientationResetDone = False

        now_msg = self.get_clock().now()

        duration_time = rclpy.duration.Duration(nanoseconds=self.buffer_duration_ms * 1e6)
        starttime = now_msg

        while rclpy.ok():
            if self.xdpcHandler.packetsAvailable():
                for dev in self.xdpcHandler.connectedDots():
                    mac = dev.portInfo().bluetoothAddress()
                    pkt = self.xdpcHandler.getNextPacket(dev.portInfo().bluetoothAddress())

                    if pkt.containsOrientation():
                        euler = pkt.orientationEuler()
                        mac = dev.portInfo().bluetoothAddress()

                        imu_msg = MovellaImu()
                        imu_msg.header.stamp = self.get_clock().now().to_msg()
                        imu_msg.roll = euler.roll()
                        imu_msg.pitch = euler.pitch()
                        imu_msg.yaw = euler.yaw()

                        self.buffer[mac].append(imu_msg)

                        
                        # print start time
                        # self.get_logger().info(f"Time: {self.get_clock().now().to_msg()}")




                    if self.get_clock().now()- starttime > duration_time:
                        # publish the buffer

                        batch = MovellaData()
                        batch.header.stamp = self.get_clock().now().to_msg()
                        # batch.imu_data.header.stamp = self.get_clock().now().to_msg()
                        batch.data = []

                        # print the buffer items
                        # self.get_logger().info(f"Buffer items: {self.buffer.items()}")

                        for mac, data in self.buffer.items():
                            sensor_msg = MovellaSensor()
                            sensor_msg.id = mac
                            sensor_msg.data = data
                            batch.data.append(sensor_msg)
                        
                        # publish the batch
                        self.buffer_pub.publish(batch)



                        
                        for k in self.buffer:

                                                    # check if the buffer mac address value is empty

                            if not self.buffer[k]:
                                self.get_logger().info(f"Buffer for {mac} is empty")

                            else:
                    
                            # print the size of the buffer
                                self.get_logger().info(f"Buffer for {mac} size: {len(self.buffer[k])}")

                            self.buffer[k].clear()
                    
                        # reset the start time
                        starttime = self.get_clock().now()
    


def main():
    rclpy.init()

    node = MovellabatchNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.stop_measurement()
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
