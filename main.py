import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Directory to monitor for downloads
DOWNLOADS_DIR = "/path/to/downloads"

# Command to scan a file using ClamAV
CLAMSCAN_CMD = "clamscan --stdout --infected --remove {}"

class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        elif event.src_path.endswith('.part'):
            # Ignore incomplete downloads
            return
        else:
            print(f"New file detected: {event.src_path}")
            self.scan_file(event.src_path)

    def scan_file(self, file_path):
        print(f"Scanning file: {file_path}")
        result = subprocess.run(CLAMSCAN_CMD.format(file_path), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("No virus found.")
        elif result.returncode == 1:
            print("Virus found. Removing file...")
            os.remove(file_path)
        else:
            print("Error occurred during scanning:", result.stderr.decode('utf-8'))

if __name__ == "__main__":
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
