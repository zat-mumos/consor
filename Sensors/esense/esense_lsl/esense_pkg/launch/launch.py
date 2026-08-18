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
ROS2 launch file for the eSense sensor communicating via Lab Streaming Layer (LSL).

Parameters:
    - esense_topic (str, default: '/sensor/esense/data')
    - esense_timer (float, default: 1.0)
    
Description:
    This launch file starts the eSense sensor streaming using LSL.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os

def generate_launch_description():
    package_name = 'esense_pkg'

    esense_sensor_arg = DeclareLaunchArgument(
        'esense_topic',
        default_value='/sensor/esense/data',
        description='Sample data and timestamp from esense sensors'
    )

    esense_sensor_timer = DeclareLaunchArgument(
        'esense_timer',
        default_value='2.0',
        description='Buffer time for sample collection'
    )

    esense_node = Node(
        package=package_name,
        executable='publish_esense_data_via_lsl',
        name='publish_esense_data_via_lsl',
        output='log',
        parameters=[{
            'esense_topic': LaunchConfiguration('esense_topic'),
            'esense_timer': LaunchConfiguration('esense_timer')
        }]
    )

    return LaunchDescription([
        esense_sensor_arg,
        esense_sensor_timer,
        esense_node
    ])