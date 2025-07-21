## EmotiBit

-  The hardware setup for the EmotiBit sensors are as follows:

![EmotiBit Hardware Setup](Sensors/emotibit/additional_info/EmotiBit-HardwareSetup.png)

<br>

- This repository is specifically for bridging the [EmotiBit sensors](https://www.emotibit.com/) with the publisher node.
- The ROS2 package for publishing EmotiBit data is *emotibit_pkg*.


#### emotibit folder contents

- additional_info: Includes any other documentation such as images, code etc.
- emotibit_pkg: ROS2 package for EmotiBit

<br>

## ROS2 package: emotibit_pkg

### Requirements & Dependencies

- WiFi connectivity ***(EmotiBit and the Linux System must be connected to the same WiFi)***
- EmotiBitOscilloscope (Installed along with the EmotiBit Software) <!-- ([Link to the webpage with installation steps](https://github.com/EmotiBit/EmotiBit_Docs/blob/master/Getting_Started.md#installing-emotibit-software)) -->
- Conda environment (for installation of liblsl)
- [liblsl](https://github.com/sccn/liblsl)
- [pylsl](https://github.com/labstreaminglayer/pylsl)
- *zat_ros2_msgs*

#### Tested Environment

- Ubuntu 22.04 + ROS2 Humble
- Python 3.8 or higher
- ofxEmotiBit ([v1.11.4](https://github.com/EmotiBit/ofxEmotiBit/releases/tag/v1.11.4))  < Software code for EmotiBit
- OpenFrameworks ([v0.11.12](https://github.com/openframeworks/openFrameworks/releases/tag/0.11.2))  < One of the requirements of ofxEmotiBit

***Go through the README.md of the ofxEmotiBit repository for other dependencies. This should have already been installed when setting up the EmotiBitOscilloscope. The steps to install the EmotiBitOscilloscope is mentioned in the next section.***


### Installation

##### EmotiBit Oscilloscope

- Follow the steps mentioned in the [EmotiBit documentation](https://github.com/EmotiBit/EmotiBit_Docs/blob/master/Getting_Started.md/#Installing-EmotiBit-Software).

##### Python packages

- Pylsl: `pip install pylsl`
- Liblsl: `conda install -c conda-forge liblsl`

##### ROS2 packages

- Create a ROS2 workspace using `mkdir -p zat_ws/src` or if a ROS2 workspace already exists then use `cd zat_ws/src`
- In src folder, download **consor** and **zat_ros2_msgs** repositories


### Usage

##### Setting up EmotiBit sensors
- Assuming that the EmotiBit software is already installed and WiFi credentials are added to the config file,
- Switch on the EmotiBit sensors (Either connect a Battery to the sensor or use the USB cable to connect to the linux system to power it on)
- Once the EmotiBit sensors are connected to the WiFi, a Blue LED light will turn on in the sensor board
- Ensure that the system is connected to the same WiFi as the EmotiBit. (There is no way to know which WiFi the EmotiBit is connected to. The system should be connected to the WiFi mentioned in the config file of the EmotiBit sensors).
- Open a new terminal
- `cd ~/of_v0.11.2_linux64gcc6_release/addons/ofxEmotiBit/EmotiBitOscilloscope/bin`
- `./EmotiBitOscilloscope`
- This command opens a UI for the EmotiBit. If the steps above are correctly followed, then signals/data can be seen in this UI.
- Click on the **Output List** icon and select **LSL**

##### Running the emotibit_pkg

###### Get the liblsl path
- We use `pylsl` library which depends on `liblsl`. However, `liblsl` is not found outside the conda environment, causing errors when running the ROS node outside the environment.
- Hence, we want to export the path for the code to find `liblsl` when it runs. To do this, 
    1. Activate an existing conda environment using `conda activate <environment name>` or create a new environment using `conda create --name <new env name> --clone <existing environment such as base>` and once created, activate this new environment
    2. Install `pylsl` and `liblsl` using commands mentioned in previous section.
    3. `conda deactivate`
    4. Run the command `find / -name "liblsl.so*" 2>/dev/null` This command returns the path where this library is installed.<br> 
    For example, */home/<user>/anaconda3/envs/<environment-name>/lib/liblsl.so*


###### Running the ROS node
- `cd zat_ws`
- `source /opt/ros/humble/setup.bash`
- `export LD_LIBRARY_PATH=<path to liblsl found in step 4 of Get the liblsl path>:$LD_LIBRARY_PATH` This adds the path to the library liblsl to the list of paths that the system will search. Also, in any terminal where this package is to be run, this command should be run similar to how ros2 is sourced.<br>
For example, *export LD_LIBRARY_PATH=/home/<user>/anaconda3/envs/<environment-name>/lib:$LD_LIBRARY_PATH*. Note that we only gave the folder name and not the file name here.
- `colcon build`
- `ros2 launch emotibit_pkg launch.py` Ensure **LSL** is enabled on the EmotiBitOscilloscope before running this command.


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
- If the WiFi connected blue LED is blinking but no EmotiBit found in Oscilloscope, ensure you or the system is connected to the correct WiFi.
- If data is not getting transferred via LSL, ensure in the Output List, LSL is selected before running any other script.
