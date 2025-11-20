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
RST =24 
DC = 4
BL = 13
bus = 0 
device = 0 
logging.basicConfig(level=logging.DEBUG)
try:
    # display with hardware SPI:
    ''' Warning!!!Don't  creation of multiple displayer objects!!! '''
    disp = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(bus, device),spi_freq=10000000,rst=RST,dc=DC,bl=BL)
    #disp = LCD_0inch96.LCD_0inch96()
    
    # Initialize library.
    disp.Init()
    # Clear display.
    disp.clear()
    #Set the backlight to 100
    disp.bl_DutyCycle(100)
    # Create blank image for drawing.
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    
    logging.info("show image")
    image = Image.open('../pic/LCD_0inch96.jpg')	
    disp.ShowImage(image)
    time.sleep(1)

    Font1 = ImageFont.truetype("../Font/Font00.ttf",30)
    Font2 = ImageFont.truetype("../Font/Font00.ttf",15)
    Font3 = ImageFont.truetype("../Font/Font02.ttf",20)
    logging.info("draw text")
    draw.text((20, 0), u'你好微雪', font = Font1, fill = "CYAN")
    draw.text((18, 50), 'Hello Waveshare', font = Font2, fill = "CYAN")
    disp.ShowImage(image1)
    time.sleep(3)

    disp.module_exit()
    logging.info("quit:")
except IOError as e:
    logging.info(e)    
except KeyboardInterrupt:
    disp.module_exit()
    logging.info("quit:")
    exit()
