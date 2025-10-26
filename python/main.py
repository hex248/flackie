from inky import auto, InkyPHAT
display: InkyPHAT = None
try:
    display = auto()
except Exception as e:
    if ("No EEPROM detected!" in str(e)):
        print("no display connected, moving on... (dev mode)")
    else:
        print(f"error with display: {e}")
        
from PIL import Image

from display import show_track

def main():
    image = Image.open("/home/ob/music/artists/Dominic Fike/Sunburn/sunburn.png")
    title = "title"
    album = "album"
    artist = "artist"
    track_progress = 30
    track_length = 120

    show_track(
        image,
        title,
        album,
        artist,
        track_progress,
        track_length,
        display
    )


if __name__ == "__main__":
    main()
