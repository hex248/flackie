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

#初始化屏幕
disp_0 = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(bus_0, device_0),spi_freq=10000000,rst=RST_0,dc=DC_0,bl=BL_0)
disp_1 = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(bus_1, device_1),spi_freq=10000000,rst=RST_1,dc=DC_1,bl=BL_1)


# Define the BCM pin number of the button
KEY1_PIN = 25
KEY2_PIN = 26

# Set the button pin to input mode and use a pull-up resistor
key1 = disp_0.gpio_mode(KEY1_PIN,disp_0.INPUT,None)
key2 = disp_0.gpio_mode(KEY2_PIN,disp_0.INPUT,None)

# Initialize button state
curr_state_key1 = 0
curr_state_key2 = 0

def key1_callback(): #按键1中断回调函数
    global curr_state_key1
    global curr_state_key2
    print("KEY1 is Pressed!!!")
    curr_state_key1 = 1
    curr_state_key2 = 0

def key2_callback(): #按键2中断回调函数
    global curr_state_key1
    global curr_state_key2
    print("KEY2 is Pressed!!!")
    curr_state_key1 = 0
    curr_state_key2 = 1

#开启按键中断
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
curr_state_key1 = 0
curr_state_key2 = 0 
disp_0.ShowImage(image1)
disp_1.ShowImage(image1)

try:
    draw.rectangle((0,0,disp_0.width,disp_0.height),fill = "WHITE")
    Font1 = ImageFont.truetype("../Font/Font00.ttf",30)
    Font2 = ImageFont.truetype("../Font/Font00.ttf",15)
    Font3 = ImageFont.truetype("../Font/Font02.ttf",20)
    
    draw.text((18, 40), 'Hello Waveshare!', font = Font2, fill = "BLUE") 
    draw.text((10, 10), u'Please press the key', font = Font2, fill = "BLACK")
    disp_0.ShowImage(image1)
    disp_1.ShowImage(image1)

    while True:
        if curr_state_key1 == 1:
            draw.rectangle((0,0,disp_0.width,disp_0.height),fill = "WHITE")            
            draw.text((20, 0), u'你好微雪', font = Font1, fill = "CYAN")
            draw.text((18, 50), 'Hello Waveshare', font = Font2, fill = "CYAN")
            disp_0.ShowImage(image1)
            disp_1.ShowImage(image1)
            while(curr_state_key1 == 1): 
                time.sleep(0.01)
                    
        if curr_state_key2 == 1:            
            draw.rectangle((0,0,disp_0.width,disp_0.height),fill = "WHITE")
            image = Image.open('../pic/LCD_0inch96.jpg')
            disp_0.ShowImage(image)
            disp_1.ShowImage(image)
            while(curr_state_key2 == 1): 
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
