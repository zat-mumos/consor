# Overview

### ROS2 Package: **physio_sensor**

Description: <br>

A ROS2 package that includes a python ROS node (in /physio_sensor directory) for publishing eSense sensor data and bash scripts (in /scripts directory) for connecting to Bluetooth and transfer this sensor data from android device to linux system


For more information, refer to the respective READMEs,
1. [ROS2 package: physio_sensor](./ROS2_physio_sensor.md)
2. [Scripts: main.sh & cmds.sh](./Scripts.md)
	


##### Pre-requisites

ROS2 Humble is used for executing the ROS2 package. 
To know more about ROS2 documentation, refer to [link](https://docs.ros.org/en/humble/index.html)


The bash scripts use the _empty_ package to communicate with the terminal and transfer data via Bluetooth. 
To know more about empty, refer to [link](https://manpages.debian.org/stretch/empty-expect/empty.1.en.html)



