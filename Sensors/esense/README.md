# eSense

- The eSense sensors consists of Skin response, temperature, respiration and pulse sensors. For more information, refer to the [Wiki](https://git.inf.h-brs.de/zat-rhein-ruhr/zat-prototype-demo/consor/-/wikis/home/eSense/Consor-Vital-Information) page
- The hardware setup for these sensors are as follows:

![eSense Hardware Setup](Sensors/eSense/misc/Images/eSense_HardwareSetup.png)

<br>

- This repository is specifically for bridging the [eSense physiological sensors](https://mindfield-esense.com/ )  with the publisher node.


#### folder contents

- misc
- esense_ble
- esense_lsl


The *misc* folder includes screenshots, images etc.

The *esense_ble* folder includes a ROS2 package to publish eSense data to a ROS node using **bluetoothctl**. The data is transferred from Android Studio to the Linux system using BLE (Bluetooth Low Energy).

The *esense_lsl* folder includes a ROS2 package to publish eSense data to a ROS node using **pylsl**.

More information can be found in the README of the respective folder.

