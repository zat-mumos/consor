# Introduction

- This repository is specifically for bridging the [eSense physiological sensors](https://mindfield-esense.com/ )  with the publisher node using **pylsl**.

- The ROS2 package for publishing eSense sensor data is *esense_pkg*.
- When the data is transferred via **Lab Streaming Layer (LSL)**, then the **physio_sensor** ROS2 package should be used.

#### esense_lsl folder contents

- esense_pkg: ROS2 package for eSense


# esense_pkg Package

### Requirements/Dependencies

- WiFi connectivity ***(eSense and the Linux System must be connected to the same WiFi/Network)***
- *zat_ros2_msgs*
- [pylsl](https://github.com/labstreaminglayer/pylsl)


### Tested environment 

- Ubuntu 22.04 + ROS2 Humble
- Python 3.8 or higher
- pylsl (v1.17.6)


### Installation

- Pylsl: `pip install pylsl`


##### ROS2 packages

- Create a ROS2 workspace using `mkdir -p zat_ws/src` or if a ROS2 workspace already exists use `cd zat_ws/src` 
- In src, download **consor** repository and **zat_ros2_msgs** package


### Usage/Steps

##### Steps to run the eSense android application

- Name of the working eSense application: ***eSense_sdk_2*** 
- Open the application on the android device.  
- To test the application, follow the steps:
    - Set the sampling rate (to 1 or 2 Hz for simplicity)
    - Set sensor type to any sensor (If not connected to any sensor, then set the sensor type to a simulator e.g. tempSimulator)
    - Click start sampling. This should prompt a dialog box asking to allow permissions if not already granted. If the sampling does not start after granting permission, click start sampling again. 
    - Click stop sampling to stop the sampling. 


##### Steps to run the 'esense_pkg' package

- Once the application is set, we can run the ROS2 package.
- Open a terminal
- In the respective ROS2 workspace (e.g. zat_ws1), `source /opt/ros/humble/setup.bash`
- `colcon build`
- `source install/setup.bash`
- `ros2 launch esense_pkg launch.py`


##### Notes

- After ros2 launch, there can be a delay where the system is trying to find the LSL streamer (android device) that streams the sensor data.
- Ensure permissions are provided to the android application.
- Ensure that the application starts sampling first before running the ROS node. 
    - This is because, on clicking 'Start Sampling', the application initiates and starts streaming the data using LSL. 
    - The ROS node is a receiver script for the data streamed by the LSL streamer. 
    - Hence, the application needs to start streaming the data before the ROS node script can find and receive this streamed data. 


##### Troubleshooting

- If the package does not build using colcon build, check 
    - whether consor is downloaded in *_ws/src
    - whether zat_ros2_msgs is downloaded in the same folder as consor (i.e., in *_ws/src)


- If there is no output after ros2 launch, check
    - if the application is running (i.e., Start sampling is clicked, and data is being sampled) on the android device
    - whether the correct android application is in use (Name of the app: eSense_sdk_2 or eSense SDK 2 Demo (ZAT))
