# © 2026 Hochschule Bonn-Rhein-Sieg <https://www.h-brs.de/>
"""
A Python script that communicates with the eSense sensor via Pylsl.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
from pylsl import StreamInlet, resolve_byprop

class EsenseLslReceiver:
    """A class to receive data from eSense sensor sent via LSL."""
    def __init__(self, stream_name: str = "eSense", inlet: StreamInlet = None):
        """Initialise for LSL communication
        Arguments:
        str stream_name: Name of the stream to be found by 'pylsl.resolve_byprop' [Default: 'eSense']
        StreamInlet inlet: A stream inlet [Default: None]
        """
        self.stream = resolve_byprop("name", stream_name)
        if inlet == None:
            inlet = StreamInlet(self.stream[0])
        self.inlet = inlet

        self.list_metadata_keys = ["Sampling_rate", "Android_API_Level", "Device_Name", "Manufacturer_Name", "Units", "Sensor_Type"]

    def get_stream_info(self):
        """Return stream information"""        
        return self.inlet.info()
    
    def get_metadata_value(self):
        """ Return values within stream metadata

        Returns:
        dict metadata: Dictionary of metadata values
        """
        info = self.get_stream_info()
        metadata = {}

        for i in self.list_metadata_keys:
            if i in ['Android_API_Level', 'Sampling_rate']:
                value = int(info.desc().child('Metadata').child_value(i))
            elif i in ['Device_Name', 'Manufacturer_Name']:
                value = self.ascii_to_string(info.desc().child('Metadata').child_value(i))
            else:
                value = info.desc().child('Metadata').child_value(i)
            metadata[str.lower(i)] = value

        return metadata

    def ascii_to_string(self, string_data: str):
        """
        Convert ASCII to String.

        Arguments:
        str string_data: ASCII value to be converted to data

        Returns:
        str data: String value of the received ASCII
        """
        print(f"helllo")
        data = string_data.strip('[]').split(',')
        data = ''.join(chr(int(ch)) for ch in data)
        return data
    
    def get_sample(self):
        """Returns sample received from sensor"""
        sample_timestamp_array, _ = self.inlet.pull_sample()
        return sample_timestamp_array
