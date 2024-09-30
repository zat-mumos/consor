#!/bin/bash

empty -f -i input -o output -L log_empty.log bluetoothctl
empty -s -o input "help\n"
empty -s -o input "power on\n"
empty -s -o input "discoverable on\n"
empty -s -o input "scan on\n"
empty -s -o input "scan off\n"
empty -s -o input "discoverable off\n"
empty -s -o input "devices\n"

# https://unix.stackexchange.com/questions/256144/read-a-file-line-by-line-and-if-condition-is-met-continue-reading-till-next-cond

file="output"
IFS='\n'
INPUT='input'
while read -r line; do
    if [[ $line == *"Galaxy Tab S9"* ]] ; then
        printline="yes"
        INPUT=$line
        echo $line
        break        
    fi
done < "$file"

echo $INPUT

# https://stackoverflow.com/questions/428109/extract-substring-in-bash
MAC_ADDRESS=$(echo $INPUT| cut -d' ' -f 2)
echo $MAC_ADDRESS
# connect $MAC_ADDRESS

connect $MAC_ADDRESS
menu gatt
list-attributes
 

# kill process
VAR1=$(pstree -g | grep bluetoothctl | cut -d '(' -f 3)
pid=$(echo $VAR1 | cut -d ')' -f 1)
echo $pid

kill $pid

echo "done"


