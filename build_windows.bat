@echo off
echo Installing required packages...
python -m pip install pyinstaller flaskwebgui

echo Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Building standalone application using PyInstaller...
python -m PyInstaller --name "Cardify" ^
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
