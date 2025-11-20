#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os
import sys 
import time
import logging
import spidev as SPI
sys.path.append("..")
from lib import LCD_0inch96
from lib import Gain_Param
from PIL import Image,ImageDraw,ImageFont
import re 
import math

# Raspberry Pi pin configuration:
RST_0 =24 
DC_0 = 4
BL_0 = 13
bus_0 = 0 
device_0 = 0 

RST_1 =23 
DC_1 = 5
BL_1 = 12
bus_1 = 0 
device_1 = 1 

logging.basicConfig(level=logging.DEBUG)

try:
    disp_0 = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(bus_0, device_0),spi_freq=10000000,rst=RST_0,dc=DC_0,bl=BL_0,bl_freq=1000)
    disp_1 = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(bus_1, device_1),spi_freq=10000000,rst=RST_1,dc=DC_1,bl=BL_1,bl_freq=1000)

    gain = Gain_Param.Gain_Param()

    disp_0.Init()
    disp_1.Init()

    disp_0.clear()
    disp_1.clear()

    disp_0.bl_DutyCycle(100)
    disp_1.bl_DutyCycle(100)

    image1 = Image.new("RGB", (disp_0.width, disp_0.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    while True:
        #IP 
        ip = gain.GET_IP()
        Font1 = ImageFont.truetype("../Font/Font00.ttf",15)
        draw.text((5, 0), 'IP : '+ip, fill = 0x3cbdc4,font=Font1) 

        #time    
        time_t = time.strftime("%H:%M:%S", time.localtime())
        time_D = time.strftime("%Y-%m-%d ", time.localtime())
        draw.text((5, 25), "Data: "+time_D, fill = 0x46D017,font=Font1)
        draw.text((5, 50), "Time: "+time_t, fill = 0xf7ba47,font=Font1)

        disp_0.ShowImage(image1)
        draw.rectangle((0,0,disp_0.width,disp_0.height),fill = "WHITE") #Cache area covered with white

        #CPU usage
        CPU_usage= os.popen('top -bi -n 2 -d 0.02').read().split('\n\n\n')[0].split('\n')[2]
        CPU_usage= re.sub('[a-zA-z%(): ]','',CPU_usage)
        CPU_usage= CPU_usage.split(',')
        
        CPU_usagex =100 - eval(CPU_usage[3])
        draw.text((5, 0), "CPU Usage: " + str(math.floor(CPU_usagex))+'%', fill = 0x0b46e3,font=Font1,)
        
        #TEMP 
        temp_t = gain.GET_Temp()
        draw.text((5, 25), "Temp: "+str(math.floor(temp_t))+'℃', fill = 0x0088ff,font=Font1) 

        #System disk usage   
        x = os.popen('df -h /')
        i2 = 0
        while 1:
            i2 = i2 + 1
            line = x.readline()
            if i2==2:
                Capacity_usage = line.split()[4] # Memory usage (%)  
                Hard_capacity = int(re.sub('[%]','',Capacity_usage))
                break

        draw.text((5, 50), "Disk Usage: "+str(math.floor(Hard_capacity))+'%', fill = 0x986DFC,font=Font1) # BGR

        disp_1.ShowImage(image1)
        draw.rectangle((0,0,disp_0.width,disp_0.height),fill = "WHITE")
        time.sleep(0.01)

    disp_0.module_exit()
    disp_1.module_exit()
    logging.info("quit:")
except IOError as e:
    logging.info(e)    
except KeyboardInterrupt:
    disp_0.module_exit()
    disp_1.module_exit()
    logging.info("quit:")
    exit()
