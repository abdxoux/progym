import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from utils import send_sms_notification


class UserAccountPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create the main frame for account management, centered
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(pady=20, padx=20, expand=True)

        # Add a title label
        ctk.CTkLabel(form_frame, text="Create New User Account", font=("Arial Bold", 24)).pack(pady=25, padx=10)

        # Create a frame for input fields
        fields_frame = ctk.CTkFrame(form_frame)
        fields_frame.pack(pady=20, padx=20)

        label_font = ctk.CTkFont(family="Arial bold", size=16)

        # Create and place labels and entry widgets
        self.full_name_entry = self.create_labeled_entry(fields_frame, "Full Name:", "Enter user's full name", 0,
                                                         label_font)
        self.contact_no_entry = self.create_labeled_entry(fields_frame, "Contact No:", "e.g., 09123456789", 1,
                                                          label_font)
        self.username_entry = self.create_labeled_entry(fields_frame, "Username:", "Enter a new username", 2,
                                                        label_font)
        self.password_entry = self.create_labeled_entry(fields_frame, "Password:", "Enter a new password", 3,
                                                        label_font, show="*")

        # Create button
        register_button = ctk.CTkButton(form_frame, text="Create Account", command=self.register_account)
        register_button.pack(pady=20, padx=10)

        self.create_database_table()

    def create_labeled_entry(self, parent, text, placeholder, row, font, show=None):
        """Helper function to create a label and an entry widget."""
        label = ctk.CTkLabel(parent, text=text, font=font)
        label.grid(row=row, column=0, padx=20, pady=15, sticky="w")
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, show=show, width=250)
        entry.grid(row=row, column=1, padx=20, pady=15, sticky="ew")
        return entry

    def create_database_table(self):
        """Ensures the accounts table exists in the database."""
        try:
            with sqlite3.connect('SQLite db/registered_users.db') as conn:
                conn.execute('''
                             CREATE TABLE IF NOT EXISTS accounts
                             (
                                 id
                                 INTEGER
                                 PRIMARY
                                 KEY,
                                 full_name
                                 TEXT,
                                 contact_no
                                 TEXT
                                 UNIQUE,
                                 username
                                 TEXT
                                 NOT
                                 NULL
                                 UNIQUE,
                                 password
                                 TEXT
                                 NOT
                                 NULL
                             )
                             ''')
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to create table: {e}")

    def is_valid(self, username, password):
        """
        Validates the username and password policy.
        - Username and Password must be at least 8 characters.
        - Must contain a mix of uppercase, lowercase letters, and numbers/symbols.
        """
        if len(username) < 8 or len(password) < 8:
            messagebox.showerror("Invalid Data", "Username and Password must be at least 8 characters long.")
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit_or_symbol = any(not c.isalpha() for c in password)

        if not (has_upper and has_lower and has_digit_or_symbol):
            messagebox.showerror("Invalid Password",
                                 "Password must contain uppercase, lowercase letters, and at least one number or symbol.")
            return False

        return True

    def register_account(self):
        full_name = self.full_name_entry.get()
        contact_no = self.contact_no_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not all([full_name, contact_no, username, password]):
            messagebox.showerror("Invalid Data", "All fields are required.")
            return

        if not (contact_no.startswith('0') and len(contact_no) == 11 and contact_no.isdigit()):
            messagebox.showerror("Invalid Contact Number",
                                 "Please enter a valid 11-digit phone number starting with 0.")
            return

        if not self.is_valid(username, password):
            # The is_valid method already shows a specific error message
            return

        try:
            with sqlite3.connect('SQLite db/registered_users.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO accounts (full_name, contact_no, username, password) VALUES (?, ?, ?, ?)',
                               (full_name, contact_no, username, password))

            # Send notification and show success message
            send_sms_notification(contact_no,
                                  f"Hello {full_name}! A user account has been created for you for the D'GRIT GYM system.")
            messagebox.showinfo("Registration Successful", "The user account has been registered successfully.")

            # Clear the entry fields
            self.full_name_entry.delete(0, 'end')
            self.contact_no_entry.delete(0, 'end')
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')

        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Error",
                                 "This username or contact number already exists. Please choose a different one.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred during registration: {e}")