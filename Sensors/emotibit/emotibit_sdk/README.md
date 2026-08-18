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
- In src folder, add **consor** and **zat_ros2_msgs** repositories. This is included in the **<< link to releases >>**.


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

- Ensure that all devices (EmotiBit sensors + Linux system(s)) are all connected to the same WiFi. If there are any problems, try troubleshooting. Refer to troubleshooting section in the << **link to documentation** >>.
