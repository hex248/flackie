
from PIL import Image
import os
from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.m4a import M4A

def optimise_and_save(image_data, save_path: str):
    with open("/tmp/album_art_extracted.png", "wb") as img_out:
        img_out.write(image_data)
    image = Image.open("/tmp/album_art_extracted.png")
    image = image.convert("RGB").resize((240,240), Image.Resampling.LANCZOS)
    # cache the image
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    image.save(save_path, format="JPEG", optimize=True, quality=50)

    return image


def get_track_info(track_path, get_image: bool = True):
    audiofile = File(track_path)
    
    # delete previous image
    if os.path.exists("/tmp/album_art_extracted.png"):
        os.remove("/tmp/album_art_extracted.png")
    image_found = False
    cache_path = f"/home/ob/.cache/flackie/images"
    if isinstance(audiofile, FLAC):
        title = audiofile.tags.get("title", ["unknown"])[0]
        album = audiofile.tags.get("album", ["unknown"])[0]
        artist = audiofile.tags.get("artist", ["unknown"])[0]
        length = int(audiofile.info.length)
        if get_image and os.path.exists(f"{cache_path}/{artist}/{album}.jpg"):
            # use cached image if available
            image = Image.open(f"{cache_path}/{artist}/{album}.jpg")
            image_found = True
        elif get_image and audiofile.pictures:
            # no cached image, extract from file
            image = optimise_and_save(audiofile.pictures[0].data, f"{cache_path}/{artist}/{album}.jpg")
            image_found = True
        elif get_image:
            print(f"no album art found in the track: {track_path}")

    elif isinstance(audiofile, MP3):
        title = audiofile.tags.get("TIT2", "unknown")
        album = audiofile.tags.get("TALB", "unknown")
        artist = audiofile.tags.get("TPE1", "unknown")
        length = int(audiofile.info.length)
        if get_image and os.path.exists(f"{cache_path}/{artist}/{album}.jpg"):
            # use cached image if available
            image = Image.open(f"{cache_path}/{artist}/{album}.jpg")
            image_found = True
        elif get_image and "APIC:" in audiofile.tags:
            # no cached image, extract from file
            image = optimise_and_save(audiofile.tags["APIC:"].data, f"{cache_path}/{artist}/{album}.jpg")
            image_found = True
        elif get_image:
            print(f"no album art found in the track: {track_path}")
    else:
        print("unsupported audio format for metadata extraction.")
        print(track_path)
    
    return title, album, artist, length, image if image_found else None