import subprocess

from PIL import Image, ImageDraw, ImageFont

def format_time(seconds: int) -> str:
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}:{secs:02d}"

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
RED = display.RED if display else "#df3131"
YELLOW = display.YELLOW if display else "#efef14"

image = Image.new("P", dimensions, WHITE)
draw = ImageDraw.Draw(image)
title_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 20)
album_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 18)
artist_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 14)
time_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 12)

padding = 10
# draw.rectangle((padding, padding, dimensions[0]-padding, dimensions[1]-padding), outline=RED)

draw.text((padding, padding), "title", BLACK, font=title_font)
draw.text((padding, padding + 26), "album", BLACK, font=album_font)
draw.text((padding, padding + 52), "artist", BLACK, font=artist_font)

track_length = 119
track_progress = 12
progress_percent = track_progress / track_length
progress_bar_height = 6

start_x = padding
start_y = dimensions[1] - padding - progress_bar_height
end_x = dimensions[0] - padding
end_y = start_y + progress_bar_height

draw.rectangle((start_x, start_y, end_x, end_y), outline=BLACK, fill=WHITE)
progress_width = int(234 * progress_percent)
draw.rectangle((start_x, start_y, start_x + progress_width, end_y), fill=BLACK)

track_progress_formatted = format_time(track_progress)
draw.text((start_x, start_y - 18), track_progress_formatted, BLACK, font=time_font)
track_length_formatted = format_time(track_length)
draw.text((end_x - 28, start_y - 18), track_length_formatted, BLACK, font=time_font)


if display:
    display.set_image(image)
    display.show()
else:
    path = "/tmp/inky-simulated-output.png"
    image.save(path)
    subprocess.run(["imv", path, "-w", "inky-floating"])
