#!/bin/bash
rm -rf dist/
# Example: build macos single-file with pyinstaller --noconsole  --windowed
pyinstaller --name "PromptForge" --clean --onefile --icon=promptforge.icns --paths="." --console --hidden-import requests --hidden-import . --add-data "frontend:./frontend" --add-data "backend:." backend/app.py
