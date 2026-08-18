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
A Python script defining custom Exceptions for EmotiBit sensor. 

Description:
    EmotiBit sensor connects to the ROS2 node via BrainFlow. Custom Python script that connects to the sensor is provided information such as Presets and Channels.
    Except for the predefined presets and channels, BrainFlow & EmotiBit does not recognise others. While this error is outputted by BrainFlow, these are defined as an exception that is raised in the pre-check before communicating with sensor.
    This will help quickly identify that the input (preset name or channel name in the EmotibitSensor() in sensors.py) provided to the function/method that will initiate communication with the sensor is incorrect.

Author:
    Swathy Cheruvalath <swathy.cheruvalath@smail.inf.h-brs.de
"""

class InvalidPresetError(Exception):
    pass

class InvalidChannelNameError(Exception):
    pass