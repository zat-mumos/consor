# Bash Scripts

The bash scripts have commands for connecting linux system and android device via Bluetooth. They are located in `/scripts` directory.

<br>

## 1. scripts/main.sh

##### Description: 

This script is the main script that is called by the ROS2 package. IWhile some functions are defined in this script, it sources most functions from cmds.sh.

##### Dependencies

- `cmds.sh` must be located in the same directory as `main.sh`
- `empty` package to be installed on the system. The steps to install this can be found in the _Installation_ section in the eSense [README](../README.md)

##### Usage: 

This script is not directly executed but instead, the ros node creates a subprocess which runs this script.

##### Functions defined in this script:

- `remove_file`
    - Description: This function removes the file if it already exists
    - Arguments: The name of the file that is to be removed

- `cleanup`
    - Description: This function includes the steps to be run on keyboard interrupt. They are:
        - disconnect the android device and turn off the visibility of linux system
        - exit bluetoothctl and kill bluetoothctl process
        - remove _input_ and _output_ fifo for empty

- `initialisation`
    - Description: This function includes steps to initialise variables and remove files such as log_files from previous run. 
        - Initialise variables *sample_no* and *sample_data* to 0
        - Remove fifo files and log files for empty

Other functions called in `main.sh` are defined in `cmds.sh` 

<br>

## 2. scripts/cmds.sh

##### Description: 

This script defines functions that help facilitate Bluetooth connection and sensor data transfer.

##### Usage: 

This script is not directly executed but instead, is sourced by `main.sh`.

##### Functions defined in this script:

- `starting_bluetoothctl`
    - Description: This function includes steps (using _empty_) to be run at the beginning once the code is executed. These steps are:
        - start bluetoothctl
        - switch on the Bluetooth of the linux system
        - change the linux system to be discovered by nearby devices
        - scan for devices 
        - display the devices found on scanning

- `connect_to_device`
    - Description: This function gets MAC address of the (android) device & connect to this device
    - Arguments: 
        - ***device_name*** is the name of the device that is advertised while scanning for devices by Bluetooth (e.g. android device)
        - ***file*** is the _input_ fifo for empty
        - ***output*** is the _output_ fifo for empty
        - ***fixed_mac_address*** is the fixed MAC address of the device that is scanned(e.g. android device's fixed MAC address)

- `go_to_gatt_menu`
    - Description: This function includes steps to go to the gatt menu in bluetoothctl. Once a characteristic is read, the script exits gatt menu automatically. Hence, each time we need to go to the gatt menu to read any characteristic

- `read_characteristic`
    - Description: This function includes steps to select attribute and read characteristic value. This value can also be saved to a file if needed.
    - Arguments:
        - ***uuid*** is the id of the characteristic to be read 
        - ***file*** is the _input_ fifo for empty
        - ***save_file_path*** is the file path where the data is to be saved, leave empty (using "") if do not want to save the data

- `disconnect_device`
    - Description: This function includes steps to disconnect the connected device
    - Arguments: 
        - ***file*** is the _output_ fifo for empty

- `switch_discoverable_off`
    - Description: This function includes steps to switch off the visibility/discoverability of this system to other devices
    - Arguments: 
        - ***file*** is the _output_ fifo for empty

- `exit_bluetoothctl`
    - Description: This function include steps to exit bluetoothctl

- `kill_bluetoothctl_process`
    - Description: This function include steps to kill existing bluetooth process using process id

<br>

## Example

An example of how functions are called in main.sh is as follows:

```

trap cleanup EXIT

initialisation 

starting_bluetoothctl

connect_to_device "<device name>" "output" "input" "<device fixed MAC address>"

go_to_gatt_menu

sampledata=$(read_characteristic "<characteristic uuid>", "output", "")
sampleno=$(read_characteristic "<characteristic uuid>", "output", "")

echo $sampleno,$sampledata >&1


```