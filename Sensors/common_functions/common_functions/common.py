from builtin_interfaces.msg import Time


# This is a common function for openbci.py & emotibit_sdk.py
def convert_time(timestamp: float) -> Time:
        """Converts a float timestamp to seconds and nanoseconds.
        Arguments:
            float timestamp: timestamp in float

        Returns:
            builtin_interfaces.msg.Time : timestamp in seconds and nanoseconds
        """
        time = Time()
        time.sec = int(timestamp)
        time.nanosec = int((timestamp%1)*1e9)
        return time

