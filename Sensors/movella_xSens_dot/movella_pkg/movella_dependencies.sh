#!/bin/bash

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