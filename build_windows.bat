@echo off
echo Installing required packages...
pip install pyinstaller flaskwebgui

echo Cleaning old builds...
rmdir /s /q build dist

echo Building standalone application using PyInstaller...
pyinstaller --name "Cardify" ^
    --onedir ^
    --noconsole ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "*.png;." ^
    --add-data "*.jpeg;." ^
    --add-data "*.pdf;." ^
    app.py

echo Build complete! Check the 'dist/Cardify' folder.
pause
