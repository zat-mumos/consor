# Bash Scripts

The bash scripts have commands for connecting linux system and android device via Bluetooth. They are located in /scripts directory.

<br>

## 1. scripts/main.sh

##### Description: 

The main script which sources from cmds.sh to run functions facilitating Bluetooth connection and sensor data transfer.

##### Dependencies

`cmds.sh` must be located in the same directory as `main.sh`

##### Usage: 

This script is not directly executed but instead, the ros node creates a subprocess which runs this script.

##### Functions defined in this script:

- `remove_file`
    - Description: Remove file if it already exists
    - Arguments: file name

- `cleanup`
    - Description: Includes steps to be run on keyboard interrupt

- `initialisation`
    - Description: Includes steps to initialise variables and remove files such as log_files from previous run

Other functions called in `main.sh` are defined in `cmds.sh`

<br>

## 2. scripts/cmds.sh

##### Description: 

This script defines functions that help facilitate Bluetooth connection and sensor data transfer.

##### Usage: 

This script is not directly executed but instead, is sourced by `main.sh`.

##### Functions defined in this script:

- `starting_bluetoothctl`
    - Description: Includes steps to be run at the beginning once code is executed

- `connect_to_device`
    - Description: Get MAC address of the device & connect to this device
    - Arguments: 
        - device_name
        - input_file
        - output_file
        - fixed_mac_address

- `go_to_gatt_menu`
    - Description: Once a characteristic is read, the script exits gatt menu automatically. Hence, each time we need to go to the gatt menu to read any characteristic

- `read_characteristic`
    - Description: Includes steps to select attribute and read characteristic value
    - Arguments:
        - uuid
        - input_file
        - save_file_path

- `disconnect_device`
    - Description: Includes steps to disconnect device
    - Arguments: input_file

- `switch_discoverable_off`
    - Description: Includes steps to switch off discoverability of devices

- `exit_bluetoothctl`
    - Description: Include steps to exit bluetoothctl

- `kill_bluetoothctl_process`
    - Description: Include steps to kill existing bluetooth process using process instead
