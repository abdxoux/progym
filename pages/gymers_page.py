import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import sqlite3
from datetime import datetime
from utils import send_sms_notification
# Import RegistrationFrame to allow promoting a gymer to a member
from pages.membership_page import RegistrationFrame


class GymersPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_sub_frame = None
        self.create_main_button()

    def create_main_button(self):
        """Creates the initial button on the Gymers page."""
        if self.current_sub_frame:
            self.current_sub_frame.destroy()
            self.current_sub_frame = None

        icons_path = os.path.join(os.path.dirname(__file__), "../templates/frame_6_icons")
        logbook_image_path = os.path.join(icons_path, 'logbook_black.png')

        try:
            logbook_image = ImageTk.PhotoImage(Image.open(logbook_image_path).resize((350, 350), Image.LANCZOS))
        except Exception as e:
            print(f"Error loading image {logbook_image_path}: {e}")
            logbook_image = None

        self.logbook_button = ctk.CTkButton(
            self, text="Gymers Logbook", image=logbook_image, compound=tk.TOP,
            command=self.show_logbook, width=350, height=350,
            fg_color="#00C957", text_color=("gray10", "gray90")
        )
        if logbook_image:
            self.logbook_button.image = logbook_image
        self.logbook_button.place(x=350, y=130)

    def show_logbook(self):
        """Hides the main button and shows the logbook frame."""
        self.logbook_button.destroy()
        self.current_sub_frame = LogbookFrame(self, on_back=self.create_main_button)
        self.current_sub_frame.pack(fill="both", expand=True)


class LogbookFrame(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.create_database_table()

        # Main layout frames
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(pady=10, padx=10, fill="x")
        main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_content_frame.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkLabel(top_frame, text="GYMERS DAILY LOG", font=("Arial bold", 26)).pack()

        # Input Form Frame (Left side)
        form_frame = ctk.CTkFrame(main_content_frame)
        form_frame.grid(row=0, column=0, padx=(0, 10), sticky="ns")
        label_font = ctk.CTkFont(family="Arial bold", size=16)

        self.first_name_entry = self.create_entry(form_frame, "First Name:", "Enter first name", label_font)
        self.middle_name_entry = self.create_entry(form_frame, "Middle Name:", "Enter middle name", label_font)
        self.last_name_entry = self.create_entry(form_frame, "Last Name:", "Enter last name", label_font)
        self.contact_no_entry = self.create_entry(form_frame, "Contact No:", "+63 9...", label_font)

        action_buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        action_buttons_frame.pack(pady=20, fill="x")
        ctk.CTkButton(action_buttons_frame, text="Attend", fg_color="Green", hover_color="darkgreen",
                      command=self.attend_log).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(action_buttons_frame, text="Delete", fg_color="Red", hover_color="darkred",
                      command=self.delete_log).pack(side="right", expand=True, padx=5)

        # Table Frame (Right side)
        table_container_frame = ctk.CTkFrame(main_content_frame)
        table_container_frame.grid(row=0, column=1, sticky="nsew")
        main_content_frame.grid_columnconfigure(1, weight=1)  # Make table expandable

        self.create_table(table_container_frame)
        self.load_data_to_table()

        ctk.CTkButton(self, text="Back", fg_color="Red", hover_color="darkred", command=self.back_button_event).pack(
            pady=(0, 20))

    def create_entry(self, parent, label_text, placeholder, font):
        ctk.CTkLabel(parent, text=label_text, font=font).pack(anchor="w", padx=10, pady=(10, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder)
        entry.pack(fill="x", padx=10, pady=5)
        return entry

    def create_table(self, parent):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=30, fieldbackground="#343638")
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")

        self.table = ttk.Treeview(parent, columns=("First Name", "M.I", "Last Name", "Contact No", "Time Start"),
                                  show="headings", height=10)
        columns = {"First Name": 150, "M.I": 50, "Last Name": 150, "Contact No": 120, "Time Start": 180}
        for col, width in columns.items():
            self.table.heading(col, text=col, anchor="center")
            self.table.column(col, width=width, anchor="center")

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.bind("<Double-1>", self.on_double_click)

    def create_database_table(self):
        with sqlite3.connect('SQLite db/visitors_log.db') as conn:
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS visitors
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             first_name
                             TEXT,
                             middle_name
                             TEXT,
                             last_name
                             TEXT,
                             contact_no
                             TEXT,
                             time_start
                             TEXT
                         )
                         ''')

    def load_data_to_table(self):
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            with sqlite3.connect('SQLite db/visitors_log.db') as conn:
                records = conn.execute(
                    "SELECT first_name, middle_name, last_name, contact_no, time_start FROM visitors ORDER BY time_start DESC").fetchall()
                for record in records:
                    self.table.insert("", "end", values=record)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load data: {e}")

    def on_double_click(self, event):
        item = self.table.focus()
        if not item: return

        data = self.table.item(item, 'values')

        if messagebox.askyesno("Promote to Member", f"Do you want to register {data[0]} {data[2]} as a full member?"):
            self.set_as_member(data)

    def set_as_member(self, data):
        """Destroys this frame and opens the RegistrationFrame with pre-filled data."""
        self.master.destroy()  # Destroy the parent GymersPage frame
        # We assume the controller can show a new page. Let's navigate to membership and pass data.
        # This is a bit of a workaround. A better solution might involve a dedicated controller method.
        # For now, let's create the registration frame directly in the main container.

        main_app_controller = self.winfo_toplevel()  # Get the MainApp instance

        # Find the container frame in MainApp
        container = None
        for child in main_app_controller.winfo_children():
            # Heuristic to find the main container. This might need adjustment.
            if isinstance(child, ctk.CTkFrame) and not hasattr(child, 'navigation_frame_label'):
                container = child
                break

        if container:
            # Clear the container first
            for widget in container.winfo_children():
                widget.destroy()

            # Switch to membership page view and create the registration frame
            main_app_controller.select_frame_by_name("MembershipPage")
            reg_frame = RegistrationFrame(container.master.frames["MembershipPage"], data=data)
            reg_frame.pack(fill="both", expand=True)

    def attend_log(self):
        first, middle, last, contact = self.first_name_entry.get(), self.middle_name_entry.get(), self.last_name_entry.get(), self.contact_no_entry.get()
        if not all([first, last, contact]):
            messagebox.showerror("Validation Error", "First Name, Last Name, and Contact No are required.")
            return

        current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        try:
            with sqlite3.connect('SQLite db/visitors_log.db') as conn:
                conn.execute(
                    'INSERT INTO visitors (first_name, middle_name, last_name, contact_no, time_start) VALUES (?, ?, ?, ?, ?)',
                    (first, middle, last, contact, current_time))

            send_sms_notification(contact,
                                  f"Hello {first}! Thank you for attending D'GRIT GYM. Time In: {current_time}")
            messagebox.showinfo("Success", "Attendance recorded successfully!")
            self.load_data_to_table()
            # Clear entries
            self.first_name_entry.delete(0, tk.END)
            self.middle_name_entry.delete(0, tk.END)
            self.last_name_entry.delete(0, tk.END)
            self.contact_no_entry.delete(0, tk.END)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to record attendance: {e}")

    def delete_log(self):
        selected_item = self.table.focus()
        if not selected_item:
            messagebox.showerror("Delete Error", "Please select a record to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this log entry?"):
            values = self.table.item(selected_item, 'values')
            try:
                with sqlite3.connect('SQLite db/visitors_log.db') as conn:
                    conn.execute("DELETE FROM visitors WHERE first_name=? AND last_name=? AND time_start=?",
                                 (values[0], values[2], values[4]))
                self.load_data_to_table()
                messagebox.showinfo("Success", "Record deleted successfully.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete record: {e}")

    def back_button_event(self):
        self.destroy()
        self.on_back()