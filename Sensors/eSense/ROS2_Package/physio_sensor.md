# physio_sensor

#### Requirements/Dependencies

- zat_ros2_msgs
- Package 'empty' to be installed on the system
- System should have a functioning Bluetooth and Bluetooth should be switched on)


#### Installation of 'empty' & Ros2 packages

- To install empty refer to 'Install_empty.md'


- Download 'consor' repository (anywhere on the system)
- In /home
- Create a workspace (e.g. zat_ws1) and a src folder
- cd zat_ws1/src
- Copy the 'physio_sensor' package/folder in consor to zat_ws1/src
- Download zat_ros2_msgs to zat_ws1/src


#### Use the packages

- Open a terminal
- cd zat_ws1
- source /opt/ros/humble/setup.bash
- colcon build
- source install/setup.bash
- ros2 launch physio_sensor launch.py


#### Notes

- After ros2 launch, it may take some time. The code prints a log and also the data that is published. Ensure that the application named 'eSense_sdk_2' is running (open and all permissions are granted) on the Tablet/Android device. Provide necessary permissions. When ros2 launch is executed, the Tablet/Android device will show a dialog box to pair with the system. After this, the data is transferred and published.


- To test the application, in the eSesnse_sdk_2 application, 
   - Set the sampling rate to 1 or 2 
   - Set Sensor type to any Simulator (e.g. tempSimulator)
   - Click start sampling and this should prompt a dialog box to allow permissions if not already granted
   - Click stop sampling to stop the sampling


- The name of the Tablet/Android device can be changed in scripts/main.sh (currently line:44 in main.sh). The entire code uses relative paths/absolute paths that are found using the code. So it should ideally work on any system without having problems w.r.t paths.


