import os
import sys
import time
import spidev as SPI
sys.path.append("..")
from lib import LCD_0inch96, LCD_1inch3
from PIL import Image, ImageDraw, ImageFont

# small display 0
TOP_RST = 24
TOP_DC = 4
TOP_BL = 13
TOP_bus = 0
TOP_device = 0
# small display 1
BOTTOM_RST = 23
BOTTOM_DC = 5
BOTTOM_BL = 12
BOTTOM_bus = 0
BOTTOM_device = 1
# main display
MAIN_RST = 27
MAIN_DC = 22
MAIN_BL = 19
MAIN_bus = 1
MAIN_device = 0

BTN1_PIN = 25
BTN2_PIN = 26

top_display = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(TOP_bus, TOP_device), spi_freq=10000000, rst=TOP_RST, dc=TOP_DC, bl=TOP_BL)
top_display.Init()
top_display.clear()
top_display.bl_DutyCycle(100)

bottom_display = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(BOTTOM_bus, BOTTOM_device), spi_freq=10000000, rst=BOTTOM_RST, dc=BOTTOM_DC, bl=BOTTOM_BL)
bottom_display.Init()
bottom_display.clear()
bottom_display.bl_DutyCycle(100)

main_display = LCD_1inch3.LCD_1inch3(spi=SPI.SpiDev(MAIN_bus, MAIN_device), spi_freq=10000000, rst=MAIN_RST, dc=MAIN_DC, bl=MAIN_BL)
main_display.Init()
main_display.clear()
main_display.bl_DutyCycle(100)


btn1 = top_display.gpio_mode(BTN1_PIN,top_display.INPUT,None)
btn2 = top_display.gpio_mode(BTN2_PIN,top_display.INPUT,None)

current_state_btn1 = 0
current_state_btn2 = 0

def btn1_callback():
    global current_state_btn1
    global current_state_btn2
    print("btn1 pressed")
    current_state_btn1 = 1
    current_state_btn2 = 0
    time.sleep(0.1)
    current_state_btn1 = 0
    print("btn1 UNPRESSED")

def btn2_callback():
    global current_state_btn1
    global current_state_btn2
    print("btn2 pressed")
    current_state_btn1 = 0
    current_state_btn2 = 1
    time.sleep(0.1)
    current_state_btn2 = 0
    print("btn2 UNPRESSED")

btn1.when_activated = btn1_callback
btn2.when_activated = btn2_callback

top_image = Image.new("RGB", (top_display.width, top_display.height), "BLACK")
top_draw = ImageDraw.Draw(top_image)
bottom_image = Image.new("RGB", (bottom_display.width, bottom_display.height), "BLACK")
bottom_draw = ImageDraw.Draw(bottom_image)
main_image = Image.new("RGB", (main_display.width, main_display.height), "BLACK")
main_draw = ImageDraw.Draw(main_image)

second_font = ImageFont.truetype("./fonts/JetBrainsMono-Regular.ttf", 20)
main_font = ImageFont.truetype("./fonts/JetBrainsMono-Regular.ttf", 30)


top_draw.text((10, 10), "1", fill="WHITE", font=second_font)
bottom_draw.text((10, 10), "2", fill="WHITE", font=second_font)
main_draw.text((10, 10), "0", fill="RED", font=main_font)

top_display.ShowImage(top_image)
bottom_display.ShowImage(bottom_image)
main_display.ShowImage(main_image)

while True:
    print("tick")
    time.sleep(1)

# shut down displays
top_display.module_exit()
bottom_display.module_exit()
main_display.module_exit()
