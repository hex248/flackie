import os

def load_library(directory: str) -> dict:
    artist_dict = {}
    artists = os.listdir(directory)
    for artist in artists:
        albums = os.listdir(os.path.join(directory, artist))
        albums.sort()
        artist_dict[artist] = {}
        for album in albums:
            tracks = os.listdir(os.path.join(directory, artist, album))
            tracks.sort()
            tracks = [track for track in tracks if track.endswith('.flac') or track.endswith('.mp3') or track.endswith('.wav') or track.endswith('.m4a')]
            if len(tracks) > 0:
                artist_dict[artist][album] = tracks
            else:
                print(f"WARNING: no valid tracks found a:{artist} al:{album}")
        if len(artist_dict[artist]) == 0:
            print(f"WARNING: no valid albums found a:{artist}")

    return artist_dict