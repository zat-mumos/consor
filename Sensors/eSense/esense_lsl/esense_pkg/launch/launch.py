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