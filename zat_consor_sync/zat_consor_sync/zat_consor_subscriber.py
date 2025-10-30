#!/usr/bin/env python3
from collections import defaultdict
import rclpy
from rclpy.node import Node
from rclpy.logging import LoggingSeverity
from builtin_interfaces.msg import Time 
import cv2
import numpy as np
import logging 
from zat_ros2_msgs.msg import MovellaData, ZatConsorSynch, EmotibitMsg, EmotibitSynchData, EsenseStream, SynchData, DataPoint

# # Uncomment lines below (till class definition) to save the output in a specific file mentioned by argument 'file_name'
# logging.basicConfig(
#      filename="data_sync_logging20-1.log",
#      filemode='a',
#      format='%(asctime)s - %(levelname)s - %(message)s',
#      level=logging.DEBUG
# )

class zat_consor_node(Node):
     def __init__(
          self,
          no_seconds: int = 1,
          movella_topic: str = '/sensor/movella/imu_data',
          esense_topic: str = '/sensor/esense/data',
          emotibit_accelerometer_topic: str = '/emotibit/acc',
          emotibit_gyroscope_topic: str = '/emotibit/gyro',
          emotibit_magnetometer_topic: str = '/emotibit/mag',
          emotibit_ppg_topic: str = '/emotibit/ppg',
          emotibit_eda_topic: str = '/emotibit/eda',
          emotibit_temperature_topic: str = '/emotibit/temp',
          emotibit_synch_topic: str = 'sensor/emotibit/data',
          consor_wearable_sensor_topic: str = 'sensor/consor/wearable/data',
          sync_topic: str = 'sensor/synched/data'):


          super().__init__('zat_consor_node')

          # self.get_logger().set_level(LoggingSeverity.DEBUG) # Uncomment this line to debug the code.

          self.declare_parameters(
               namespace='',
               parameters=[
                    ('sync_period', no_seconds),
                    ('movella_topic', movella_topic),
                    ('esense_topic', esense_topic),
                    ('emotibit_accelerometer_topic', emotibit_accelerometer_topic),
                    ('emotibit_gyroscope_topic', emotibit_gyroscope_topic),
                    ('emotibit_magnetometer_topic', emotibit_magnetometer_topic),
                    ('emotibit_ppg_topic', emotibit_ppg_topic),
                    ('emotibit_eda_topic', emotibit_eda_topic),
                    ('emotibit_temperature_topic', emotibit_temperature_topic),
                    ('emotibit_synch_topic', emotibit_synch_topic),
                    ('consor_wearable_sensor_topic', consor_wearable_sensor_topic),
                    ('sync_topic', sync_topic)
               ])

          no_seconds = self.get_parameter('sync_period').value
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
          sync_topic=self.get_parameter('sync_topic').value 

          self._esense_data = None
          self._movella_data = None
          self._emotibit_synch_data = None
          self._old_esense_data = None
          self._old_movella_data = None
          self._old_emotibit_synch_data = None
          self._emotibit_streams = ["accelerometer","gyroscope","magnetometer","ppg","eda","temperature"]
          self._no_seconds = no_seconds


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
          self._sync_publisher=self.create_publisher(SynchData,sync_topic,10)

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
          
          dict_msgs = {}
          
          if "esense" in final_data: 
               msg.esense_data = [final_data["esense"]]
               dict_msgs["esense"] = self.esense_data
          if "movella" in final_data:
               msg.movella_data = [final_data["movella"]]
               dict_msgs["movella"] = self.movella_data
          if "emotibit" in final_data:
               msg.emotibit_data = [final_data["emotibit"]]
               dict_msgs["emotibit"] = self.synched_flattened_emotibit_data
          
          self.merge_data(dict_msgs)

          main_msg = SynchData()
          for key in self.merged.keys():
               batch_sync = []
               
               timestamp = self.convert_time(key, False)
               main_msg.header.stamp = timestamp

               data = self.merged[key]
               for i in range(len(data)):
                    self.get_logger().debug(f"self.merged[key][i]: {data[i]}")
                    for k, v in data[i].items():
                         msg2 = DataPoint()
                         if data[i]['name'] == 'movella':
                              msg2.device_name = 1 #data[i]['name']
                         elif data[i]['name'] == 'emotibit':
                              msg2.device_name = 2
                         elif data[i]['name'] == 'esense':
                              msg2.device_name = 3
                         else:
                              msg2.device_name = 0
                         msg2.device_id = str(data[i]['id'])

                         if k not in ('name', 'id'):
                              msg2.modality_name = k
                              msg2.value = v
                              batch_sync.append(msg2)
               main_msg.data = batch_sync
               self.get_logger().debug(f"-------- \nmain_msg: {main_msg} \n----------------------")
               logging.debug(f"Main msg: {main_msg}")

          self._consor_publisher.publish(msg)
          self._sync_publisher.publish(main_msg)

          self.get_logger().info(f"Published synced data")

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
          self._flatten_movella_data(self._movella_data) # flatten movella data
          self.get_logger().info("Movella data received")

     def _flatten_movella_data(self, msg):
          self.movella_data = defaultdict(list)
          self.get_logger().debug("flatten msgs")
          
          for movella_sensor in msg.data: # msg - MovellaData .data
               for data in movella_sensor.data: # msg - MovellaSensor .data  => gives access to fields in MovellaImu
                    temp_dict = {}
                    temp_dict['id'] = movella_sensor.id  # msg - MovellaSensor .id
                    temp_dict['name'] = 'movella'

                    ts = data.header.stamp # header of MovellaImu
                    ts_ = self.convert_time(ts) # convert builtin-interfaces.Time to (double) timestamp 

                    # convert timestamp to required precision
                    ts_ = round(ts_ * self._no_seconds) / self._no_seconds

                    if ts_ not in self.movella_data:
                         self.movella_data[ts_] = []

                    for fields in data.__slots__: # iterate through each field to get their names & values
                         if fields not in ('_header'): # except header, add all other fields & their values to temp_dict
                              field_name = fields.strip('_')
                              field_value = getattr(data, fields)
                              temp_dict[field_name] = field_value
                              self.get_logger().debug(f"fields: {fields.strip('_')}, {getattr(data, fields)}")
                    
                    self.get_logger().debug(f"temp_dict: {temp_dict}")
                    
                    if temp_dict not in self.movella_data[ts_]:
                         self.movella_data[ts_].append(temp_dict) 
               self.movella_data = dict(sorted(self.movella_data.items()))


     def _esense_callback(self,msg):
          self._esense_data = msg
          self._flatten_esense_data(msg)
          self.get_logger().info("eSense data received")
     
     def _flatten_esense_data(self, msg):
          self.esense_data = defaultdict(list)
          self.get_logger().debug('esense flatten msgs')

          for data in msg.data:
               temp_dict = {}
               temp_dict['name'] = 'esense'
                    
               ts = data.header.stamp
               ts_ = self.convert_time(ts)

               # convert timestamp to required precision
               ts_ = round(ts_ * self._no_seconds) / self._no_seconds
               
               if ts_ not in self.esense_data:
                    self.esense_data[ts_] = []

               for fields in msg.__slots__:
                    if fields in ('id'):
                         id_ = msg.id
                         break
                    else:
                         id_ = 0
               
               temp_dict['id'] = id_

               field = msg.sensor_type
               if field == 'temperature':
                    field_name = 'temp'
               elif field == 'conductance':
                    field_name = 'cond'
               elif field == 'respiration':
                    field_name = 'resp'
               elif field == 'tempSimulator':
                    field_name = 'tempSim'
               elif field == 'condSimulator':
                    field_name = 'condSim'
               elif field == 'respSimulator':
                    field_name = 'respSim'
               else:
                    field_name = 'none'

               temp_dict[field_name] = data.sample_data

               self.get_logger().debug(f"each data: {data}")
               if temp_dict not in self.esense_data[ts_]:
                    self.esense_data[ts_].append(temp_dict)
          self.esense_data = dict(sorted(self.esense_data.items()))
          self.get_logger().debug(f"{self.esense_data}\n")


     # Since each modality in emotibit has its own ros2 topic, when new msgs are received emotibit_sync() is called
     def _emotibit_accelerometer_callback(self, msg):
          data = msg
          stream = "accelerometer"
          self._emotibit_synch(data,stream)

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
     

     def _emotibit_synch(self, data, stream):
          """
          This function combines data from all modalities from emotibit that is published as separate topics into a single msg
          """
          self.synched_flattened_emotibit_data = defaultdict(list)

          if self._emotibit_synch_data is None:
               self._emotibit_synch_data = EmotibitSynchData()
               setattr(self._emotibit_synch_data, stream, [data])
          else:
               setattr(self._emotibit_synch_data, stream, [data])
          
          temp_var = [True if getattr(self._emotibit_synch_data, attr) not in (None, []) else False 
                      for attr in self._emotibit_streams]
          self.get_logger().debug(f"temp_var: {temp_var}")
          if all(temp_var):
               self.get_logger().debug(f"emotibit sync data: {self._emotibit_synch_data}\n\n\n")
               self._emotibit_synch_publisher.publish(self._emotibit_synch_data)

               # Flatten the msg once all modalities are received
               self.synched_flattened_emotibit_data = self._emotibit_flatten_msgs(self._emotibit_synch_data)
               self.get_logger().info("Emotibit data received")

     def _emotibit_flatten_msgs(self, msg_):
          """
          Since each message is a nested batched msg, they should be flattened to get the timestamp for each sample.
          """

          # _msg: EmotibitSynchData.msg
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
               
               self.get_logger().debug(f"msg_: {msg_}")
               flattened_data = self._emotibit_flatten_helper_msg(msg, s, emotibit_data)
               flat_emotibit_data = dict(sorted(flattened_data.items()))
          self.get_logger().debug(f"{flat_emotibit_data.keys()}\n{flat_emotibit_data}\n\n")
          return flat_emotibit_data

     def _emotibit_flatten_helper_msg(self, msg, s, emotibit_data):
          """
          A helper function to flatten msgs from individual streams but also combine it with previously received msgs in case they have the same timestamp
          """
          # msg - EmotibitMsg.msg
          for index, timestamp in enumerate(msg.timestamp):
               temp_dict = {}
               temp_dict['name'] = 'emotibit'
                    
               ts = timestamp
               ts_ = self.convert_time(ts)

               # convert timestamp to required precision
               ts_ = round(ts_ * self._no_seconds) / self._no_seconds

               if ts_ not in emotibit_data:
                    emotibit_data[ts_] = []

               for fields in msg.__slots__:
                    if fields in ('id'):
                       id_ = msg.id
                       break
                    else:
                         id_ = 0 # in case of only a single sensor is present

               # if 'id' not in emotibit_data[ts_]:
               temp_dict['id'] = id_
               self.get_logger().debug(f"emotibit_data: {emotibit_data}, temp_dict: {temp_dict}")

               # i iterates through each channel
               for i in range(len(msg.data)): # msg.data -> gives access to EmotibitData.msg
                    # Each channel has an EmotibitData.msg, hence if len(msg.data) is more than 1 then a suffix for channel no is added.
                    if len(msg.data) > 1:
                         field_name = f"{s}_{i+1}"
                    else:
                         field_name = f"{s}"
                    field_value = msg.data[i].data[index] # Each datapoint has its own timestamp, hence index of timestamp is used to get the corresponding datavalue/datapoint
                    temp_dict[field_name] = field_value 
               
               if temp_dict not in emotibit_data[ts_]:
                    id_found = False
                    temp_index = 0
                    for t in range(len(emotibit_data[ts_])):
                         if temp_dict['id'] == emotibit_data[ts_][t]['id']:
                              id_found = True
                              temp_index = t
                              break
                    if id_found:
                         emotibit_data[ts_][temp_index].update(temp_dict)
                    else: 
                         emotibit_data[ts_].append(temp_dict)
          return emotibit_data
     


     def convert_time(self, timestamp, bool_to_nanos: bool =True):
          if bool_to_nanos:
               seconds = timestamp.sec
               nanosec = timestamp.nanosec * 1e-9

               time = seconds + nanosec
          else:
               time = Time()
               time.sec = int(timestamp)
               time.nanosec = int((timestamp % 1) * 1e9)

          return time
     


     def merge_data(self, dict_msgs:dict):
          """
          A function to merge data from multiple sensors into a single variable, synched w.r.t. the sample's timestamps
          """
          self.merged = defaultdict(list)

          # Separate the msgs to different variables
          if "movella" in dict_msgs:
               movella_msg = dict_msgs["movella"]
          if "emotibit" in dict_msgs:
               emotibit_msg = dict_msgs["emotibit"]
          if "esense" in dict_msgs:
               esense_msg = dict_msgs["esense"]
          
          # check if each msg variables are defined else define them as empty to avoid variable errors in the further code
          movella_msg = movella_msg if 'movella_msg' in locals() else {}
          emotibit_msg = emotibit_msg if 'emotibit_msg' in locals() else {}
          esense_msg = esense_msg if 'esense_msg' in locals() else {}

          for key in movella_msg.keys() | emotibit_msg.keys() | esense_msg.keys(): # combines unique keys from both msgs (keys here are the timestamps in decimals)

               # self.merged[key] = []

               if key in movella_msg:
                    temp_movella = self.flatten_nested_lists(movella_msg[key])
                    self.merged[key].extend(temp_movella)

               if key in emotibit_msg:
                    temp_emotibit = self.flatten_nested_lists(emotibit_msg[key])
                    self.merged[key].extend(temp_emotibit)

               if key in esense_msg:
                    temp_esense = self.flatten_nested_lists(esense_msg[key])
                    self.merged[key].extend(temp_esense)

          self.merged = dict(sorted(self.merged.items())) # sort the items by keys so that we get them in ascending order of timestamps
          self.get_logger().debug(f"merged: {self.merged}\n\n")
          logging.debug(f"merged: {self.merged}\n\n")

     def flatten_nested_lists(self, temp_dict):
          new_temp = []
          for k in range(len(temp_dict)):
               new_temp.append(temp_dict[k])
          return new_temp
               
          


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