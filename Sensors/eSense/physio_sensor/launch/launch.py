from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import os


def generate_launch_description():
    package_name='physio_sensor'

    esense_sensor_arg = DeclareLaunchArgument(
        'esense_topic',
        default_value='/sensor/esense/data',
        description='Sample no and data from esense sensors'
    )

    esense_sensor_timer = DeclareLaunchArgument(
        'esense_timer',
        default_value='2.0',
        description='Buffer time for sample collection'
    )
    
    esense_bash_script_path = DeclareLaunchArgument(
       'esense_bash_script_path',
       default_value=os.path.join(get_package_share_directory(package_name), 'scripts', 'main.sh'),
       description='Path to main.sh bash script for esense sensors'
   )

    physiosensor_node = Node(
        package=package_name,
        executable='publish_esense_data',
        name='esense_physiological_sensors',
        output='screen',
        parameters=[{
            'esense_topic': LaunchConfiguration('esense_topic'),
            'esense_timer': LaunchConfiguration('esense_timer'),
           'esense_bash_script_path' : LaunchConfiguration('esense_bash_script_path')
        }]
    )
    
    return LaunchDescription([
        esense_sensor_arg,
        esense_sensor_timer,
        esense_bash_script_path,
        physiosensor_node
    ])
