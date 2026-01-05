# Consor: Connectivity for Sensor Network

### Introduction
The overall idea of this repository is to act as generalized middleware component mainly designed to connect different sensor drivers with a ROS Node on different modes of communication (such as Bluetooth, WiFi, etc.)


All supported sensors have a publisher that publishes the sensor data to specific ROS Topics.

This repository also contains a wiki with information specific to the each sensor and can be found [here](https://git.inf.h-brs.de/zat-rhein-ruhr/zat-prototype-demo/consor/-/wikis/home)

##### Compatibility
- **Supported Sensors**: eSense, Movella xsense dot, EmotiBit, OpenBCI <!--Compatible with eSense sensor Network  -->
- **ROS Compatibility**: Compatible with ROS2 Humble
- **Customizable**: Extendable to support additional sensors


##### Repository folder contents

Sensors currently supported by this repository have a separate folder and can be found in _Sensors_ directory. These sensors are as follows:

1. eSense
2. Movella xsense dot
3. EmotiBit
4. OpenBCI

To synchronise the sensors and publish it as a single ros2 message a Ros2 node can be found in the `zat_consor_synch` folder


##### Repository branches

- main: Consists of the most recent code for the aforementioned supported sensors

The current requirement is to publish the sensor data to a ROS node and this code is continuously updated in the *main* branch. 

### Installation & Usage

The installation and usage details are dependent on the sensors and can be found in the READMEs for each sensor in the _Sensors_ directory or using the links mentioned below:

1. [eSense README](Sensors/esense)
2. [Movella README](Sensors/movella_xSens_dot)
3. [EmotiBit README](Sensors/emotibit)
4. [OpenBCI README](Sensors/openbci)

For installing and running the synchronisation node follow the steps in the README file in folder `zat_consor_synch` or using this link
1. [zat_consor_synch](zat_consor_sync)


<!-- This section is more like common steps to follow, we can add it later with detail steps once we have more clarity on how sensors will be configured and so on

### Important Notes
- Make sure to start the specific mode of communication for the required sensors (e.g. WiFi, Bluetooth, etc.)
- Ensure all sensor drivers are properly installed and configured before using the bridge
- Correct File path, location and the workspace of the developed package with appropriate ROS sourcing needs to be done
- Verify that the ROS environment is correctly set up
- Use the correct topic names and message types for your application (Refer specific sensor Readme!)
- Test the bridge thoroughly in a controlled environment before deploying it 
-->


### Development in Pipeline

Integration with other sensors including

- Movella xsense dot IMU sensors
- OpenBCI & Emotibit
<!-- - eSense pulse sensor

- Sensor integration with IMU sensors ([Movella Xsens DOT] (https://www.movella.com/products/wearables/movella-dot) )
- Sensor integration with pulse sensor -->

<!-- 
### Known Issues
- TBD 
 -->

<!-- - Major focus is to simplify the integration of the sensor network with ROS ecosystem giving ROS Topics as endpoints for further integration  -->


### Contributors

- Jay Parikh
- Oviya Rajavel
- Swathy Cheruvalath
