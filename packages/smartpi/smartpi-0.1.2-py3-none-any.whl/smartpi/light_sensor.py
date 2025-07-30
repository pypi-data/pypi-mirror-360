# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver



#光电读取 port:连接P端口；command:1:读取；2:开灯；3:关灯；
#def get_value(port:bytes,command:bytes) -> Optional[bytes]:
#    light_str=[0xA0, 0x02, 0x00, 0xBE]
#    light_str[0]=0XA0+port
#    light_str[2]=command 
#    response = base_driver.single_operate_sensor(light_str)
#    if response:
#        return 0
#    else:
#        return -1
        
def get_value(port:bytes) -> Optional[bytes]:
    light_str=[0xA0, 0x02, 0x00, 0xBE]
    light_str[0]=0XA0+port
    light_str[2]=1 
    response = base_driver.single_operate_sensor(light_str)
    if response:
        return 0
    else:
        return -1