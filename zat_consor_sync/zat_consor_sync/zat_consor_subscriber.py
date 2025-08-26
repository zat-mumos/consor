#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from zat_ros2_msgs.msg import MovellaData, PhysioSensor, ZatConsorSynch, EmotibitMsg, EmotibitSynchData


class zat_consor_node(Node):
    def __init__(
            self,
            movella_topic: str = '/sensor/movella/imu_data',
            esense_topic: str = '/sensor/esense/data',
            emotibit_accelerometer_topic: str = '/emotibit/acc',
            emotibit_gyroscope_topic: str = '/emotibit/gyro',
            emotibit_magnetometer_topic: str = '/emotibit/mag',
            emotibit_ppg_topic: str = '/emotibit/ppg',
            emotibit_eda_topic: str = '/emotibit/eda',
            emotibit_temperature_topic: str = '/emotibit/temp',
            emotibit_synch_topic: str = 'sensor/emotibit/data',
            consor_wearable_sensor_topic: str = 'sensor/consor/wearable/data'):


        super().__init__('zat_consor_node')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('movella_topic', movella_topic),
                ('esense_topic', esense_topic),
                ('emotibit_accelerometer_topic', emotibit_accelerometer_topic),
                ('emotibit_gyroscope_topic', emotibit_gyroscope_topic),
                ('emotibit_magnetometer_topic', emotibit_magnetometer_topic),
                ('emotibit_ppg_topic', emotibit_ppg_topic),
                ('emotibit_eda_topic', emotibit_eda_topic),
                ('emotibit_temperature_topic', emotibit_temperature_topic),
                ('emotibit_synch_topic', emotibit_synch_topic),
                ('consor_wearable_sensor_topic', consor_wearable_sensor_topic)
            ])


        movella_topic=self.get_parameter('movella_topic').value
        esense_topic = self.get_parameter('esense_topic').value
        emotibit_accelerometer_topic = self.get_parameter('emotibit_accelerometer_topic').value
        emotibit_gyroscope_topic = self.get_parameter('emotibit_gyroscope_topic').value
        emotibit_magnetometer_topic = self.get_parameter('emotibit_magnetometer_topic').value
        emotibit_ppg_topic = self.get_parameter('emotibit_ppg_topic').value
        emotibit_eda_topic = self.get_parameter('emotibit_eda_topic').value
        emotibit_temperature_topic = self.get_parameter('emotibit_temperature_topic').value
        emotibit_synch_topic = self.get_parameter('emotibit_synch_topic').value
        consor_wearable_sensor_topic=self.get_parameter('consor_wearable_sensor_topic').value 

        self._esense_data = None
        self._movella_data = None
        self._emotibit_synch_data = None
        self._old_esense_data = None
        self._old_movella_data = None
        self._old_emotibit_synch_data = None
        self._emotibit_streams = ["emotibit_accelerometer","emotibit_gyroscope","emotibit_magnetometer","emotibit_ppg","emotibit_eda","emotibit_temperature"]
        


        self._movella_subscriber = self.create_subscription(MovellaData,
                                                            movella_topic,
                                                            self._movella_callback,
                                                            10)
        
        self._esense_subscriber = self.create_subscription(PhysioSensor,
                                                           esense_topic,
                                                           self._esense_callback,
                                                           10)
        
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
        
        self._emotibit_synch_publisher = self.create_publisher(EmotibitSynchData,
                                                               emotibit_synch_topic,
                                                               10)
        
        self._consor_publisher=self.create_publisher(ZatConsorSynch,consor_wearable_sensor_topic,10)

        timer_period=0.5
        self.timer=self.create_timer(timer_period,self.timer_callback)

    def timer_callback(self):
            """to publish the synchronized data of the wearble sensors"""
            
            msg=ZatConsorSynch()

            sensors = {"esense": ("_esense_data", "_old_esense_data"),
                       "movella": ("_movella_data", "_old_movella_data"),
                       "emotibit": ("_emotibit_synch_data", "_old_emotibit_synch_data")}
            
            final_data = {}
            used_new = []
            
            for name, (new_data, old_data) in sensors.items():
               cur_val = getattr(self, new_data)
               old_val = getattr(self, old_data)
               if cur_val is not None:
                    final_data[name] = cur_val
                    used_new.append(name)
               elif old_val is not None:
                    final_data[name] = old_val
               else:
                    return  

            msg.esense_data = [final_data["esense"]]
            msg.movella_data = [final_data["movella"]]
            msg.emotibit_data = [final_data["emotibit"]]

            self._consor_publisher.publish(msg)

            for name, (new_data, old_data) in sensors.items():
                 cur_val = getattr(self, new_data)
                 if cur_val is not None:
                      setattr(self, old_data, cur_val)
                      setattr(self, new_data, None)

            if used_new:
                 self.get_logger().info(
                      f"Published consor data with latest {', '.join(used_new)} data"
                      f" and old data for the rest"
                 )
                  


    def _movella_callback(self,msg): 
          self._movella_data = msg
          self.get_logger().info("Movella data received")

    def _esense_callback(self,msg):
         self._esense_data = msg
         self.get_logger().info("eSense data received")

    def _emotibit_synch(self, data, stream):
         if self._emotibit_synch_data is None:
              self._emotibit_synch_data = EmotibitSynchData()
         else:
              setattr(self._emotibit_synch_data, stream, [data])
              if all(getattr(self._emotibit_synch_data, attr) is not None 
               for attr in self._emotibit_streams):
               self._emotibit_synch_publisher.publish(self._emotibit_synch_data)
                   

    def _emotibit_accelerometer_callback(self, msg):
         data = msg
         stream = "emotibit_accelerometer"
         self._emotibit_synch(data,stream)

    def _emotibit_gyroscope_callback(self, msg):
         data = msg
         stream = "emotibit_gyroscope"
         self._emotibit_synch(data,stream)

    def _emotibit_magnetometer_callback(self, msg):
         data = msg
         stream = "emotibit_magnetometer"
         self._emotibit_synch(data,stream)

    def _emotibit_ppg_callback(self, msg):
         data = msg
         stream = "emotibit_ppg"
         self._emotibit_synch(data,stream)  

    def _emotibit_eda_callback(self, msg):
         data = msg
         stream = "emotibit_eda"
         self._emotibit_synch(data,stream) 

    def _emotibit_temperature_callback(self, msg):
         data = msg
         stream = "emotibit_temperature"
         self._emotibit_synch(data,stream)      

def main():
     rclpy.init(args= None)
     consor =  zat_consor_node(
             movella_topic = '/sensor/movella/imu_data',
             esense_topic = '/sensor/esense/data',
             emotibit_accelerometer_topic = '/emotibit/acc',
             emotibit_gyroscope_topic= '/emotibit/gyro',
             emotibit_magnetometer_topic = '/emotibit/mag',
             emotibit_ppg_topic = '/emotibit/ppg',
             emotibit_eda_topic = '/emotibit/eda',
             emotibit_temperature_topic= '/emotibit/temp',
             emotibit_synch_topic = 'sensor/emotibit/data',
             consor_wearable_sensor_topic = 'sensor/consor/wearable/data')
     rclpy.spin(consor)

     consor.destroy_node()
     rclpy.shutdown()
     
if __name__ == '__main__':
     main()