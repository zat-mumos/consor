# ROS2 Node (Publisher)

#### ROS2 package: 

physio_sensor

#### File name: 

physio_sensor/physio_sensor/physio_sensor.py

#### ROS Node name: 

SensorDataEsense

#### Description: 

Publishes sensor data to ROS2 topic

#### ROS Topic: 

`/sensor/esense_data`

#### ROS Message: 

`PhysioSensor.msg`

###### *ROS2 Message Definition:*

*This message is defined in zat_ros2_msgs repository.*

- *std_msgs/Header header*
- *int sample_no*
- *float sample_data*

#### Parameters:

1. `bash_script_path`
    - Type:             File path string (str)
    - Default value:    None
    - Description:      Stores the path to the bash script
2. `timer`
    - Type:             float
    - Default value:    0.5
    - Description:      Frequency for publishing

#### Launch command:

`ros2 launch physio_sensor launch.py`

For more information on how to install the package and use it, refer to [this](Sensors/eSense) README in Sensors/eSense directory.

