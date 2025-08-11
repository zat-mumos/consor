from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import os


def generate_launch_description():
    package_name='openbci_pkg'

    bci_modality = DeclareLaunchArgument(
        'modality_name',
        default_value='eeg',
        description='The modality to measure using OpenBCI sensors. Select one between the following: eeg, ecg, eog, emg'
    )

    bci_timer = DeclareLaunchArgument(
        'openbci_timer',
        default_value='1.0',
        description='Buffer time for sample collection'
    )
    
    bci_port = DeclareLaunchArgument(
       'port_name',
       default_value='/dev/ttyACM0',
       description='Port that the BLE dongle for OpenBCI sensors are connected to'
   )

    openbci_node = Node(
        package=package_name,
        executable='publish_openbci_data',
        name='openbci_sensors',
        output='log',
        parameters=[{
            'modality_name': LaunchConfiguration('modality_name'),
            'openbci_timer': LaunchConfiguration('openbci_timer'),
            'port_name' : LaunchConfiguration('port_name')
        }],
    )
    
    return LaunchDescription([
        bci_modality,
        bci_timer,
        bci_port,
        openbci_node
    ])
