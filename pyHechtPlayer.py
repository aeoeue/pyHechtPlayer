import pyautogui
import time
import csv
import schedule
from datetime import datetime, timedelta
from tkinter import Tk, Label, Button, Entry, filedialog, StringVar, IntVar
import pickle
from playsound import playsound
import dbus
import os

# Save and load previous session data
PICKLE_FILE = "app_state.pkl"

# Function to load previously saved file path, start jingle, last jingle, and last_seconds
def load_previous_state():
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, 'rb') as f:
            return pickle.load(f)
    return {'file_path': '', 'start_jingle': '', 'last_jingle': '', 'last_seconds': 200}

# Function to save file path, start jingle, last jingle, and last_seconds on app close
def save_state(file_path, start_jingle, last_jingle, last_seconds):
    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump({'file_path': file_path, 'start_jingle': start_jingle, 'last_jingle': last_jingle, 'last_seconds': last_seconds}, f)

# Play jingles and manage media
def playStartJingle(start_jingle):
    playPause_media_player()
    print("Start jingle playing.", datetime.now())
    play_music(start_jingle)
    playPause_media_player()

def playLastMinutesJingle(last_jingle):
    playPause_media_player()
    print("Last minutes jingle playing.", datetime.now())
    play_music(last_jingle)
    playPause_media_player()

def playPause_media_player():
    try:
        session_bus = dbus.SessionBus()
        spotify_service = session_bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')
        spotify_interface = dbus.Interface(spotify_service, 'org.mpris.MediaPlayer2.Player')
        spotify_interface.PlayPause()
    except dbus.exceptions.DBusException:
        print("Spotify DBus service not found. Make sure Spotify is running.")

def play_music(file_path):
    playsound(file_path, block=True)

# Scheduling functions
def schedule_actions(file_path, start_jingle, last_jingle, last_seconds):
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            date_str, time_slot = row
            date = datetime.strptime(date_str, '%d.%m.%Y')
            start_time_str, end_time_str = time_slot.split('-')
            start_time = datetime.strptime(start_time_str, '%H:%M')
            end_time = datetime.strptime(end_time_str, '%H:%M')

            start_action_time = datetime.combine(date.date(), start_time.time())
            schedule.every().day.at(start_action_time.strftime('%H:%M')).do(playStartJingle, start_jingle=start_jingle)

            end_action_time = datetime.combine(date.date(), end_time.time()) - timedelta(seconds=last_seconds)
            schedule.every().day.at(end_action_time.strftime('%H:%M')).do(playLastMinutesJingle, last_jingle=last_jingle)

            print("Scheduled Start Jingle at:", start_action_time, "and Last Minutes Jingle at:", end_action_time)

    while True:
        schedule.run_pending()
        time.sleep(1)

# Tkinter App for file selection and configuration
class JingleSchedulerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Jingle Scheduler")

        # Load previously used file path, start jingle, last jingle, and last seconds
        previous_state = load_previous_state()
        self.file_path = StringVar(value=previous_state['file_path'])
        self.start_jingle = StringVar(value=previous_state['start_jingle'])
        self.last_jingle = StringVar(value=previous_state['last_jingle'])
        self.last_seconds = IntVar(value=previous_state['last_seconds'])

        # File path label and button
        Label(master, text="Schedule File:").grid(row=0, column=0)
        self.file_label = Label(master, textvariable=self.file_path)
        self.file_label.grid(row=0, column=1)
        Button(master, text="Select File", command=self.select_file).grid(row=0, column=2)

        # Start jingle selection
        Label(master, text="Start Jingle:").grid(row=1, column=0)
        self.start_jingle_label = Label(master, textvariable=self.start_jingle)
        self.start_jingle_label.grid(row=1, column=1)
        Button(master, text="Select Start Jingle", command=self.select_start_jingle).grid(row=1, column=2)

        # Last jingle selection
        Label(master, text="Last Jingle:").grid(row=2, column=0)
        self.last_jingle_label = Label(master, textvariable=self.last_jingle)
        self.last_jingle_label.grid(row=2, column=1)
        Button(master, text="Select Last Jingle", command=self.select_last_jingle).grid(row=2, column=2)

        # Last seconds before the end
        Label(master, text="Seconds before end:").grid(row=3, column=0)
        self.last_seconds_entry = Entry(master, textvariable=self.last_seconds)
        self.last_seconds_entry.grid(row=3, column=1)

        # Start scheduling button
        self.start_button = Button(master, text="Start Scheduling", command=self.start_scheduling)
        self.start_button.grid(row=4, column=1)

        # Exit and save state on close
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select Schedule File", filetypes=[("TSV Files", "*.tsv")])
        if file_path:
            self.file_path.set(file_path)

    def select_start_jingle(self):
        start_jingle = filedialog.askopenfilename(title="Select Start Jingle MP3", filetypes=[("MP3 Files", "*.mp3")])
        if start_jingle:
            self.start_jingle.set(start_jingle)

    def select_last_jingle(self):
        last_jingle = filedialog.askopenfilename(title="Select Last Jingle MP3", filetypes=[("MP3 Files", "*.mp3")])
        if last_jingle:
            self.last_jingle.set(last_jingle)

    def start_scheduling(self):
        file_path = self.file_path.get()
        start_jingle = self.start_jingle.get()
        last_jingle = self.last_jingle.get()
        last_seconds = self.last_seconds.get()

        if file_path and start_jingle and last_jingle:
            print(f"Scheduling actions with file {file_path}, start_jingle={start_jingle}, last_jingle={last_jingle}, and last_seconds={last_seconds}")
            schedule_actions(file_path, start_jingle, last_jingle, last_seconds)
        else:
            print("Please select all required files (schedule file, start jingle, and last jingle).")

    def on_closing(self):
        save_state(self.file_path.get(), self.start_jingle.get(), self.last_jingle.get(), self.last_seconds.get())
        self.master.quit()

# Run the Tkinter app
if __name__ == "__main__":
    root = Tk()
    app = JingleSchedulerApp(root)
    root.mainloop()
