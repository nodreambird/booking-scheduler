# Booking Scheduler

A modern, user-friendly GUI application for managing recurring bookings with a calendar interface.

## Features

- Modern dark-themed GUI using CustomTkinter
- Interactive calendar view with booking indicators
- Single and recurring booking support
- Conflict detection
- Persistent JSON-based storage
- Standalone Windows executable

## Requirements

- Python 3.12+
- Dependencies (for development):
  - CustomTkinter
  - TkCalendar
  - python-dateutil
  - PyInstaller (for building executable)

## Installation

### Option 1: Run from Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/booking-scheduler.git
cd booking-scheduler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python booking_scheduler_gui.py
```

### Option 2: Standalone Executable

1. Download the latest release from the Releases page
2. Run `BookingSchedulerApp.exe`

## Usage

1. Select a date from the calendar
2. Choose a time slot and duration
3. Set recurrence options if needed
4. Click "Add Booking" to create the booking
5. View your bookings in the list below
6. Delete bookings by selecting them and clicking "Delete Selected"

## Building the Executable

To build the standalone executable:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Run the build script:
```bash
build_exe.bat
```

The executable will be created in the `output` directory.

## Development

- `booking_scheduler_gui.py`: Main GUI application
- `booking_manager.py`: Core booking logic
- `bookings.json`: Persistent storage
- `build_exe.bat`: Build script for creating executable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - See LICENSE file for details