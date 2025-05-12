## Introduction

- The eSense repository is specifically for bridging the [eSense physiological sensors](https://mindfield-esense.com/ )  with the publisher node.
- The ROS2 package for publishing eSense sensor data is 'physio_sensor'.

## physio_sensor Package

### Requirements/Dependencies

- zat_ros2_msgs
- 'empty' package should be installed on the system
- Bluetooth must be functioning and switched on 

### Installation

#### 'empty' package

- Download the package using (https://sourceforge.net/projects/empty/) or use an existing/already downloaded zip file of the empty package
- The code is tested with empty-0.6.23c 
- Extract the zip folder for the `empty` package. Move this folder to `home` directory
- Open a terminal
- `cd empty-0.6.23c`
- `make`
- `sudo make install`


- To check if `empty` is installed, 
    - Open a terminal
    - either use `man empty` to see the manual pages for empty
    - or `which empty` to see the location where empty is installed
    - or `empty -v` to see the version of empty that is installed


#### ROS2 packages

- Create a ROS2 workspace using `mkdir -p zat_ws/src` or `cd zat_ws/src` if using an existing ROS workspace
- In src, download consor repository and zat_ros2_msgs package


### Usage/Steps

#### Steps to run the eSense android application

- Name of the working eSense application: **eSense_sdk_2** 
- Open the application on the android device. Ensure that it is running. 
- To test the application, follow the steps:
    - Set the sampling rate (to 1 or 2 Hz for simplicity)
    - Set sensor type to any sensor (If not using any sensor, then set the sensor type to a simulator e.g. tempSimulator)
    - Click start sampling. This should prompt a dialog box asking to allow permissions if not already granted. If the sampling does not start after granting permission, click start sampling again. 
    - Click stop sampling to stop the sampling. 


#### Steps to run the 'physio_sensor' package

- Once the application is set, we can run the ROS2 package.
- Open a terminal
- In the respective ROS2 workspace (e.g. zat_ws1), `source/opt/humble/setup.bash`
- `colcon build`
- `source install/setup.bash`
- `ros2 launch physio_sensor launch.py`

- The andoid device on executing ros2 launch may show a dialog box asking to pair with the system. Allow pairing. Then, the data is transferred and gets published. 


#### Notes

- After ros2 launch, there can be a delay where the system is trying to connect to the Bluetooth android device.
- Ensure permissions are provided to the android application
- There are no hard coded paths anywhere in the code and should work on any system


#### Troubleshooting

- If the package does not build using colcon build, check 
    - whether consor is downloaded in *_ws/src
    - whether zat_ros2_msgs is downloaded in the same folder as consor


- If there is no output after ros2 launch, check
    - whether Bluetooth is switched on, in the system and on the android device
    - whether the name of the android device (currently line: 44 in main.sh) is correctly mentioned in the main.sh (Location: physio_sensor/scripts/main.sh)
    - whether the correct android application is in use (Name of the app: eSense_sdk_2 or eSense SDK 2 Demo)
    - whether `empty` package is installed on the system

