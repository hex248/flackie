import threading
import time
import pyaudio
import soundfile as sf
import sys


player_lock = threading.Lock()
player_thread = None
stop_event = None
pause_event = None


def playback_thread(file_path, stop_event: threading.Event, pause_event: threading.Event):
    try:
        data, samplerate = sf.read(file_path, dtype="float32")

        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paFloat32,
                        channels=1 if data.ndim == 1 else data.shape[1],
                        rate=samplerate,
                        output=True)

        chunk_size = 1024
        for i in range(0, len(data), chunk_size):
            if stop_event.is_set():
                print("interrupted playback")
                break

            pause_event.wait()

            chunk = data[i:i + chunk_size]
            stream.write(chunk.tobytes())

        try:
            stream.stop_stream()
            stream.close()
        except Exception:
            pass
        try:
            p.terminate()
        except Exception:
            pass

        print("playback finished")
    except Exception as e:
        print(f"playback error: {e}")


def play_file(file_path):
    global player_thread, stop_event, pause_event

    with player_lock:
        # stop existing playback if any
        if player_thread and player_thread.is_alive():
            # clear events
            stop_event.set()
            pause_event.set()
            player_thread.join(timeout=1.0)

        stop_event = threading.Event()
        pause_event = threading.Event()
        pause_event.set() # unpaused

        player_thread = threading.Thread(target=playback_thread, args=(file_path, stop_event, pause_event), daemon=True)
        player_thread.start()


def toggle_pause():
    global pause_event
    if pause_event is None:
        return None
    if pause_event.is_set():
        # pause
        pause_event.clear()
        print("paused")
        return False
    else:
        # unpause
        pause_event.set()
        print("resumed")
        return True


def stop_playback():
    global player_thread, stop_event, pause_event
    print("stopping playback")
    if stop_event:
        stop_event.set()
    if pause_event:
        # ensure thread isn't blocked on pause
        pause_event.set()
    if player_thread:
        player_thread.join(timeout=1.0)