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
ROS2 launch file for the Movella DOT wearable-sensor.

Subscribers:
    None

Publishers:
    /sensor/movella/imu_data: A ROS 2 topic that publishes imu data from movella sensor

Parameters:
    output_rate (int, default: 60)
    imu_topic
    buffer_duration (int, default: 500)
    
Description:
    This launch file starts the Movella sensor streaming IMU data with a default output rate of 60 Hz.

Author:
    Jay Parikh <jay.parikh@smail.inf.h-brs.de>
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'movella_pkg'
    

    imu_topic_arg = DeclareLaunchArgument(
    'imu_topic',
    default_value='/sensor/movella/imu_data',
    description='Movella IMU data publisher topic'
    )

    imu_buffer_duration_arg = DeclareLaunchArgument(
    'buffer_duration',
    default_value='500',
    description='buffer data collection duration in milliseconds'
    )

    

    output_rate_arg = DeclareLaunchArgument(
        'output_rate',
        default_value='60',
        description='Output rate (Hz) for publishing IMU data'
    )

    # Define your ROS 2 node
    movella_node = Node(
        package=package_name,
        executable='imu_batch_node',  # must match entry in setup.py
        name='movella_dot_node',
        output='screen',
        parameters=[{
            'output_rate': LaunchConfiguration('output_rate'),
            'imu_topic': LaunchConfiguration('imu_topic'),
            'buffer_duration': LaunchConfiguration('buffer_duration')
        }]
    )

    return LaunchDescription([
        output_rate_arg,
        imu_topic_arg,
        imu_buffer_duration_arg,
        movella_node
    ])
