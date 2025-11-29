import state

levels = ["artist", "album", "track"]
current_level_idx = 0

##############
# NAVIGATION #
##############
artist_idx = 0
album_idx = 0
track_idx = 0

def nav_cycle(diff=1):
    global current_level_idx
    current_level_idx += diff
    if current_level_idx < 0:
        current_level_idx = len(levels) - 1
    elif current_level_idx >= len(levels):
        current_level_idx = 0

def choice_cycle(diff, update_track_callback):
    global artist_idx, album_idx, track_idx
    
    artists = state.get_artists()
    albums = state.get_albums()
    tracks = state.get_tracks()

    if current_level_idx == 0:
        old = artist_idx
        artist_idx += diff
        if artist_idx < 0:
            artist_idx = len(artists) - 1
        elif artist_idx >= len(artists):
            artist_idx = 0
        # reset album and track idx
        album_idx = 0
        track_idx = 0

        if old != artist_idx:
            state.update_cached_lists(artist_idx, album_idx)
            update_track_callback(play=True)
    elif current_level_idx == 1:
        old = album_idx
        album_idx += diff
        if album_idx < 0:
            album_idx = len(albums) - 1
        elif album_idx >= len(albums):
            album_idx = 0
        # reset track idx
        track_idx = 0

        if old != album_idx:
            state.update_cached_lists(artist_idx, album_idx)
            update_track_callback(play=True)
    elif current_level_idx == 2:
        old = track_idx
        track_idx += diff
        if track_idx < 0:
            track_idx = len(tracks) - 1
        elif track_idx >= len(tracks):
            track_idx = 0
        
        if old != track_idx:
            update_track_callback(get_image=False, play=True)

def get_current_level_idx():
    return current_level_idx

def get_indices():
    return artist_idx, album_idx, track_idx
