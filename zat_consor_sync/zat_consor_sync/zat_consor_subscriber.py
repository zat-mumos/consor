#!/usr/bin/env python3
from collections import defaultdict
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from zat_ros2_msgs.msg import MovellaData, ZatConsorSynch, EmotibitMsg, EmotibitSynchData,  EsenseStream


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
          self._emotibit_streams = ["accelerometer","gyroscope","magnetometer","ppg","eda","temperature"]


          self._movella_subscriber = self.create_subscription(MovellaData,
                                                            movella_topic,
                                                            self._movella_callback,
                                                            10)
        
          self._esense_subscriber = self.create_subscription(EsenseStream,
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


          if not final_data:
               self.get_logger().warn("No sensor data yet, skipping publish")
               return
            
          if "esense" in final_data: 
               msg.esense_data = [final_data["esense"]]
          if "movella" in final_data:
               msg.movella_data = [final_data["movella"]]
          if "emotibit" in final_data:
               msg.emotibit_data = [final_data["emotibit"]]

          if "movella" in final_data and "emotibit" in final_data:
               self.merge_data(self.movella_data, self.synched_flattened_emotibit_data)

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
                  

     def _flatten_movella_data(self, msg):
          self.movella_data = defaultdict(list)
          self.get_logger().info("flatten msgs")

          for each_movella_sensor in msg.data:
               temp_dict = {}
               temp_dict['id'] = each_movella_sensor.id
               for each_data in each_movella_sensor.data:
                    values = []
                    ts = each_data.header.stamp
                    ts_ = self.convert_time(ts)
                    values.append(ts)
                    for fields in each_data.__slots__:
                         if fields not in ('_header'):
                              # self.get_logger().info(f"fields: {fields.strip('_')}, {getattr(each_data, fields)}")
                              values.append((fields.strip('_'), getattr(each_data, fields)))
                    self.movella_data[ts_] = values
               self.movella_data = dict(sorted(self.movella_data.items()))
               # self.get_logger().info(f"{self.movella_data}\n")



     def _movella_callback(self,msg): 
          self._movella_data = msg
          self._flatten_movella_data(self._movella_data)
          self.get_logger().info("Movella data received")

     def _esense_callback(self,msg):
          self._esense_data = msg
          self.get_logger().info("eSense data received")

     def _emotibit_synch(self, data, stream):
          if self._emotibit_synch_data is None:
               self._emotibit_synch_data = EmotibitSynchData()
               setattr(self._emotibit_synch_data, stream, [data])
          else:
               setattr(self._emotibit_synch_data, stream, [data])
          
          temp_var = [True if getattr(self._emotibit_synch_data, attr) not in (None, []) else False 
                      for attr in self._emotibit_streams]
          # self.get_logger().info(f"temp_var: {temp_var}")
          if all(temp_var):
               # self.get_logger().info(f"emotibit sync data: {self._emotibit_synch_data}\n\n\n")
               self._emotibit_synch_publisher.publish(self._emotibit_synch_data)

               # Flatten the msg once all modalities are received
               self.synched_flattened_emotibit_data = self._emotibit_flatten_msgs(self._emotibit_synch_data)
               self.get_logger().info("Emotibit data received")

     def _emotibit_flatten_msgs(self, msg_):
          emotibit_data = defaultdict(list)
          for stream in self._emotibit_streams:
               if stream == 'accelerometer':
                    msg = msg_.accelerometer[0]
                    s = 'acc'
               elif stream == 'gyroscope':
                    msg = msg_.gyroscope[0]
                    s = 'gyro'
               elif stream == 'magnetometer':
                    msg = msg_.magnetometer[0]
                    s = 'mag'
               elif stream == 'ppg':
                    msg = msg_.ppg[0]
                    s = 'ppg'
               elif stream == 'eda':
                    msg = msg_.eda[0]
                    s = 'eda'
               elif stream == 'temperature':
                    msg = msg_.temperature[0]
                    s = 'temp'
               # self.get_logger().info(f"msg_: {msg_}")
               flattened_data = self._emotibit_flatten_helper_msg(msg, s, emotibit_data)
               flat_emotibit_data = dict(sorted(flattened_data.items()))
          # self.get_logger().info(f"{flat_emotibit_data.keys()}\n{flat_emotibit_data}\n\n")
          return flat_emotibit_data

     def _emotibit_flatten_helper_msg(self, msg, s, emotibit_data):
          for index, timestamp in enumerate(msg.timestamp):
               values = []
               ts = timestamp
               ts_ = self.convert_time(ts)
               if ts not in emotibit_data[ts_]:
                    values.append(ts)
               for i in range(len(msg.data)):
                    if len(msg.data) > 1:
                         values.append((f"{s}_{i+1}", msg.data[i].data[index]))
                    else:
                         values.append((f"{s}", msg.data[i].data[index]))
               
               # self.get_logger().info(f"1: {msg.data[0].data[index]}, 2: {msg.data[1].data[index]}, 3: {msg.data[2].data[index]}\nvalues: {values}") 
               if ts_ not in emotibit_data:
                    # self.get_logger().info(f"11: {index} {ts_}")
                    emotibit_data[ts_] = values
               else:
                    # self.get_logger().info(f"22 : {ts_}")
                    emotibit_data[ts_].extend(values)
          return emotibit_data

     def convert_time(self, header):
          seconds = header.sec
          nanosec = header.nanosec * 1e-9

          time = seconds + nanosec
          return time
     
     def merge_data(self, movella_msg, emotibit_msg):
          self.merged = defaultdict(list)
          for key in movella_msg.keys() | emotibit_msg.keys():
               if key in movella_msg and key in emotibit_msg:
                    self.merged[key] = {
                         'k':1,
                         'movella': movella_msg[key],
                         'emotibit': emotibit_msg[key]
                    }
               elif key in movella_msg:
                    self.merged[key] = {
                         'k':2,
                         'movella': movella_msg[key]
                    }
               else:
                    self.merged[key] = {
                         'k':3,
                         'emotibit': emotibit_msg[key]
                    }
          self.merged = dict(sorted(self.merged.items()))
          self.get_logger().info(f"merged: {self.merged}\n\n")


     def _emotibit_accelerometer_callback(self, msg):
          data = msg
          stream = "accelerometer"
          self._emotibit_synch(data,stream)
          self.get_logger().info("Added accelerator code")
          # self.get_logger().info(str(self._emotibit_synch_data.accelerometer))

     def _emotibit_gyroscope_callback(self, msg):
          data = msg
          stream = "gyroscope"
          self._emotibit_synch(data,stream)

     def _emotibit_magnetometer_callback(self, msg):
          data = msg
          stream = "magnetometer"
          self._emotibit_synch(data,stream)

     def _emotibit_ppg_callback(self, msg):
          data = msg
          stream = "ppg"
          self._emotibit_synch(data,stream)  

     def _emotibit_eda_callback(self, msg):
          data = msg
          stream = "eda"
          self._emotibit_synch(data,stream) 

     def _emotibit_temperature_callback(self, msg):
          data = msg
          stream = "temperature"
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