@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Building executable...
pyinstaller --noconfirm --onefile --windowed ^
    --add-data "bookings.json;." ^
    --hidden-import customtkinter ^
    --hidden-import tkcalendar ^
    --hidden-import babel.numbers ^
    --name "BookingScheduler" ^
    booking_scheduler_gui.py

echo Build complete! Executable is in the dist folder.
