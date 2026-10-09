# zat_stress
This repository includes ROS2 packages and nodes related to processing the signals for stress detection and predicting labels.  This pipeline is divided into 3 parts.  Each with its own node.  They are:
1. Extract features
2. Predict/Infer labels
3. Get responses based on the predictions 

## ROS2 Package: zat_stress

### Requirements & Dependencies

This package integrates code from repository [Stress-Management-using-Physiological-Signals-and-conversational-agents](https://github.com/prachi0711/Stress-Management-using-Physiological-Signals-and-conversational-agents.git).  The required files from this repository is added in a separate *vendor* folder along with its LICENSE.

### Tested Environment

- Ubuntu 22.04 + ROS2 Humble
- Python 3.10
- Scikit-learn (v.1.17.2)

### Installation

##### ROS2 packages

- Create a ROS2 workspace
```
mkdir -p zat_ws/src
```
- If a ROS2 workspace is created or already exists, go to the workspace
```
cd zat_ws/src
```
- In the `src` folder, add `consor` repository (included in the **<< link to releases >>**)
- Build and source the workspace
```
cd ~/zat_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

### Usage

Once the workspace is sourced, the commands can be used to run the node are mentioned below.

##### To Extract Features, run

```
ros2 run zat_stress extract_features
```

##### To Infer/Predict Labels, run

```
ros2 run zat_stress predict_labels
```

##### To Get Responses based on predictions, run

```
ros2 run zat_stress get_response
```
