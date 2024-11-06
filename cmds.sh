#!/bin/bash

echo "starting bluetoothctl"
empty -f -i input -o output -L log_empty.log bluetoothctl
empty -s -o input "power on\n"
empty -s -o input "discoverable on\n"
empty -s -o input "scan on\n"
empty -s -o input "scan off\n"
empty -s -o input "discoverable off\n"
empty -s -o input "devices\n"


#### Get name of device from the list of devices

echo "get device mac address"
device_name="Galaxy Tab S9"
# https://unix.stackexchange.com/questions/256144/read-a-file-line-by-line-and-if-condition-is-met-continue-reading-till-next-cond
file="output"
IFS='\n'
INPUT='input'
while read -r line; do
    if [[ $line == *"$device_name"* ]] ; then
        printline="yes"
        INPUT=$line
        break        
    fi
done < "$file"

echo $INPUT


#### Get the MAC address from the line (containing the device name) extracted earlier 

# https://stackoverflow.com/questions/10586153/how-to-split-a-string-into-an-array-in-bash
IFS=' ' read -r -a array <<< "$INPUT"
for element in "${array[@]}"
do
    # #https://stackoverflow.com/questions/4260467/what-is-a-regular-expression-for-a-mac-address
    # https://stackoverflow.com/questions/21112707/check-if-a-string-matches-a-regex-in-bash-script
    if [[ "$element" =~ ^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$ ]]; then
        MAC_ADDRESS=$element
    fi
done

echo "mac address: " $MAC_ADDRESS
echo "connecting to device"
empty -s -o input "connect $MAC_ADDRESS\n"

while read -r line; do
    if [[ "$line" == *" Device $MAC_ADDRESS Connected: yes"* ]]; then
	echo "Connected"
        break
    fi
done < "$file"
empty -s -o input "menu gatt\n"
empty -s -o input "list-attributes \n"

var=0
array=()
uuid="3cfb298f-3dcb-4be0-b5d4-3cbc0e79cab1"
attr=''
prev=''

while read -r line; do
    lin=$(echo $line | sed -e 's,^[[:blank:]]*,,g')
        
    # https://stackoverflow.com/questions/58369763/read-previous-line-using-bash
    if [[ "$lin" == "$uuid" ]]; then
        if [ ! -z "${prev}" ]; then
        	attr="${prev}"
        	line2="${lin}"
        	echo "uuid: $uuid"
        fi
        break
    fi
    prev="${line}"
done < "$file"

attr=$(echo $attr | sed -e 's,^[[:blank:]]*,,g')
echo "attribute name: ${attr}"

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
    	echo "attribute value: "
    	echo "$attrVal"
    	echo ''
    	break
    fi
done < "$file"

empty -s -o input "back\n"
empty -s -o input "disconnect \n"

lin="Successful disconnected"
while read -r line; do
    if [[ "$line" == *"$lin"* ]]; then
	echo "Disconnected"
        break
    fi
done < "$file"

empty -s -o input "discoverable off\n"

lin="Changing discoverable off succeeded"
while read -r line; do
    if [[ "$line" == *"$lin"* ]]; then
    	echo "Discoverable off"
        break
    fi
done < "$file"

empty -s -o input "exit\n"

# kill process
VAR1=$(pstree -g | grep bluetoothctl | cut -d '(' -f 3)
pid=$(echo $VAR1 | cut -d ')' -f 1)
# https://stackoverflow.com/questions/48261038/shell-script-how-to-check-if-variable-is-null-or-no
if [[ -n "$pid" ]]; then
	echo $pid
	kill $pid
	echo "Process killed"
fi
echo "done"

