#!/bin/bash

source $(dirname "$0")/cmds.sh

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
kill_bluetoothctl_process
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

