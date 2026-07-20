## OpenBCI Documentation

- This repository is specifically for bridging the [OpenBCI sensors](https://openbci.com/) with the publisher node.
- The ROS2 package for publishing OpenBCI data is *openbci_pkg*.

### openbci hardware setup
- Setup the OpenBCI Ganglion board as mentioned in their [documentation](https://docs.openbci.com/GettingStarted/GettingStartedLanding/) 

<br>

## ROS2 package: openbci_pkg

### Requirements & Dependencies

- BLE dongle that is included in the kit
- [brainflow](https://brainflow.readthedocs.io/en/stable/)
- *zat_ros2_msgs*
- *common_functions*

#### Tested Environment

- Ubuntu 22.04 + ROS2 Humble
- Python 3.8 or higher
- brainflow (5.18.0)


### Installation

##### Python packages

`python3 -m pip install brainflow`

Installation instructions can be found on [this](https://brainflow.readthedocs.io/en/stable/BuildBrainFlow.html) page

##### ROS2 packages

- Create a ROS2 workspace using `mkdir -p zat_ws/src` or if a ROS2 workspace already exists then use `cd zat_ws/src`
- In src folder, download **consor** and **zat_ros2_msgs** repositories


### Usage

#### Setting up the OpenBCI sensors
- Go through the documentation for details on how to setup the Ganglion board on [this](https://docs.openbci.com/GettingStarted/GettingStartedLanding/#biosensing-setups) page

#### Running the openbci_pkg

Ensure that the OpenBCI setup is complete (i.e., is as per the documentation) & that the Ganglion board is switched ON.

- Open a terminal
- `cd zat_ws`
- `source /opt/ros/humble/setup.bash`
- `colcon build`
- `source install/setup.bash`
- `ros2 launch openbci_pkg launch_bci.py`

