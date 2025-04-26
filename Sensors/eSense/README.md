## The eSense repository is specifically for bridging the [eSense physiological sensors](https://mindfield-esense.com/ )  with the publisher node

### Some of the sensors are:

1. Skin Response [Skin Resistance Measurement](https://mindfield.de/en/esense-skin-response/)
2. Temperature [Measuring Skin Temperature](https://mindfield.de/en/esense-temperature/)
3. Respiration [Breath training](https://mindfield.de/en/esense-respiration/)
4. Pulse [HRV Biofeedback](https://mindfield.de/en/esense-pulse/)

### Basic working

- The bash script [main.sh](main.sh) sources [cmds.sh](cmds.sh)

- The python file [physio_sensor.py](physio_sensor.py) pipes **main.sh** and publishes the _sample no_ & _sample data_ to ROS node



### Important path changes

[**main.sh**](main.sh)

- change the path accordingly of sourcing in [cmds.sh](cmds.sh)

- change the first parameter device_name where the sensors are connected to the android device

```
connect_to_device() {
    device_name="$1" output_dir="$2" input_dir="$3"
}
```

[**physio_sensor.py**](physio_sensor.py)

- Change the path of the main.sh file correctly:


```
class SensorDataEsense(Node):
    def __init__(self, 
                 **bash_script_path="../main.sh"**


```


### Setting up the environment

- Make sure you have the ros2 environment setup correctly
- Then you need to build your ros package for the ros2 publisher node


```
source \opt\ros\(version)\setup.bash
cd ~\consor_ws
colcon build
```




### Important Characteristics and their UUIDs

- Sample no: 		"0d6d433d-ef16-4543-ac24-c6e08841a56e"

- Sample data: 		"3cfb298f-3dcb-4be0-b5d4-3cbc0e79cab1"

<!-- Android API Level: 	"24e3bd1c-c366-4cda-950b-2b7c46e4a13d"

Device name: 		"00002a00-0000-1000-8000-00805f9b34fb"

Manufacturer name: 	"00002a29-0000-1000-8000-00805f9b34fb"

Sensor type: 		"44e61fc0-0c53-492f-ab20-b86759702bc7"

Measuring units: 	"0e4476c4-a32d-4c93-9686-37e957c5b979"

Samples per second: 	"b46b8c16-55d4-4536-9f90-1074de740d29" -->


<!-- Carrier amplitude: 	"3a5dc305-e506-43ee-8da2-547e5a577886"

Decoder load pct: 	"aa3e90f8-3b7c-48de-a93a-0c9e034cd429"

Logical time: 		"e0e2c940-5db3-47c4-88de-32d6ae34187a"

Real time: 		"188d76e4-b00e-45f7-9c11-d4d25c10a7d1" -->


<!-- ### Link to mindfield eSense
https://mindfield-esense.com/  -->

<!-- 
### Links to eSense sensor documentation
1. Skin Response (Skin Resistance Measurement): https://mindfield.de/en/esense-skin-response/
2. Skin Response (Manual/Handbuch): https://help.mindfield.de/en/skin-response-manual

3. Temperature (Measuring Skin Temperature): https://mindfield.de/en/esense-temperature/
4. Temperature (Manual/Handbuch): https://help.mindfield.de/en/temperature-manual 

5. Respiration (Breath training): https://mindfield.de/en/esense-respiration/
6. Respiration (Manual/Handbuch): https://help.mindfield.de/respiration-handbuch

7. Pulse (HRV Biofeedback): https://mindfield.de/en/esense-pulse/
8. Pulse (Manual/handbuch): https://help.mindfield.de/pulse-handbuch -->


<!-- #### More Links on the esense sensors
1. Comparison of eSense sensors: https://mindfield.de/en/esense-comparison/
2. Stream eSense data using OSC: https://help.mindfield.de/helpdesk/esense-daten-zu-einem-pc-mac-browser-streamen-esense-web-app-osc#eckb-article-body
3. Types of electrodes: https://help.mindfield.de/helpdesk/elektrodentypen#eckb-article-body
4. Possible position of electrodes: https://help.mindfield.de/helpdesk/moegliche-ableitpositionen-der-elektroden#eckb-article-body
 -->

### Important Observations

- BLE characteristics values are not reset when the same application is run continuously. That is, in the first run, all values are initialised

- In the second run, the characteristics hold the last value read by the sensor. Hence, in the current version, it is better to restart the application to ensure all values are reset or we start the bash code after the application starts sampling.

- Need to manually delete the input & output file in case of unexpected exit. Also kill the process manually using command line.
