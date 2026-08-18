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


# Description: This script is used to communicate with another device and transfer data via BLE.
# Author: Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>

source $(dirname "$0")/cmds.sh

remove_file() {
# Remove file if already exists
# Arguments: 
#		- The name of the file to be removed

# https://stackoverflow.com/questions/31318068/shell-script-to-remove-a-file-if-it-already-exist
if [ -a "$1" ]; then
	rm "$1"
	#echo "File $1 removed"
fi

}

cleanup () {
# Includes steps to be run on keyboard interrupt
# Arguments:
#			None

disconnect_device "output"
switch_discoverable_off "output"
exit_bluetoothctl
kill_bluetoothctl_process
remove_file "input"
remove_file "output"
}


initialisation () {
# Includes steps to initialise variables and remove files from the previous run
# Arguments:
# 			None

sample_data=0
sample_no=0
remove_file "data"
remove_file "$read_from_file_name"
remove_file "input"
remove_file "output"
remove_file "log_empty.log"
}


trap cleanup EXIT

initialisation 

starting_bluetoothctl

connect_to_device "Galaxy Tab S9" "output" "input" "<Device MAC Address>"

go_to_gatt_menu
 
# Sample no, sample data
declare -a array_a=( "0d6d433d-ef16-4543-ac24-c6e08841a56e" "3cfb298f-3dcb-4be0-b5d4-3cbc0e79cab1" )


# https://stackoverflow.com/questions/3737740/is-there-a-better-way-to-run-a-command-n-times-in-bash
while true; do
	IFS=' '
	for element in "${array_a[@]}"
	do
	    if [ "$element" == "0d6d433d-ef16-4543-ac24-c6e08841a56e" ]; then
	    	sampleno=$(read_characteristic "$element" "output" "")
	    elif [ "$element" == "3cfb298f-3dcb-4be0-b5d4-3cbc0e79cab1" ]; then
	    	sampledata=$(read_characteristic "$element" "output" "")
	    else
	    	read_characteristic "$element" "output" ""
	    fi
	    
	    go_to_gatt_menu
	
	done
	echo $sampleno,$sampledata >&1
done

