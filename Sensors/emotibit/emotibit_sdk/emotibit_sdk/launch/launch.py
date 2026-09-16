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
ROS2 launch file for the EmotiBit sensor communicating via BrainFlow.

Parameters:
    - topic_names (list, default: ["default_topic"])
    - stream_names (list, default: ["default_stream"])
    - callback_timer (float, default: 1e-5)
    - emotibit_timer (float, default: 1e-5)

Description:
    This launch file starts the EmotiBit sensor streaming using BrainFlow.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import os


def generate_launch_description():
    package_name_emotibit='emotibit_sdk'

    return LaunchDescription([Node(
        package=package_name_emotibit,
        executable='publish_emotibit_data_with_sdk',
        name='sensor_data_emotibit_with_sdk',
        output='log',
        parameters= [os.path.join(get_package_share_directory(package_name_emotibit), 'config', 'emotibit_params.yaml')],
        emulate_tty=True
        )]
    )
    
