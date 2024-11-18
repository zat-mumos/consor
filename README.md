### Characteristics and their UUIDs

Android API Level: 	"24e3bd1c-c366-4cda-950b-2b7c46e4a13d"

Device name: 		"00002a00-0000-1000-8000-00805f9b34fb"

Manufacturer name: 	"00002a29-0000-1000-8000-00805f9b34fb"

Sensor type: 		"44e61fc0-0c53-492f-ab20-b86759702bc7"

Measuring units: 	"0e4476c4-a32d-4c93-9686-37e957c5b979"

Samples per second: 	"b46b8c16-55d4-4536-9f90-1074de740d29"

Sample no: 		"0d6d433d-ef16-4543-ac24-c6e08841a56e"

Logical time: 		"e0e2c940-5db3-47c4-88de-32d6ae34187a"

Real time: 		"188d76e4-b00e-45f7-9c11-d4d25c10a7d1"

Sample data: 		"3cfb298f-3dcb-4be0-b5d4-3cbc0e79cab1"

Carrier amplitude: 	"3a5dc305-e506-43ee-8da2-547e5a577886"

Decoder load pct: 	"aa3e90f8-3b7c-48de-a93a-0c9e034cd429"


#### Observations

BLE characteristics values are not reset when the same application is run continuously. That is, in the first run, all values are initialised. In the second run, the characteristics hold the last value read by the sensor. Hence, in the current version, it is better to restart the application to ensure all values are reset or we start the bash code after the application starts sampling.

Need to manually delete the input & output file in case of unexpected exit. Also kill the process manually using command line.
