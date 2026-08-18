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


# Description: This script is used to install required dependencies to run the ROS packages for emotibit sensors.
# Author: Jay Parikh <jay.parikh@smail.inf.h-brs.de>


## liblsl package

sudo apt update

sudo apt install -y libpugixml1v5 wget

# wget https://github.com/sccn/liblsl/releases/download/v1.16.2/liblsl-1.16.2-jammy_amd64.deb

# sudo dpkg -i liblsl-1.16.2-jammy_amd64.deb

# sudo apt-get install -f -y


LIBLSL_URL="https://github.com/sccn/liblsl/releases/download/v1.16.2/liblsl-1.16.2-jammy_amd64.deb"

LIBLSL_FILE="liblsl.deb"

# temp directory for downloading the package
TEMP_DIR=$(mktemp -d)

wget -O "$TEMP_DIR/$LIBLSL_FILE" "$LIBLSL_URL"

sudo dpkg -i "$TEMP_DIR/$LIBLSL_FILE"

sudo apt-get install -f -y

# clean up
rm -rf "$TEMP_DIR"


## pylsl package

pip3 install pylsl

