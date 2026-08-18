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
ROS2 launch file for the EmotiBit sensor using the EmotiBit Oscilloscope.
    
Description:
    This launch file starts the EmotiBit sensor streaming using the EmotiBit Oscilloscope.
    The modalities and the ROS2 topics are specified in config/emotibit_params.yaml

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    package_name_emotibit='emotibit_oscilloscope'

    return LaunchDescription([Node(
        package=package_name_emotibit,
        executable='publish_emotibit_data_with_oscilloscope',
        name='sensor_data_emotibit_with_oscilloscope',
        output='log',
        parameters=[PathJoinSubstitution([FindPackageShare(package_name_emotibit), 'config', 'emotibit_params.yaml'])]
    )
    ])
    
