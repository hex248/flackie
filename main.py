import os

# if there is no spi port dev mode is true
dev = not os.path.exists("/dev/spidev0.0")

print(dev)


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

if dev:
    images = {
        "0": Image.new("RGB", (240, 240), "black"),
        "1": Image.new("RGB", (80, 160), "black"),
        "2": Image.new("RGB", (80, 160), "black"),
    }
else:
    display.init([0,1,2])
    images = display.get_images()


second_font = ImageFont.truetype("./fonts/JetBrainsMono-Regular.ttf", 20)
main_font = ImageFont.truetype("./fonts/JetBrainsMono-Regular.ttf", 30)
running = True

timer = 0
tick_time = 0.1

def loop():
    global timer
    print("tick")
    if int(timer) == timer:
        print(f"{timer}s")
    
    pass

def main():
    global timer
    global tick_time
    global running
    global dev

    path = "/home/ob/music/artists"
    library = load_library(path)

    title = "title"
    album = "album"
    artist = "artist"
    progress = 0
    length = 0

    artist_idx = 0
    album_idx = 0
    track_idx = 0
    
    def get_data():
        artists = list(library.keys())
        artists.sort()
        albums = list(library[artists[artist_idx]].keys())
        albums.sort()
        tracks = library[artists[artist_idx]][albums[album_idx]]
        tracks.sort()
        return artists, albums, tracks

    artists, albums, tracks = get_data()
    current_playback_state = None

    # get random artist
    artist = artists[artist_idx]
    album = albums[album_idx]
    track = tracks[track_idx]

    track_path = os.path.join("/home/ob/music/artists", artist, album, track)
    track, album, artist, length, img = get_track_info(track_path)

    main_image = images["0"]
    main_draw = ImageDraw.Draw(main_image)

    top_image = images["1"]
    top_draw = ImageDraw.Draw(top_image)
    
    bottom_image = images["2"]
    bottom_draw = ImageDraw.Draw(bottom_image)

    main_image.paste(img.resize(main_image.size), (0,0))
    top_draw.text((0, 0), album, fill="WHITE", font=main_font)
    bottom_draw.text((0, 0), track, fill="WHITE", font=main_font)


    display.draw_to(0, main_image)
    display.draw_to(1, top_image)
    display.draw_to(2, bottom_image)
    
    while running:
        loop()
        time.sleep(tick_time)
        timer += tick_time
    
    close()




if __name__ == "__main__":
    main()
