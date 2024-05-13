import os
import subprocess
import platform
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Get the username of the current user
username = os.getlogin()

# Directory to monitor for downloads
DOWNLOADS_DIR = os.path.join("C:", "Users", username, "Downloads")

# VirusTotal API key (replace 'YOUR_API_KEY' with your actual API key)
API_KEY = 'YOUR_API_KEY'

# Function to download a file from a URL
def download_file(url, save_path):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

# Function to scan a file using VirusTotal API
def scan_file(file_path):
    print(f"Scanning file: {file_path}")
    url = 'https://www.virustotal.com/vtapi/v2/file/scan'
    params = {'apikey': API_KEY}
    files = {'file': (file_path, open(file_path, 'rb'))}
    response = requests.post(url, files=files, params=params)
    if response.status_code == 200:
        result = response.json()
        if result['response_code'] == 1:
            print("Scan completed.")
            positives = result['positives']
            if positives > 0:
                print(f"Virus detected by {positives} out of {result['total']} scanners.")
                # Optionally, you can remove the file here
                # os.remove(file_path)
            else:
                print("No virus detected.")
        else:
            print("Scan failed:", result['verbose_msg'])
    else:
        print("Error occurred during scanning:", response.status_code)

# Event handler for file system events
class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        elif event.src_path.endswith('.part'):
            # Ignore incomplete downloads
            return
        else:
            print(f"New file detected: {event.src_path}")
            scan_file(event.src_path)

if __name__ == "__main__":
    # Start monitoring the downloads directory
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS_DIR, recursive=False)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
