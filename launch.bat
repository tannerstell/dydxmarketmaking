@echo off
echo Killing existing Python processes.
TASKKILL /F /IM python.exe /T
call "C:\Users\tanne\PycharmProjects\dydx - 3.4\venv\Scripts\activate.bat"
main.py

pause