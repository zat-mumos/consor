#!/usr/bin/env python3
from collections import defaultdict, deque
from decimal import Decimal
import threading

import rclpy
from rclpy.node import Node
from rclpy.logging import LoggingSeverity
from builtin_interfaces.msg import Time 
import cv2
import numpy as np
import logging 
from zat_ros2_msgs.msg import MovellaData, ZatConsorSynch, EmotibitMsg, EmotibitSynchData, EsenseStream, SynchData, DataPoint
import math
import copy

class ZatConsorNode(Node):
     def __init__(
          self,
          sync_period: float = 0.001,
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


          self.declare_parameters(
               namespace='',
               parameters=[
                    ('sync_period', sync_period),
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

          sync_period = self.get_parameter('sync_period').value
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
          self._emotibit_streams = ["accelerometer", "gyroscope", "magnetometer", "ppg", "eda", "temperature"]

          self.list_ids = { # keep track of how many sensors are presnt
               'movella': [], 'emotibit': [], 'esense':[]
          }
          self.count_keys={
               'movella': {
                    'total_keys': 18,
                    'curr_keys': {}
               },
               'emotibit': {
                    'total_keys': 16,
                    'curr_keys': {}
               },
               'esense': {
                    'total_keys': 3,
                    'curr_keys': {}
               }
          }
          
          self.prev_timestamp = None
          self.prev_data = None
          self.next_timestamp = None
          self.sync_period = sync_period
          self.sync_period_expo = abs(int(math.log10(self.sync_period)))
          self._no_seconds = 10 ** self.sync_period_expo
          self.get_logger().info(f"Precision: {sync_period}")
          self.get_logger().info(f"sampling rate: {self._no_seconds}") # i.e., if sync period=0.001 then self._no_seconds=1000 which is the srate
          
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
        
          self._consor_publisher = self.create_publisher(ZatConsorSynch, consor_wearable_sensor_topic, 10)
          self._sync_publisher = self.create_publisher(SynchData, sync_topic, 10)

          self.temp = 0

          timer_period = 1.0
          self.get_logger().info(f"Precision: {sync_period}")
          self.get_logger().info(f"sampling rate: {self._no_seconds}") # i.e., if sync period=0.001 then self._no_seconds=1000 which is the srate
          self.get_logger().info(f"callback timer duration: {timer_period}")
          self.timer = self.create_timer(timer_period, self.timer_callback)

     def timer_callback(self):
          """to publish the synchronized data of the wearble sensors"""
          
          msg = ZatConsorSynch()

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
          self.get_logger().debug(f"No of keys: {len(self.merged.keys())}")
          for key in self.merged.keys(): # every key is a new timestamp and therefore, the main msg is reset for each key since synchronised data can only have one timestamp. Also, the data is not batched here.
               main_msg = SynchData()
               batch_sync = []
               self.get_logger().debug(f"timestamp key: {key}")
               timestamp = self.convert_time(key, False)
               self.get_logger().debug(f"timestamp key: {timestamp}")
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
               self._sync_publisher.publish(main_msg)
               self.get_logger().info(f"Published synched msg")

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
          self._flatten_movella_data(self._movella_data) # flatten movella data
          self.get_logger().info("Movella data received")

     def _flatten_movella_data(self, msg):
          self.movella_data = defaultdict(list)
          self.get_logger().debug("flatten msgs")

          sensor_name = 'movella'
          for movella_sensor in msg.data: # msg - MovellaData .data
               for data in movella_sensor.data: # msg - MovellaSensor .data  => gives access to fields in MovellaImu
                    temp_dict = {}
                    temp_dict['id'] = movella_sensor.id  # msg - MovellaSensor .id
                    temp_dict['name'] = sensor_name

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
                         id_found = False
                         temp_index = 0
                         for t in range(len(self.movella_data[ts_])):
                              if temp_dict['id'] == self.movella_data[ts_][t]['id']:
                                   id_found = True
                                   temp_index = t
                                   break
                         if id_found:
                              self.movella_data[ts_][temp_index].update(temp_dict)
                         else:
                              self.movella_data[ts_].append(temp_dict) 
                    if movella_sensor.id not in self.count_keys[sensor_name]['curr_keys']: self.count_keys[sensor_name]['curr_keys'][movella_sensor.id] = 0
                    if movella_sensor.id not in self.list_ids[sensor_name]: self.list_ids[sensor_name].append(movella_sensor.id)
                    self.initialise_prev_data(sensor_name, self.movella_data[ts_])
               self.movella_data = dict(sorted(self.movella_data.items()))


     def _esense_callback(self,msg):
          self._esense_data = msg
          self._flatten_esense_data(msg)
          self.get_logger().info("eSense data received")
     
     def _flatten_esense_data(self, msg):
          self.esense_data = defaultdict(list)
          self.get_logger().debug('esense flatten msgs')

          sensor_name = 'esense'
          for data in msg.data:
               temp_dict = {}
                    
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
               temp_dict['name'] = sensor_name

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
                    id_found = False
                    temp_index = 0
                    for t in range(len(self.esense_data[ts_])):
                         if temp_dict['id'] == self.esense_data[ts_][t]['id']:
                              id_found = True
                              temp_index = t
                              break
                    if id_found:
                         self.esense_data[ts_][temp_index].update(temp_dict)
                    else: 
                         self.esense_data[ts_].append(temp_dict)
               if id_ not in self.count_keys[sensor_name]['curr_keys']: self.count_keys[sensor_name]['curr_keys'][id_] = 0
               if id_ not in self.list_ids[sensor_name]: self.list_ids[sensor_name].append(id_)
               self.initialise_prev_data(sensor_name, self.esense_data[ts_])
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

          sensor_name = 'emotibit'
          for index, timestamp in enumerate(msg.timestamp): # msg - EmotibitMsg.msg
               temp_dict = {}
                    
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
               temp_dict['name'] = sensor_name
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

          if id_ not in self.count_keys[sensor_name]['curr_keys']: self.count_keys[sensor_name]['curr_keys'][id_] = 0
          if id_ not in self.list_ids[sensor_name]: self.list_ids[sensor_name].append(id_)
          self.initialise_prev_data(sensor_name, emotibit_data[ts_])
          return emotibit_data
     
     def convert_time(self, timestamp, bool_to_s: bool =True):
          if bool_to_s:
               seconds = Decimal(timestamp.sec)
               nanosec = Decimal(timestamp.nanosec) / Decimal(1000000000)
               time = seconds + nanosec
          else:
               time = Time()
               time.sec = int(timestamp)
               temp_var = round((timestamp % 1) * self._no_seconds) # get no. of digits according to precision (dynamic to user input) instead of (fixed) nanoseconds
               i = 9 - self.sync_period_expo #len(str(temp_var)) # sync_period_exp is used here so that .509 = 509,000,000 ns & .013 = 13,000,000 ns
               while i >= 0:
                    try:
                         time.nanosec = int(temp_var) * (10 ** i)
                         break
                    except:
                         i = i - 1
               self.get_logger().debug(f"Timestamp: {timestamp} ; nanos: {time.nanosec}")

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

          if self.prev_data is not None:
               for key in sorted(movella_msg.keys() | emotibit_msg.keys() | esense_msg.keys()): # combines unique keys from both msgs (keys here are the timestamps in decimals) & sorts them in ascending order
                    bool_upd_prev_data = False
                    while not bool_upd_prev_data:
                         if self.prev_timestamp is None: # i.e., first iteration
                              self.prev_timestamp = key
                              self.next_timestamp = self.prev_timestamp + self.sync_period
                              bool_upd_prev_data = True
                              self.get_logger().debug(f"0. {self.prev_timestamp}\t{self.next_timestamp}\tkey:{key}\tsync_period:{self.sync_period}")
                         else: # at this point, self.prev_timestamp & self.next_timestamp is not None & self.prev_data is updated from prev.iteration
                              if self.next_timestamp is not None:
                                   if key == self.next_timestamp:
                                        self.prev_timestamp = self.next_timestamp
                                        self.next_timestamp = key + self.sync_period
                                        bool_upd_prev_data = True 
                                        self.get_logger().debug(f"1. {self.prev_timestamp}\t{self.next_timestamp}\tkey:{key}\tsync_period:{self.sync_period}")
                                   elif key < self.prev_timestamp: 
                                        self.get_logger().debug(f"Continuing .....")
                                        break
                                   elif key != self.next_timestamp:
                                        self.temp +=1
                                        self.prev_timestamp = self.next_timestamp
                                        self.next_timestamp = self.next_timestamp + self.sync_period
                                        bool_upd_prev_data = False # self.prev_data is not updated when key differs from self.next_timestamp - datapoints received at unequal intervals of time
                                        self.get_logger().debug(f"2. {self.prev_timestamp}\t{self.next_timestamp}\tkey:{key}\tsync_period:{self.sync_period}")
                         
                         self.next_timestamp = round(self.next_timestamp * self._no_seconds)/self._no_seconds # if sync_period is 0.1, adding this to timestamp does not increment exactly by 0.1 but sometimes as 0.999998
                         new_key = self.prev_timestamp # in case of missing timestamps
                         if key in movella_msg:
                              self.get_logger().warn("MOVELLA")
                              temp_movella = self.flatten_nested_lists('movella', movella_msg[key], bool_upd_prev_data)
                              self.merged[new_key].extend(temp_movella)

                         if key in emotibit_msg:
                              temp_emotibit = self.flatten_nested_lists('emotibit', emotibit_msg[key], bool_upd_prev_data)
                              self.merged[new_key].extend(temp_emotibit)

                         if key in esense_msg:
                              temp_esense = self.flatten_nested_lists('esense', esense_msg[key], bool_upd_prev_data)
                              self.merged[new_key].extend(temp_esense)
               self.merged = dict(sorted(self.merged.items())) # sort the items by keys so that we get them in ascending order of timestamps
               self.get_logger().debug(f"merged: {self.merged}\n\n")
               # if self.temp == 3:
               #      self.get_logger().error("self.temp == 3")

          else:
               self.get_logger().error(f"CONDITION not SET: self.prev_data is None\ndict_msgs: {dict_msgs}")

     def flatten_nested_lists(self, sensor_name, temp_dict, bool_upd_prev_data:bool=False):
          if bool_upd_prev_data:
               for j in range(len(temp_dict)): # for multiple ids
                    # assuming all ids are already added to self.prev_data
                    for i in range(len(self.prev_data[sensor_name])):
                         if temp_dict[j]['id'] == self.prev_data[sensor_name][i]['id']:
                              for k,v in temp_dict[j].items():
                                   self.prev_data[sensor_name][i][k] = v
          new_temp = copy.deepcopy(self.prev_data[sensor_name])
          return new_temp

     def initialise_prev_data(self, sensor_name, list_dict_sensor_values:list=[]):
          if self.prev_data is None:
               self.prev_data = {}
          if sensor_name not in self.prev_data.keys():
               self.prev_data[sensor_name] = [] # list for data from multiple ids
          
          if self.prev_data[sensor_name] == []:
               for j in range(len(list_dict_sensor_values)):
                    self.helper_init_prev_data(sensor_name,0,j,list_dict_sensor_values,False)

          elif self.prev_data[sensor_name] != [] and len(list_dict_sensor_values) > 0:
               for j in range(len(list_dict_sensor_values)): # for each id 
                    bool_id_found = False
                    for i in range(len(self.prev_data[sensor_name])): # for each id in self.prev_data
                         if list_dict_sensor_values[j]['id'] !=  self.prev_data[sensor_name][i]['id']:
                              bool_id_found = False
                              continue
                         else:
                              bool_id_found = True
                              self.helper_init_prev_data(sensor_name,i,j,list_dict_sensor_values,bool_id_found)
                    if bool_id_found == False: # new id found which is not a part of self.prev_data
                         self.helper_init_prev_data(sensor_name, 0, j, list_dict_sensor_values, bool_id_found)


     def helper_init_prev_data(self, sensor_name:str, i:int=0, j:int=0, list_dict_sensor_values:list=[], bool_data_init:bool=False):
          curr_id = list_dict_sensor_values[j]['id']
          if self.count_keys[sensor_name]['curr_keys'][curr_id] < self.count_keys[sensor_name]['total_keys']:
               if bool_data_init:
                    for k,v in list_dict_sensor_values[j].items():
                         if k not in self.prev_data[sensor_name][i].keys(): # count exceeds total keys due to repetition & does not include all keys either w/o this condition
                              if k == 'id' or k == 'name':
                                   self.prev_data[sensor_name][i][k] = v
                              else:
                                   self.prev_data[sensor_name][i][k] = 0.0
                              self.count_keys[sensor_name]['curr_keys'][curr_id] += 1
               else:
                    self.prev_data[sensor_name].append({})
                    len_prev_data = len(self.prev_data[sensor_name]) - 1
                    for k, v in list_dict_sensor_values[j].items():
                         if k not in self.prev_data[sensor_name][len_prev_data].keys(): # count exceeds total keys due to repetition & does not include all keys either w/o this condition
                              if k=='id' or k=='name':
                                   self.prev_data[sensor_name][len_prev_data][k] = v
                              else:
                                   self.prev_data[sensor_name][len_prev_data][k] = 0.0
                              self.count_keys[sensor_name]['curr_keys'][curr_id] += 1

                              
     
               
def main():
     rclpy.init(args= None)
     consor =  ZatConsorNode(
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