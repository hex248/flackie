
from PIL import Image
import os
from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.m4a import M4A

def get_track_info(track_path, get_image: bool = True):
    audiofile = File(track_path)
    
    # delete previous image
    if os.path.exists("/tmp/album_art_extracted.png"):
        os.remove("/tmp/album_art_extracted.png")
    image_found = False
    if isinstance(audiofile, FLAC):
        title = audiofile.tags.get("title", ["unknown"])[0]
        album = audiofile.tags.get("album", ["unknown"])[0]
        artist = audiofile.tags.get("artist", ["unknown"])[0]
        length = int(audiofile.info.length)
        if get_image and audiofile.pictures:
            picture = audiofile.pictures[0]
            image_data = picture.data
            with open("/tmp/album_art_extracted.png", "wb") as img_out:
                img_out.write(image_data)
            image_found = True
        elif get_image:
            print(f"no album art found in the track: {track_path}")
    elif isinstance(audiofile, MP3):
        title = audiofile.tags.get("TIT2", "unknown")
        album = audiofile.tags.get("TALB", "unknown")
        artist = audiofile.tags.get("TPE1", "unknown")
        length = int(audiofile.info.length)
        if get_image and "APIC:" in audiofile.tags:
            apic = audiofile.tags["APIC:"]
            image_data = apic.data
            with open("/tmp/album_art_extracted.png", "wb") as img_out:
                img_out.write(image_data)
            image_found = True
        elif get_image:
            print(f"no album art found in the track: {track_path}")
    else:
        print("unsupported audio format for metadata extraction.")
        print(track_path)
    
    if image_found:
        image = Image.open("/tmp/album_art_extracted.png")
        image = image.convert("RGB")
    
    return title, album, artist, length, image if image_found else None