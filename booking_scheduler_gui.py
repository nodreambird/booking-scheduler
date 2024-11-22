import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime, timedelta, date
from dateutil.rrule import rrule, WEEKLY, MONTHLY, YEARLY
from dateutil.relativedelta import relativedelta
import json
import os
import calendar
import tkinter as tk
from tkinter import ttk

class BookingSchedulerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Booking Scheduler")
        self.geometry("1000x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize booking storage
        self.storage_file = 'bookings.json'
        self.bookings = self.load_bookings()

        # Create main layout frames
        self.create_layout()
        
        # Create widgets
        self.create_calendar_frame()
        self.create_booking_frame()
        self.create_list_frame()
        
        # Update the bookings list
        self.update_bookings_list()
        self.update_calendar()

    def create_layout(self):
        # Create main frames
        self.calendar_frame = ctk.CTkFrame(self)
        self.calendar_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.booking_frame = ctk.CTkFrame(self)
        self.booking_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def create_calendar_frame(self):
        # Calendar label
        calendar_label = ctk.CTkLabel(self.calendar_frame, text="Select Date", font=("Arial", 16, "bold"))
        calendar_label.pack(pady=5)

        # Create calendar widget with specific style
        style = ttk.Style()
        style.configure('my.Calendar', 
            background='gray20',
            foreground='white',
            fieldbackground='gray20',
            selectbackground='blue',
            selectforeground='white')
        
        self.cal = Calendar(self.calendar_frame, 
            selectmode='day', 
            date_pattern='y-mm-dd',
            style='my.Calendar',
            showweeknumbers=False)
        self.cal.pack(padx=10, pady=5)
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)

    def create_booking_frame(self):
        # Booking form label
        booking_label = ctk.CTkLabel(self.booking_frame, text="Add Booking", font=("Arial", 16, "bold"))
        booking_label.pack(pady=5)

        # Name entry
        self.name_var = ctk.StringVar()
        name_label = ctk.CTkLabel(self.booking_frame, text="Name:")
        name_label.pack(pady=2)
        self.name_entry = ctk.CTkEntry(self.booking_frame, textvariable=self.name_var)
        self.name_entry.pack(pady=2)

        # Time entry frame
        time_frame = ctk.CTkFrame(self.booking_frame)
        time_frame.pack(pady=5)

        # Hour selection
        hour_label = ctk.CTkLabel(time_frame, text="Hour:")
        hour_label.pack(side="left", padx=5)
        self.hour_var = ctk.StringVar(value="09")
        hours = [f"{i:02d}" for i in range(24)]
        self.hour_menu = ctk.CTkOptionMenu(time_frame, variable=self.hour_var, values=hours)
        self.hour_menu.pack(side="left", padx=5)

        # Minute selection
        minute_label = ctk.CTkLabel(time_frame, text="Minute:")
        minute_label.pack(side="left", padx=5)
        self.minute_var = ctk.StringVar(value="00")
        minutes = [f"{i:02d}" for i in range(0, 60, 15)]
        self.minute_menu = ctk.CTkOptionMenu(time_frame, variable=self.minute_var, values=minutes)
        self.minute_menu.pack(side="left", padx=5)

        # Duration selection
        duration_label = ctk.CTkLabel(self.booking_frame, text="Duration (minutes):")
        duration_label.pack(pady=2)
        self.duration_var = ctk.StringVar(value="60")
        durations = ["30", "60", "90", "120"]
        self.duration_menu = ctk.CTkOptionMenu(self.booking_frame, variable=self.duration_var, values=durations)
        self.duration_menu.pack(pady=2)

        # Recurrence options
        recurrence_label = ctk.CTkLabel(self.booking_frame, text="Recurrence:")
        recurrence_label.pack(pady=2)
        self.recurrence_var = ctk.StringVar(value="none")
        self.recurrence_menu = ctk.CTkOptionMenu(
            self.booking_frame,
            variable=self.recurrence_var,
            values=["none", "weekly", "monthly", "yearly"],
            command=self.on_recurrence_change
        )
        self.recurrence_menu.pack(pady=2)

        # Until date frame (hidden by default)
        self.until_frame = ctk.CTkFrame(self.booking_frame)
        until_label = ctk.CTkLabel(self.until_frame, text="Repeat Until:")
        until_label.pack(side="left", padx=5)
        self.until_cal = Calendar(self.until_frame, selectmode='day', date_pattern='y-mm-dd')
        self.until_cal.pack(pady=5)

        # Add booking button
        self.add_button = ctk.CTkButton(self.booking_frame, text="Add Booking", command=self.add_booking)
        self.add_button.pack(pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(self.booking_frame, text="")
        self.status_label.pack(pady=5)

    def create_list_frame(self):
        # Bookings list label
        list_label = ctk.CTkLabel(self.list_frame, text="Current Bookings", font=("Arial", 16, "bold"))
        list_label.pack(pady=5)

        # Create textbox for bookings
        self.bookings_text = ctk.CTkTextbox(self.list_frame, height=200)
        self.bookings_text.pack(padx=10, pady=5, fill="both", expand=True)

    def load_bookings(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                bookings = json.load(f)
                for booking in bookings:
                    if 'recurrence' not in booking:
                        booking['recurrence'] = None
                return bookings
        return []

    def save_bookings(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.bookings, f, indent=2)

    def get_recurrence_instances(self, booking, start_date, end_date):
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
        check_until = new_end
        if recurrence:
            check_until = datetime.fromisoformat(recurrence['until'])

        for booking in self.bookings:
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

    def add_booking(self):
        # Get booking details
        name = self.name_var.get().strip()
        if not name:
            self.show_status("Please enter a name", "error")
            return

        date_str = self.cal.get_date()
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        duration = int(self.duration_var.get())

        # Create datetime objects
        start = datetime.strptime(f"{date_str} {hour}:{minute}", "%Y-%m-%d %H:%M")
        end = start + timedelta(minutes=duration)

        # Handle recurrence
        recurrence = None
        if self.recurrence_var.get() != "none":
            until_date = self.until_cal.get_date()
            until = datetime.strptime(f"{until_date} 23:59", "%Y-%m-%d %H:%M")
            recurrence = {
                'type': self.recurrence_var.get(),
                'until': until.isoformat()
            }

        # Check for conflicts
        conflict = self.check_conflicts(start, end, recurrence)
        if conflict:
            self.show_status(f"Conflict with existing booking: {conflict['name']}", "error")
            return

        # Add the booking
        booking = {
            'name': name,
            'start': start.isoformat(),
            'end': end.isoformat(),
            'recurrence': recurrence
        }
        self.bookings.append(booking)
        self.save_bookings()

        # Update UI
        self.show_status("Booking added successfully!", "success")
        self.name_var.set("")
        self.update_bookings_list()
        self.update_calendar()

    def update_bookings_list(self):
        self.bookings_text.delete("1.0", "end")
        if not self.bookings:
            self.bookings_text.insert("1.0", "No bookings found.")
            return

        # Sort bookings by start time
        sorted_bookings = sorted(self.bookings, key=lambda x: x['start'])

        for booking in sorted_bookings:
            start = datetime.fromisoformat(booking['start'])
            end = datetime.fromisoformat(booking['end'])
            
            booking_text = f"Name: {booking['name']}\n"
            booking_text += f"Date: {start.strftime('%Y-%m-%d')}\n"
            booking_text += f"Time: {start.strftime('%H:%M')} - {end.strftime('%H:%M')}\n"
            
            if booking['recurrence']:
                booking_text += f"Recurrence: {booking['recurrence']['type']} "
                booking_text += f"until {booking['recurrence']['until'].split('T')[0]}\n"
            
            booking_text += "-" * 40 + "\n"
            self.bookings_text.insert("end", booking_text)

    def update_calendar(self):
        try:
            # Clear existing tags
            try:
                self.cal.calevent_remove('all')
            except tk.TclError:
                # If no events exist, this is fine
                pass

            # Get current month's start and end dates
            current_date = datetime.strptime(self.cal.get_date(), "%Y-%m-%d")
            year = current_date.year
            month = current_date.month
            
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)

            # Add events for all bookings
            for booking in self.bookings:
                instances = self.get_recurrence_instances(booking, start_date, end_date)
                for instance in instances:
                    event_date = datetime.fromisoformat(instance['start']).date()
                    try:
                        self.cal.calevent_create(event_date, booking['name'], "booking")
                    except tk.TclError as e:
                        print(f"Could not create calendar event: {e}")
            
            # Configure tag colors
            try:
                self.cal.tag_config('booking', background='lightgreen', foreground='black')
            except tk.TclError:
                # If tag already exists, this is fine
                pass
        except Exception as e:
            print(f"Error updating calendar: {e}")
            self.show_status("Error updating calendar display", "error")

    def on_date_select(self, event=None):
        self.update_calendar()

    def on_recurrence_change(self, choice):
        if choice == "none":
            self.until_frame.pack_forget()
        else:
            self.until_frame.pack(pady=5)

    def show_status(self, message, status_type="info"):
        color = "green" if status_type == "success" else "red" if status_type == "error" else "white"
        self.status_label.configure(text=message, text_color=color)

if __name__ == "__main__":
    app = BookingSchedulerGUI()
    app.mainloop()
