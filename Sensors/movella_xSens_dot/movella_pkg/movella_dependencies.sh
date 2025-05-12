#!/bin/bash

# wheel path select according to the python version 

if [[ $(python3 --version) == *"3.10"* ]]; then
    WHEEL_PATH="./movella_sdk/movelladot_pc_sdk-2023.6.0-cp310-none-linux_x86_64.whl"

elif [[ $(python3 --version) == *"3.9"* ]]; then
    WHEEL_PATH="/movella_sdk/movelladot_pc_sdk-2023.6.0-cp39-none-linux_x86_64.whl"
    
elif [[ $(python3 --version) == *"3.8"* ]]; then
    WHEEL_PATH="/movella_sdk/movelladot_pc_sdk-2023.6.0-cp38-none-linux_x86_64.whl"

elif [[ $(python3 --version) == *"3.7"* ]]; then
    WHEEL_PATH="/movella_sdk/movelladot_pc_sdk-2023.6.0-cp37-none-linux_x86_64.whl"

else
    echo "Unsupported Python version."
    exit 1
fi

pip install "$WHEEL_PATH"

