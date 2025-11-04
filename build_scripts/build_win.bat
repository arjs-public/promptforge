@echo off
REM Example Windows build using pyinstaller
pyinstaller --onefile --add-data "..\frontend;frontend" app.py
