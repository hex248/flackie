import signal

# for debugging without actual device
import tkinter as tk
window = None
from PIL import ImageTk
class InkySimulator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = None

    def __init_label(self):
        global window
        if window is None:
            window = tk.Tk()

        if self.image:
            self.tk_image = ImageTk.PhotoImage(self.image.convert("RGB"))
        else:
            self.tk_image = None

        self.label = tk.Label(window, image=self.tk_image, bg="black")
        self.label.pack()

    def set_image(self, image):
        self.image = image
        if not hasattr(self, "label"):
            self.__init_label()

        if self.image is not None:
            tk_image = ImageTk.PhotoImage(self.image.convert("RGB"))
            self.label.configure(image=tk_image)
            self.label.image = tk_image

    def show(self):
        # process updates (image change)
        if window:
            try:
                window.update_idletasks()
                window.update()
            except tk.TclError:
                pass
    def close(self):
        if window:
            window.destroy()
        signal.raise_signal(signal.SIGKILL)
        

from inky import auto, InkyPHAT
try:
    display = auto()
except Exception as e:
    if ("No EEPROM detected!" in str(e)):
        print("no display connected, moving on... (dev mode)")
        window = tk.Tk()

        inky_simulator = InkySimulator(250, 122)
        display = inky_simulator
    else:
        print(f"error with display: {e}")

        
from PIL import Image
import random
import time
import os
from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.m4a import M4A


from display import show_track
from library import load_library

# tkinter setup
window.title("inky-floating")
window.geometry("250x122")
window.configure(bg="black")

window.bind_all("<Key>", lambda e: display.close() if getattr(e, "keysym", "").lower() == "q" else None)
window.bind_all("<Escape>", lambda e: display.close())
window.bind_all("<Control-c>", lambda e: display.close())

def get_track_info(track_path):
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
        length = int(audiofile.info.length)
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
    
    return title, album, artist, length, image if image_found else None

def get_random_track(parent_path, library):
    random_artist = random.choice(list(library.keys()))
    random_album = random.choice(list(library[random_artist].keys()))
    random_track = random.choice(library[random_artist][random_album])

    track_path = os.path.join(parent_path, random_artist, random_album, random_track)

    return track_path

def main():
    path = "/home/ob/music/artists"
    library = load_library(path)

    image = None
    title = "title"
    album = "album"
    artist = "artist"
    progress = 0
    
    track_path = get_random_track(path, library)
    title, album, artist, length, image = get_track_info(track_path)

    print(f"playing {title} by {artist} from the album {album}")

    show_track(
        art_image=image,
        title=title,
        album=album,
        artist=artist,
        track_progress=progress,
        track_length=length,
        display_device=display
    )

    # hang for 5 seconds
    time.sleep(5)



if __name__ == "__main__":
    main()
