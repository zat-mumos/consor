#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from zat_ros2_msgs.msg import EmotibitMsg, EmotibitSynchData, EsenseStream, SynchData, DataPoint

class EmotibitStreamsCombine(Node):
    """
    Combine data from different modalities and publish to a ROS topic.
    """
    def __init__(
            self, 
            timer_period = 0.8,
            emotibit_accelerometer_topic: str = '/emotibit/acc',
            emotibit_gyroscope_topic: str = '/emotibit/gyro',
            emotibit_magnetometer_topic: str = '/emotibit/mag',
            emotibit_ppg_topic: str = '/emotibit/ppg',
            emotibit_eda_topic: str = '/emotibit/eda',
            emotibit_temperature_topic: str = '/emotibit/temp',
            emotibit_synch_topic: str = 'sensor/emotibit/data'):
        """
        Initialise the EmotibitStreamsCombine class.
        """
        super().__init__('emotibit_streams_combine')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('timer_period', timer_period),
                ('emotibit_accelerometer_topic', emotibit_accelerometer_topic),
                ('emotibit_gyroscope_topic', emotibit_gyroscope_topic),
                ('emotibit_magnetometer_topic', emotibit_magnetometer_topic),
                ('emotibit_ppg_topic', emotibit_ppg_topic),
                ('emotibit_eda_topic', emotibit_eda_topic),
                ('emotibit_temperature_topic', emotibit_temperature_topic),
                ('emotibit_synch_topic', emotibit_synch_topic)
            ])
        
        # Get parameter values
        timer_period = self.get_parameter('timer_period').value
        emotibit_accelerometer_topic = self.get_parameter('emotibit_accelerometer_topic').value
        emotibit_gyroscope_topic = self.get_parameter('emotibit_gyroscope_topic').value
        emotibit_magnetometer_topic = self.get_parameter('emotibit_magnetometer_topic').value
        emotibit_ppg_topic = self.get_parameter('emotibit_ppg_topic').value
        emotibit_eda_topic = self.get_parameter('emotibit_eda_topic').value
        emotibit_temperature_topic = self.get_parameter('emotibit_temperature_topic').value
        emotibit_synch_topic = self.get_parameter('emotibit_synch_topic').value
        
        self._timer_period = timer_period
        self._emotibit_streams = ["accelerometer", "gyroscope", "magnetometer", "ppg", "eda", "temperature"]

        self._emotibit_accelerometer_subscriber = self.create_subscription(EmotibitMsg, 
                                                                        emotibit_accelerometer_topic, 
                                                                        self._emotibit_accelerometer_callback, 
                                                                        10)

    
        self._emotibit_gyroscope_subscriber = self.create_subscription(EmotibitMsg,
                                                                    emotibit_gyroscope_topic, 
                                                                    self._emotibit_gyroscope_callback, 
                                                                    10)
    
        self._emotibit_magnetometer_subscriber = self.create_subscription(EmotibitMsg, 
                                                                    emotibit_magnetometer_topic, 
                                                                    self._emotibit_magnetometer_callback, 
                                                                    10)
    
        self._emotibit_ppg_subscriber = self.create_subscription(EmotibitMsg, 
                                                            emotibit_ppg_topic, 
                                                            self._emotibit_ppg_callback, 
                                                            10)
    
        self._emotibit_eda_subscriber = self.create_subscription(EmotibitMsg, 
                                                            emotibit_eda_topic, 
                                                            self._emotibit_eda_callback, 
                                                            10)
    
        self._emotibit_temperature_subscriber = self.create_subscription(EmotibitMsg, 
                                                                    emotibit_temperature_topic, 
                                                                    self._emotibit_temperature_callback, 
                                                                    10)
    
        self._emotibit_synch_publisher = self.create_publisher(EmotibitSynchData, emotibit_synch_topic, 10)

        self._emotibit_dict = {"accelerometer": None, 
                               "gyroscope": None, 
                               "magnetometer": None, 
                               "ppg": None, 
                               "eda": None, 
                               "temperature": None}

        self.timer1 = self.create_timer(self._timer_period, self._emotibit_synch_callback)

    # Since each modality in emotibit has its own ros2 topic, when new msgs are received emotibit_sync() is called
    def _emotibit_accelerometer_callback(self, msg: EmotibitMsg):
        self._emotibit_dict["accelerometer"] = msg

    def _emotibit_gyroscope_callback(self, msg: EmotibitMsg):
        self._emotibit_dict["gyroscope"] = msg

    def _emotibit_magnetometer_callback(self, msg: EmotibitMsg):
        self._emotibit_dict["magnetometer"] = msg

    def _emotibit_ppg_callback(self, msg: EmotibitMsg):
        self._emotibit_dict["ppg"] = msg  

    def _emotibit_eda_callback(self, msg: EmotibitMsg):
        self._emotibit_dict["eda"] = msg 

    def _emotibit_temperature_callback(self, msg: EmotibitMsg):
        self._emotibit_dict["temperature"] = msg      

    def _emotibit_synch_callback(self):
        """
        This function combines data from all modalities from emotibit that is published as separate topics into a single msg
        """
        emotibit_synch_data = EmotibitSynchData()

        for stream in self._emotibit_dict:
            if self._emotibit_dict[stream] is None:
                self.get_logger().warn("Emotibit data not received")
                return

            setattr(emotibit_synch_data, stream, [self._emotibit_dict[stream]])
        
        self.get_logger().debug(f"emotibit sync data: {emotibit_synch_data}\n\n\n")
        self._emotibit_synch_publisher.publish(emotibit_synch_data)

        self.get_logger().info("Emotibit data received")
        self._emotibit_dict = {"accelerometer": None, 
                               "gyroscope": None, 
                               "magnetometer": None, 
                               "ppg": None, 
                               "eda": None, 
                               "temperature": None}                            
    
def main():
    rclpy.init(args= None)
    emotibit_data =  EmotibitStreamsCombine(
        emotibit_accelerometer_topic = '/emotibit/acc',
        emotibit_gyroscope_topic= '/emotibit/gyro',
        emotibit_magnetometer_topic = '/emotibit/mag',
        emotibit_ppg_topic = '/emotibit/ppg',
        emotibit_eda_topic = '/emotibit/eda',
        emotibit_temperature_topic= '/emotibit/temp',
        emotibit_synch_topic = 'sensor/emotibit/data')
    rclpy.spin(emotibit_data)

    emotibit_data.destroy_node()
    rclpy.shutdown()
     
if __name__ == '__main__':
    main()