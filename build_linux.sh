#!/bin/bash
# Install required packages
pip install pyinstaller flaskwebgui

# Clean old builds
rm -rf build/ dist/

# Build standalone directory using PyInstaller
# --onedir creates a folder with the executable and all dependencies
# --add-data includes all necessary templates, static files, and images
pyinstaller --name "Cardify" \
    --onedir \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --add-data "*.png:." \
    --add-data "*.jpeg:." \
    --add-data "*.pdf:." \
    app.py

echo "Build complete! Check the 'dist/Cardify' folder."
