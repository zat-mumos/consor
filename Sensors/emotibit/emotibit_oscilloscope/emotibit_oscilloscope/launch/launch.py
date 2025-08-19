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
    
