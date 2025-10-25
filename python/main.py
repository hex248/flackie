import subprocess

from PIL import Image, ImageDraw, ImageFont

# set up display - if it isn't available, it will move on in dev mode
from inky import auto, InkyPHAT
display: InkyPHAT = None
try:
    display = auto()
except Exception as e:
    if ("No EEPROM detected!" in str(e)):
        print("no display connected, moving on... (dev mode)")
    else:
        print(f"error with display: {e}")

dimensions = (display.width, display.height) if display else (250, 122)

WHITE = display.WHITE if display else "#ffffff"
BLACK = display.BLACK if display else "#000000"
RED = display.RED if display else "#ff0000"
YELLOW = display.YELLOW if display else "#ffff00"

image = Image.new("P", dimensions, WHITE)
draw = ImageDraw.Draw(image)
font = ImageFont.load_default(40)

draw.text((10, 10), "inky", BLACK, font=font)


if display:
    display.set_image(image)
    display.show()
else:
    path = "/tmp/inky-simulated-output.png"
    image.save(path)
    subprocess.run(["imv", path, "-w", "inky-floating"])