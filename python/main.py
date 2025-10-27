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
import os
from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.m4a import M4A


from display import show_track
from library import load_library
import random

def main():
    path = "/home/ob/music/artists"
    library = load_library(path)

    image = None
    title = "title"
    album = "album"
    artist = "artist"
    track_progress = 30
    track_length = 120


    random_artist = random.choice(list(library.keys()))
    random_album = random.choice(list(library[random_artist].keys()))
    random_track = random.choice(library[random_artist][random_album])

    track_path = os.path.join(path, random_artist, random_album, random_track)
    audiofile = File(track_path)
    
    # delete previous image
    if os.path.exists("/tmp/album_art_extracted.png"):
        os.remove("/tmp/album_art_extracted.png")
    image_found = False
    if isinstance(audiofile, FLAC):
        title = audiofile.tags.get("title", ["unknown"])[0]
        album = audiofile.tags.get("album", ["unknown"])[0]
        artist = audiofile.tags.get("artist", ["unknown"])[0]
        if audiofile.pictures:
            picture = audiofile.pictures[0]
            image_data = picture.data
            with open("/tmp/album_art_extracted.png", "wb") as img_out:
                img_out.write(image_data)
            image_found = True
        else:
            print(f"no album art found in the track: {track_path}")
    elif isinstance(audiofile, MP3):
        title = audiofile.tags.get("TIT2", "unknown")
        album = audiofile.tags.get("TALB", "unknown")
        artist = audiofile.tags.get("TPE1", "unknown")
        if "APIC:" in audiofile.tags:
            apic = audiofile.tags["APIC:"]
            image_data = apic.data
            with open("/tmp/album_art_extracted.png", "wb") as img_out:
                img_out.write(image_data)
            image_found = True
        else:
            print(f"no album art found in the track: {track_path}")
    else:
        print("unsupported audio format for metadata extraction.")
        print(track_path)
    
    if image_found:
        image = Image.open("/tmp/album_art_extracted.png")
        image = image.convert("RGB")

    print(f"playing {title} by {artist} from the album {album}")

    show_track(
        art_image=image,
        title=title,
        album=album,
        artist=artist,
        track_progress=track_progress,
        track_length=track_length,
        display_device=display
    )


if __name__ == "__main__":
    main()
