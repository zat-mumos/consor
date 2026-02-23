# Introduction

- This repository is specifically for bridging the [eSense physiological sensors](https://mindfield-esense.com/ )  with the publisher node using **pylsl**.

- The hardware setup for these sensors are as follows:

![eSense Hardware Setup](Sensors/esense/misc/Images/eSense_HardwareSetup_LSL.png)

<br>

- The ROS2 package for publishing eSense sensor data is *esense_pkg*.
- When the data is transferred via **Lab Streaming Layer (LSL)**, then the **esense_pkg** ROS2 package should be used.

#### esense_lsl folder contents

- esense_pkg: ROS2 package for eSense

# esense_pkg Package

### Requirements/Dependencies

- WiFi connectivity ***(eSense and the Linux System must be connected to the same WiFi/Network)***
- [zat_ros2_msgs](https://git.inf.h-brs.de/zat-rhein-ruhr/zat-prototype-demo/zat_ros2_msgs)
- [pylsl](https://github.com/labstreaminglayer/pylsl)
- [liblsl](https://github.com/sccn/liblsl)
- Either conda environment (for installation of liblsl) or the source code (.deb) for liblsl from the [release](https://github.com/sccn/liblsl/releases) page.

### Tested environment 

- Ubuntu 22.04 + ROS2 Humble
- Python 3.8 or higher
- pylsl (v1.17.6)
- liblsl ([v1.16.2](https://github.com/sccn/liblsl/releases/tag/v1.16.2)) < Requirement for pylsl library

### Installation

- Pylsl: `pip install pylsl`
- Liblsl: There are 2 ways to install this.
    - Option 1: (Conda installation is required.)
        1. Activate an existing conda environment using `conda activate <environment name>` or create a new environment using `conda create --name <new env name> --clone <existing environment such as base>` and once created, activate this new environment
        2. `conda install -c conda-forge liblsl`
    - Option 2:
        1. Go to the [liblsl GitHub repository](https://github.com/sccn/liblsl).
        2. Navigate to the [Release page](https://github.com/sccn/liblsl/releases)
        3. Download the .deb file specific to your system.  (For example, if the system is Jammy, download: liblsl-1.16.2-jammy_amd64.deb)
        4. Go to the Downloads folder and open a terminal
        5. Run the command: `sudo dpkg -i liblsl-1.16.2-jammy_amd64.deb`

##### ROS2 packages

- Create a ROS2 workspace using `mkdir -p zat_ws/src` or if a ROS2 workspace already exists use `cd zat_ws/src` 
- In src, download **consor** and **zat_ros2_msgs** repositories.
    - If GitLab is [setup preferably with SSH](https://docs.gitlab.com/user/ssh/) and access to [zat_ros2_msgs](https://git.inf.h-brs.de/zat-rhein-ruhr/zat-prototype-demo/zat_ros2_msgs) is granted then clone the repositories using the following command:
        ```
        # Clone zat_ros2_msgs repository
        git clone git@git.inf.h-brs.de:zat-rhein-ruhr/zat-prototype-demo/zat_ros2_msgs.git

        # Clone consor repository
        git clone git@git.inf.h-brs.de:zat-rhein-ruhr/zat-prototype-demo/consor.git
        ```
    - If GitLab is not setup, then manually download the repositories.


### Usage/Steps

##### Steps to run the eSense android application

- Name of the working eSense application: ***eSense_sdk_2*** 
- Open the application on the android device.  
- To test the application, follow the steps:
    - Set the sampling rate (to 1 or 2 Hz for simplicity)
    - Set sensor type to any sensor (If not connected to any sensor, then set the sensor type to a simulator e.g. tempSimulator)
    - Click start sampling.  This should prompt a dialog box asking to allow permissions if not already granted.  If the sampling does not start after granting permission, click start sampling again. 
    - Click stop sampling to stop the sampling. 


##### Steps to run the 'esense_pkg' package


###### *Follow these steps if 'liblsl' was installed using Option 1 (in the section above).  (Scroll down to see how to run the emotibit_pkg in case 'liblsl' was installed using Option 2)*

1. Get the liblsl path
- We use `pylsl` library which depends on `liblsl`.  However, `liblsl` is not found outside the conda environment, causing errors when running the ROS node outside the environment.
- Hence, we want to export the path for the code to find `liblsl` when it runs.  To do this, 
    1. Activate an existing conda environment using `conda activate <environment name>` or create a new environment using `conda create --name <new env name> --clone <existing environment such as base>` and once created, activate this new environment
    2. Install `pylsl` and `liblsl` using commands mentioned in previous section.
    3. `conda deactivate`
    4. Run the command `find / -name "liblsl.so*" 2>/dev/null` This command returns the path where this library is installed.<br> 
    For example, */home/<user>/anaconda3/envs/<environment-name>/lib/liblsl.so*

2. Running the ROS node
- `cd zat_ws`
- `source /opt/ros/humble/setup.bash`
- `export LD_LIBRARY_PATH=<path to liblsl found in step 4 of Get the liblsl path>:$LD_LIBRARY_PATH` This adds the path to the library liblsl to the list of paths that the system will search.  Also, in any terminal where this package is to be run, this command should be run similar to how ros2 is sourced.<br>
For example, *export LD_LIBRARY_PATH=/home/\<user\>/anaconda3/envs/\<environment-name\>/lib:$LD_LIBRARY_PATH*.  Note that we only gave the folder name and not the file name here.
- `colcon build`
- `source install/setup.bash`
- `ros2 launch esense_pkg launch.py`

###### *Follow these steps if 'liblsl' was installed using Option 2 (in the section above)*

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
