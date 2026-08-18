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


# Description: This script is used to install required dependencies to run the ROS packages for
#        all the sensors (movella, esense, openbci, emotibit).
# Author: Jay Parikh <jay.parikh@smail.inf.h-brs.de>


SENSOR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Sensor script paths

MOVELLA_DEPENDENCY_DIR="$SENSOR_DIR/movella_xSens_dot/movella_pkg/movella_dependencies.sh"

eSense_DEPENDENCY_DIR="$SENSOR_DIR/esense/esense_ble/esense_dependencies.sh"

DEFAULT_SCRIPTS=("$MOVELLA_DEPENDENCY_DIR" "$eSense_DEPENDENCY_DIR")


if [ $# -eq 0 ]; then
    echo "Install dependencies for all sensors"
    for script in "${DEFAULT_SCRIPTS[@]}"; do

        if [ -f "$script" ]; then
            echo "Running dependency script: $script"
            bash "$script"
        else
            echo "Dependency script not found: $script"
        fi

    
    done

else
    for sensor in "$@"; do
        case $sensor in
            "movella")
                if [ -f "$MOVELLA_DEPENDENCY_DIR" ]; then
                    echo "Running dependency script for Movella"
                    pip install -r "$SENSOR_DIR/sensor_requirements.txt"
                    bash "$MOVELLA_DEPENDENCY_DIR"
                    
                else
                    echo "Movella dependency script not found"
                fi
                ;;
            "esense")
                if [ -f "$eSense_DEPENDENCY_DIR" ]; then
                    echo "Running dependency script for eSense"
                    pip install -r "$SENSOR_DIR/sensor_requirements.txt"
                    bash "$eSense_DEPENDENCY_DIR"
                else
                    echo "eSense dependency script not found"
                fi
                ;;

            "openbci")
                echo "Running dependency script for OpenBCI"
                pip install -r "$SENSOR_DIR/sensor_requirements.txt"
                ;;

            "emotibit")
                echo "Running dependency script for emotibit"
                pip install -r "$SENSOR_DIR/sensor_requirements.txt"
                ;;

            *)
                echo "Unknown sensor: $sensor"
                echo "Available sensors: movella, esense, emotibit, openbci"
                ;;
        esac
    done
fi


