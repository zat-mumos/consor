# Zat Consor Sync

A ROS 2 package for synchronizing multiple **Consor wearable sensors** and publishing their data as a unified ROS message: `ZatConsorSynch.msg`.

Currently supported sensors:
1. **eSense**  
2. **Movella**  
3. **Emotibit**

---


## Requirements

- ROS 2 Humble 
- Python 3.8+  
- [`zat_ros2_msgs`](https://git.inf.h-brs.de/zat-rhein-ruhr/zat-prototype-demo/zat_ros2_msgs)  

---

## Tested Environment

- **OS:** Ubuntu 22.04  
- **ROS 2:** Humble  
- **Python:** 3.8+  

---

## Installation

Create a new ROS 2 workspace (or use an existing one) and clone the repository:

```bash
mkdir -p ~/zat_ws/src
cd ~/zat_ws/src

# Clone with SSH
git clone git@git.inf.h-brs.de:zat-rhein-ruhr/zat-prototype-demo/consor.git

```
Build the workspace and source it:

```bash
cd ~/zat_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash

```

## Usage

After sourcing the workspace, to run the node:

```bash
ros2 run zat_consor_sync zat_consor

```