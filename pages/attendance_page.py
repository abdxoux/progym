import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import sqlite3
import cv2
from datetime import datetime
from utils import send_sms_notification


class AttendancePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_sub_frame = None
        self.create_main_buttons()

    def create_main_buttons(self):
        # Clear any existing sub-frame
        if self.current_sub_frame:
            self.current_sub_frame.destroy()
            self.current_sub_frame = None

        # Define paths and load images
        icons_path = os.path.join(os.path.dirname(__file__), "../templates/frame_3_icons")
        scan_image = self.load_image(os.path.join(icons_path, 'scan_black.png'))
        record_image = self.load_image(os.path.join(icons_path, 'record_black.png'))

        # Create buttons
        self.scan_qr_button = self.create_button("Scan QR Code", scan_image, self.show_scan_frame, 150)
        self.view_records_button = self.create_button("Attendance Records", record_image, self.show_records_frame, 600)

    def load_image(self, path):
        try:
            return ImageTk.PhotoImage(Image.open(path).resize((300, 300), Image.LANCZOS))
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

    def create_button(self, text, image, command, x_pos):
        button = ctk.CTkButton(
            self, text=text, image=image, compound=tk.TOP, command=command,
            width=300, height=300, fg_color="#00C957", text_color=("gray10", "gray90")
        )
        button.image = image  # Keep a reference
        button.place(x=x_pos, y=150)
        return button

    def clear_main_buttons(self):
        self.scan_qr_button.destroy()
        self.view_records_button.destroy()

    def show_scan_frame(self):
        self.clear_main_buttons()
        self.current_sub_frame = ScanFrame(self, on_back=self.create_main_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)

    def show_records_frame(self):
        self.clear_main_buttons()
        self.current_sub_frame = RecordsFrame(self, on_back=self.create_main_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)


class ScanFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.create_ui_elements()

    def create_ui_elements(self):
        icons_path = os.path.join(os.path.dirname(__file__), "../templates/frame_3_icons")
        time_in_image = self.load_image(os.path.join(icons_path, 'time_in.png'))
        time_out_image = self.load_image(os.path.join(icons_path, 'time_out.png'))

        self.create_button("Time In", time_in_image, self.scan_qr_code_time_in, 300)
        self.create_button("Time Out", time_out_image, self.scan_qr_code_time_out, 550)

        back_button = ctk.CTkButton(self, text="Back", fg_color="Red", hover_color="darkred",
                                    command=self.back_button_event)
        back_button.place(x=450, y=550)

    def load_image(self, path):
        return ImageTk.PhotoImage(Image.open(path).resize((200, 200), Image.LANCZOS))

    def create_button(self, text, image, command, x_pos):
        button = ctk.CTkButton(
            self, text=text, image=image, compound=tk.TOP, command=command,
            width=200, height=200, fg_color="#00C957", text_color=("gray10", "gray90")
        )
        button.image = image
        button.place(x=x_pos, y=150)

    def scan_qr_code_time_in(self):
        qr_code_data = self.scan_qr_code()
        if qr_code_data:
            self.record_attendance(qr_code_data, "Time In")

    def scan_qr_code_time_out(self):
        qr_code_data = self.scan_qr_code()
        if qr_code_data:
            self.record_attendance(qr_code_data, "Time Out")

    def record_attendance(self, member_data, attendance_type):
        try:
            first_name, middle_name, last_name, contact_no, subscription_id = member_data.split(',')
            current_datetime = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

            # Check subscription status
            with sqlite3.connect('SQLite db/registration_form.db') as conn_reg:
                cursor_reg = conn_reg.cursor()
                status_result = cursor_reg.execute('SELECT status FROM registration WHERE subscription_id = ?',
                                                   (subscription_id,)).fetchone()
                if not status_result or status_result[0] == 'Expired':
                    messagebox.showerror("Error", f"Subscription ID {subscription_id} is not active or has expired.")
                    return

            # Record attendance
            with sqlite3.connect('SQLite db/attendance_records.db') as conn_att:
                cursor_att = conn_att.cursor()
                if attendance_type == "Time In":
                    cursor_att.execute(
                        'INSERT INTO attendance_records (first_name, middle_name, last_name, contact_no, subscription_id, time_in) VALUES (?, ?, ?, ?, ?, ?)',
                        (first_name, middle_name, last_name, contact_no, subscription_id, current_datetime))
                    sms_message = f"Hello {first_name}!, You have successfully timed in at D'GRIT GYM at {current_datetime}."
                else:  # Time Out
                    cursor_att.execute(
                        'UPDATE attendance_records SET time_out = ? WHERE subscription_id = ? AND time_out IS NULL',
                        (current_datetime, subscription_id))
                    sms_message = f"Hello {first_name}!, Thank you for coming. You have successfully timed out at {current_datetime}."

                conn_att.commit()
                send_sms_notification(contact_no, sms_message)
                messagebox.showinfo("Success", f"{attendance_type} recorded for {first_name} {last_name}.")
                self.display_details_window(member_data, attendance_type, current_datetime)

        except (sqlite3.Error, ValueError, Exception) as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    @staticmethod
    def scan_qr_code():
        cap = cv2.VideoCapture(0)
        data = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow('QR Code Scanner (Press Q to quit)', frame)
            detector = cv2.QRCodeDetector()
            qr_data, _, _ = detector.detectAndDecode(frame)
            if qr_data:
                data = qr_data
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        return data

    def display_details_window(self, member_data, attendance_type, current_datetime):
        details_window = ctk.CTkToplevel(self)
        details_window.title("Attendance Details")
        details_window.geometry("450x350")
        details_window.attributes('-topmost', True)

        try:
            first_name, middle_name, last_name, contact_no, subscription_id = member_data.split(',')
            data_dict = {
                "Attendance Type": attendance_type, "First Name": first_name, "Middle Name": middle_name,
                "Last Name": last_name, "Contact No": contact_no, "Subscription ID": subscription_id,
                "Timestamp": current_datetime
            }
            for i, (key, value) in enumerate(data_dict.items()):
                ctk.CTkLabel(details_window, text=f"{key}:", font=("Arial", 12, "bold")).grid(row=i, column=0, padx=10,
                                                                                              pady=5, sticky="w")
                ctk.CTkLabel(details_window, text=value).grid(row=i, column=1, padx=10, pady=5, sticky="w")

            ctk.CTkButton(details_window, text="OK", command=details_window.destroy).grid(row=len(data_dict), column=0,
                                                                                          columnspan=2, pady=20)
        except ValueError:
            ctk.CTkLabel(details_window, text="Invalid QR Code Data Format").pack(pady=20)

    def back_button_event(self):
        self.destroy()
        self.on_back()


class RecordsFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.create_database_table()
        self.create_ui_elements()

    def create_database_table(self):
        with sqlite3.connect('SQLite db/attendance_records.db') as conn:
            conn.cursor().execute('''
                                  CREATE TABLE IF NOT EXISTS attendance_records
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
                                      contact_no
                                      TEXT,
                                      subscription_id
                                      TEXT,
                                      time_in
                                      TEXT,
                                      time_out
                                      TEXT
                                  )
                                  ''')
            conn.commit()

    def create_ui_elements(self):
        label = ctk.CTkLabel(self, text="Members' Attendance Records", font=("Arial bold", 28))
        label.pack(pady=20, padx=10)

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=30, fieldbackground="#343638")
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")

        self.records_table = ttk.Treeview(table_frame,
                                          columns=("First Name", "M.I", "Last Name", "Contact No", "Subscription ID",
                                                   "Time In", "Time Out"), show="headings")

        columns = {"First Name": 150, "M.I": 50, "Last Name": 150, "Contact No": 120, "Subscription ID": 120,
                   "Time In": 180, "Time Out": 180}
        for col, width in columns.items():
            self.records_table.heading(col, text=col)
            self.records_table.column(col, width=width, anchor="center")

        self.records_table.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.records_table.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.records_table.configure(yscrollcommand=scrollbar.set)

        self.load_attendance_records()

        back_button = ctk.CTkButton(self, text="Back", fg_color="Red", hover_color="darkred",
                                    command=self.back_button_event)
        back_button.pack(pady=20, side=tk.BOTTOM)

    def load_attendance_records(self):
        for row in self.records_table.get_children():
            self.records_table.delete(row)
        try:
            with sqlite3.connect('SQLite db/attendance_records.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT first_name, middle_name, last_name, contact_no, subscription_id, time_in, time_out FROM attendance_records ORDER BY DATETIME(time_in) DESC')
                for record in cursor.fetchall():
                    self.records_table.insert("", tk.END, values=record)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching attendance records: {e}")

    def back_button_event(self):
        self.destroy()
        self.on_back()