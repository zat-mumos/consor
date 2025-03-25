#!/bin/bash

source /home/user/<path to consor>/consor/cmds.sh

read_from_file_name='datafile.txt'
save_filepath="./$read_from_file_name" 
echo "file: $save_filepath"



remove_file() {

# Remove file if already exists
# https://stackoverflow.com/questions/31318068/shell-script-to-remove-a-file-if-it-already-exist
if [ -a "$1" ]; then
	rm "$1"
	#echo "File $1 removed"
fi

}

cleanup () {
disconnect_device "output"
switch_discoverable_off "output"
exit_bluetoothctl
kill_process
remove_file "input"
remove_file "output"
}


initialisation () {
sample_data=0
sample_no=0
remove_file "data"
remove_file "$read_from_file_name"
remove_file "input"
remove_file "output"
remove_file "log_empty.log"
}

read_metadata() {
# Android API Level
read_characteristic "24e3bd1c-c366-4cda-950b-2b7c46e4a13d" "output" ""

go_to_gatt_menu

# Device name
read_characteristic "00002a00-0000-1000-8000-00805f9b34fb" "output" ""

go_to_gatt_menu

# Manufacturer
read_characteristic "00002a29-0000-1000-8000-00805f9b34fb" "output" ""

go_to_gatt_menu

# Sensor Type
read_characteristic "44e61fc0-0c53-492f-ab20-b86759702bc7" "output" ""

go_to_gatt_menu

# Measuring units
read_characteristic "0e4476c4-a32d-4c93-9686-37e957c5b979" "output" ""

go_to_gatt_menu

# Samples per second
read_characteristic "b46b8c16-55d4-4536-9f90-1074de740d29" "output" ""
}


trap cleanup EXIT

initialisation 

starting_bluetoothctl

connect_to_device "Galaxy Tab S9" "output" "input"

go_to_gatt_menu
 
# Sample no, sample data
declare -a array_a=( "0d6d433d-ef16-4543-ac24-c6e08841a56e" "3cfb298f-3dcb-4be0-b5d4-3cbc0e79cab1" )


# https://stackoverflow.com/questions/3737740/is-there-a-better-way-to-run-a-command-n-times-in-bash
while true; do
	IFS=' '
	for element in "${array_a[@]}"
	do
	    if [ "$element" == "0d6d433d-ef16-4543-ac24-c6e08841a56e" ]; then
	    	sample_no=$(read_characteristic "$element" "output" "")
	    elif [ "$element" == "3cfb298f-3dcb-4be0-b5d4-3cbc0e79cab1" ]; then
	    	sample_data=$(read_characteristic "$element" "output" "")
	    else
	    	read_characteristic "$element" "output" ""
	    fi
	    
	    go_to_gatt_menu
	
	done
	echo $sample_no,$sample_data > $save_filepath
	export var_list="$sample_no,$sample_data"
done

