#!/bin/bash

starting_bluetoothctl() {
empty -f -i input -o output -L log_empty.log bluetoothctl
empty -s -o input "power on\n"
empty -s -o input "discoverable on\n"
empty -s -o input "scan on\n"
empty -s -o input "scan off\n"
empty -s -o input "discoverable off\n"
empty -s -o input "devices\n"
}



#### Get name of device from the list of devices & connect to this device
connect_to_device() {
device_name=$1
# https://unix.stackexchange.com/questions/256144/read-a-file-line-by-line-and-if-condition-is-met-continue-reading-till-next-cond
file=$2
IFS='\n'
INPUT=$3
while read -r line; do
    if [[ $line == *"$device_name"* ]] ; then
        printline="yes"
        INPUT=$line
        break        
    fi
done < "$file"

echo "Input: " $INPUT

#### Get the MAC address from the line (containing the device name) extracted earlier 
# https://stackoverflow.com/questions/10586153/how-to-split-a-string-into-an-array-in-bash
IFS=' ' read -r -a array <<< "$INPUT"
for element in "${array[@]}"
do
    # https://stackoverflow.com/questions/4260467/what-is-a-regular-expression-for-a-mac-address
    # https://stackoverflow.com/questions/21112707/check-if-a-string-matches-a-regex-in-bash-script
    if [[ "$element" =~ ^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$ ]]; then
        MAC_ADDRESS=$element
    fi
done

echo "connecting to device with MAC address: " $MAC_ADDRESS
#echo "connecting to device"
empty -s -o input "connect $MAC_ADDRESS\n"

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
    	#echo "$1" 
    	connect_to_device "$1" "$2" "$3"
    	break
    fi
    #sleep 1
done < "$file"

#empty -s -o input "menu gatt\n"
#empty -s -o input "list-attributes \n"
}



# Once a characteristic is read, the script exits gatt menu automatically. Hence, each time we need to go to the gatt menu to read any characteristic
go_to_gatt_menu() {
empty -s -o input "menu gatt\n"
empty -s -o input "list-attributes \n"
}



# select attribute, read characteristic value, add it to a file
read_characteristic() {
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
empty -s -o input "exit\n"
}



# kill process
kill_bluetoothctl_process() {
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
