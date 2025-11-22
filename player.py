from rich.console import Console
console = Console()
print = console.print
# suppress pyaudio ALSA warnings
import os, sys
devnull = os.open(os.devnull, os.O_WRONLY)
os.dup2(devnull, sys.stderr.fileno())

import threading
import time
import pyaudio
import soundfile as sf


player_lock = threading.Lock()
player_thread = None
stop_event = None
pause_event = None


def playback_thread(file_path, stop_event: threading.Event, pause_event: threading.Event):
    try:
        print(f"[green]playing [bold]{file_path}[/bold][/green]")
        data, samplerate = sf.read(file_path, dtype="float32")

        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paFloat32,
                        channels=1 if data.ndim == 1 else data.shape[1],
                        rate=samplerate,
                        output=True)

        chunk_size = 1024
        for i in range(0, len(data), chunk_size):
            if stop_event.is_set():
                print("[red]interrupted playback[/red]")
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

        print("[blue]playback finished[/blue]")
    except Exception as e:
        print(f"[red]playback error: {e}[/red]")


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
        print("[yellow]paused[/yellow]")
        return False
    else:
        # unpause
        pause_event.set()
        print("[green]resumed[/green]")
        return True


def stop_playback():
    global player_thread, stop_event, pause_event
    print("[yellow]stopping playback[/yellow]")
    if stop_event:
        stop_event.set()
    if pause_event:
        # ensure thread isn't blocked on pause
        pause_event.set()
    if player_thread:
        player_thread.join(timeout=1.0)