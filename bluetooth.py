from rich.console import Console
console = Console()
print = console.print

import subprocess
import time
import os
DEVICE_MAC = os.getenv("BLUETOOTH_DEVICE_MAC")

def connect_to_device():
    if not DEVICE_MAC:
        print("[blue]BLUETOOTH:[/blue] unable to connect to device. please define [bold]BLUETOOTH_DEVICE_MAC[/bold] environment variable")
        return
    try:
        # check if already connected
        initial_check = subprocess.run(
            ["bluetoothctl", "info", DEVICE_MAC],
            stdout=subprocess.PIPE,
            text=True,
        )
        if "Connected: yes" in initial_check.stdout:
            print(f"[blue]BLUETOOTH:[/blue] [green]already connected to [bold]{DEVICE_MAC}[/bold][/green]")
            return True
        # NOT CONNECTED
        print(f"[blue]BLUETOOTH:[/blue] [yellow]attempting to connect to [bold]{DEVICE_MAC}[/bold][/yellow]")
        # attempt connection
        subprocess.run(
            ["bluetoothctl", "connect", DEVICE_MAC],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        # verify connection
        result = subprocess.run(
            ["bluetoothctl", "info", DEVICE_MAC],
            stdout=subprocess.PIPE,
            text=True,
        )
        if "Connected: yes" in result.stdout:
            print(f"[blue]BLUETOOTH:[/blue] [green]successfully connected to [bold]{DEVICE_MAC}[/bold][/green]")
            return True
        
    except subprocess.CalledProcessError as e:
        print(f"[blue]BLUETOOTH:[/blue] [red]failed to connect to [bold]{DEVICE_MAC}[/bold]: {e.stderr}[/red]")
    
    return False
