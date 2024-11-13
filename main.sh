#!/bin/bash

source cmds.sh


cleanup () {
empty -s -o gnu_input "exit\n"

disconnect_device "output"

switch_discoverable_off "output"

exit_bluetoothctl

kill_process
 }
 
trap cleanup EXIT

empty -f -i gnu_input -o gnu_output -L log_empty_gnu.log gnuplot -p

starting_bluetoothctl

connect_to_device "Galaxy Tab S9" "output" "input"

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

go_to_gatt_menu

# logical time, real time, carrier amplitude, decoder load pct 
# "e0e2c940-5db3-47c4-88de-32d6ae34187a" "188d76e4-b00e-45f7-9c11-d4d25c10a7d1" "3a5dc305-e506-43ee-8da2-547e5a577886" "aa3e90f8-3b7c-48de-a93a-0c9e034cd429"
 
# Sample no, sample data
declare -a array_a=( "0d6d433d-ef16-4543-ac24-c6e08841a56e" "3cfb298f-3dcb-4be0-b5d4-3cbc0e79cab1" )


# https://stackoverflow.com/questions/3737740/is-there-a-better-way-to-run-a-command-n-times-in-bash
while true; do
	IFS=' '
	for element in "${array_a[@]}"
	do
	    if [ "$element" == "0d6d433d-ef16-4543-ac24-c6e08841a56e" ] || [ "$element" == "3cfb298f-3dcb-4be0-b5d4-3cbc0e79cab1" ]; then
	    	read_characteristic "$element" "output" "/home/user/<path to datafile>/datafile"
	    else
	    	read_characteristic "$element" "output" ""
	    fi
	    empty -s -o gnu_input "plot 'datafile' using 1:2 with linespoints\n"
	    go_to_gatt_menu

	done
done

