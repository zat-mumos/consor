# ZAT Prototype Setup

## System requirements

- The CPU should be 64-bit (x86_64) architecture (amd64)
- Ubuntu 22.04 LTS (clean install with full desktop version)
- Internet connectivity (wired or wireless)
- Bluetooth 5.0 or higher (BLE required)
- Sudo access to the machine

## Prerequisites

- Check if git is installed: `sudo apt install git`
- Python 3.7 and above: `python3 --version`
- Check if pip is installed: `sudo apt install python3-pip`
- Check if CMake is installed: `sudo apt install cmake`
- Check if ROS 2 Humble installed: `echo $ROS_DISTRO`
- Configure the GIT identity as our server requires it!

```
git config --global user.name "Your Full Name"
git config --global user.email "your_email@example.com"
```
- Verify the configuration: `git config --global –list`

## SSH setup ([documentation](https://docs.gitlab.com/user/ssh/))

- Generate SSH key for gitlab
- Print the public key and copy it on the gitlab ssh settings
- Check it using: `ssh -T git@git.inf.h-brs.de`

<!-- ## Python Virtual Environment

- Create a new virtual environment (for e.g. `zat_venv`): `python3 -m venv zat_venv`
- Activating the environment: `source zat_venv/bin/activate`
- The new virtual enviroment would not have pip: `pip install --upgrade pip` -->


## Clone Repository (ZAT-Launcher [readme](https://git.inf.h-brs.de/zat-rhein-ruhr/zat-prototype-demo/zat_launcher/-/blob/main/README.md?ref_type=heads))

- Create a workspace folder (for e.g. `zat_ws`): `mkdir -p zat_ws/src && cd zat_ws/src`

- Clone the `zat-launcher` repository (through HTTPS):
```
git clone 'https://git.inf.h-brs.de/zat-rhein-ruhr/zat-prototype-demo/zat_launcher.git'

```

## Installation

- Follow  the zat-launcher [README](../../../zat_launcher/README.md) to install the dependencies and build the project 

### For running all the sensor dependencies installation:

```
cd src/consor/Sensors
chmod +x sensor_dependencies.sh
./sensor_dependencies.sh
```

(_Do not give sudo access to the shell scripts!_)

### For running _ONLY_ the Movella xSens DOT sensor installtion:
```
cd src/consor/Sensors
chmod +x sensor_dependencies.sh
./sensor_dependencies.sh movella
```


### For running _ONLY_ the eSense sensor installtion:
```
cd src/consor/Sensors
chmod +x sensor_dependencies.sh
./sensor_dependencies.sh esense
```

### For running _ONLY_ the EmotiBit sensor installtion:
```
cd src/consor/Sensors
chmod +x sensor_dependencies.sh
./sensor_dependencies.sh emotibit
```

### For running _ONLY_ the OpenBCI sensor installtion:
```
cd src/consor/Sensors
chmod +x sensor_dependencies.sh
./sensor_dependencies.sh openbci
```



## Build the Project

### Source the ROS2 Humble if not added in the bashrc:

`source /opt/ros/humble/setup.bash`
- Build the project using `colcon build` (_outside the workspace!_)

- **If the build fails due to missing ‘vision_msgs’**

Try: `sudo apt install ros-humble-vision-msgs`

- Source the setup.bash : `source install/setup.bash`

**Follow the readme of the respective sub-repositories for launching it**