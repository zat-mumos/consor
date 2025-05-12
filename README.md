# Consor: Connectivity for Sensor Network

### Introduction
- The repository idea is to act as a generalized middleware component mainly designed to connect sensor drivers with a ROS Node on different modes of communication 
- Each sensor will have a Publisher with important ROS Topics to directly subscribe to the sensor data
- Major focus is to simplify the integration of the sensor network with ROS ecosystem giving ROS Topics as endpoints for further integration 


### Repository branches

- main: Consists of the most recent code for eSense and Movella sensors

The current requirement is to publish the sensor data to a ROS node and this code exists in the *main* branch.


### Compatibility
- **Supported Sensors**: Compatible with eSense sensor Network 
- **ROS Compatibility**: Compatible with ROS2 (foxy, humble)
- **Customizable**: Extendable to support additional sensors


### Important Notes
- Make sure to start the specific mode of communication for the required sensors (e.g. WiFi, Bluetooth, etc.)
- Ensure all sensor drivers are properly installed and configured before using the bridge
- Correct File path, location and the workspace of the developed package with appropriate ROS sourcing needs to be done
- Verify that the ROS environment is correctly set up
- Use the correct topic names and message types for your application (Refer specific sensor Readme!)
- Test the bridge thoroughly in a controlled environment before deploying it


### Development in Pipeline

- Sensor integration with IMU sensors ([Movella Xsens DOT] (https://www.movella.com/products/wearables/movella-dot) )
- Sensor integration with pulse sensor


### Known Issues
- TBD