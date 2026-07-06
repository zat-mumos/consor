from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

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
    
