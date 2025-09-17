import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import os
import sqlite3
import qrcode
import shutil
from datetime import datetime
from tkcalendar import DateEntry
from dateutil.relativedelta import relativedelta
import cv2
import io
from utils import send_sms_notification


class EmployeesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_sub_frame = None
        self.create_main_buttons()

    def create_main_buttons(self):
        if self.current_sub_frame:
            self.current_sub_frame.destroy()
            self.current_sub_frame = None

        icons_path = os.path.join(os.path.dirname(__file__), "../templates/frame_7_icons")
        register_image = self.load_image(os.path.join(icons_path, 'register_black.png'))
        view_image = self.load_image(os.path.join(icons_path, 'list_black.png'))
        attendance_image = self.load_image(os.path.join(icons_path, 'scan_black.png'))

        self.register_button = self.create_button("Register Employee", register_image, self.show_register_frame, 100)
        self.view_button = self.create_button("View Employee Info", view_image, self.show_view_frame, 400)
        self.attendance_button = self.create_button("Employee Attendance", attendance_image, self.show_attendance_frame,
                                                    700)

    def load_image(self, path):
        try:
            return ImageTk.PhotoImage(Image.open(path).resize((250, 250), Image.LANCZOS))
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

    def create_button(self, text, image, command, x_pos):
        button = ctk.CTkButton(
            self, text=text, image=image, compound=tk.TOP, command=command,
            width=250, height=250, fg_color="#00C957", text_color=("gray10", "gray90")
        )
        if image: button.image = image
        button.place(x=x_pos, y=180)
        return button

    def clear_main_buttons(self):
        self.register_button.destroy()
        self.view_button.destroy()
        self.attendance_button.destroy()

    def show_register_frame(self):
        self.clear_main_buttons()
        self.current_sub_frame = RegisterEmployeeFrame(self, on_back=self.create_main_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)

    def show_view_frame(self):
        self.clear_main_buttons()
        self.current_sub_frame = ViewEmployeeFrame(self, on_back=self.create_main_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)

    def show_attendance_frame(self):
        self.clear_main_buttons()
        self.current_sub_frame = EmployeeAttendanceFrame(self, on_back=self.create_main_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)


class RegisterEmployeeFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.create_database_table()

        # GUI layout is very similar to TrainerRegistrationFrame
        label = ctk.CTkLabel(self, text="Register Employee", font=("Arial bold", 26))
        label.pack(pady=20, padx=10)
        outer_frame = ctk.CTkFrame(self)
        outer_frame.pack(pady=20, padx=10)
        widget_frames = ctk.CTkFrame(outer_frame)
        widget_frames.pack(pady=5, padx=10)
        label_font = ctk.CTkFont(family="Arial bold", size=16)

        personal_info_frame = ctk.CTkFrame(widget_frames)
        personal_info_frame.grid(row=0, column=0, padx=10, pady=5)
        # ... (Add all entry and combobox widgets similar to trainer registration)
        self.first_name_entry = self.create_widget(personal_info_frame, "entry", "First Name:", "Enter first name", 2,
                                                   label_font)
        # ... create all other widgets

        # For brevity, let's assume the full form is created here...
        # A simple placeholder
        ctk.CTkLabel(self, text="Employee Registration Form Area").pack(pady=50)

        # Buttons
        register_button = ctk.CTkButton(outer_frame, text="Register", fg_color="Green", hover_color="darkgreen",
                                        command=self.register_employee)
        register_button.pack(pady=15)
        back_button = ctk.CTkButton(self, text="Back", fg_color="Red", hover_color="darkred", command=self.on_back)
        back_button.pack(pady=10)

    def create_widget(self, parent, widget_type, text, placeholder, row, font):
        # Helper to create widgets
        pass

    def create_database_table(self):
        with sqlite3.connect('SQLite db/register_employee.db') as conn:
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS employees
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY,
                             first_name
                             TEXT,
                             middle_name
                             TEXT,
                             last_name
                             TEXT,
                             age
                             INTEGER,
                             sex
                             TEXT,
                             birth_date
                             DATE,
                             address
                             TEXT,
                             nationality
                             TEXT,
                             contact_no
                             TEXT
                             UNIQUE,
                             emergency_contact_no
                             TEXT,
                             status
                             TEXT
                             DEFAULT
                             'Active',
                             photo_data
                             BLOB
                         )
                         ''')

    def register_employee(self):
        # Logic to register employee, similar to register_trainer
        # 1. Get data from all entry fields
        # 2. Validate data
        # 3. Read photo file to BLOB
        # 4. INSERT into 'employees' table in 'register_employee.db'
        # 5. Generate QR code and save to 'templates/employee_qrcodes'
        # 6. Send SMS notification
        # 7. Show success message and go back
        messagebox.showinfo("Info", "Register employee functionality to be implemented.")


class ViewEmployeeFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        # Full implementation would be very similar to ViewTrainerFrame
        ctk.CTkLabel(self, text="View Employees Area").pack(pady=50)
        ctk.CTkButton(self, text="Back", fg_color="Red", command=self.on_back).pack()


class EmployeeAttendanceFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.current_sub_frame = None
        self.create_attendance_buttons()

    def create_attendance_buttons(self):
        if self.current_sub_frame:
            self.current_sub_frame.destroy()
            self.current_sub_frame = None

        icons_path = os.path.join(os.path.dirname(__file__), "../templates/frame_7_icons")
        scan_image = self.load_image(os.path.join(icons_path, 'scan_black.png'))
        records_image = self.load_image(os.path.join(icons_path, 'list_black.png'))

        self.scan_button = self.create_button("Take Attendance", scan_image, self.show_scan_frame, 300)
        self.records_button = self.create_button("View Attendance Records", records_image, self.show_records_frame, 550)

        ctk.CTkButton(self, text="Back", fg_color="Red", hover_color="darkred", command=self.on_back).pack(
            side="bottom", pady=20)

    def load_image(self, path):
        try:
            return ImageTk.PhotoImage(Image.open(path).resize((200, 200), Image.LANCZOS))
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

    def create_button(self, text, image, command, x_pos):
        button = ctk.CTkButton(
            self, text=text, image=image, compound=tk.TOP, command=command,
            width=200, height=200, fg_color="#00C957", text_color=("gray10", "gray90")
        )
        if image: button.image = image
        button.place(x=x_pos, y=150)
        return button

    def clear_buttons(self):
        self.scan_button.destroy()
        self.records_button.destroy()

    def show_scan_frame(self):
        self.clear_buttons()
        self.current_sub_frame = EmployeeScanQrFrame(self, on_back=self.create_attendance_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)

    def show_records_frame(self):
        self.clear_buttons()
        self.current_sub_frame = RecordsAttendanceFrame(self, on_back=self.create_attendance_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)


class EmployeeScanQrFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        # This frame would contain Time In / Time Out buttons and QR scanning logic
        # Very similar to ScanFrame in attendance_page.py but for employees
        ctk.CTkLabel(self, text="Employee QR Scan Area (Time In/Out)").pack(pady=50)
        ctk.CTkButton(self, text="Back", fg_color="Red", command=self.on_back).pack()


class RecordsAttendanceFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        # This frame would display a table of employee attendance records
        # Very similar to RecordsFrame in attendance_page.py
        ctk.CTkLabel(self, text="Employee Attendance Records Table").pack(pady=50)
        ctk.CTkButton(self, text="Back", fg_color="Red", command=self.on_back).pack()