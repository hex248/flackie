from rich.console import Console
console = Console()
print = console.print

import dotenv
dotenv.load_dotenv()
import os
import time
import display
import bluetooth
import state
import navigation
import ui
import controls
from player import play_file, toggle_pause, stop_playback
from utils import get_track_info

def close():
    stop_playback()
    display.clean_up()

running = True
bluetooth_connected = False

#########################
# DISPLAY & IMAGE SETUP #
#########################
ui.init_ui()

######################
# LOAD MUSIC LIBRARY #
######################
state.init_library()
artist_idx, album_idx, track_idx = navigation.get_indices()
state.update_cached_lists(artist_idx, album_idx)


##########################################################
# SET TRACK DETAILS (FIRST ARTIST,ALBUM,TRACK AVAILABLE) #
##########################################################
title = "title"
album = "album"
artist = "artist"
progress = 0
length = 0
img = None

current_playback_state = True

def update_track_data(get_image = True, play = False):
    global title, album, artist, length, img, progress, current_playback_state
    
    artist_idx, album_idx, track_idx = navigation.get_indices()
    artists = state.get_artists()
    albums = state.get_albums()
    tracks = state.get_tracks()

    artist = artists[artist_idx]
    album = albums[album_idx]
    track = tracks[track_idx]

    track_path = os.path.join(state.get_library_path(), artist, album, track)
    
    title, album, artist, length, img = get_track_info(track_path, get_image=get_image)
    if bluetooth_connected and play:
        stop_playback()
        play_file(track_path)
        current_playback_state = True
        progress = 0

update_track_data()

###########
# BUTTONS #
###########
def btn1_callback():
    navigation.nav_cycle(1)
    displays = [1] # only update top display
    ui.draw(current_playback_state, title, album, artist, img, progress, length, displays)

def btn2_callback():
    navigation.choice_cycle(1, update_track_data)
    displays = [1,2] # update top and bottom display
    # if artist or album changed, update main display too
    if navigation.get_current_level_idx() in [0, 1]:
        displays.append(0)
    ui.draw(current_playback_state, title, album, artist, img, progress, length, displays)

controls.init_controls()
controls.register_callbacks(btn1_callback, btn2_callback)

# initial draw
ui.draw(current_playback_state, title, album, artist, img, progress, length, [0,1,2])

bluetooth_connected = bluetooth.connect_to_device()
########
# LOOP #
########
timer = 0
while running:
    # if not bluetooth_connected:
    #     if timer >= 1.0 or timer == 0:
    #         timer = 0
    #         bluetooth_connected = bluetooth.connect_to_device()
        
    #     timer += 0.1
    time.sleep(0.1)
    pass

close()
