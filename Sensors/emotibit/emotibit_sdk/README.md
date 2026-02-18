# Emotibit with BrainFlow SDK

- This repository is specifically for bridging the [EmotiBit sensors](https://www.emotibit.com/) with the publisher node using BrainFlow SDK.
- The ROS2 package for publishing EmotiBit data is *emotibit_sdk*.


## ROS2 package: emotibit_sdk

### Requirements & Dependencies

- WiFi connectivity ***(EmotiBit and the Linux System(s) must be connected to the same WiFi)***
- [BrainFlow](https://brainflow.org/)
- [zat_ros2_msgs](https://git.inf.h-brs.de/zat-rhein-ruhr/zat-prototype-demo/zat_ros2_msgs.git)

#### Tested Environment

- Ubuntu 22.04 + ROS2 Humble
- Python 3.8 or higher
- BrainFlow (5.18.0)

### Installation

##### Python package

- brainflow `python -m pip install brainflow`
<br>[Link](https://brainflow.readthedocs.io/en/stable/index.html) to the brainflow documentation

##### ROS2 packages

- Create a ROS2 workspace using `mkdir -p zat_ws/src` or if a ROS2 workspace already exists then use `cd zat_ws/src`
- In src folder, download **consor** and **zat_ros2_msgs** repositories


### Usage

#### Running the emotibit_pkg

```
# go to zat workspace
cd zat_ws
```
```
# source ROS
source /opt/ros/humble/setup.bash
```
```
# build the workspace
colcon build
```
```
# source the workspace
source install/setup.bash
```
```
# launch the package
ros2 launch emotibit_sdk launch.py
```

###### Notes

- Ensure that all devices (EmotiBit sensors + Linux system(s)) are all connected to the same WiFi. If there are any problems, try troubleshooting. Some troubleshooting steps are mentioned at the end of this README.


##### Troubleshooting

- If the package does not build using colcon build, check 
    - whether consor is downloaded in *_ws/src
    - whether zat_ros2_msgs is downloaded in the same folder as consor (i.e., in *_ws/src)
- If the WiFi connected blue LED is blinking but no EmotiBit found, 
    - Ensure you or the system is connected to the correct WiFi.
    - If there are multiple networks that are configured on the EmotiBit config file, ensure that the credentials for the network that the Linux system(s) is connected to is at the beginning of all other networks. But it is always better to configure only a single network in the config file of the EmotiBit that the EmotiBit sensor connects to. 
    - If still facing issues, try connecting all devices (EmotiBit sensors + Linux system(s)) to a local WiFi hotspot. 
- If any error (such as BOARD_NOT_READY_ERROR) occurs, wait for a few seconds and run ros2 launch command again.


### Data Streams

- Accelerometer (3 channels)
- Gyroscope (3 channels)
- Magnetometer (3 channels)
- PPG (3 channels)
- EDA (1 channel)
- Temperature (1 channel)

