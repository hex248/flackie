import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
from utils import get_track_info

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

padding = 10

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

    art_size = 75

    if art_image:
        art_image = art_image.resize((art_size, art_size)).convert("RGB")
        # use main image as palette source for quantization
        art_image = art_image.quantize(palette=image, dither=Image.Dither.NONE)

        image.paste(art_image, (dimensions[0] - art_size - padding, dimensions[1] - art_size - padding))

    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 16)
    album_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 14)
    artist_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 14)
    time_font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 12)

    draw.text((padding, padding), f"{title}", WHITE, font=title_font, stroke_fill=BLACK, stroke_width=1)
    draw.text((padding, padding + 26), f"{album}", WHITE, font=album_font, stroke_fill=BLACK, stroke_width=1)
    draw.text((padding, padding + 50), f"{artist}", WHITE, font=artist_font, stroke_fill=BLACK, stroke_width=1)

    progress_percent = track_progress / track_length
    progress_bar_height = 6

    start_x = padding
    start_y = dimensions[1] - padding - progress_bar_height
    end_x = dimensions[0] - padding
    if art_image:
        end_x -= art_size + padding
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


def show_selector(library, artist_idx, album_idx, track_idx, level, current_playback_state, title, album, artist, length, image, display_device=None):

    dimensions = (display_device.width, display_device.height) if display_device else (250, 122)
    
    image = Image.new("P", dimensions, BLACK)
    image.putpalette(PALETTE_RGB + [0] * (768 - len(PALETTE_RGB)))

    draw = ImageDraw.Draw(image)

    # cross for centering
    # draw.line((0, dimensions[1] // 2, dimensions[0], dimensions[1] // 2), fill=RED, width=1)
    # draw.line((dimensions[0] // 2, 0, dimensions[0] // 2, dimensions[1]), fill=RED, width=1)

    font_size = 48
    font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", font_size)
    font_small = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", 12)


    artists = list(library.keys())
    artists.sort()
    current_artist = artists[artist_idx]
    albums = list(library[current_artist].keys())
    albums.sort()
    current_album = albums[album_idx]
    tracks = library[current_artist][current_album]
    tracks.sort()
    current_track = tracks[track_idx]

    if level == "artist":
        text = current_artist
    elif level == "album":
        text = current_album
    elif level == "track":
        text = current_track
        ## get track information from file
        track_path = os.path.join("/home/ob/music/artists", current_artist, current_album, current_track)
        current_title, album, artist, length, img = get_track_info(track_path)
        if current_title:
            text = current_title
    else:
        text = "unknown"

    mode_text = ""
    if level == "artist": mode_text += "[artist]"
    else: mode_text += " artist "
    if level == "album": mode_text += "[album]"
    else: mode_text += " album "
    if level == "track": mode_text += "[track]"
    else: mode_text += " track "
    
    mode_text_length = font_small.getlength(mode_text)
    draw.text((dimensions[0]/2 - mode_text_length/2, dimensions[1] - padding - 12), mode_text, WHITE, font=font_small)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    while text_width > dimensions[0] - 2 * padding and font_size > 10:
        font_size -= 2
        font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

    text_x = (dimensions[0] - text_width) // 2
    text_y = ((dimensions[1] - text_height) // 2) - (font_size / 4)
    draw.text((text_x, text_y), text, WHITE, font=font, stroke_fill=BLACK, stroke_width=1)

    if current_playback_state == True:
        draw.text((padding, padding), f"playing {title} - {artist}", WHITE, font=font_small, stroke_fill=BLACK, stroke_width=1)
    elif current_playback_state == False:
        draw.text((padding, padding), f"paused {title} - {artist}", WHITE, font=font_small, stroke_fill=BLACK, stroke_width=1)
    elif current_playback_state == None:
        draw.text((padding, padding), "select a track to play", WHITE, font=font_small, stroke_fill=BLACK, stroke_width=1)


    if display_device:
        display_device.set_image(image)
        display_device.show()
    else:
        path = "/tmp/inky-simulated-output.png"
        image.save(path)
        subprocess.run(["imv", path, "-w", "inky-floating"])