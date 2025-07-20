import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SimulationDataHandler(FileSystemEventHandler):
    def __init__(self, process_callback):
        super().__init__()
        self.process_callback = process_callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            print(f"New simulation data detected: {event.src_path}")
            self.process_callback(event.src_path)

def start_watching(folder_to_watch, process_callback):
    event_handler = SimulationDataHandler(process_callback)
    observer = Observer()
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    observer.start()
    print(f"Started watching folder: {folder_to_watch}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Example usage (to be integrated with PyQt5 app):
if __name__ == "__main__":
    def dummy_process(path):
        print(f"Processing: {path}")
    folder = input("Enter folder to watch for simulation data: ")
    start_watching(folder, dummy_process) 