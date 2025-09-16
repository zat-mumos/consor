# Introduction

- This repository is specifically for bridging the [eSense physiological sensors](https://mindfield-esense.com/ )  with the publisher node using **bluetoothctl**. 

- The hardware setup for these sensors are as follows:

![eSense Hardware Setup](Sensors/esense/misc/Images/eSense_HardwareSetup_BLE.png)

<br>

- The ROS2 package for publishing eSense sensor data is *physio_sensor*.
- When the data is transferred via **Bluetooth**, then the **physio_sensor** ROS2 package should be used.



#### esense_ble folder contents

- docs: Includes documentation about the ROS2 package and bluetoothctl bash scripts
- physio_sensor: ROS2 package for eSense when data is transferred via BLE (Bluetooth Low Energy).


# physio_sensor Package

### Requirements/Dependencies

- *zat_ros2_msgs*
- *empty* should be installed on the system. (Refer below to section Installation: 'empty' package for steps to install this package.)
- Bluetooth must be functioning and switched on (on the system and the Android device)

### Tested environment 

- Ubuntu 20.04, 22.04
- ROS2 (foxy, humble)
- Python 3.8 or higher
- System Bluetooth version 5.2 & Android Bluetooth version 5.3

### Installation

##### 'empty' package

- Download the package using (https://sourceforge.net/projects/empty/) or use an existing/already downloaded zip file of the empty package
- The code is tested with empty-0.6.23c 
- Extract the zip folder for the *empty* package. Move this folder to **home** directory
- Open a terminal
- `cd empty-0.6.23c`
- `make`
- `sudo make install`


- To check if **empty** is installed, 
    - Open a terminal
    - either use `man empty` to see the manual pages for empty
    - or `which empty` to see the location where empty is installed
    - or `empty -v` to see the version of empty that is installed


##### ROS2 packages

- Create a ROS2 workspace using `mkdir -p zat_ws/src` or if a ROS2 workspace already exists use `cd zat_ws/src` 
- In src, download **consor** repository and **zat_ros2_msgs** package


### Usage/Steps

##### Steps to run the eSense android application

- Name of the working eSense application: ***eSense_sdk_2*** 
- Ensure *Nearby Devices* permissions are granted to the eSense application since the communication happens via Bluetooth.
- Open the application on the android device.  
- To test the application, follow the steps:
    - Set the sampling rate (to 1 or 2 Hz for simplicity)
    - Set sensor type to any sensor (If not connected to any sensor, then set the sensor type to a simulator e.g. tempSimulator)
    - Click start sampling. This should prompt a dialog box asking to allow permissions if not already granted. If the sampling does not start after granting permission, click start sampling again. 
    - Click stop sampling to stop the sampling. 


##### Steps to run the 'physio_sensor' package

- Once the application is set, we can run the ROS2 package.
- Open a terminal
- In the respective ROS2 workspace (e.g. zat_ws1), `source /opt/ros/humble/setup.bash`
- `colcon build`
- `source install/setup.bash`
- `ros2 launch physio_sensor launch.py`

- The andoid device on executing ros2 launch may show a dialog box asking to pair with the system. Allow pairing. Then, the data is transferred and gets published. 


##### Notes

- After ros2 launch, there can be a delay where the system is trying to connect to the Bluetooth android device.
- Ensure permissions are provided to the android application
- There are no hard coded paths anywhere in the code and should work on any system


##### Troubleshooting

- If the package does not build using colcon build, check 
    - whether consor is downloaded in *_ws/src
    - whether zat_ros2_msgs is downloaded in the same folder as consor (i.e., in *_ws/src)


- If there is no output after ros2 launch, check
    - whether Bluetooth is switched on, in the system and on the android device
    - whether the name of the android device (currently line: 44 in main.sh) is correctly mentioned in the main.sh (Location: physio_sensor/scripts/main.sh)
    - whether the correct android application is in use (Name of the app: eSense_sdk_2 or eSense SDK 2 Demo)
    - whether *empty* package is installed on the system (refer to above section Installation: 'empty' package)


- If the eSense_SDK_2 application does not open/crashes, go to the app settings on the android device and enable *Nearby Devices* permissions. Also check if Bluetooth is enabled on the device and if Bluetooth is OFF, switch Bluetooth ON.