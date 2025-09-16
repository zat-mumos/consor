#!/bin/bash

starting_bluetoothctl() {
# Includes steps to be run at the beginning
# Arguments:
#			None

empty -f -i input -o output -L log_empty.log bluetoothctl
empty -s -o input "power on\n"
empty -s -o input "discoverable on\n"
empty -s -o input "scan on\n"
empty -s -o input "scan off\n"
empty -s -o input "discoverable off\n"
empty -s -o input "devices\n"
}



connect_to_device() {
# Get MAC address of the device & connect to this device
# Arguments:
#		- device_name: name of the device that is advertised while scanning for Bluetooth devices (e.g. "Galaxy Tab S9")
# 		- file: input fifo for empty (i.e., "input")
# 		- output: output fifo for empty (i.e., "output")
# 		- fixed_mac_address: the fixed MAC address of the device mentioned in variable device_name (e.g., A1:2B:3C:4D:5E:F6)

device_name=$1
fixed_mac_address=$4
boolean_mac_address="false"
# https://unix.stackexchange.com/questions/256144/read-a-file-line-by-line-and-if-condition-is-met-continue-reading-till-next-cond
file=$2
IFS='\n'

while read -r line2; do
	IFS='\n'
    if [[ $line2 == *"$device_name"* ]] ; then  # If device name found
        printline="yes"

		echo "Input:  $line2"

		#### Get the MAC address from the line (containing the device name) extracted earlier 
		# https://stackoverflow.com/questions/10586153/how-to-split-a-string-into-an-array-in-bash
		IFS=' ' read -r -a array <<< "$line2"
		for element in "${array[@]}"
		do
			# https://stackoverflow.com/questions/4260467/what-is-a-regular-expression-for-a-mac-address
			# https://stackoverflow.com/questions/21112707/check-if-a-string-matches-a-regex-in-bash-script
			if [[ "$element" =~ ^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$ && "$element" != "$fixed_mac_address" ]]; then # get mac address & check if it is not fixed mac address
				MAC_ADDRESS=$element
				boolean_mac_address="true"
				echo "MAC_ADDR: $MAC_ADDRESS"
				break
			fi
		done
	fi

	if [[ "$boolean_mac_address" == "true" ]]; then # If random Mac address found, exit loop
		break
	fi
done < "$file"

echo "connecting to device with MAC address: " $MAC_ADDRESS
empty -s -o input "connect $MAC_ADDRESS\n"

# Wait for a second to allow the device to connect to the system
sleep 1

temp_start=$EPOCHSECONDS
# Check if the device is connected
while read -r line; do
    now=$EPOCHSECONDS
    if [[ "$line" == *" Device $MAC_ADDRESS Connected: yes"* ]]; then
	echo "Connected"
        break
    fi
    # https://stackoverflow.com/questions/27555727/timeouting-a-while-loop-in-linux-shell-script
    #echo "Working to connect ...$now $((EPOCHSECONDS-temp_start))"
    if (( now-temp_start > 3 )); then
    	boolean_connect="false"
    	echo "Retrying due to timeout error ..."
    	exit_bluetoothctl
    	kill_bluetoothctl_process
    	starting_bluetoothctl
    	connect_to_device "$1" "$2" "$3" "$4"
    	break
    fi
done < "$file"

}



go_to_gatt_menu() {
# Includes steps to go to the gatt_menu. Once a characteristic is read, the script exits gatt menu automatically. Hence, each time we need to go to the gatt menu to read any characteristic
# Arguments:
# 			None

empty -s -o input "menu gatt\n"
empty -s -o input "list-attributes \n"
}



read_characteristic() {
# Includes steps to select attribute and read characteristic value. This value can also be saved to a file if needed.
# Arguments:
# 		- uuid: id of characteristic to be read (e.g. 0d6d433d-ef16-4543-ac24-c6e08841a56e)
# 		- file: input fifo for empty (i.e., "input")
#		- save_file_path: path of the file where the characteristic is to be read, leave empty ("") if not to be saved

uuid=$1
file=$2
save_file_path=$3
#echo "filepath: $save_file_path"

uuid_sample_no="0d6d433d-ef16-4543-ac24-c6e08841a56e"
uuid_sample_data="3cfb298f-3dcb-4be0-b5d4-3cbc0e79cab1"

var=0
attr=''
prev=''

while read -r line; do
    lin=$(echo $line | sed -e 's,^[[:blank:]]*,,g') # for removing characters before the attribute
        
    # https://stackoverflow.com/questions/58369763/read-previous-line-using-bash
    if [[ "$lin" == "$uuid" ]]; then
        if [ ! -z "${prev}" ]; then
        	attr="${prev}"
        	line2="${lin}"
        	#echo "uuid: $uuid"
        fi
        break
    fi
    prev="${line}"
done < "$file"

attr=$(echo $attr | sed -e 's,^[[:blank:]]*,,g')
#echo "attribute name: ${attr}"

empty -s -o input "select-attribute $attr\n"

empty -s -o input "attribute-info\n"
empty -s -o input "read\n"

lin="Attribute $attr Value:"
attrVal=''
readAttr=''
while read -r line; do
    if [[ "$line" == *"$lin"* ]]; then
    	readAttr="true"
    	continue
    	echo "'read' completed"
    fi
    
    if [[ "$readAttr" == "true" ]]; then
    	attrVal="$line"
    	#echo "attribute value: "
    	#echo "$attrVal"
    	#echo ''
    	break
    fi
done < "$file"

# Save characteristic values of sample no and sample data to same/separate files to be plotted later
# https://stackoverflow.com/questions/16203088/bash-if-statement-with-multiple-conditions-throws-an-error
if [ "$uuid" == "$uuid_sample_data" ] || [ "$uuid" == "$uuid_sample_no" ]; then
	#aV=$(echo $attrVal | sed -e 's,^[[:blank:]]*,,g')
	aV=$(echo $attrVal | sed -e 's,[[:blank:]]*$,,g')
	# https://stackoverflow.com/questions/22727107/how-to-find-the-last-field-using-cut
	aV=$(echo $aV | rev | cut -d" " -f 1 | rev )
	
	if [[ "$uuid" == "$uuid_sample_no" ]]; then
		#echo "Sample no: $aV"
		# https://stackoverflow.com/questions/12297820/how-to-append-strings-to-the-same-line-instead-of-creating-a-new-line
		echo -n "$aV" #>> "$save_file_path"
	else
		#echo "Sample data: $aV"
		# https://stackoverflow.com/questions/11618696/shell-write-variable-contents-to-a-file
		echo "$aV" #>> "$save_file_path"
		#echo ""
	fi
fi
}



disconnect_device() {
# Includes steps to disconnect device
# Arguments:
# 			file: output fifo for empty (i.e., "output")

file=$1

empty -s -o input "back\n"
empty -s -o input "disconnect \n"

lin="Successful disconnected"
while read -r line; do
    if [[ "$line" == *"$lin"* ]]; then
	echo "Disconnected"
        break
    fi
done < "$file"
}



switch_discoverable_off() {
# Includes steps to switch off the visibility/discoverability of this system to other devices
# Arguments:
# 			file: output fifo for empty (i.e., "output")

file=$1

empty -s -o input "discoverable off\n"

lin="Changing discoverable off succeeded"
while read -r line; do
    if [[ "$line" == *"$lin"* ]]; then
    	echo "Discoverable off"
        break
    fi
done < "$file"
}


exit_bluetoothctl() {
# Include steps to exit bluetoothctl
# Arguments:
# 			None

empty -s -o input "exit\n"
}



# kill process
kill_bluetoothctl_process() {
# Include steps to kill existing bluetooth process using process id
# Arguments:
#			None

VAR1=$(pstree -g | grep bluetoothctl | cut -d '(' -f 3)
pid=$(echo $VAR1 | cut -d ')' -f 1)
# https://stackoverflow.com/questions/48261038/shell-script-how-to-check-if-variable-is-null-or-no
if [[ -n "$pid" ]]; then
	echo $pid
	kill $pid
	echo "Process killed"
fi
echo "done"
}
