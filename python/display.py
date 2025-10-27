import subprocess
from PIL import Image, ImageDraw, ImageFont

WHITE = 0
BLACK = 1
RED = 2
YELLOW = 3

PALETTE_RGB = [
    255, 255, 255,  # white
    0, 0, 0,        # black
    223, 49, 49,    # red
    239, 239, 20,   # yellow
]

def format_time(seconds: int) -> str:
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}:{secs:02d}"


def show_track(
    art_image: Image.Image,
    title: str,
    album: str,
    artist: str,
    track_progress: int,
    track_length: int,
    display_device = None,
):
    dimensions = (display_device.width, display_device.height) if display_device else (250, 122)

    image = Image.new("P", dimensions, BLACK)
    # Pillow expects a palette of (256*3), so the rest must be padded with zeros
    image.putpalette(PALETTE_RGB + [0] * (768 - len(PALETTE_RGB)))

    padding = 10
    art_size = 75

    if art_image:
        art_image = art_image.resize((art_size, art_size)).convert("RGB")
        # use main image as palette source for quantization
        art_image = art_image.quantize(palette=image, dither=Image.Dither.NONE)

        image.paste(art_image, (dimensions[0] - art_size - padding, padding))

    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 18)
    album_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 14)
    artist_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 14)
    time_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 12)

    draw.text((padding, padding), f"{title}", WHITE, font=title_font, stroke_fill=BLACK, stroke_width=1)
    draw.text((padding, padding + 28), f"{album}", WHITE, font=album_font, stroke_fill=BLACK, stroke_width=1)
    draw.text((padding, padding + 50), f"{artist}", WHITE, font=artist_font, stroke_fill=BLACK, stroke_width=1)

    progress_percent = track_progress / track_length
    progress_bar_height = 6

    start_x = padding
    start_y = dimensions[1] - padding - progress_bar_height
    end_x = dimensions[0] - padding
    end_y = start_y + progress_bar_height

    progress_width = int(234 * progress_percent)
    draw.rectangle((start_x, start_y, start_x + progress_width, end_y), fill=RED)
    draw.rectangle((start_x, start_y, end_x, end_y), outline=RED)

    track_progress_formatted = format_time(track_progress)
    draw.text((start_x, start_y - 18), track_progress_formatted, WHITE, font=time_font)
    track_length_formatted = format_time(track_length)
    draw.text((end_x - 28, start_y - 18), track_length_formatted, WHITE, font=time_font)


    if display_device:
        display_device.set_image(image)
        display_device.show()
    else:
        path = "/tmp/inky-simulated-output.png"
        image.save(path)
        subprocess.run(["imv", path, "-w", "inky-floating"])
