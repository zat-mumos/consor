#!/bin/bash

source cmds.sh

# https://stackoverflow.com/questions/48167083/how-to-include-bash-scripts-with-relative-path
read_from_file_name='datafile'
#save_file_path="$(dirname "$0")/$read_from_file_name"
save_filepath="./$read_from_file_name"
echo "file: $save_filepath"



remove_file() {

# Remove file if already exists
# https://stackoverflow.com/questions/31318068/shell-script-to-remove-a-file-if-it-already-exist
if [ -f "$1" ]; then
	rm "$1"
	echo "File $1 removed"
fi

}

cleanup () {
empty -s -o gnu_input "exit\n"

disconnect_device "output"

switch_discoverable_off "output"

exit_bluetoothctl

kill_process

remove_file "input"
remove_file "output"
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
# initial checks
remove_file "data"
remove_file "$read_from_file_name"
remove_file "input"
remove_file "output"
remove_file "log_empty.log"
remove_file "log_empty_gnu.log"


empty -f -i gnu_input -o gnu_output -L log_empty_gnu.log gnuplot -p

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
	    if [ "$element" == "0d6d433d-ef16-4543-ac24-c6e08841a56e" ] || [ "$element" == "3cfb298f-3dcb-4be0-b5d4-3cbc0e79cab1" ]; then
	    	read_characteristic "$element" "output" "$save_filepath"
	    else
	    	read_characteristic "$element" "output" ""
	    fi
	    empty -s -o gnu_input "plot '$read_from_file_name' using 1:2 with linespoints\n"
	    go_to_gatt_menu

	done
done

