# © 2026 Hochschule Bonn-Rhein-Sieg <https://www.h-brs.de/>
# 
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
# Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program. If not, see <https://www.gnu.org/licenses/>.

"""
This file contains constants that are useful for testing emotibit_sdk.py with the help of unit-tests.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de>
"""
import numpy as np
import pandas as pd
import zat_ros2_msgs.msg
import std_msgs.msg
import builtin_interfaces.msg

# Board description
board_description_default = {'accel_channels': [1, 2, 3], 'gyro_channels': [4, 5, 6], 'magnetometer_channels': [7, 8, 9], 'marker_channel': 11, 'name': 'Emotibit', 'num_rows': 12, 'package_num_channel': 0, 'sampling_rate': 25, 'timestamp_channel': 10}
board_description_auxiliary = {'marker_channel': 5, 'name': 'Emotibit', 'num_rows': 6, 'package_num_channel': 0, 'ppg_channels': [1, 2, 3], 'sampling_rate': 25, 'timestamp_channel': 4}
board_description_ancillary = {'eda_channels': [1], 'marker_channel': 5, 'name': 'Emotibit', 'num_rows': 6, 'other_channels': [3], 'package_num_channel': 0, 'sampling_rate': 15, 'temperature_channels': [2], 'timestamp_channel': 4}


# Data from sensor
board_data_default = np.array([[52595, 52595, 52595, 52611, 52611, 52628, 52628, 52628, 52645, 52645, 52645],
                            [-0.294, -0.293, -0.293, -0.295, -0.292, -0.293, -0.294, -0.292, -0.294, -0.296, -0.294],
                            [-0.157, -0.157, -0.159, -0.157, -0.16, -0.158, -0.158, -0.158, -0.158, -0.156, -0.158],
                            [1.021, 1.018, 1.018, 1.017, 1.018, 1.02, 1.016, 1.016, 1.021, 1.019, 1.018],
                            [-0.519, -0.519, -0.519, -0.488, -0.488, -0.519, -0.488, -0.519, -0.488, -0.488, -0.519],
                            [0.183, 0.122, 0.122, 0.153, 0.153, 0.153, 0.183, 0.153, 0.153, 0.153, 0.183],
                            [-0.397, -0.397, -0.366, -0.427, -0.427, -0.366, -0.397, -0.397, -0.366, -0.397, -0.397],
                            [-11, -10, -11, -11, -10, -11, -11, -12, -11, -10, -11],
                            [4, 4, 5, 4, 4, 4, 3, 3, 3, 4, 3],
                            [-12, -10, -11, -11, -11, -10, -10, -10, -12, -11, -11],
                            [1778498622.087964, 1778498622.087965, 1778498622.087967, 1778498622.195255, 1778498622.195257, 1778498622.352508, 1778498622.35251, 
                                1778498622.352511, 1778498622.402883, 1778498622.402885, 1778498622.402887],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

board_data_auxiliary = np.array([[52583, 52583, 52583, 52598, 52598, 52615, 52615, 52615, 52632, 52632, 52632],
                            [3412, 3400, 3399, 3407, 3389, 3396, 3403, 3400, 3388, 3388, 3389],
                            [3915, 3931, 3917, 3924, 3921, 3917, 3914, 3915, 3905, 3907, 3914],
                            [549, 595, 589, 580, 553, 529, 557, 578, 578, 555, 577],
                            [1778498622.085108, 1778498622.08511, 1778498622.085112, 1778498622.195184, 1778498622.195186, 1778498622.35147, 1778498622.351472, 
                                1778498622.351474, 1778498622.398259, 1778498622.398262, 1778498622.398265],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

board_data_ancillary = np.array([[52584, 52584, 52599, 52616, 52616, 52633, 52633],
                            [0.031494, 0.031305, 0.031408, 0.031746, 0.031482, 0.0313, 0.031213],
                            [0, 0, 0, 30.585, 30.585, 30.537, 30.537],
                            [0, 0, 27.414, 27.439, 27.439, 27.439, 27.439],
                            [1778498622.085131, 1778498622.08514, 1778498622.195197, 1778498622.351492, 1778498622.351501, 1778498622.398302, 1778498622.398316],
                            [0, 0, 0, 0, 0, 0, 0]])


# Formatted data: DEFAULT PRESET (test stream: Accelerometer)
channels_default_preset = [1, 2, 3]
list_data_def_preset = [[-0.294, -0.157,  1.021], [-0.293, -0.157,  1.018], [-0.293, -0.159,  1.018], [-0.295, -0.157,  1.017], [-0.292, -0.160,  1.018],[-0.293, -0.158,  1.020], 
                        [-0.294, -0.158,  1.016], [-0.292, -0.158,  1.016], [-0.294, -0.158,  1.021], [-0.296, -0.156,  1.019], [-0.294, -0.158,  1.018]]
sensor_data_default_preset = pd.DataFrame(list_data_def_preset, columns=channels_default_preset)
timestamp_default_preset = [1778498622.087964, 1778498622.087965, 1778498622.087967, 1778498622.195255, 1778498622.195257, 1778498622.352508, 
                            1778498622.35251, 1778498622.352511, 1778498622.402883, 1778498622.402885, 1778498622.402887]
var_preset_default = 'def'
formatted_timestamp_default_preset = [1778498622.087964, 1778498622.127964, 1778498622.167964, 1778498622.207964, 1778498622.2479641, 1778498622.287964, 
                                      1778498622.327964, 1778498622.367964, 1778498622.407964, 1778498622.447964, 1778498622.4879642]
formatted_sensor_data_default = [[-0.294, -0.157,  1.021],[-0.293, -0.157,  1.018], [-0.293, -0.159,  1.018], [-0.295, -0.157,  1.017], [-0.292, -0.160,  1.018], [-0.293, -0.158,  1.020], 
                                 [-0.294, -0.158,  1.016], [-0.292, -0.158,  1.016], [-0.294, -0.158,  1.021], [-0.296, -0.156,  1.019],[-0.294, -0.158,  1.018]]
sensor_data_final_default = pd.DataFrame(formatted_sensor_data_default, columns=channels_default_preset)


# Formatted data: AUXILIARY PRESET (test stream: PPG)
channels_auxiliary_preset = [1, 2, 3]
list_data_aux_preset = [[3412.0,  3915.0,  549.0], [3400.0,  3931.0,  595.0], [3399.0,  3917.0,  589.0], [3407.0,  3924.0,  580.0], [3389.0,  3921.0,  553.0], [3396.0,  3917.0,  529.0], 
                        [3403.0,  3914.0,  557.0], [3400.0,  3915.0,  578.0], [3388.0,  3905.0,  578.0], [3388.0,  3907.0,  555.0], [3389.0,  3914.0,  577.0]]

sensor_data_auxiliary_preset = pd.DataFrame(list_data_aux_preset, columns=channels_auxiliary_preset)

timestamp_auxiliary_preset = [1778498622.085108, 1778498622.08511, 1778498622.085112, 1778498622.195184, 1778498622.195186, 1778498622.35147, 
                              1778498622.351472, 1778498622.351474, 1778498622.398259, 1778498622.398262, 1778498622.398265]
var_preset_auxiliary = 'aux'
formatted_timestamp_auxiliary_preset = [1778498622.085108, 1778498622.125108, 1778498622.165108, 1778498622.205108, 1778498622.2451081, 1778498622.285108, 
                                        1778498622.325108, 1778498622.365108, 1778498622.405108, 1778498622.445108, 1778498622.4851081]
formatted_sensor_data_auxiliary = [[3412.0,  3915.0,  549.0], [3400.0,  3931.0,  595.0], [3399.0,  3917.0,  589.0], [3407.0,  3924.0,  580.0], [3389.0,  3921.0,  553.0], [3396.0,  3917.0,  529.0], 
                                   [3403.0,  3914.0,  557.0], [3400.0,  3915.0,  578.0], [3388.0,  3905.0,  578.0], [3388.0,  3907.0,  555.0], [3389.0,  3914.0,  577.0]]
sensor_data_final_auxiliary = pd.DataFrame(formatted_sensor_data_auxiliary, columns=channels_auxiliary_preset)


# Formatted data: ANCILIARY PRESET (test stream: Temperature)
channels_anciliary_preset = [2]
list_data_anc_preset = [ 0.000, 0.000, 0.000, 30.585, 30.585, 30.537, 30.537]
sensor_data_anciliary_preset = pd.DataFrame(list_data_anc_preset, columns=channels_anciliary_preset)
timestamp_anciliary_preset = [1778498622.085131, 1778498622.08514, 1778498622.195197, 1778498622.351492, 1778498622.351501, 1778498622.398302, 1778498622.398316]
var_preset_anciliary = 'anc'
formatted_timestamp_anciliary_preset = [1778498622.085131, 1778498622.1517975, 1778498622.2184644, 1778498622.285131] # timestamp reduced since zeroes removed from sensor data
formatted_sensor_data_anciliary = [30.585, 30.585, 30.537, 30.537]
sensor_data_final_anciliary = pd.DataFrame(formatted_sensor_data_anciliary, columns=channels_anciliary_preset)


# Published_msgs
main_msg_default_preset = zat_ros2_msgs.msg.EmotibitMsg(header=std_msgs.msg.Header(stamp=builtin_interfaces.msg.Time(sec=0, nanosec=0), frame_id=''), 
                                                    stream=1, 
                                                    data=[
                                                        zat_ros2_msgs.msg.EmotibitData(channel=1, 
                                                                                    data=[-0.294, -0.293, -0.293, -0.295, -0.292, -0.293, -0.294, -0.292, -0.294, -0.296, -0.294]), 
                                                        zat_ros2_msgs.msg.EmotibitData(channel=2, 
                                                                                    data=[-0.157, -0.157, -0.159, -0.157, -0.16, -0.158, -0.158, -0.158, -0.158, -0.156, -0.158]), 
                                                        zat_ros2_msgs.msg.EmotibitData(channel=3, 
                                                                                    data=[1.021, 1.018, 1.018, 1.017, 1.018, 1.02, 1.016, 1.016, 1.021, 1.019, 1.018])
                                                    ], 
                                                    timestamp=[
                                                            builtin_interfaces.msg.Time(sec=1778498622, nanosec=87964057), builtin_interfaces.msg.Time(sec=1778498622, nanosec=127964019), 
                                                            builtin_interfaces.msg.Time(sec=1778498622, nanosec=167963981), builtin_interfaces.msg.Time(sec=1778498622, nanosec=207963943), 
                                                            builtin_interfaces.msg.Time(sec=1778498622, nanosec=247964143), builtin_interfaces.msg.Time(sec=1778498622, nanosec=287964105), 
                                                            builtin_interfaces.msg.Time(sec=1778498622, nanosec=327964067), builtin_interfaces.msg.Time(sec=1778498622, nanosec=367964029), 
                                                            builtin_interfaces.msg.Time(sec=1778498622, nanosec=407963991), builtin_interfaces.msg.Time(sec=1778498622, nanosec=447963953), 
                                                            builtin_interfaces.msg.Time(sec=1778498622, nanosec=487964153)
                                                    ])

main_msg_auxiliary_preset = zat_ros2_msgs.msg.EmotibitMsg(header=std_msgs.msg.Header(stamp=builtin_interfaces.msg.Time(sec=0, nanosec=0), frame_id=''), 
                                                    stream=4, 
                                                    data=[
                                                        zat_ros2_msgs.msg.EmotibitData(channel=1, 
                                                                                    data=[3412.0, 3400.0, 3399.0, 3407.0, 3389.0, 3396.0, 3403.0, 3400.0, 3388.0, 3388.0, 3389.0]), 
                                                        zat_ros2_msgs.msg.EmotibitData(channel=2, 
                                                                                        data=[3915.0, 3931.0, 3917.0, 3924.0, 3921.0, 3917.0, 3914.0, 3915.0, 3905.0, 3907.0, 3914.0]), 
                                                        zat_ros2_msgs.msg.EmotibitData(channel=3, data=[549.0, 595.0, 589.0, 580.0, 553.0, 529.0, 557.0, 578.0, 578.0, 555.0, 577.0])
                                                    ], 
                                                    timestamp=[
                                                        builtin_interfaces.msg.Time(sec=1778498622, nanosec=85108041), builtin_interfaces.msg.Time(sec=1778498622, nanosec=125108003), 
                                                        builtin_interfaces.msg.Time(sec=1778498622, nanosec=165107965), builtin_interfaces.msg.Time(sec=1778498622, nanosec=205107927), 
                                                        builtin_interfaces.msg.Time(sec=1778498622, nanosec=245108127), builtin_interfaces.msg.Time(sec=1778498622, nanosec=285108089), 
                                                        builtin_interfaces.msg.Time(sec=1778498622, nanosec=325108051), builtin_interfaces.msg.Time(sec=1778498622, nanosec=365108013), 
                                                        builtin_interfaces.msg.Time(sec=1778498622, nanosec=405107975), builtin_interfaces.msg.Time(sec=1778498622, nanosec=445107936), 
                                                        builtin_interfaces.msg.Time(sec=1778498622, nanosec=485108137)
                                                    ])

main_msg_anciliary_preset = zat_ros2_msgs.msg.EmotibitMsg(header=std_msgs.msg.Header(stamp=builtin_interfaces.msg.Time(sec=0, nanosec=0), frame_id=''), 
                                                    stream=6, 
                                                    data=[
                                                        zat_ros2_msgs.msg.EmotibitData(channel=0, 
                                                                                    data=[30.585, 30.585, 30.537, 30.537])
                                                    ], 
                                                    timestamp=[
                                                        builtin_interfaces.msg.Time(sec=1778498622, nanosec=85130929), builtin_interfaces.msg.Time(sec=1778498622, nanosec=151797533), 
                                                        builtin_interfaces.msg.Time(sec=1778498622, nanosec=218464374), builtin_interfaces.msg.Time(sec=1778498622, nanosec=285130977)
                                                    ])
