# Booking Scheduler Application

A modern, user-friendly booking management system with recurring booking capabilities and automatic conflict resolution.

## Features

- Modern dark-themed GUI interface
- Calendar view with booking indicators
- Add single or recurring bookings (weekly/monthly/yearly)
- Automatic conflict detection
- Persistent storage of bookings
- Easy time selection with dropdowns
- View all bookings in a sorted list

## Installation

1. Download the latest release zip file
2. Extract all files to a directory of your choice
3. Run `BookingSchedulerApp.exe`

## Usage

1. **Adding a Booking**
   - Select a date from the calendar
   - Enter the booking name
   - Choose time and duration
   - Select recurrence pattern (if needed)
   - Click "Add Booking"

2. **Viewing Bookings**
   - Calendar shows dates with bookings
   - Bottom panel displays all bookings sorted by date
   - Recurring bookings show their pattern and end date

## Requirements

- Windows 10/11
- No additional software required (standalone executable)

## Technical Details

Built with:
- Python 3.12
- CustomTkinter for modern UI
- TkCalendar for calendar widget
- JSON-based storage
- PyInstaller for packaging