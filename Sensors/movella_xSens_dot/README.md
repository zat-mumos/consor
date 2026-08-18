# Movella xSens DOT Package

This ROS2 package provides an integration mechanism for working with Movella Xsens Dot Sensors and the Proxy server


### Installation

Follow the steps below to install the Movella PC SDK for python and then the further publisher nodes

### Prerequisites

Ensure you have the following installed:

- ROS VERSION CURRENTLY TESTED ON : ROS2 Humble
- Python 3.x (8,9,10,11)
- Movella SDK. This package lets you connect Movella DOT IMU sensors and stream their data (orientation, acceleration, gyroscope, etc.)
    - Download it from [Xsens Software](https://www.xsens.com/support/software-documentation?hsCtaTracking=39d661fa-2ea8-4478-955e-01d0d8885f14%7C3ad1c7d6-9c3a-42e9-b424-5b15b9d0924e) under the Xsens DOT section, in the "Latest stable software - PC" subsection, and clic on the Linux version.
    - Unzip the Movella SDK package

### Steps to Install

#### 1. Clone the Repository:

- Go inside the zat_ws/src

- Clone the repo:

`git clone https://git.inf.h-brs.de/zat-rhein-ruhr/zat-prototype-demo/consor.git`


#### 2.Install Dependencies:

- Navigate to the movella_xsens_dot package directory

- Make the movella_dependencies.sh executable (chmod +x ./movella_dependencies.sh)

- Navigate to the movella_pkg directory and copy the Movella SDK package here

- Return to movella_xsens_dot package directory and run the bash script 
`./movella_dependencies.sh`


#### 3. Build the ROS2 package:

- Go outside the ~/zat_ws and build the movella package
`colcon build --packages-select movella_pkg`

#### 4. Run the launch file with parameters:

`ros2 launch movella_pkg movella_launch`


