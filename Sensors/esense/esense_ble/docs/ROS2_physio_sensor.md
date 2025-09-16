# ROS2 Node (Publisher)

#### ROS2 package: 

physio_sensor

#### File name: 

physio_sensor/physio_sensor/physio_sensor.py

#### ROS Node name: 

SensorDataEsense

#### Description: 

Publishes sensor data to ROS2 topic

#### ROS2 Topic: 

`/sensor/esense/data`

#### ROS Message: 

- `Esense.msg`
- `PhysioSensor.msg`

###### *ROS2 Message Definition:*

*These messages are defined in zat_ros2_msgs repository.*

- Esense.msg
    - *std_msgs/Header header*
    - *float sample_data*

- PhysioSensor.msg
    - *std_msgs/Header header*
    - *Esense[] data*

#### Parameters:

1. `esense_topic`
    - Type:             String
    - Default value:    '/sensor/esense/data'
    - Description:      Topic that publishes the eSense sample data and timestamp
2. `esense_bash_script_path`
    - Type:             File path (String)
    - Default value:    None
    - Description:      Stores the path to the main bash script for eSense sensors
3. `esense_timer`
    - Type:             float
    - Default value:    2.0
    - Description:      Buffer time for sample collection

#### Launch command:

`ros2 launch physio_sensor launch.py`

For more information on how to install the package and use it, refer to [this](Sensors/eSense) README in Sensors/eSense directory.

