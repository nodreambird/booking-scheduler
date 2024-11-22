from datetime import datetime, timedelta, date
from colorama import init, Fore, Style
from tabulate import tabulate
import json
import os
import calendar
from dateutil.rrule import rrule, WEEKLY, MONTHLY, YEARLY
from dateutil.relativedelta import relativedelta

class BookingScheduler:
    def __init__(self, storage_file='bookings.json'):
        """
        Initialize the booking scheduler with a storage file
        """
        self.storage_file = storage_file
        self.bookings = self.load_bookings()
        init(autoreset=True)  # Initialize colorama for colored output

    def load_bookings(self):
        """
        Load existing bookings from a JSON file
        """
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                bookings = json.load(f)
                # Convert old format bookings to new format if necessary
                for booking in bookings:
                    if 'recurrence' not in booking:
                        booking['recurrence'] = None
                return bookings
        return []

    def save_bookings(self):
        """
        Save bookings to a JSON file
        """
        with open(self.storage_file, 'w') as f:
            json.dump(self.bookings, f, indent=2)

    def parse_datetime(self, date_str, time_str):
        """
        Parse date and time strings into a datetime object
        """
        try:
            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            print(Fore.RED + "Invalid date or time format. Use YYYY-MM-DD HH:MM")
            return None

    def get_recurrence_instances(self, booking, start_date, end_date):
        """
        Get all instances of a recurring booking between start_date and end_date
        """
        if not booking['recurrence']:
            return [{'start': booking['start'], 'end': booking['end']}]

        start = datetime.fromisoformat(booking['start'])
        end = datetime.fromisoformat(booking['end'])
        duration = end - start

        recur_type = booking['recurrence']['type']
        until = datetime.fromisoformat(booking['recurrence']['until'])
        
        if recur_type == 'weekly':
            freq = WEEKLY
        elif recur_type == 'monthly':
            freq = MONTHLY
        elif recur_type == 'yearly':
            freq = YEARLY
        else:
            return [{'start': booking['start'], 'end': booking['end']}]

        instances = []
        for dt in rrule(freq=freq, dtstart=start, until=min(until, end_date)):
            if dt >= start_date:
                instance_end = dt + duration
                instances.append({
                    'start': dt.isoformat(),
                    'end': instance_end.isoformat()
                })

        return instances

    def check_conflicts(self, new_start, new_end, recurrence=None):
        """
        Check for scheduling conflicts, including recurring bookings
        """
        check_until = new_end
        if recurrence:
            check_until = datetime.fromisoformat(recurrence['until'])

        for booking in self.bookings:
            # Get all instances of the existing booking up to our check_until date
            existing_instances = self.get_recurrence_instances(
                booking,
                new_start,
                check_until
            )

            for instance in existing_instances:
                existing_start = datetime.fromisoformat(instance['start'])
                existing_end = datetime.fromisoformat(instance['end'])
                
                if (new_start < existing_end and new_end > existing_start):
                    return booking

        return None

    def add_booking(self, name, date, start_time, end_time=None, duration=60, recurrence=None):
        """
        Add a new booking with optional recurrence
        """
        start = self.parse_datetime(date, start_time)
        if not start:
            return False

        # If end time not provided, calculate based on duration
        if not end_time:
            end = start + timedelta(minutes=int(duration))
        else:
            end = self.parse_datetime(date, end_time)
            if not end:
                return False

        # For recurring bookings, check conflicts up to the until date
        conflict = self.check_conflicts(start, end, recurrence)
        if conflict:
            print(Fore.RED + "Conflict detected with existing booking:")
            if conflict.get('recurrence'):
                print(f"Recurring booking: {conflict['name']} ({conflict['recurrence']['type']})")
            else:
                print(f"Single booking: {conflict['name']}")
            return False

        # Add the booking
        booking = {
            'name': name,
            'start': start.isoformat(),
            'end': end.isoformat(),
            'recurrence': recurrence
        }
        self.bookings.append(booking)
        self.save_bookings()
        
        print(Fore.GREEN + f"Booking added: {name}")
        if recurrence:
            print(Fore.GREEN + f"Recurring {recurrence['type']} until {recurrence['until']}")
        return True

    def list_bookings(self):
        """
        List all current bookings
        """
        if not self.bookings:
            print(Fore.YELLOW + "No bookings found.")
            return

        # Prepare bookings for tabulate
        table_data = []
        for booking in self.bookings:
            recur_info = ""
            if booking['recurrence']:
                recur_info = f"[{booking['recurrence']['type']} until {booking['recurrence']['until']}]"
            
            table_data.append([
                booking['name'],
                datetime.fromisoformat(booking['start']).strftime('%Y-%m-%d %H:%M'),
                datetime.fromisoformat(booking['end']).strftime('%Y-%m-%d %H:%M'),
                recur_info
            ])

        # Print table
        print(Fore.CYAN + tabulate(table_data,
            headers=['Name', 'Start', 'End', 'Recurrence'],
            tablefmt='pretty'))

    def show_calendar(self, year=None, month=None):
        """
        Display a calendar view with bookings
        """
        if year is None or month is None:
            today = date.today()
            year = today.year
            month = today.month

        # Calculate start and end of month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Get calendar for the specified month
        cal = calendar.monthcalendar(year, month)
        
        # Get all bookings for this month, including recurring instances
        bookings_by_day = {}
        for booking in self.bookings:
            instances = self.get_recurrence_instances(booking, start_date, end_date)
            for instance in instances:
                booking_date = datetime.fromisoformat(instance['start']).date()
                if booking_date.year == year and booking_date.month == month:
                    if booking_date.day not in bookings_by_day:
                        bookings_by_day[booking_date.day] = []
                    bookings_by_day[booking_date.day].append({
                        'name': booking['name'],
                        'start': instance['start'],
                        'end': instance['end'],
                        'recurrence': booking.get('recurrence')
                    })

        # Print calendar header
        month_name = calendar.month_name[month]
        print(Fore.CYAN + f"\n{month_name} {year}".center(34))
        print(Fore.WHITE + "Mo Tu We Th Fr Sa Su".center(34))

        # Print calendar days
        for week in cal:
            week_str = ""
            for day in week:
                if day == 0:
                    week_str += "   "
                else:
                    if day in bookings_by_day:
                        week_str += Fore.GREEN + f"{day:2d}*" + Fore.RESET
                    else:
                        week_str += f"{day:2d} "
            print(week_str.center(34))

        print("\n" + Fore.GREEN + "*" + Fore.RESET + " indicates days with bookings")

    def show_day_bookings(self, year, month, day):
        """
        Show all bookings for a specific day, including recurring instances
        """
        target_date = datetime(year, month, day)
        end_date = target_date + timedelta(days=1)
        day_bookings = []

        for booking in self.bookings:
            instances = self.get_recurrence_instances(booking, target_date, end_date)
            for instance in instances:
                instance_date = datetime.fromisoformat(instance['start']).date()
                if instance_date == target_date.date():
                    day_bookings.append({
                        'name': booking['name'],
                        'start': instance['start'],
                        'end': instance['end'],
                        'recurrence': booking.get('recurrence')
                    })

        if not day_bookings:
            print(Fore.YELLOW + f"No bookings found for {target_date.date()}")
            return

        # Sort bookings by start time
        day_bookings.sort(key=lambda x: x['start'])

        # Prepare table data
        table_data = []
        for booking in day_bookings:
            start_time = datetime.fromisoformat(booking['start'])
            end_time = datetime.fromisoformat(booking['end'])
            recur_info = ""
            if booking.get('recurrence'):
                recur_info = f"[{booking['recurrence']['type']}]"
            
            table_data.append([
                booking['name'],
                start_time.strftime('%H:%M'),
                end_time.strftime('%H:%M'),
                recur_info
            ])

        print(Fore.CYAN + f"\nBookings for {target_date.date()}")
        print(tabulate(table_data, 
            headers=['Name', 'Start', 'End', 'Recurrence'],
            tablefmt='pretty'))

def main():
    scheduler = BookingScheduler()

    while True:
        print("\n--- Booking Scheduler ---")
        print("1. Add Booking")
        print("2. List All Bookings")
        print("3. Show Calendar")
        print("4. View Day's Bookings")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            name = input("Enter booking name: ")
            date = input("Enter date (YYYY-MM-DD): ")
            start_time = input("Enter start time (HH:MM): ")
            duration = input("Enter duration in minutes (default 60): ") or 60
            
            # Ask about recurrence
            recur = input("Make this a recurring booking? (y/n): ").lower()
            recurrence = None
            if recur == 'y':
                print("\nRecurrence type:")
                print("1. Weekly")
                print("2. Monthly")
                print("3. Yearly")
                recur_choice = input("Choose recurrence type (1-3): ")
                
                if recur_choice in ['1', '2', '3']:
                    recur_type = {
                        '1': 'weekly',
                        '2': 'monthly',
                        '3': 'yearly'
                    }[recur_choice]
                    
                    until_date = input("Enter end date for recurrence (YYYY-MM-DD): ")
                    try:
                        until = datetime.strptime(f"{until_date} 23:59", "%Y-%m-%d %H:%M")
                        recurrence = {
                            'type': recur_type,
                            'until': until.isoformat()
                        }
                    except ValueError:
                        print(Fore.RED + "Invalid date format for recurrence end date")
                        continue
                else:
                    print(Fore.RED + "Invalid recurrence type selected")
                    continue
            
            scheduler.add_booking(name, date, start_time, duration=int(duration), recurrence=recurrence)

        elif choice == '2':
            scheduler.list_bookings()

        elif choice == '3':
            year = input("Enter year (press Enter for current): ") or datetime.now().year
            month = input("Enter month (1-12, press Enter for current): ") or datetime.now().month
            scheduler.show_calendar(int(year), int(month))

        elif choice == '4':
            year = input("Enter year (press Enter for current): ") or datetime.now().year
            month = input("Enter month (1-12, press Enter for current): ") or datetime.now().month
            day = input("Enter day: ")
            if day:
                scheduler.show_day_bookings(int(year), int(month), int(day))
            else:
                print(Fore.RED + "Day is required")

        elif choice == '5':
            break

        else:
            print(Fore.RED + "Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
