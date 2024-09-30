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
        break
    fi
done < "$file"

empty -s -o input "menu gatt\n"
empty -s -o input "list-attributes \n"

while read -r line; do
    echo "line: $line"
    echo " ---------------------------------"
done < "$file"

empty -s -o input "back\n"
empty -s -o input "disconnect \n"
empty -s -o input "discoverable off\n"
empty -s -o input "exit\n"

# kill process
VAR1=$(pstree -g | grep bluetoothctl | cut -d '(' -f 3)
pid=$(echo $VAR1 | cut -d ')' -f 1)
echo $pid

kill $pid

echo "done"

