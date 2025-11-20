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
from PIL import Image,ImageDraw,ImageFont

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

import re 
import math
from lib import Gain_Param

#Initialize screen
disp_0 = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(bus_0, device_0),spi_freq=10000000,rst=RST_0,dc=DC_0,bl=BL_0)
disp_1 = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(bus_1, device_1),spi_freq=10000000,rst=RST_1,dc=DC_1,bl=BL_1)

# Define the BCM pin number of the button
KEY1_PIN = 25
KEY2_PIN = 26

# Set the button pin to input mode and use a pull-up resistor
# GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(KEY2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
key1 = disp_0.gpio_mode(KEY1_PIN,disp_0.INPUT,None)
key2 = disp_0.gpio_mode(KEY2_PIN,disp_0.INPUT,None)

# Initialize button state
curr_state_key1 = 0
curr_state_key2 = 0

def key1_callback(): # Key 1 interrupt callback function
    global curr_state_key1
    global curr_state_key2
    curr_state_key1 = 1
    curr_state_key2 = 0

def key2_callback():# Key 2 interrupt callback function
    global curr_state_key1
    global curr_state_key2
    curr_state_key1 = 0
    curr_state_key2 = 1
    
#Enable key interrupt
key1.when_activated = key1_callback
key2.when_activated = key2_callback

#Initialize variables that control the screen through keystrokes
flat_1 = 0
flat_2 = 0

disp_0.Init()
disp_1.Init()

disp_0.clear()
disp_1.clear()

disp_0.bl_DutyCycle(100)
disp_1.bl_DutyCycle(100)

image1 = Image.new("RGB", (disp_0.width, disp_0.height), "WHITE")
draw = ImageDraw.Draw(image1)
gain = Gain_Param.Gain_Param()

disp_0.ShowImage(image1)
disp_1.ShowImage(image1)

logging.basicConfig(level=logging.DEBUG)

try:
    while True:
        if curr_state_key1 == 1:
            draw.rectangle((0,0,disp_0.width,disp_0.height),fill = "WHITE")
            Font1 = ImageFont.truetype("../Font/Font00.ttf",30)
            Font2 = ImageFont.truetype("../Font/Font00.ttf",15)
            Font3 = ImageFont.truetype("../Font/Font02.ttf",20)
            logging.info("draw text")
            draw.text((20, 0), u'你好微雪', font = Font1, fill = "CYAN")
            draw.text((18, 50), 'Hello Waveshare', font = Font2, fill = "CYAN")
            disp_0.ShowImage(image1)
            disp_1.ShowImage(image1)
            time.sleep(1.5)

            logging.info("show image")
            image = Image.open('../pic/LCD_0inch96.jpg')
            disp_0.ShowImage(image)
            disp_1.ShowImage(image)
            time.sleep(1.5)

        if curr_state_key2 == 1:
            #IP 
            draw.rectangle((0,0,disp_0.width,disp_0.height),fill = "WHITE")
            ip = gain.GET_IP()
            Font1 = ImageFont.truetype("../Font/Font00.ttf",15)
            draw.text((5, 0), 'IP : '+ip, fill = 0x3cbdc4,font=Font1) 

            #time 
            time_t = time.strftime("%H:%M:%S", time.localtime())
            time_D = time.strftime("%Y-%m-%d ", time.localtime())
            draw.text((5, 25), "Data: "+time_D, fill = 0x46D017,font=Font1)
            draw.text((5, 50), "Time: "+time_t, fill = 0xf7ba47,font=Font1)

            disp_0.ShowImage(image1)
            draw.rectangle((0,0,disp_0.width,disp_0.height),fill = "BLACK") #The cache area is covered with black

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
