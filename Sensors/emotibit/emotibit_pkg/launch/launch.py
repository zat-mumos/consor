from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import os


def generate_launch_description():
    package_name_emotibit='emotibit_pkg'


    emotibit_sensor_arg = DeclareLaunchArgument(
        'emotibit_topic',
        default_value='/sensor/emotibit/data',
        description='Sample data and timestamp from emotibit sensors'
    )

    emotibit_sensor_timer = DeclareLaunchArgument(
        'emotibit_timer',
        default_value='2.0',
        description='Buffer time for sample collection'
    )
    
    emotibit_stream_type = DeclareLaunchArgument(
       'emotibit_stream_type',
       default_value='["EDA", "Temperature"]',
       description='Type of the data stream to be read. Select at least one from the following: ["GyroscopeX", "GyroscopeY", "GyroscopeZ", "AccelerometerX", "AccelerometerY", "AccelerometerZ", "MagnetometerX", "MagnetometerY", "MagnetometerZ", "PPGRed", "PPGGreen", "PPGInfrared", "Thermopile", "Temperature", "EDA", "HeartRate", "SCRFrequency", "SCRAmplitude", "SCRRiseTime"]'
   )

    emotibit_sensor_node = Node(
        package=package_name_emotibit,
        executable='publish_emotibit_data',
        name='emotibit_sensors',
        output='screen',
        # env={'PYLSL_LIB': liblsl_path},
        parameters=[{
            'emotibit_topic': LaunchConfiguration('emotibit_topic'),
            'emotibit_timer': LaunchConfiguration('emotibit_timer'),
            'emotibit_stream_type' : LaunchConfiguration('emotibit_stream_type')
        }]
    )
    
    return LaunchDescription([
        # SetEnvironmentVariable(name='LD_LIBRARY_PATH', value=liblsl_path+':'+os.environ.get('LD_LIBRARY_PATH', '')),
        emotibit_sensor_arg,
        emotibit_sensor_timer,
        emotibit_stream_type,
        emotibit_sensor_node
    ])
