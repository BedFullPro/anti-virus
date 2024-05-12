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

# Function to download a file from a URL
def download_file(url, save_path):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

# Function to install ClamAV
def install_clamav():
    # Check if ClamAV is already installed
    try:
        result = subprocess.run("clamscan --version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("ClamAV is already installed.")
            return
    except FileNotFoundError:
        pass  # ClamAV not found, proceed with installation

    # Determine the platform (e.g., Windows 64-bit)
    system = platform.system()
    machine = platform.machine()
    if system != 'Windows':
        print("Automatic installation is only supported on Windows.")
        return

    # Determine the download URL based on the platform
    if machine.endswith('64'):
        url = 'https://www.clamav.net/downloads/production/clamav-0.103.0-win-x64-portable.zip'
    else:
        url = 'https://www.clamav.net/downloads/production/clamav-0.103.0-win-x86-portable.zip'

    # Path to save the downloaded ClamAV installer
    installer_path = os.path.join(os.path.dirname(__file__), 'clamav_installer.zip')

    # Download the ClamAV installer
    print(f"Downloading ClamAV installer from {url}")
    download_file(url, installer_path)

    # Extract the installer
    print("Extracting ClamAV installer...")
    extract_cmd = f'powershell Expand-Archive -Path "{installer_path}" -DestinationPath "{os.path.dirname(__file__)}"'
    subprocess.run(extract_cmd, shell=True)

    # Find the installer executable
    installer_executable = os.path.join(os.path.dirname(__file__), 'clamav_installer.exe')

    # Execute the ClamAV installer
    print("Installing ClamAV...")
    result = subprocess.run(installer_executable, shell=True)
    if result.returncode == 0:
        print("ClamAV installation successful.")
    else:
        print("ClamAV installation failed.")

    # Clean up - remove the downloaded installer
    os.remove(installer_path)

# Function to scan a file using ClamAV
def scan_file(file_path):
    print(f"Scanning file: {file_path}")
    result = subprocess.run(f'clamscan --stdout --infected --remove "{file_path}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print("No virus found.")
    elif result.returncode == 1:
        print("Virus found. Removing file...")
        os.remove(file_path)
    else:
        print("Error occurred during scanning:", result.stderr.decode('utf-8'))

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
    # Install ClamAV if not already installed
    install_clamav()

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
