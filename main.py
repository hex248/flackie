import os

# if there is no spi port dev mode is true
dev = not os.path.exists("/dev/spidev0.0")

import time
import display
from player import play_file, toggle_pause, stop_playback
from library import load_library
from utils import get_track_info
from PIL import Image, ImageDraw, ImageFont



levels = ["artist", "album", "track"]
current_level_idx = 0

def close():
    stop_playback()
    display.clean_up()

#########################
# DISPLAY & IMAGE SETUP #
#########################
if dev:
    images = {
        "0": Image.new("RGB", (240, 240), "black"),
        "1": Image.new("RGB", (80, 160), "black"),
        "2": Image.new("RGB", (80, 160), "black"),
    }
else:
    display.init([0,1,2])
    images = display.get_images()

padding = 10

second_font = ImageFont.truetype("./fonts/JetBrainsMono-Regular.ttf", 12)
main_font = ImageFont.truetype("./fonts/JetBrainsMono-Regular.ttf", 30)


def draw(current_playback_state, title, album, artist, img, progress, length, displays: list[int] = [0,1,2]):
    if 0 in displays:
        if img is not None:
            #############
            # COVER ART #
            #############
            main_image = Image.new("RGB", (images["0"].width, images["0"].height), "BLACK")
            main_image.paste(img.resize(main_image.size), (0, 0))
            display.draw_to(0, main_image)
    
    if 1 in displays:
        top_image = Image.new("RGB", (images["1"].width, images["1"].height), "BLACK")
        top_draw = ImageDraw.Draw(top_image)
        ###############
        # NAV OPTIONS #
        ###############
        top_draw.text((top_image.width/2 - 72, 0), "artist  album  track", "WHITE", font=second_font)
        x_coords = [(8, 51), (66, 101), (116, 152)]
        
        #################
        # NAV SELECTION #
        #################
        if current_level_idx == 0:
            top_draw.rectangle((x_coords[0][0], 16, x_coords[0][1], 17), fill="WHITE")
            text = artist
        elif current_level_idx == 1:
            top_draw.rectangle((x_coords[1][0], 16, x_coords[1][1], 17), fill="WHITE")
            text = album
        elif current_level_idx == 2:
            top_draw.rectangle((x_coords[2][0], 16, x_coords[2][1], 17), fill="WHITE")
            text = title
        else:
            text = "unknown"
        
        #################
        # SELECTED ITEM #
        #################
        font_size = 36
        font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", font_size)

        bbox = top_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        while text_width > top_image.width - 2 * padding and font_size > 6:
            font_size -= 1
            font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", font_size)
            bbox = top_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

        text_x = (top_image.width - text_width) // 2
        text_y = ((top_image.height - text_height) // 2) - (font_size / 4)
        top_draw.text((text_x, text_y + 10), text, "WHITE", font=font, stroke_fill="BLACK", stroke_width=1)

        display.draw_to(1, top_image)
    
    if 2 in displays:
        bottom_image = Image.new("RGB", (images["2"].width, images["2"].height), "BLACK")
        bottom_draw = ImageDraw.Draw(bottom_image)
        if current_playback_state is not None:
            #######################
            # CURRENT TRACK TITLE #
            #######################
            font_size = 36
            font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", font_size)
            bbox = bottom_draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            while text_width > bottom_image.width - 2 * padding and font_size > 10:
                font_size -= 1
                font = ImageFont.truetype("./fonts/JetBrainsMono-SemiBold.ttf", font_size)
                bbox = bottom_draw.textbbox((0, 0), title, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            
            text_x = (bottom_image.width - text_width) // 2
            text_y = ((bottom_image.height - text_height) // 2) - (font_size / 4)
            bottom_draw.text((text_x, text_y), title, "WHITE", font=font, stroke_fill="BLACK", stroke_width=1)
        

            ##########################
            # CURRENT PLAYBACK STATE #
            ##########################
            if current_playback_state == True:
                bottom_draw.text((0, 0), f"PLAYING", "WHITE", font=second_font, stroke_fill="BLACK", stroke_width=1)
            elif current_playback_state == False:
                bottom_draw.text((0, 0), f"PAUSED", "WHITE", font=second_font, stroke_fill="BLACK", stroke_width=1)
        
        else:
            bottom_draw.text((0, 0 ), "none", "WHITE", font=second_font, stroke_fill="BLACK", stroke_width=1)

        ################
        # PROGRESS BAR #
        ################
        progress_percent = progress / length
        progress_bar_height = 6

        start_x = padding
        start_y = bottom_image.height - padding - progress_bar_height
        end_x = bottom_image.width - padding
        end_y = start_y + progress_bar_height

        progress_width = int((end_x-start_x) * progress_percent)
        bottom_draw.rectangle((start_x, start_y, start_x + progress_width, end_y), fill="#c13f3f")
        bottom_draw.rectangle((start_x, start_y, end_x, end_y), outline="#c13f3f")


        #########################
        # DRAW IMAGE TO DISPLAY #
        #########################
        display.draw_to(2, bottom_image)
# end of draw function

running = True

######################
# LOAD MUSIC LIBRARY #
######################
artist_idx = 0
album_idx = 0
track_idx = 0

path = "/home/ob/music/artists"
library = load_library(path)

def get_data():
    artists = list(library.keys())
    artists.sort()
    albums = list(library[artists[artist_idx]].keys())
    albums.sort()
    tracks = library[artists[artist_idx]][albums[album_idx]]
    tracks.sort()
    return artists, albums, tracks

artists, albums, tracks = get_data()


##############
# NAVIGATION #
##############
def nav_cycle(diff=1):
    global current_level_idx
    current_level_idx += diff
    if current_level_idx < 0:
        current_level_idx = len(levels) - 1
    elif current_level_idx >= len(levels):
        current_level_idx = 0

def choice_cycle(diff=1):
    global artist_idx
    global album_idx
    global track_idx
    global artists
    global albums
    global tracks

    if current_level_idx == 0:
        artist_idx += diff
        if artist_idx < 0:
            artist_idx = len(artists) - 1
        elif artist_idx >= len(artists):
            artist_idx = 0
        # reset album and track idx
        album_idx = 0
        track_idx = 0
        update_track_data()
    elif current_level_idx == 1:
        album_idx += diff
        if album_idx < 0:
            album_idx = len(albums) - 1
        elif album_idx >= len(albums):
            album_idx = 0
        # reset track idx
        track_idx = 0
        update_track_data()
    elif current_level_idx == 2:
        track_idx += diff
        if track_idx < 0:
            track_idx = len(tracks) - 1
        elif track_idx >= len(tracks):
            track_idx = 0
        update_track_data(get_image=False)


##########################################################
# SET TRACK DETAILS (FIRST ARTIST,ALBUM,TRACK AVAILABLE) #
##########################################################
title = "title"
album = "album"
artist = "artist"
progress = 0
length = 0

current_playback_state = True

# get random artist
artist = artists[artist_idx]
album = albums[album_idx]
track = tracks[track_idx]

def update_track_data(get_image: bool = True):
    global title
    global album
    global artist
    global length
    global img
    global progress
    global artists
    global albums
    global tracks

    artists, albums, tracks = get_data()
    artist = artists[artist_idx]
    album = albums[album_idx]
    track = tracks[track_idx]

    track_path = os.path.join("/home/ob/music/artists", artist, album, track)
    
    title, album, artist, length, img = get_track_info(track_path, get_image=get_image)
    progress = 0


update_track_data()

###########
# BUTTONS #
###########
btn1, btn2, = display.get_buttons()

def btn1_callback():
    nav_cycle(1)
    displays = [1,2]
    draw(current_playback_state, title, album, artist, img, progress, length, displays)

def btn2_callback():
    choice_cycle(1)
    displays = [1,2]
    # if artist or album changed, update main display
    if current_level_idx in [0, 1]:
        displays.append(0)
    draw(current_playback_state, title, album, artist, img, progress, length, displays)

btn1.when_activated = btn1_callback
btn2.when_activated = btn2_callback

# initial draw
draw(current_playback_state, title, album, artist, img, progress, length, [0,1,2])

while running:
    # progress += 1
    # # only updates screen 2 (shows progress)
    # draw(current_playback_state, title, album, artist, img, progress, length, [2])
    # time.sleep(0.1)
    pass

close()
