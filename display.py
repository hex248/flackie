import sys
import time
import spidev as SPI
sys.path.append("..")
from lib import LCD_0inch96, LCD_1inch3
from PIL import Image, ImageDraw, ImageFont

# main display
MAIN_RST = 27
MAIN_DC = 22
MAIN_BL = 19
MAIN_bus = 1
MAIN_device = 0
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

main_display = LCD_1inch3.LCD_1inch3(spi=SPI.SpiDev(MAIN_bus, MAIN_device), spi_freq=10000000, rst=MAIN_RST, dc=MAIN_DC, bl=MAIN_BL)
top_display = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(TOP_bus, TOP_device), spi_freq=10000000, rst=TOP_RST, dc=TOP_DC, bl=TOP_BL)
bottom_display = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(BOTTOM_bus, BOTTOM_device), spi_freq=10000000, rst=BOTTOM_RST, dc=BOTTOM_DC, bl=BOTTOM_BL)


BTN1_PIN = 25
BTN2_PIN = 26


def init(displays: list[int] = [0,1,2]):
    if 0 in displays:
        main_display.Init()
        main_display.clear()
        main_display.bl_DutyCycle(100)

    if 1 in displays:
        top_display.Init()
        top_display.clear()
        top_display.bl_DutyCycle(100)

    if 2 in displays:
        bottom_display.Init()
        bottom_display.clear()
        bottom_display.bl_DutyCycle(100)


def get_images(displays: list[int] = [0,1,2]):
    to_return = {}
    if 0 in displays:
        main_image = Image.new("RGB", (main_display.width, main_display.height), "BLACK")
        to_return["0"] = main_image
        draw_to(0, main_image)

    if 1 in displays:
        top_image = Image.new("RGB", (top_display.width, top_display.height), "BLACK")
        to_return["1"] = top_image
        draw_to(1, top_image)

    if 2 in displays:
        bottom_image = Image.new("RGB", (bottom_display.width, bottom_display.height), "BLACK")
        to_return["2"] = bottom_image
        draw_to(2, bottom_image)
        
    return to_return

def get_buttons():
    btn1 = top_display.gpio_mode(BTN1_PIN,top_display.INPUT,None)
    btn2 = top_display.gpio_mode(BTN2_PIN,top_display.INPUT,None)
    return btn1, btn2


# display: 0, 1, 2
def draw_to(display: int, image: Image):
    if display == 0:
        main_display.ShowImage(image)
    elif display == 1:
        top_display.ShowImage(image)
    elif display == 2:
        bottom_display.ShowImage(image)

def clean_up():
    top_display.module_exit()
    bottom_display.module_exit()
    main_display.module_exit()
