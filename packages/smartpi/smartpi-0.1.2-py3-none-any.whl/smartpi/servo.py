# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver


###############################################
#                  servo.servo_operate(1,1,0)                  
#                  time.sleep(0.5)
#                  servo.servo_operate(1,1,180)
#                  time.sleep(0.5)
###############################################

#舵机控制 port:连接P端口；command:1:驱动  angle:角度
def servo_operate(port:bytes,command:bytes,angle:bytes) -> Optional[bytes]:
    servo_str=[0xA0, 0x0E, 0x01, 0x71, 0x00, 0xBE]
    servo_str[0]=0XA0+port
    servo_str[2]=command
    servo_str[4]=angle
    response = base_driver.single_operate_sensor(servo_str)
    if response:
        return 0
    else:
        return -1
        