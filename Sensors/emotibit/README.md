## EmotiBit

- This repository is specifically for bridging the [EmotiBit sensors](https://www.emotibit.com/) with the publisher node.
- The ROS2 package for publishing EmotiBit data is *emotibit_pkg*.

### emotibit hardware setup
- There are two ways in which the EmotiBit sensors can be set up. The hardware setup for the EmotiBit sensors are as follows:


#### Option A:

![EmotiBit Hardware Setup A](Sensors/emotibit/additional_info/images/EmotiBit-HardwareSetupA.png)

<br>

In this setup, there is a single linux system that runs the EmotiBit Oscilloscope and the ROS node. The EmotiBit sensors and the Linux system are connected to the same WiFi.

#### Option B:

![EmotiBit Hardware Setup B](Sensors/emotibit/additional_info/images/EmotiBit-HardwareSetupB.png)

<br>

In this setup, there are two linux systems (Device A and Device B) where Device A runs the EmotiBit Oscilloscope and Device B runs the ROS node. The EmotiBit sensors and both linux systems are connected to the same WiFi. While testing this setup, we set up a common WiFi hotspot for these three devices.

#### emotibit folder contents

- additional_info: Includes any other documentation such as images, code etc.
- emotibit_pkg: ROS2 package for EmotiBit

<br>

## ROS2 package: emotibit_pkg

### Requirements & Dependencies

- WiFi connectivity ***(EmotiBit and the Linux System(s) must be connected to the same WiFi)***
- EmotiBitOscilloscope (Installed along with the EmotiBit Software) <!-- ([Link to the webpage with installation steps](https://github.com/EmotiBit/EmotiBit_Docs/blob/master/Getting_Started.md#installing-emotibit-software)) -->
- [pylsl](https://github.com/labstreaminglayer/pylsl)
- [liblsl](https://github.com/sccn/liblsl)
- Either conda environment (for installation of liblsl) or the source code (.deb) for liblsl from the [release](https://github.com/sccn/liblsl/releases) page.
- *zat_ros2_msgs*

#### Tested Environment

- Ubuntu 22.04 + ROS2 Humble
- Python 3.8 or higher
- ofxEmotiBit ([v1.11.4](https://github.com/EmotiBit/ofxEmotiBit/releases/tag/v1.11.4))  < Software code for EmotiBit
- OpenFrameworks ([v0.11.12](https://github.com/openframeworks/openFrameworks/releases/tag/0.11.2))  < One of the requirements of ofxEmotiBit
- pylsl (v1.17.6)
- liblsl ([v1.16.2](https://github.com/sccn/liblsl/releases/tag/v1.16.2)) < Requirement for pylsl library

***Go through the README.md of the ofxEmotiBit repository for other dependencies. This should have already been installed when setting up the EmotiBitOscilloscope. The steps to install the EmotiBitOscilloscope is mentioned in the next section.***


### Installation

##### EmotiBit Oscilloscope

- Follow the steps mentioned in the [EmotiBit documentation](https://github.com/EmotiBit/EmotiBit_Docs/blob/master/Getting_Started.md/#Installing-EmotiBit-Software).

##### Python packages

- Pylsl: `pip install pylsl`
- Liblsl: There are 2 ways to install this.
    - Option 1: (Conda installation is required.)
        1. Activate an existing conda environment using `conda activate <environment name>` or create a new environment using `conda create --name <new env name> --clone <existing environment such as base>` and once created, activate this new environment
        2. `conda install -c conda-forge liblsl`
    - Option 2:
        1. Go to the [liblsl GitHub repository](https://github.com/sccn/liblsl).
        2. Navigate to the [Release page](https://github.com/sccn/liblsl/releases)
        3. Download the .deb file specific to your system. (For example, if the system is Jammy, download: liblsl-1.16.2-jammy_amd64.deb)
        4. Go to the Downloads folder and open a terminal
        5. Run the command: `sudo dpkg -i liblsl-1.16.2-jammy_amd64.deb`

##### ROS2 packages

- Create a ROS2 workspace using `mkdir -p zat_ws/src` or if a ROS2 workspace already exists then use `cd zat_ws/src`
- In src folder, download **consor** and **zat_ros2_msgs** repositories


### Usage

#### Setting up EmotiBit sensors
- Assuming that the EmotiBit software is already installed and WiFi credentials are added to the config file,
- Switch on the EmotiBit sensors (Either connect a Battery to the sensor or use the USB cable to connect to the linux system to power it on)
- Once the EmotiBit sensors are connected to the WiFi, a Blue LED light will turn on in the sensor board
- Ensure that the system is connected to the same WiFi as the EmotiBit. (There is no way to know which WiFi the EmotiBit is connected to. The system should be connected to the WiFi mentioned in the config file of the EmotiBit sensors).
- Open a new terminal
- `cd ~/of_v0.11.2_linux64gcc6_release/addons/ofxEmotiBit/EmotiBitOscilloscope/bin`
- `./EmotiBitOscilloscope`
- This command opens a UI for the EmotiBit. If the steps above are correctly followed, then signals/data can be seen in this UI.
- Click on the **Output List** icon and select **LSL**

#### Running the emotibit_pkg

##### *Follow these steps if 'liblsl' was installed using Option 1 (in the section above). (Scroll down to see how to run the emotibit_pkg in case 'liblsl' was installed using Option 2)*

1. Get the liblsl path
- We use `pylsl` library which depends on `liblsl`. However, `liblsl` is not found outside the conda environment, causing errors when running the ROS node outside the environment.
- Hence, we want to export the path for the code to find `liblsl` when it runs. To do this, 
    1. Activate an existing conda environment using `conda activate <environment name>` or create a new environment using `conda create --name <new env name> --clone <existing environment such as base>` and once created, activate this new environment
    2. Install `pylsl` and `liblsl` using commands mentioned in previous section.
    3. `conda deactivate`
    4. Run the command `find / -name "liblsl.so*" 2>/dev/null` This command returns the path where this library is installed.<br> 
    For example, */home/<user>/anaconda3/envs/<environment-name>/lib/liblsl.so*

2. Running the ROS node
- `cd zat_ws`
- `source /opt/ros/humble/setup.bash`
- `export LD_LIBRARY_PATH=<path to liblsl found in step 4 of Get the liblsl path>:$LD_LIBRARY_PATH` This adds the path to the library liblsl to the list of paths that the system will search. Also, in any terminal where this package is to be run, this command should be run similar to how ros2 is sourced.<br>
For example, *export LD_LIBRARY_PATH=/home/\<user\>/anaconda3/envs/\<environment-name\>/lib:$LD_LIBRARY_PATH*. Note that we only gave the folder name and not the file name here.
- `colcon build`
- `source install/setup.bash`
- `ros2 launch emotibit_pkg launch.py` Ensure **LSL** is enabled on the EmotiBitOscilloscope before running this command.


##### *Follow these steps if 'liblsl' was installed using Option 2 (in the section above)*

- Running the ROS node
    - `cd zat_ws`
    - `source /opt/ros/humble/setup.bash`
    - `colcon build`
    - `source install/setup.bash`
    - `ros2 launch emotibit_pkg launch.py` Ensure **LSL** is enabled on the EmotiBitOscilloscope before running this command.



###### Notes

- Ensure that all devices (EmotiBit sensors + Linux system(s)) are all connected to the same WiFi. If there are any problems, try troubleshooting. Some troubleshooting steps are mentioned at the end of this README.

### Additional Info

##### additional_code

The folder named *Additional_code* within the *additional_info* folder contains independent python files to get the names of the channels, metadata and the sample. The names of these files and their usage is mentioned in the sections below.
 
###### Contents

- get_data_channels.py
- get_data.py
- get_metadata.py

###### Usage

- Run the EmotibitOscilloscope
- Ensure that EmotiBit is connected to the Oscilloscope
- Select LSL as the Output type
- Run the python file using `~/<path to file>/<file name>`


##### Troubleshooting

- If the package does not build using colcon build, check 
    - whether consor is downloaded in *_ws/src
    - whether zat_ros2_msgs is downloaded in the same folder as consor (i.e., in *_ws/src)
- If the WiFi connected blue LED is blinking but no EmotiBit found in Oscilloscope, 
    - Ensure you or the system is connected to the correct WiFi.
    - If there are multiple networks that are configured on the EmotiBit config file, ensure that the credentials for the network that the Linux system(s) is connected to is at the beginning of all other networks.
    - If still facing issues, try connecting all devices (EmotiBit sensors + Linux system(s)) to a local WiFi hotspot. 
- If data is not getting transferred via LSL, ensure in the Output List, LSL is selected before running any other script.

