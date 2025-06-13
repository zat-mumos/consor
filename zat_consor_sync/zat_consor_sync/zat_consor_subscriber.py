#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from zat_ros2_msgs.msg import MovellaData, PhysioSensor, ZatConsorSynch


class zat_consor_node(Node):
    def __init__(
            self,
            movella_topic: str = '/sensor/movella/imu_data',
            esense_topic: str = '/sensor/esense/data',
            consor_wearable_sensor_topic: str = 'sensor/consor/wearable/data'):


        super().__init__('zat_consor_node')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('movella_topic', movella_topic),
                ('esense_topic', esense_topic),
                ('consor_wearable_sensor_topic', consor_wearable_sensor_topic)
            ])


        movella_topic=self.get_parameter('movella_topic').value
        esense_topic = self.get_parameter('esense_topic').value
        consor_wearable_sensor_topic=self.get_parameter('consor_wearable_sensor_topic').value

        self._esense_data = None
        self._movella_data = None
        self._old_esense_data = None
        self._old_movella_data = None


        self._movella_subscriber = self.create_subscription(MovellaData,
                                                            movella_topic,
                                                            self._movella_callback,
                                                            10)
        
        self._esense_subscriber = self.create_subscription(PhysioSensor,
                                                           esense_topic,
                                                           self._esense_callback,
                                                           10)
        
        self._consor_publisher=self.create_publisher(ZatConsorSynch,consor_wearable_sensor_topic,10)

        timer_period=0.5
        self.timer=self.create_timer(timer_period,self.timer_callback)

    def timer_callback(self):
            
            msg=ZatConsorSynch()

            if self._esense_data and self._movella_data is not None:

                msg.esense_data=[self._esense_data]
                msg.movella_data=[self._movella_data]

                self._consor_publisher.publish(msg)

                self._old_esense_data = self._esense_data
                self._old_movella_data = self._movella_data

                self._esense_data = None
                self._movella_data = None

                self.get_logger().info("Pusblished consor data with latest Movella and eSense data")

            elif self._esense_data and self._old_movella_data is not None :
                 
                 msg.esense_data=[self._esense_data]
                 msg.movella_data=[self._old_movella_data]

                 self._old_esense_data = self._esense_data
                 self._esense_data = None

                 self.get_logger().info("Pusblished consor data with latest eSense data and old Movella data")

            elif self._movella_data and self._old_esense_data is not None:

                 msg.esense_data=[self._old_esense_data]
                 msg.movella_data=[self._movella_data]

                 self._old_movella_data = self._movella_data
                 self._movella_data = None
                 
                 self.get_logger().info("Pusblished consor data with latest Movella data and old eSense data")


    def _movella_callback(self,msg):
          self._movella_data = msg
          self._flag_1 = True
          self.get_logger().info("Movella data received")

    def _esense_callback(self,msg):
         self._esense_data = msg
         self._flag_2 = True
         self.get_logger().info("eSense data received")


def main():
     rclpy.init(args= None)
     consor =  zat_consor_node(
             movella_topic = '/sensor/movella/imu_data',
             esense_topic = '/sensor/esense/data',
             consor_wearable_sensor_topic = 'sensor/consor/wearable/data')
     rclpy.spin(consor)

     consor.destroy_node()
     rclpy.shutdown()
     
if __name__ == '__main__':
     main()


        
