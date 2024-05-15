import os
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Get the username of the current user
username = os.getlogin()

# Directory to monitor for downloads
DOWNLOADS_DIR = os.path.join("C:", "Users", username, "Downloads")

# MetaDefender Cloud API key
API_KEY = "2db345ea1d49d5016b5bf27d45548ae0"

# Function to download a file from a URL
def download_file(url, save_path):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

# Function to scan a file using MetaDefender Cloud API
def scan_file(file_path):
    print(f"Scanning file: {file_path}")
    url = 'https://api.metadefender.com/v4/file'
    headers = {'apikey': API_KEY}
    files = {'file': (os.path.basename(file_path), open(file_path, 'rb'))}
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        result = response.json()
        if result.get('file_info') and result['file_info'].get('scan_results'):
            scan_results = result['file_info']['scan_results']
            if scan_results['scan_all_result_i'] == 0:
                print("No threat detected.")
            else:
                print("Threat detected.")
                for engine, result in scan_results['scan_details'].items():
                    if result['threat_found']:
                        print(f"{engine}: {result['threat_found']}")
        else:
            print("Scan failed:", result.get('error', {}).get('messages', ['Unknown error']))
    else:
        print("Error occurred during scanning:", response.status_code)

# Event handler for file system events
class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        elif event.src_path.endswith(('.part', '.crdownload')):
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
