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
