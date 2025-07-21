# emotibit_pkg

### ROS2 Package: **emotibit_pkg**

Description: <br>

A ROS2 package that includes a python ROS node (loc: /emotibit_pkg) for publishing EmotiBit sensor data.    


##### Pre-requisites

ROS2 Humble is used for executing the ROS2 package. 
To know more about ROS2 documentation, refer to [link](https://docs.ros.org/en/humble/index.html)

For other dependencies, refer to the main README of this repository.

<br>

# ROS2 Node (Publisher)

#### ROS2 package: 

emotibit_pkg

#### File name: 

emotibit_pkg/emotibit_pkg/emotibit.py

#### ROS Node name: 

SensorDataEmotibit

#### Description: 

Publishes sensor data to ROS2 topics

#### ROS2 Topic: 

One ROS2 topic is defined per stream. Hence, there are multiple ROS2 topics. These are stored in the *emotibit_params.yaml* file (loc: emotibit_pkg/config).

#### ROS Message: 

- `EmotibitStream.msg`

###### *ROS2 Message Definition:*

*These messages are defined in zat_ros2_msgs repository.*

- EmotibitStream.msg
    - *string stream_name*
    - *builtin_interfaces/Time[] timestamp*
    - *float64[] sensor_data*


#### Parameters:

The parameters are defined in the *emotibit_params.yaml* file. It includes,

1. `topic_names`
    - Type:             List of strings
    - Default value:    ["default_topic"]
    - Description:      A list of topics (specific to the data stream) that publishes the EmotiBit data
2. `stream_names`
    - Type:             List of strings
    - Default value:    ["default_stream"]
    - Description:      A list of data streams that is to be published
3. `emotibit_timer`
    - Type:             float
    - Default value:    1.0
    - Description:      Buffer/batch time for sample collection. For example, if this value is 5.0, then the data for each stream mentioned in *stream_names* will be collected for 5.0 seconds.

#### Launch command:

`ros2 launch emotibit_pkg launch.py`

For more information on how to install the package and use it, refer to [this](Sensors/emotibit) README (loc: Sensors/emotibit directory).

