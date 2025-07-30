# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver


#²ÊµÆ¿ØÖÆ port:Á¬½ÓP¶Ë¿Ú£»command:0:¹ØµÆ£»1:ºì£»2:ÂÌ£»3:À¶£»4:»Æ£»5:×Ï£»6:Çà£»7:°×
def set_color(port:bytes,command:bytes) -> Optional[bytes]:
    color_lamp_str=[0xA0, 0x05, 0x00, 0xBE]
    color_lamp_str[0]=0XA0+port
    color_lamp_str[2]=command
    response = base_driver.single_operate_sensor(color_lamp_str)
    if response:
        return 0
    else:
        return -1
        