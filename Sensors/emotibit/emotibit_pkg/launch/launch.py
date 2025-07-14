from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

import os


def generate_launch_description():
    package_name_emotibit='emotibit_pkg'

    return LaunchDescription([Node(
        package=package_name_emotibit,
        executable='publish_emotibit_data',
        name='sensor_data_emotibit',
        output='screen',
        parameters=[PathJoinSubstitution([FindPackageShare(package_name_emotibit), 'config', 'emotibit_params.yaml'])]
    )
    ])
    
