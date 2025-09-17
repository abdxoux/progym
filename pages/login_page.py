import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import ImageTk
import sqlite3
import random
import string
from utils import send_sms_notification, center_window


class LoginPage(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.geometry("400x550")
        self.title("Login")
        self.resizable(False, False)
        center_window(self, 400, 550)

        self.background_image = ImageTk.PhotoImage(file="templates/pat.png")
        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.logo_image = ImageTk.PhotoImage(file="templates/gym_dark.png")
        self.logo_label = ctk.CTkLabel(self, text="", font=("arial", 20), image=self.logo_image, compound=tk.LEFT)
        self.logo_label.pack(pady=20)

        self.frame = ctk.CTkFrame(master=self)
        self.frame.pack(pady=30, padx=40, fill='both', expand=True)

        self.label = ctk.CTkLabel(master=self.frame, text="Login", font=("Arial bold", 18))
        self.label.pack(pady=12, padx=10)

        self.user_entry = ctk.CTkEntry(master=self.frame, placeholder_text="Username")
        self.user_entry.pack(pady=12, padx=10)

        self.user_pass = ctk.CTkEntry(master=self.frame, placeholder_text="Password", show="*")
        self.user_pass.pack(pady=12, padx=10)

        self.show_password_checkbox = ctk.CTkCheckBox(master=self.frame, text='Show Password',
                                                      command=self.toggle_password_visibility)
        self.show_password_checkbox.pack(pady=12, padx=10)

        self.login_button = ctk.CTkButton(master=self.frame, text='Login', command=self.login)
        self.login_button.pack(pady=12, padx=10)

        self.forgot_password_button = ctk.CTkButton(master=self.frame, text='Reset Username & Password?',
                                                    fg_color="Red",
                                                    text_color=("gray10", "gray90"), hover_color=("red3", "red4"),
                                                    command=self.forgot_password)
        self.forgot_password_button.pack(pady=12, padx=10)

    def login(self):
        username = self.user_entry.get()
        password = self.user_pass.get()

        if not username or not password:
            messagebox.showerror(title="Login Failed", message="Please enter both username and password")
            return

        conn = sqlite3.connect('SQLite db/registered_users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = ? AND password = ?', (username, password))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            messagebox.showinfo(title="Login Successful", message="You have logged in Successfully")
            self.on_login_success()
        else:
            messagebox.showerror(title="Login Failed", message="Invalid Username and password")

    def toggle_password_visibility(self):
        if self.user_pass.cget("show") == "":
            self.user_pass.configure(show="*")
        else:
            self.user_pass.configure(show="")

    def is_valid_password(self, password):
        return (
                any(c.isupper() for c in password) and
                any(c.islower() for c in password) and
                any(c.isdigit() for c in password) and
                any(c in string.punctuation for c in password)
        )

    def forgot_password(self):
        otp = ''.join(random.choices(string.digits, k=6))

        while True:
            user_phone_number = simpledialog.askstring('Enter Phone Number',
                                                       'Enter your phone number (e.g., 09123456789):')

            if user_phone_number is None:
                break

            if user_phone_number.startswith('0') and len(user_phone_number) == 11 and user_phone_number[1:].isdigit():
                conn = sqlite3.connect('SQLite db/registered_users.db')
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM accounts WHERE contact_no = ?', (user_phone_number,))
                registered_user = cursor.fetchone()
                conn.close()

                if registered_user:
                    send_sms_notification(user_phone_number, f'Your OTP is: {otp}')
                    entered_otp = simpledialog.askstring('Enter OTP', 'Enter the OTP sent to your phone:', show='*')

                    if entered_otp is None:
                        break

                    if entered_otp == otp:
                        new_username = simpledialog.askstring('New Username', 'Enter your new username:')
                        new_password = simpledialog.askstring('New Password', 'Enter your new password:', show='*')

                        if new_username and new_password:
                            if self.is_valid_password(new_password):
                                conn = sqlite3.connect('SQLite db/registered_users.db')
                                cursor = conn.cursor()
                                cursor.execute('UPDATE accounts SET username = ?, password = ? WHERE contact_no = ?',
                                               (new_username, new_password, user_phone_number))
                                send_sms_notification(user_phone_number,
                                                      f'Your username and password have been reset. Username: {new_username}. Password:{new_password}.')
                                conn.commit()
                                conn.close()
                                messagebox.showinfo('Password Reset Successful',
                                                    'Your password has been reset successfully.')
                            else:
                                messagebox.showerror('Invalid Password', 'Password must meet the specified policy.')
                        else:
                            messagebox.showerror('Error', 'New username and password are required.')
                        break
                    else:
                        messagebox.showerror('Invalid OTP', 'The entered OTP is incorrect.')
                else:
                    messagebox.showerror('Unregistered Phone Number', 'The entered phone number is not registered.')
                    break
            else:
                messagebox.showerror('Invalid Phone Number',
                                     'Please enter a valid phone number starting with 0 and 11 digits long.')