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
Test file to record and publish IMU data

Subscribers:
    None

Publishers:
    IMU_publisher
    
Description:
    Test file to record and publish IMU data


Author:
    Jay Parikh <jay.parikh@smail.inf.h-brs.de>
"""

import sys
import os
import rclpy
from rclpy.node import Node
from rclpy.logging import get_logger
from std_msgs.msg import String  # Publish JSON as String messages
from zat_ros2_msgs.msg import Imu


# Add the path to xdpchandler.py

sys.path.append(os.path.expanduser('~/zat_ws/src/movella_pkg/movella_pkg/examples/xdpcsdk/python'))



from xdpchandler import XdpcHandler
import movelladot_pc_sdk  # Movella SDK


class MovellaNode(Node):
    def __init__(self):
        super().__init__('movella_node')

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


        # either connect to the ble sensors or else gives an error

        self.xdpcHandler.connectDots()
        if len(self.xdpcHandler.connectedDots()) == 0:
            self.get_logger().error("Could not connect to any Movella DOT device(s). Aborting.")
            self.xdpcHandler.cleanup()
            rclpy.shutdown()
            return

        # dynamical publishers

        self.IMU_publishers = {} # pub dict


        for idx, dev in enumerate(self.xdpcHandler.connectedDots(), start=1):
            topic_name = f"imu_sensor_{idx}"
            publisher = self.create_publisher(Imu, topic_name, 10)

            # Store publisher per device
            self.IMU_publishers[dev.portInfo().bluetoothAddress()] = publisher
            self.get_logger().info(f"Created publisher on topic: {topic_name}")

            # Set device settings

            ## filter profile check
            filterProfiles = dev.getAvailableFilterProfiles()
            for f in filterProfiles:
                self.get_logger().info(f"Available filter profile: {f.label()}")
            if dev.setOnboardFilterProfile("General"):
                self.get_logger().info("Success set profile General")
            else:
                self.get_logger().error("filter profile failed!")

            self.get_logger().info("device into measurement mode.")
            if not dev.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedEuler):
                self.get_logger().error(f"Could not put device into measurement mode. Reason: {device.lastResultText()}")
                continue

        self.get_logger().info("Main loop. Continuously recording and publishing IMU data.")
        self.record_data()

    def record_data(self):
        orientationResetDone = False
        startTime = movelladot_pc_sdk.XsTimeStamp_nowMs()

        while rclpy.ok():
            if self.xdpcHandler.packetsAvailable():
                for device in self.xdpcHandler.connectedDots():
                    packet = self.xdpcHandler.getNextPacket(device.portInfo().bluetoothAddress())

                    if packet.containsOrientation():
                        euler = packet.orientationEuler()
                        # freeacc = packet.freeAcceleration()

                        imu_data = Imu()
                        # imu_data.header.stamp = self.get_clock().now().to_msg()
                        imu_data.roll = round(euler.x(), 2)
                        imu_data.pitch = round(euler.y(), 2)
                        imu_data.yaw = round(euler.z(), 2)

                        publisher = self.IMU_publishers.get(device.portInfo().bluetoothAddress())
                        if publisher:
                            msg = imu_data


                            publisher.publish(msg)

    def stop_measurement(self):
        self.get_logger().info("Stopping measurement...")
        for device in self.xdpcHandler.connectedDots():
            if not device.stopMeasurement():
                self.get_logger().error("Failed to stop measurement.")
        self.xdpcHandler.cleanup()


def main():
    rclpy.init()

    node = MovellaNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.stop_measurement()
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
