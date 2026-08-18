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
This file contains constants that are useful for testing esense_pkg.py with the help of unit-tests.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
import rclpy.clock
import zat_ros2_msgs.msg
import std_msgs.msg
import builtin_interfaces.msg
import rclpy

metadata = {'sampling_rate': 1, 'android_api_level': 35, 'device_name': 'gts9wifi', 'manufacturer_name': 'samsung', 'units': '°C_sim', 'sensor_type': 'tempSimulator'}
sample = [['1785661749', '373208000', '   19.000', '    1'], 'dummy_value']

# stream info constants
stream_info_android_api_level = "35"
stream_info_device_name = "[103, 116, 115, 57, 119, 105, 102, 105]"
stream_info_manufacturer_name = "[115, 97, 109, 115, 117, 110, 103]"
stream_info_sensor_type = "tempSimulator"
stream_info_sampling_rate = "1"
stream_info_units = "°C_sim"

batch_data = [zat_ros2_msgs.msg.Esense(
                                    header=std_msgs.msg.Header(stamp=builtin_interfaces.msg.Time(sec=1785661749, nanosec=373208000), frame_id=''), 
                                    sample_data=19.0
                                )
                            ]
timestamp = builtin_interfaces.msg.Time(sec=1785661749, nanosec=373208000)
seconds = 1785661749
nanoseconds = 373208000
start_time = rclpy.time.Time(nanoseconds=1785661449761436748, clock_type=rclpy.clock.ClockType.ROS_TIME)
duration = rclpy.duration.Duration(nanoseconds = int(0)*1e9)

sample_msg = zat_ros2_msgs.msg.EsenseStream(
                                        header=std_msgs.msg.Header(stamp=builtin_interfaces.msg.Time(sec=1785661749, nanosec=373208000), frame_id=''), 
                                        data=[zat_ros2_msgs.msg.Esense(
                                                    header=std_msgs.msg.Header(stamp=builtin_interfaces.msg.Time(sec=1785661749, nanosec=373208000), frame_id=''), 
                                                    sample_data=19.0)
                                            ], 
                                        sensor_type='tempSimulator', sample_rate=1, unit_name='°C_sim'
                                    )