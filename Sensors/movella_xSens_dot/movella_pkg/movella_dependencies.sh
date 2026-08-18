#!/bin/bash
# © 2026 Hochschule Bonn-Rhein-Sieg <https://www.h-brs.de/>
# 
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
# Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program. If not, see <https://www.gnu.org/licenses/>.


# Description: This script is used to install required dependencies to run the ROS package for movella sensors.
# Author: Jay Parikh <jay.parikh@smail.inf.h-brs.de>


# wheel path select according to the python version 

CURRENT_DIR=$(pwd)

FIXED_WHEEL_PATH="$CURRENT_DIR/movella_xSens_dot/movella_pkg/movella_sdk"

if [[ $(python3 --version) == *"3.10"* ]]; then

    WHEEL_PATH="$FIXED_WHEEL_PATH/movelladot_pc_sdk-2023.6.0-cp310-none-linux_x86_64.whl"

elif [[ $(python3 --version) == *"3.9"* ]]; then
    WHEEL_PATH="$FIXED_WHEEL_PATH/movelladot_pc_sdk-2023.6.0-cp39-none-linux_x86_64.whl"
    
elif [[ $(python3 --version) == *"3.8"* ]]; then
    WHEEL_PATH="$FIXED_WHEEL_PATH/movelladot_pc_sdk-2023.6.0-cp38-none-linux_x86_64.whl"

elif [[ $(python3 --version) == *"3.7"* ]]; then
    WHEEL_PATH="$FIXED_WHEEL_PATH/movelladot_pc_sdk-2023.6.0-cp37-none-linux_x86_64.whl"

else
    echo "Unsupported Python version."
    exit 1
fi

# dependencies installation for movella dot sdk
sudo apt update && sudo apt install -y libsuitesparse-dev

pip3 install pynput

pip3 install "$WHEEL_PATH"