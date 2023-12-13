@echo off
echo Killing existing Python processes.
TASKKILL /F /IM python.exe /T
call "C:\enter\path\here\venv\Scripts\activate.bat"
main.py

pause
