# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver


##############################################################
#            motor.write_motor_dir(1,0)
#            motor.write_motor_speed(1,100)
#            time.sleep(0.5)
#            motor.write_motor_dir(1,1)
#            motor.write_motor_speed(1,50)
#            time.sleep(0.5)
##############################################################

#马达编码读取 port:连接M端口；
def read_motor_code(port:bytes) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x01, 0xBE]           
    motor_str[0]=0XA0+port       
    response = base_driver.single_operate_sensor(motor_str)
    if response:
        return 0
    else:
        return -1
        
#马达速度控制 port:连接M端口；speed:0~100
def write_motor_speed(port:bytes,speed:bytes) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x02, 0x71, 0x00, 0xBE]           
    motor_str[0]=0XA0+port
    motor_str[4]=speed
    response = base_driver.single_operate_sensor(motor_str)
    if response:
        return 0
    else:
        return -1
        
#马达速度编码控制 port:连接M端口；speed:0~100；code:0~65535
def motor_servoctl(port:bytes,speed:bytes,code:int) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x04, 0x81, 0x00, 0x81, 0x00, 0x00, 0xBE]           
    motor_str[0]=0XA0+port
    motor_str[4]=speed
    motor_str[6]=code//256
    motor_str[7]=code%256
    response = base_driver.single_operate_sensor(motor_str)
    if response:
        return 0
    else:
        return -1
        
#马达方向控制 port:连接M端口；dir:
def write_motor_dir(port:bytes,direc:bytes) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x06, 0x71, 0x00, 0xBE]           
    motor_str[0]=0XA0+port
    motor_str[4]=direc
    response = base_driver.single_operate_sensor(motor_str)
    if response:
        return 0
    else:
        return -1
        