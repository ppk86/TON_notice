import asyncio
import websockets
import json
from win10toast import ToastNotifier
import tkinter as tk
import threading
import subprocess
import sys

def show_notification(title, message):
    """Display a Windows notification."""
    toaster = ToastNotifier()
    toaster.show_toast(title, message, duration=10)

async def websocket_listener(app):
    """Connect to the WebSocket server and listen for events."""
    uri = "ws://localhost:11398"

    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                event = json.loads(message)

                if event.get("Type") == "TERRORS":
                    terror_name = event.get("DisplayName", "Unknown")
                    if terror_name != "???":
                        app.update_terror(terror_name)
                        if app.notifications_enabled:
                            show_notification("Terror Update", f"Terror: {terror_name}")
                            app.update_sent_status(True)

                elif event.get("Type") == "ROUND_TYPE":
                    round_name = event.get("DisplayName", "Unknown")
                    if round_name != "Intermission":
                        app.update_round(round_name)
                        if app.notifications_enabled:
                            show_notification("Round Update", f"Round: {round_name}")
                            app.update_sent_status(True)

            except Exception as e:
                print(f"Error: {e}")

# List of required libraries
required_libraries = ["websockets", "win10toast"]

# Function to install libraries
def install_libraries():
    for library in required_libraries:
        try:
            __import__(library)
        except ImportError:
            print(f"Library '{library}' is not installed. Attempting to install...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", library])
                print(f"Successfully installed '{library}'.")
            except Exception as e:
                print(f"Failed to install '{library}'. Please install it manually using 'pip install {library}'. Error: {e}")

# Install required libraries
install_libraries()

# Create a more detailed GUI
class WebSocketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WebSocket Listener")
        self.root.geometry("500x400")  # Adjusted window size

        self.status_label = tk.Label(root, text="Status: Disconnected", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.terror = "None"  # Initialize terror attribute
        self.round_info = "None"  # Initialize round_info attribute

        self.terror_label = tk.Label(root, text=f"Terror: {self.terror}", font=("Arial", 12))
        self.terror_label.pack(pady=10)

        self.round_label = tk.Label(root, text=f"Round: {self.round_info}", font=("Arial", 12))
        self.round_label.pack(pady=10)

        self.sent_status_label = tk.Label(root, text="Notification Sent: No", font=("Arial", 12))
        self.sent_status_label.pack(pady=10)

        self.toggle_button = tk.Button(root, text="Notifications: ON", command=self.toggle_notifications)
        self.toggle_button.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Listening", command=self.start_listening)
        self.start_button.pack(pady=10)

        self.notifications_enabled = True

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")

    def update_terror(self, terror):
        self.terror = terror if terror else "None"
        self.terror_label.config(text=f"Terror: {self.terror}")

    def update_round(self, round_info):
        self.round_info = round_info if round_info else "None"
        self.round_label.config(text=f"Round: {self.round_info}")

    def update_sent_status(self, sent):
        self.sent_status_label.config(text=f"Notification Sent: {'Yes' if sent else 'No'}")

    def toggle_notifications(self):
        self.notifications_enabled = not self.notifications_enabled
        self.toggle_button.config(text="Notifications: ON" if self.notifications_enabled else "Notifications: OFF")

    def start_listening(self):
        self.update_status("Connected")
        threading.Thread(target=lambda: asyncio.run(websocket_listener(self)), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = WebSocketApp(root)
    root.mainloop()
