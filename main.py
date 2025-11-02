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
from utils import get_track_info


from display import show_track, show_selector
from library import load_library

# tkinter setup
window.title("inky-floating")
window.geometry("250x122")
window.configure(bg="black")

levels = ["artist", "album", "track"]
current_level_idx = 0
window.bind_all("<Key>", lambda e: display.close() if getattr(e, "keysym", "").lower() == "q" else None)
window.bind_all("<Escape>", lambda e: display.close())
window.bind_all("<Control-c>", lambda e: display.close())


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

    artist_idx = 0
    album_idx = 0
    track_idx = 0

    artists = []
    albums = []
    tracks = []
    
    def get_data():
        artists = list(library.keys())
        artists.sort()
        albums = list(library[artists[artist_idx]].keys())
        albums.sort()
        tracks = library[artists[artist_idx]][albums[album_idx]]
        tracks.sort()
        return artists, albums, tracks

    artists, albums, tracks = get_data()
    
    show_selector(library, artist_idx, album_idx, track_idx, levels[current_level_idx], display)

    def change_level():
        global current_level_idx
        current_level_idx = (current_level_idx + 1) % len(levels)
        print(f"changing level to: {levels[current_level_idx]} ({current_level_idx})")
        show_selector(library, artist_idx, album_idx, track_idx, levels[current_level_idx], display)
    window.bind_all("<space>", lambda e: change_level())

    def change_item(operation = 1):
        nonlocal artist_idx, album_idx, track_idx
        nonlocal artists, albums, tracks
        if current_level_idx == 0:
            artist_idx = (artist_idx + operation) % len(artists)
            # reset lower levels
            album_idx = 0
            track_idx = 0
        elif current_level_idx == 1:
            album_idx = (album_idx + operation) % len(albums)
            # reset lower level
            track_idx = 0
        elif current_level_idx == 2:
            track_idx = (track_idx + operation) % len(tracks)
        artists, albums, tracks = get_data()
        show_selector(library, artist_idx, album_idx, track_idx, levels[current_level_idx], display)
    
    window.bind_all("<Up>", lambda e: change_item(-1))
    window.bind_all("<Down>", lambda e: change_item(1))

    window.mainloop()


if __name__ == "__main__":
    main()
