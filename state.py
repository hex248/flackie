import os
from library import load_library

######################
# LOAD MUSIC LIBRARY #
######################
path = None
library = {}
artists = []
albums = []
tracks = []

def init_library():
    global path, library, artists
    path = os.getenv("ARTISTS_DIRECTORY", "/home/ob/music/artists")
    library = load_library(path)
    artists = list(library.keys())
    artists.sort()

def update_cached_lists(artist_idx, album_idx):
    global albums, tracks
    # update albums based on current artist
    if artists:
        current_artist = artists[artist_idx]
        albums = list(library[current_artist].keys())
        albums.sort()
        
        # update tracks based on current album
        if albums and album_idx < len(albums):
            current_album = albums[album_idx]
            tracks = library[current_artist][current_album]
            tracks.sort()
        else:
            tracks = []
    else:
        albums = []
        tracks = []

def get_artists():
    return artists

def get_albums():
    return albums

def get_tracks():
    return tracks

def get_library_path():
    return path
