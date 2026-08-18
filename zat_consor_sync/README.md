# Zat Consor Sync

A ROS 2 package for synchronizing multiple **Consor wearable sensors**.  The data from multiple sensors are:
- batched together and published as a unified ROS message: **ZatConsorSynch.msg**. 
- synchronised and published as a unified ROS message: **SyncData.msg**

Currently supported sensors:
1. **eSense**  
2. **Movella**  
3. **Emotibit**

---


## Requirements

- ROS 2 Humble 
- Python 3.8+  
- [zat_ros2_msgs](https://git.inf.h-brs.de/zat-rhein-ruhr/zat-prototype-demo/zat_ros2_msgs)  

---

## Tested Environment

- **OS:** Ubuntu 22.04  
- **ROS 2:** Humble  
- **Python:** 3.8+  

---

## Installation

Download the latest version of the release. Create a new ROS 2 workspace (or use an existing one) and add the repository to the src folder within the workspace:

```bash
mkdir -p ~/zat_ws/src
cd ~/zat_ws/src
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