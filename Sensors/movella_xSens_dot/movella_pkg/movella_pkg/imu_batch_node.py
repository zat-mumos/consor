# © 2026 Hochschule Bonn-Rhein-Sieg <https://www.h-brs.de/>
# 
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
# Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program. If not, see <https://www.gnu.org/licenses/>.

"""
This file establishes the connection between the Movella DOT sensors and ROS for data recording

Subscribers:
    None

Publishers:
    buffer_pub: MovellaData, default: 100000

Parameters:
    output_rate
    imu_topic
    buffer_duration (in milliseconds)
    
Description:
    Movella DOT device scanning and connection through BLE.
    Calibrates and starts streaming data from buffer.


Author:
    Jay Parikh <jay.parikh@smail.inf.h-brs.de>
"""

import sys
import os,time
import rclpy
import threading
from rclpy.node import Node
from rclpy.logging import get_logger
from std_msgs.msg import String  # Publish JSON as String messages
from zat_ros2_msgs.msg import MovellaData, MovellaImu, MovellaSensor
from builtin_interfaces.msg import Time

# sys.path.append(os.path.expanduser('~/ros2_movella/src/movella_pkg/movella_pkg/examples/xdpcsdk/python'))




import movelladot_pc_sdk  # Movella SDK
from movella_pkg.xdpchandler import XdpcHandler
from collections import defaultdict

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



        self.declare_parameter('output_rate', 1)

        self.declare_parameter('imu_topic', '/sensor/movella/imu_data')

        self.declare_parameter('buffer_duration', 3000)  # in milliseconds

        buffer_duration_ms = int(self.get_parameter('buffer_duration').value)  # in milliseconds

        self.get_logger().info(f"Buffer duration (ms): {buffer_duration_ms}")

        output_rate = int(self.get_parameter('output_rate').value)

        self.get_logger().info(f"Output rate (Hz): {output_rate}")

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

            # if not dev.startMeasurement(movelladot_pc_sdk.XsPayloadMode_CustomMode4):
            #     self.get_logger().error("Could not start measurement mode")

        ## initial measurement mandatory for calibration

        orientationResetDone = False

        for device in self.xdpcHandler.connectedDots():
            if not device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_OrientationEuler):
                self.get_logger().error(f"Could not start measurement mode for device {device.portInfo().bluetoothAddress()}")

        self.get_logger().info("Collecting data for 10 seconds to stabilize orientation...")

        startTime = movelladot_pc_sdk.XsTimeStamp_nowMs()

        while movelladot_pc_sdk.XsTimeStamp_nowMs() - startTime <= 10000:

            if self.xdpcHandler.packetsAvailable():
                s = ""
                for device in self.xdpcHandler.connectedDots():
                    # Retrieve a packet
                    packet = self.xdpcHandler.getNextPacket(device.portInfo().bluetoothAddress())

                    if packet.containsOrientation():
                        euler = packet.orientationEuler()
                        s += f"Roll:{euler.x():7.2f}, Pitch:{euler.y():7.2f}, Yaw:{euler.z():7.2f}| "

                self.get_logger().info("%s\r" % s)


        ## Reset heading
        for device in self.xdpcHandler.connectedDots():
            self.get_logger().info(f"Resetting heading for device {device.portInfo().bluetoothAddress()}: ")
            if device.resetOrientation(movelladot_pc_sdk.XRM_Heading):
                self.get_logger().info("OK")
            else:
                self.get_logger().info(f"NOK: {device.lastResultText()}")
            
            device.stopMeasurement()
        self.get_logger().info("-----------------------------------------")

        ## Switch to desired measurement mode

        for device in self.xdpcHandler.connectedDots():
            if not device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_CustomMode4):
                self.get_logger().error(f"Could not start measurement mode for device {device.portInfo().bluetoothAddress()}")


        
        
        # buffer batch publisher
        # self.buffer_pub = self.create_publisher(MovellaData, '/movella/data', 100000)

        # imu data publisher topic through launch file

        buffer_topic = self.get_parameter('imu_topic').value

        self.buffer_pub = self.create_publisher(MovellaData, buffer_topic, 100000)

        self.buffer = defaultdict(list)

        # self.buffer = { dev.portInfo().bluetoothAddress(): [] for dev in self.xdpcHandler.connectedDots() }

        # buffer list
        self.get_logger().info(f"Buffer: {self.buffer}")



        buffer_duration_ms = self.get_parameter('buffer_duration').value

        self.get_logger().info(f"Buffer duration (ms): {buffer_duration_ms}")

        # self.buffer_duration_ms = 
        
        self.buffer_duration_ms = buffer_duration_ms

        # self.start_time = self.get_clock().now().to_msg()
        # self.logger.info(f"data collection from {self.start_time} for {self.buffer_duration} sec")
        self.record_data_flag = True
        self.worker_thread = threading.Thread(target=self.record_batch_data)
        self.worker_thread.daemon = True
        self.worker_thread.start()

        self.get_logger().info("The thread has started")



        # self.record__batch_data()

    def record_batch_data(self):

        duration_time = rclpy.duration.Duration(nanoseconds=self.buffer_duration_ms * 1e6)

        buffer_flag = False # flag to indicate if buffer duration has passed

        while self.record_data_flag:
            if self.xdpcHandler.packetsAvailable():
                for dev in self.xdpcHandler.connectedDots():
                    mac = dev.portInfo().bluetoothAddress()
                    pkt = self.xdpcHandler.getNextPacket(dev.portInfo().bluetoothAddress())
                    imu_msg = MovellaImu()
                    imu_msg.header.stamp = self.get_clock().now().to_msg()

                    if not buffer_flag:

                        starttime = self.get_clock().now()
                        buffer_flag = True

                    if pkt.containsOrientation():
                        quat = pkt.orientationQuaternion()
                        
                        mac = dev.portInfo().bluetoothAddress()

                        imu_msg.quat_x = quat[0]
                        imu_msg.quat_y = quat[1]
                        imu_msg.quat_z = quat[2]
                        imu_msg.quat_w = quat[3]

                        # euler = pkt.orientationEuler()
                        # euler_x = euler.x()
                        # euler_y = euler.y()
                        # euler_z = euler.z()
                        
                        # print start time
                        # self.get_logger().info(f"Time: {self.get_clock().now().to_msg()}")t
                    
                    if pkt.containsCalibratedAcceleration():
                        acc = pkt.calibratedAcceleration()
                        mac = dev.portInfo().bluetoothAddress()

                        imu_msg.ax = acc[0]
                        imu_msg.ay = acc[1]
                        imu_msg.az = acc[2]

                        # self.buffer[mac].append(imu_msg)
                    
                    if pkt.containsCalibratedGyroscopeData():
                        gyr = pkt.calibratedGyroscopeData()
                        mac = dev.portInfo().bluetoothAddress()

                        imu_msg.gyro_x = gyr[0]
                        imu_msg.gyro_y = gyr[1]
                        imu_msg.gyro_z = gyr[2]

                        # self.buffer[mac].append(imu_msg)

                    if pkt.containsCalibratedMagneticField():
                        mag = pkt.calibratedMagneticField()
                        mac = dev.portInfo().bluetoothAddress()

                        imu_msg.mag_x = mag[0]
                        imu_msg.mag_y = mag[1]
                        imu_msg.mag_z = mag[2]

                        
                    self.buffer[mac].append(imu_msg)





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



                        
                        # for k in self.buffer:

                        #                             # check if the buffer mac address value is empty

                        #     if not self.buffer[k]:
                        #         self.get_logger().info(f"Buffer for {mac} is empty")

                        #     else:
                    
                        #     # print the size of the buffer
                        #         self.get_logger().info(f"Buffer for {mac} size: {len(self.buffer[k])}")

                        #     self.buffer[k].clear()
                    
                        # reset the start time
                        self.buffer = defaultdict(list)
                        self.get_logger().info(f"Buffer cleared after {self.buffer_duration_ms} ms")
                        buffer_flag = False
    


def main(args=None):
    rclpy.init(args=args)

    node = MovellabatchNode()

    try:
        rclpy.spin(node)
        print("The init is done")
    except KeyboardInterrupt:
        
        node.stop_measurement()
    finally:
        node.record_data_flag = False
        node.worker_thread.join(timeout=1.0)
        node.xdpcHandler.cleanup()
        time.sleep(3)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    sys.exit(main(args=sys.argv))
