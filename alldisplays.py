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


top_image = Image.new("RGB", (top_display.height, top_display.width), "BLACK")
top_draw = ImageDraw.Draw(top_image)
bottom_image = Image.new("RGB", (bottom_display.height, bottom_display.width), "BLACK")
bottom_draw = ImageDraw.Draw(bottom_image)
main_image = Image.new("RGB", (main_display.height, main_display.width), "BLACK")
main_draw = ImageDraw.Draw(main_image)

font20 = ImageFont.truetype("../lib/Font/Font01.ttf", 20)

top_draw.text((10, 10), "Top Display", fill="WHITE", font=font20)
bottom_draw.text((10, 10), "Bottom Display", fill="WHITE", font=font20)
main_draw.text((10, 10), "Main Display", fill="WHITE", font=font20)

print("putting text on displays")
top_display.ShowImage(top_image.rotate(270))
bottom_display.ShowImage(bottom_image.rotate(270))
main_display.ShowImage(main_image.rotate(270))

time.sleep(10)


# shut down displays
top_display.module_exit()
bottom_display.module_exit()
main_display.module_exit()