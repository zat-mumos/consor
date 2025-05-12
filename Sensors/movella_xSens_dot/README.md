# Movella xSens DOT Package

This ROS2 package provides an integration mechanism for working with Movella Xsens Dot Sensors and the Proxy server


### Installation

Follow the steps below to install the Movella PC SDK for python and then the further publisher nodes

### Prerequisites

Ensure you have the following installed:

- ROS VERSION CURRENTLY TESTED ON : ROS2 Humble
- Python 3.x (8,9,10,11)

### Steps to Install

#### 1. Clone the Repository:

- go inside the zat_ws/src

- git clone https://git.inf.h-brs.de/zat-rhein-ruhr/zat-prototype-demo/consor.git 


#### 2.Install Dependencies:

- Navigate to the movella_xsens_dot package directory

- make the movella_dependencies.sh executable (chmod +x ./movella_dependencies.sh)

- run the bash script (./movella_dependencies.sh)


#### 3. Build the ROS2 package:

- go outside the ~/zat_ws and try colcon build --packages-select movella_pkg

#### 4. Run the launch file with parameters:

- ros2 launch movella_pkg movella_launch.py


