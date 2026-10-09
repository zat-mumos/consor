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
- Numpy (1.26.4)
- Scikit-learn (v.1.17.2)
- Neurokit2 (v0.2.12)
- PyTorch (v2.2.0)

### Installation

##### Python packages/modules

```
pip install numpy==1.26.4
```
```
pip install neurokit2
```


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

Ensure that the EmotiBit sensor node & the synch nodes are running. To do this, run the following commands in separate terminals.
```
ros2 launch emotibit_sdk launch.py
```

```
ros2 run emotibit_sdk combine_emotibit_modalities
```

```
ros2 run zat_consor_sync zat_consor
```

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

In case of any issues, refer to the Troubleshooting section in the documentation **<< link to documentation section >>**
