ZAT Prototype Setup
## 1. System requirements
The CPU should be 64-bit (x86_64) architecture (amd64)
Ubuntu 22.04 LTS (clean install with full desktop version)
Internet connectivity (wired or wireless)
Bluetooth 5.0 or higher (BLE required)
Sudo access to the machine
## 2. Prerequisites
Check if git is installed: sudo apt install git
Python 3.7 and above: (python3 --version)
Check if pip is installed sudo apt install python3-pip
Check if CMake is installed sudo apt install cmake
Check if ROS 2 Humble installed (echo $ROS_DISTRO)
Verify the GIT identity as our server requires it!
git config --global user.name "Your Full Name"
git config --global user.email "your_email@example.com"
Verify the configuration: (git config --global –list)
## 3.  SSH setup (documentation)
Generate SSH key for gitlab
Print the public key and copy it on the gitlab ssh settings
Check it using (ssh -T git@git.inf.h-brs.de)
## 4.  Python Virtual Environment
Create a new virtual environment (for e.g. zat_venv) (python3 -m venv zat_venv)
Activating the environment: source zat_venv/bin/activate
The new virtual enviroment would not have pip: pip install --upgrade pip


## 5.  Clone Repository (ZAT-Launcher readme)
git@git.inf.h-brs.de:zat-rhein-ruhr/zat-prototype-demo/zat_launcher.git
## 6.  Install Dependencies
Make the bash script executable
chmod +x dependencies.sh
./dependencies.sh (Do not give sudo access to the shell scripts! )

### For running the Movella xSens DOT sensors:
cd consor/Sensors/movella_xSens_dot/movella_pkg
chmod +x movella_dependencies.sh
./movella_dependencies.sh (Do not give sudo access to the shell scripts! )

## 7.  Build the Project
### Source the ROS2 Humble if not added in the bashrc:
source /opt/ros/humble/setup.bash
Build the project using colcon build (outside the workspace!)
If the build fails due to missing ‘vision_msgs’
Try: sudo apt install ros-humble-vision-msgs
Source the setup.bash : source install/setup.bash
Follow the readme of the respective sub-repositories for launching it