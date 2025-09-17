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


class TrainersPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_sub_frame = None
        self.create_main_buttons()

    def create_main_buttons(self):
        if self.current_sub_frame:
            self.current_sub_frame.destroy()
            self.current_sub_frame = None

        icons_path = os.path.join(os.path.dirname(__file__), "../templates/frame_5_icons")
        register_image = self.load_image(os.path.join(icons_path, 'trainer_black.png'))
        view_image = self.load_image(os.path.join(icons_path, 'list_black.png'))
        attendance_image = self.load_image(os.path.join(icons_path, 'scan_black.png'))

        self.register_button = self.create_button("Register Trainer", register_image, self.show_register_frame, 100)
        self.view_button = self.create_button("View Trainer Records", view_image, self.show_view_frame, 400)
        self.attendance_button = self.create_button("Trainer Attendance", attendance_image, self.show_attendance_frame,
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
        button.image = image
        button.place(x=x_pos, y=180)
        return button

    def clear_main_buttons(self):
        self.register_button.destroy()
        self.view_button.destroy()
        self.attendance_button.destroy()

    def show_register_frame(self):
        self.clear_main_buttons()
        self.current_sub_frame = TrainerRegistrationFrame(self, on_back=self.create_main_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)

    def show_view_frame(self):
        self.clear_main_buttons()
        self.current_sub_frame = ViewTrainerFrame(self, on_back=self.create_main_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)

    def show_attendance_frame(self):
        self.clear_main_buttons()
        self.current_sub_frame = TrainerAttendanceFrame(self, on_back=self.create_main_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)


class TrainerRegistrationFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.create_database_table()

        label = ctk.CTkLabel(self, text="Register Trainer", font=("Arial bold", 26))
        label.pack(pady=20, padx=10)

        outer_frame = ctk.CTkFrame(self)
        outer_frame.pack(pady=20, padx=10)

        widget_frames = ctk.CTkFrame(outer_frame)
        widget_frames.pack(pady=5, padx=10)

        label_font = ctk.CTkFont(family="Arial bold", size=16)

        # Personal Info Frame
        personal_info_frame = ctk.CTkFrame(widget_frames)
        personal_info_frame.grid(row=0, column=0, padx=10, pady=5)
        self.first_name_entry = self.create_entry(personal_info_frame, "First Name:", "Enter first name", 2, label_font)
        self.middle_name_entry = self.create_entry(personal_info_frame, "Middle Name:", "Enter middle name", 3,
                                                   label_font)
        self.last_name_entry = self.create_entry(personal_info_frame, "Last Name:", "Enter last name", 4, label_font)

        birth_date_label = ctk.CTkLabel(personal_info_frame, text="Date of Birth:", font=label_font)
        birth_date_label.grid(row=5, column=0, padx=20, pady=5, sticky="w")
        self.birth_date_entry = DateEntry(personal_info_frame, width=20, date_pattern="yyyy-mm-dd")
        self.birth_date_entry.grid(row=5, column=1, padx=20, pady=15, sticky="w")
        self.birth_date_entry.bind("<<DateEntrySelected>>", self.calculate_age)

        self.age_entry = self.create_entry(personal_info_frame, "Age:", "Calculated age", 6, label_font)
        self.sex_entry = self.create_combobox(personal_info_frame, "Sex:", ["Male", "Female", "Other"], 7, label_font)
        self.address_entry = self.create_entry(personal_info_frame, "Address:", "Enter address", 8, label_font)

        # Contact Info Frame
        contact_frame = ctk.CTkFrame(widget_frames)
        contact_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ns")
        self.nationality_combo = self.create_combobox(contact_frame, "Nationality:", ["Filipino", "American", "Other"],
                                                      0, label_font, use_pack=True)
        self.contact_no_entry = self.create_entry(contact_frame, "Contact No:", "+639...", None, label_font,
                                                  use_pack=True)
        self.emergency_contact_entry = self.create_entry(contact_frame, "Emergency No:", "+639...", None, label_font,
                                                         use_pack=True)

        upload_button = ctk.CTkButton(contact_frame, text="Upload Photo", command=self.upload_trainer_photo)
        upload_button.pack(pady=10, padx=10, fill="x")
        self.uploaded_photo_entry = ctk.CTkEntry(contact_frame, placeholder_text="photo.png/jpg")
        self.uploaded_photo_entry.pack(pady=5, padx=10, fill="x")

        # Buttons
        register_button = ctk.CTkButton(outer_frame, text="Register", fg_color="Green", hover_color="darkgreen",
                                        command=self.register_trainer)
        register_button.pack(pady=15)
        back_button = ctk.CTkButton(self, text="Back", fg_color="Red", hover_color="darkred", command=self.on_back)
        back_button.pack(pady=10)

    def create_entry(self, parent, text, placeholder, row, font, use_pack=False):
        label = ctk.CTkLabel(parent, text=text, font=font)
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder)
        if use_pack:
            label.pack(anchor="w", padx=10, pady=(10, 0))
            entry.pack(fill="x", padx=10, pady=5)
        else:
            label.grid(row=row, column=0, padx=20, pady=5, sticky="w")
            entry.grid(row=row, column=1, padx=20, pady=5)
        return entry

    def create_combobox(self, parent, text, values, row, font, use_pack=False):
        label = ctk.CTkLabel(parent, text=text, font=font)
        combo = ctk.CTkComboBox(parent, values=values)
        if use_pack:
            label.pack(anchor="w", padx=10, pady=(10, 0))
            combo.pack(fill="x", padx=10, pady=5)
        else:
            label.grid(row=row, column=0, padx=20, pady=5, sticky="w")
            combo.grid(row=row, column=1, padx=20, pady=5)
        return combo

    def create_database_table(self):
        with sqlite3.connect('SQLite db/register_trainer.db') as conn:
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS trainer
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

    def calculate_age(self, event=None):
        try:
            birth_date = datetime.strptime(self.birth_date_entry.get(), '%Y-%m-%d')
            age = relativedelta(datetime.now(), birth_date).years
            self.age_entry.delete(0, tk.END)
            self.age_entry.insert(0, str(age))
        except (ValueError, TypeError):
            pass

    def upload_trainer_photo(self):
        filename = filedialog.askopenfilename(title="Select Photo",
                                              filetypes=(("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")))
        if filename:
            try:
                dest_dir = "templates/trainer_profile"
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, os.path.basename(filename))
                shutil.copy(filename, dest_path)
                self.uploaded_photo_entry.delete(0, tk.END)
                self.uploaded_photo_entry.insert(0, os.path.basename(dest_path))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload photo: {e}")

    def register_trainer(self):
        try:
            with open(os.path.join("templates/trainer_profile", self.uploaded_photo_entry.get()), 'rb') as f:
                photo_data = f.read()
        except (FileNotFoundError, Exception) as e:
            messagebox.showerror("File Error", f"Could not read photo file. Please upload a photo. Error: {e}")
            return

        trainer_data = (
            self.first_name_entry.get(), self.middle_name_entry.get(), self.last_name_entry.get(),
            self.age_entry.get(), self.sex_entry.get(), self.birth_date_entry.get(),
            self.address_entry.get(), self.nationality_combo.get(), self.contact_no_entry.get(),
            self.emergency_contact_entry.get(), 'Active', photo_data
        )

        if not all(trainer_data[:9]):
            messagebox.showerror("Validation Error", "Please fill all required fields.")
            return

        try:
            with sqlite3.connect('SQLite db/register_trainer.db') as conn:
                conn.execute('''
                             INSERT INTO trainer (first_name, middle_name, last_name, age, sex, birth_date,
                                                  address, nationality, contact_no, emergency_contact_no, status,
                                                  photo_data)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                             ''', trainer_data)

            self.generate_trainer_qr(trainer_data[0], trainer_data[1], trainer_data[2], trainer_data[8])
            send_sms_notification(trainer_data[8],
                                  f"Hello {trainer_data[0]}! You are now registered as a Trainer at D'GRIT Gym.")
            messagebox.showinfo("Success", "Trainer registered successfully!")
            self.master.on_back()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This contact number is already registered.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def generate_trainer_qr(self, first, middle, last, contact):
        qr_data = f"{first},{middle},{last},{contact}"
        folder_path = "templates/trainer_qrcodes"
        os.makedirs(folder_path, exist_ok=True)
        qr = qrcode.make(qr_data)
        qr.save(os.path.join(folder_path, f"dgrit_trainer_{last}.png"))


class ViewTrainerFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.edit_window = None

        label = ctk.CTkLabel(self, text="Trainer Information", font=("Arial bold", 28))
        label.pack(pady=20, padx=10)

        search_frame = ctk.CTkFrame(self)
        search_frame.pack(pady=10, padx=10, fill="x")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by name...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(search_frame, text="Search", command=self.search_record).pack(side="left")
        ctk.CTkButton(search_frame, text="Clear", fg_color="red", hover_color="darkred",
                      command=self.clear_search).pack(side="left", padx=5)

        self.create_table()
        self.refresh_table()

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="View / Edit", command=self.edit_record).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Back", fg_color="red", hover_color="darkred", command=self.on_back).pack(
            side="left", padx=10)

    def create_table(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=30, fieldbackground="#343638")
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")

        self.table = ttk.Treeview(table_frame,
                                  columns=("ID", "First Name", "Last Name", "Age", "Sex", "Contact No", "Status"),
                                  show="headings")
        columns = {"ID": 50, "First Name": 200, "Last Name": 200, "Age": 80, "Sex": 100, "Contact No": 150,
                   "Status": 120}
        for col, width in columns.items():
            self.table.heading(col, text=col, anchor="center")
            self.table.column(col, width=width, anchor="center")

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)

    def refresh_table(self, search_term=None):
        for item in self.table.get_children():
            self.table.delete(item)
        with sqlite3.connect('SQLite db/register_trainer.db') as conn:
            cursor = conn.cursor()
            query = "SELECT id, first_name, last_name, age, sex, contact_no, status FROM trainer"
            params = []
            if search_term:
                query += " WHERE first_name LIKE ? OR last_name LIKE ?"
                params.extend([f'%{search_term}%', f'%{search_term}%'])
            cursor.execute(query, params)
            for row in cursor.fetchall():
                self.table.insert("", "end", values=row)

    def search_record(self):
        self.refresh_table(self.search_entry.get())

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.refresh_table()

    def edit_record(self):
        selected_item = self.table.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a trainer to edit.")
            return
        record_id = self.table.item(selected_item)['values'][0]

        if self.edit_window is None or not self.edit_window.winfo_exists():
            self.edit_window = EditTrainerForm(self, record_id, on_close=self.refresh_table)
        else:
            self.edit_window.lift()


class EditTrainerForm(ctk.CTkToplevel):
    def __init__(self, master, record_id, on_close):
        super().__init__(master)
        self.record_id = record_id
        self.on_close_callback = on_close

        self.title("Edit Trainer Info")
        self.geometry("500x600")

        with sqlite3.connect('SQLite db/register_trainer.db') as conn:
            self.data = conn.execute("SELECT * FROM trainer WHERE id=?", (self.record_id,)).fetchone()

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        try:
            photo = Image.open(io.BytesIO(self.data[-1])).resize((150, 150), Image.LANCZOS)
            self.photo_img = ImageTk.PhotoImage(photo)
            self.photo_label = ctk.CTkLabel(main_frame, image=self.photo_img, text="")
            self.photo_label.pack(pady=10)
        except:
            self.photo_label = ctk.CTkLabel(main_frame, text="No Image")
            self.photo_label.pack(pady=10)

        ctk.CTkButton(main_frame, text="Change Photo", command=self.change_photo).pack()

        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=250)
        scroll_frame.pack(fill="x", pady=10)

        self.entries = {}
        fields = ["First Name", "Middle Name", "Last Name", "Age", "Sex", "Birth Date", "Address", "Nationality",
                  "Contact No", "Emergency No", "Status"]
        for i, field in enumerate(fields):
            label = ctk.CTkLabel(scroll_frame, text=f"{field}:", font=("Arial", 14, "bold"))
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
            if field == "Status":
                self.entries[field] = ctk.CTkComboBox(scroll_frame, values=["Active", "Inactive", "On Leave"],
                                                      width=250)
                self.entries[field].set(self.data[i + 1])
            else:
                self.entries[field] = ctk.CTkEntry(scroll_frame, width=250)
                self.entries[field].insert(0, self.data[i + 1])
            self.entries[field].grid(row=i, column=1, padx=10, pady=5)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="Update", command=self.update_record).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Delete", fg_color="red", hover_color="darkred",
                      command=self.delete_record).pack(side="left", padx=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def change_photo(self):
        # Implementation for changing photo, similar to registration
        pass

    def update_record(self):
        # Implementation for updating the record in the database
        pass

    def delete_record(self):
        # Implementation for deleting the record from the database
        pass

    def on_close(self):
        self.on_close_callback()
        self.destroy()


class TrainerAttendanceFrame(ctk.CTkFrame):
    # This class will be a placeholder or can be implemented fully
    # similar to AttendancePage but for trainers. For brevity, I'll
    # create a simplified version.
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        label = ctk.CTkLabel(self, text="Trainer Attendance - Coming Soon", font=("Arial", 24))
        label.pack(pady=100)
        ctk.CTkButton(self, text="Back", command=self.on_back, fg_color="red").pack()