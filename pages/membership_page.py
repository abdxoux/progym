import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import os
import io
import shutil
import sqlite3
import random
import string
import qrcode
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utils import send_sms_notification


class MembershipPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Define the path to the directory containing your image files
        frame_2_icons = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../templates/frame_2_icons")

        # Load and resize the images
        register_image = self.load_and_resize_image(os.path.join(frame_2_icons, 'register_black.png'), (300, 300))
        view_image = self.load_and_resize_image(os.path.join(frame_2_icons, 'list_black.png'), (300, 300))

        # Create the buttons
        self.create_button("Register Members", register_image, self.register_member, 150, 150)
        self.create_button("View Members", view_image, self.view_member, 600, 150)

    def load_and_resize_image(self, path, size):
        try:
            return ImageTk.PhotoImage(Image.open(path).resize(size, Image.LANCZOS))
        except FileNotFoundError:
            print(f"Error: Image not found at {path}")
            return None

    def create_button(self, text, image, command, x, y):
        button = ctk.CTkButton(
            master=self, text=text, image=image, compound=tk.TOP,
            command=command, width=300, height=300,
            fg_color="#00C957", text_color=("gray10", "gray90")
        )
        button.image = image  # Keep a reference to avoid garbage collection
        button.place(x=x, y=y)

    def register_member(self):
        self.show_frame(RegistrationFrame)

    def view_member(self):
        self.show_frame(ViewFrame)

    def show_frame(self, FrameClass, data=None):
        # Destroys any existing frame before creating a new one
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and not isinstance(widget, ctk.CTkButton):
                widget.destroy()

        if data:
            frame = FrameClass(self, data=data)
        else:
            frame = FrameClass(self)
        frame.pack(fill='both', expand=True)
        # Re-create main buttons if they were destroyed
        if not any(isinstance(w, ctk.CTkButton) and w.cget('text') in ["Register Members", "View Members"] for w in
                   self.winfo_children()):
            self.__init__(self.master, self.controller)


class RegistrationFrame(ctk.CTkFrame):
    def __init__(self, master, data=None, **kwargs):
        super().__init__(master, **kwargs)

        # Create a connection to the database
        self.conn = sqlite3.connect('SQLite db/registration_form.db')
        self.cursor = self.conn.cursor()

        # STEP 1: PERSONAL INFORMATION
        label = ctk.CTkLabel(self, text="D'Grit Gym Membership Registration", font=("Arial bold", 26))
        label.pack(pady=20, padx=10)

        outer_frame = ctk.CTkFrame(self)
        outer_frame.pack(pady=20, padx=10)

        widget_frames = ctk.CTkFrame(outer_frame)
        widget_frames.pack(pady=10, padx=10)

        label_font = ctk.CTkFont(family="Arial bold", size=16)

        # Personal Info Frame
        personal_info_frame = ctk.CTkFrame(widget_frames)
        personal_info_frame.grid(row=0, column=0, padx=10, pady=10)

        self.first_name_entry = self.create_entry(personal_info_frame, "First Name:", "Enter your first name", 2,
                                                  label_font)
        self.middle_name_entry = self.create_entry(personal_info_frame, "Middle Name:", "Enter your middle name", 3,
                                                   label_font)
        self.last_name_entry = self.create_entry(personal_info_frame, "Last Name:", "Enter your last name", 4,
                                                 label_font)

        # If data is provided (from gymers page), populate the entry fields
        if data:
            self.first_name_entry.insert(0, data[0])
            self.middle_name_entry.insert(0, data[1])
            self.last_name_entry.insert(0, data[2])

        # Birth Date and Age
        birth_date_label = ctk.CTkLabel(personal_info_frame, text="Date of Birth:", font=label_font)
        birth_date_label.grid(row=5, column=0, padx=20, pady=5, sticky="w")
        self.birth_date_entry = DateEntry(personal_info_frame, width=20, date_pattern="yyyy-mm-dd")
        self.birth_date_entry.grid(row=5, column=1, padx=20, pady=15, sticky="w")
        self.birth_date_entry.bind("<<DateEntrySelected>>", self.calculate_age)

        self.age_entry = self.create_entry(personal_info_frame, "Age:", "Enter your age", 6, label_font)

        # Sex
        sex_label = ctk.CTkLabel(personal_info_frame, text="Sex:", font=label_font)
        sex_label.grid(row=7, column=0, padx=20, pady=5, sticky="w")
        self.sex_entry = ctk.CTkComboBox(personal_info_frame, values=["Male", "Female", "Other"])
        self.sex_entry.grid(row=7, column=1, padx=20, pady=5)

        self.address_entry = self.create_entry(personal_info_frame, "Address:", "Enter your address", 8, label_font)

        # Contact and Subscription Frame
        contact_sub_frame = ctk.CTkFrame(widget_frames)
        contact_sub_frame.grid(row=0, column=1, padx=10, pady=10)

        # Contact Info
        self.nationality_combo = self.create_combobox(contact_sub_frame, "Nationality:",
                                                      ["Select Nationality", "Filipino", "American", "Chinese",
                                                       "Japanese", "Korean", "Other"], label_font)
        self.contact_no_entry = self.create_entry(contact_sub_frame, "Contact No:", "+63 9123456789", None, label_font,
                                                  pack_instead_of_grid=True)
        self.email_entry = self.create_entry(contact_sub_frame, "Email Address:", "example@gmail.com", None, label_font,
                                             pack_instead_of_grid=True)
        self.emergency_contact_entry = self.create_entry(contact_sub_frame, "Emergency Contact No:", "+63 9123456789",
                                                         None, label_font, pack_instead_of_grid=True)

        # Subscription Info
        subscription_frame = ctk.CTkFrame(widget_frames)
        subscription_frame.grid(row=0, column=2, padx=10, pady=10)

        self.subscription_id_entry = self.create_entry(subscription_frame, "Subscription ID:", "DG-XXXXXXXX", 1,
                                                       label_font)
        self.subscription_id_entry.configure(state="disabled")
        self.set_subscription_id()

        self.subscription_plan_entry = self.create_combobox(subscription_frame, "Subscription Plan:",
                                                            ["Weekly", "Monthly", "Yearly"], label_font, row=2)
        self.subscription_plan_entry.set("Monthly")

        upload_button = ctk.CTkButton(subscription_frame, text="Upload Photo", command=self.upload_photo)
        upload_button.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.uploaded_photo_entry = ctk.CTkEntry(subscription_frame, placeholder_text=".png/.jpg/etc")
        self.uploaded_photo_entry.grid(row=3, column=1, padx=20, pady=10)

        self.user_reference_entry = self.create_entry(subscription_frame, "User Reference:", "User ID or Name", 5,
                                                      label_font)

        # Action Buttons
        register_button = ctk.CTkButton(outer_frame, text="Register", fg_color="Green", text_color=("gray10", "gray90"),
                                        hover_color=("green3", "green4"), command=self.register_subscription)
        register_button.pack(pady=20, side=tk.TOP)

        back_button = ctk.CTkButton(self, text="Back", fg_color="Red", text_color=("gray10", "gray90"),
                                    hover_color=("red3", "red4"), command=self.back_button_event)
        back_button.place(x=450, y=550)

    def create_entry(self, parent, label_text, placeholder, row, font, pack_instead_of_grid=False):
        label = ctk.CTkLabel(parent, text=label_text, font=font)
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder)
        if pack_instead_of_grid:
            label.pack(pady=3, padx=10, anchor="w")
            entry.pack(pady=0, padx=10, fill="x")
        else:
            label.grid(row=row, column=0, padx=20, pady=5, sticky="w")
            entry.grid(row=row, column=1, padx=20, pady=5)
        return entry

    def create_combobox(self, parent, label_text, values, font, row=None):
        label = ctk.CTkLabel(parent, text=label_text, font=font)
        combo = ctk.CTkComboBox(parent, values=values)
        if row is not None:
            label.grid(row=row, column=0, padx=20, pady=10, sticky="w")
            combo.grid(row=row, column=1, padx=20, pady=15)
        else:
            label.pack(pady=5, padx=10, anchor="w")
            combo.pack(pady=5, padx=10, fill="x")
        return combo

    def upload_photo(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select Photo",
                                              filetypes=(("png files", "*.png"), ("jpg files", "*.jpg"),
                                                         ("all files", "*.*")))
        if filename:
            try:
                member_profile_dir = "templates/member_profile"
                os.makedirs(member_profile_dir, exist_ok=True)
                photo_path = os.path.join(member_profile_dir, os.path.basename(filename))
                shutil.copy(filename, photo_path)
                self.uploaded_photo_entry.delete(0, tk.END)
                self.uploaded_photo_entry.insert(0, os.path.basename(photo_path))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload photo: {str(e)}")

    def calculate_age(self, event):
        try:
            birth_date_obj = datetime.strptime(self.birth_date_entry.get(), '%Y-%m-%d')
            age = relativedelta(datetime.now(), birth_date_obj).years
            self.age_entry.delete(0, tk.END)
            self.age_entry.insert(0, str(age))
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter a valid date in the format YYYY-MM-DD.")

    def set_subscription_id(self):
        letters = string.ascii_uppercase + string.digits
        result_str = "DG-" + ''.join(random.choice(letters) for i in range(8))
        self.subscription_id_entry.configure(state="normal")
        self.subscription_id_entry.delete(0, tk.END)
        self.subscription_id_entry.insert(0, result_str)
        self.subscription_id_entry.configure(state="disabled")
        return result_str

    def register_subscription(self):
        # Gather data
        first_name = self.first_name_entry.get()
        # ... gather all other fields
        contact_no = self.contact_no_entry.get()
        subscription_plan = self.subscription_plan_entry.get()
        subscription_id = self.set_subscription_id()

        # Validation
        if not all([first_name, self.last_name_entry.get(), self.age_entry.get(), self.sex_entry.get(),
                    self.birth_date_entry.get(), self.address_entry.get(), self.nationality_combo.get(), contact_no,
                    self.email_entry.get(), self.emergency_contact_entry.get(), subscription_plan,
                    self.user_reference_entry.get(), self.uploaded_photo_entry.get()]):
            messagebox.showerror("Validation Error", "All fields are required.")
            return

        if len(contact_no) != 11 or not contact_no.startswith('0'):
            messagebox.showerror("Validation Error", "Contact No must be a valid 11-digit number starting with 0.")
            return

        # Calculate expiration date
        duration_map = {"Weekly": timedelta(days=7), "Monthly": timedelta(weeks=4), "Yearly": timedelta(weeks=52)}
        duration = duration_map.get(subscription_plan)
        if not duration:
            messagebox.showerror("Validation Error", "Invalid subscription plan.")
            return

        start_date = datetime.now()
        end_date = start_date + duration
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Photo data
        try:
            photo_file_path = os.path.join("templates/member_profile", self.uploaded_photo_entry.get())
            with open(photo_file_path, 'rb') as file:
                photo_data = file.read()
        except Exception as e:
            messagebox.showerror("Photo Error", f"Could not read photo file: {e}")
            return

        # Database insertion
        try:
            self.cursor.execute('''
                                INSERT INTO registration (first_name, middle_name, last_name, age, sex, birth_date,
                                                          address,
                                                          nationality, contact_no, email, emergency_contact_no,
                                                          subscription_id,
                                                          subscription_plan, start_date, end_date, user_reference,
                                                          photo_data)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (first_name, self.middle_name_entry.get(), self.last_name_entry.get(),
                                      self.age_entry.get(), self.sex_entry.get(), self.birth_date_entry.get(),
                                      self.address_entry.get(), self.nationality_combo.get(), contact_no,
                                      self.email_entry.get(), self.emergency_contact_entry.get(), subscription_id,
                                      subscription_plan, start_date_str, end_date_str, self.user_reference_entry.get(),
                                      sqlite3.Binary(photo_data)))
            self.conn.commit()

            self.generate_qr_code(first_name, self.middle_name_entry.get(), self.last_name_entry.get(), contact_no,
                                  subscription_id)

            sms_message = f"Hello {first_name}!, You have Successfully Subscribed for {subscription_plan} Plan. Subscription ID:{subscription_id}. Start Date: {start_date_str} End Date: {end_date_str}, - D'GRIT GYM"
            send_sms_notification(contact_no, sms_message)
            messagebox.showinfo("Registration Successful", "User registered successfully!")
            self.clear_form()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def generate_qr_code(self, first_name, middle_name, last_name, contact_no, subscription_id):
        data_string = f"{first_name},{middle_name},{last_name},{contact_no},{subscription_id}"
        folder_path = "templates/member_qrcodes"
        os.makedirs(folder_path, exist_ok=True)
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(data_string)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        file_path = os.path.join(folder_path, f"dgrit_{last_name}.png")
        qr_img.save(file_path)

    def clear_form(self):
        for entry in [self.first_name_entry, self.middle_name_entry, self.last_name_entry, self.age_entry,
                      self.address_entry, self.contact_no_entry, self.email_entry, self.emergency_contact_entry,
                      self.user_reference_entry, self.uploaded_photo_entry]:
            entry.delete(0, tk.END)
        self.sex_entry.set("")
        self.nationality_combo.set("Select Nationality")
        self.subscription_plan_entry.set("Monthly")
        self.birth_date_entry.set_date(datetime.now())

    def back_button_event(self):
        self.destroy()


class ViewFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.edit_form = None

        label = ctk.CTkLabel(self, text="Gym Members' Information", font=("Arial bold", 28))
        label.pack(pady=20, padx=10)

        # Search Bar
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(pady=10, padx=10, fill="x")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter a name to search")
        self.search_entry.pack(padx=10, pady=10, side="left", fill="x", expand=True)
        ctk.CTkButton(search_frame, text="Search", command=self.search_record).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Clear", command=self.clear_search, fg_color="red",
                      hover_color="darkred").pack(side="left", padx=5)

        # Table
        self.create_table()
        self.refresh_table()

        # Action Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10, padx=10)
        ctk.CTkButton(button_frame, text="View/Edit", command=self.edit_record).pack(padx=10, pady=10)
        ctk.CTkButton(self, text="Back", fg_color="Red", hover_color="darkred", command=self.destroy).pack(pady=5,
                                                                                                           side=tk.TOP)

    def create_table(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=30, fieldbackground="#343638",
                        bordercolor="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        self.table = ttk.Treeview(table_frame, columns=("ID", "First Name", "Middle Name", "Last Name", "Contact No",
                                                        "Subscription ID", "Start Date", "End Date", "Status"),
                                  show="headings", height=10)

        columns = {"ID": 50, "First Name": 120, "Middle Name": 120, "Last Name": 120, "Contact No": 100,
                   "Subscription ID": 120, "Start Date": 100, "End Date": 100, "Status": 80}
        for col, width in columns.items():
            self.table.heading(col, text=col, anchor='center')
            self.table.column(col, width=width, anchor='center')

        self.table.pack(side=tk.LEFT, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.configure(yscrollcommand=scrollbar.set)

    def search_record(self):
        search_term = self.search_entry.get()
        self.refresh_table(search_term)

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.refresh_table()

    def refresh_table(self, search_term=None):
        for row in self.table.get_children():
            self.table.delete(row)

        conn = sqlite3.connect('SQLite db/registration_form.db')
        cursor = conn.cursor()

        query = "SELECT id, first_name, middle_name, last_name, contact_no, subscription_id, start_date, end_date, status FROM registration"
        params = []
        if search_term:
            query += " WHERE first_name LIKE ? OR last_name LIKE ?"
            params.extend([f'%{search_term}%', f'%{search_term}%'])

        cursor.execute(query, params)
        records = cursor.fetchall()
        conn.close()

        for record in records:
            self.table.insert("", tk.END, values=record)

    def edit_record(self):
        selected_item = self.table.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to view/edit.")
            return

        if self.edit_form is None or not self.edit_form.winfo_exists():
            record_data = self.table.item(selected_item)["values"]
            id_value = record_data[0]
            self.edit_form = EditForm(self, id_value, self.table)
        else:
            self.edit_form.lift()


class EditForm(ctk.CTkToplevel):
    def __init__(self, master, id_value, table_reference):
        super().__init__(master)
        self.table = table_reference
        self.id_value = id_value

        self.title("Edit Member Information")
        self.geometry("500x600")
        self.resizable(False, False)
        # Center the window
        self.after(10, lambda: self.geometry(
            f"+{int(self.winfo_screenwidth() / 2 - self.winfo_width() / 2)}+{int(self.winfo_screenheight() / 2 - self.winfo_height() / 2)}"))

        # Database connection
        self.conn = sqlite3.connect('SQLite db/registration_form.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM registration WHERE id=?", (self.id_value,))
        self.member_data = self.cursor.fetchone()

        if not self.member_data:
            messagebox.showerror("Error", "Member not found.")
            self.destroy()
            return

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Photo
        try:
            photo_blob = self.member_data[-1]
            photo_image = Image.open(io.BytesIO(photo_blob)).resize((150, 150), Image.LANCZOS)
            self.photo_ctk_image = ImageTk.PhotoImage(photo_image)
            self.photo_label = ctk.CTkLabel(main_frame, text="", image=self.photo_ctk_image)
            self.photo_label.pack(pady=10)
            ctk.CTkButton(main_frame, text="Change Image", command=self.change_photo).pack()
        except Exception as e:
            print(f"Could not load image: {e}")

        # Scrollable Frame for entries
        edit_frame = ctk.CTkScrollableFrame(main_frame, width=450, height=250)
        edit_frame.pack(pady=10, padx=10, fill="x")

        # Entries
        label_font = ctk.CTkFont(family="Arial", size=14, weight="bold")
        labels = ["First Name", "Middle Name", "Last Name", "Age", "Sex", "Date of Birth", "Address", "Nationality",
                  "Contact No", "Email Address", "Emergency Contact No", "Subscription ID", "Subscription Plan",
                  "Start Date", "End Date", "User Reference", "Status"]
        self.entry_fields = {}
        for i, text in enumerate(labels):
            label = ctk.CTkLabel(edit_frame, text=f"{text}:", font=label_font)
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = ctk.CTkEntry(edit_frame, width=250)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, self.member_data[i + 1])
            self.entry_fields[text] = entry

        # QR Code
        try:
            qr_code_path = os.path.join("templates/member_qrcodes", f"dgrit_{self.member_data[3]}.png")
            qr_image = Image.open(qr_code_path).resize((100, 100), Image.LANCZOS)
            self.qr_ctk_image = ImageTk.PhotoImage(qr_image)
            qr_label = ctk.CTkLabel(edit_frame, text="", image=self.qr_ctk_image)
            qr_label.grid(row=len(labels), column=0, columnspan=2, pady=10)
            ctk.CTkButton(edit_frame, text="Download QR", command=self.download_qr_code).grid(row=len(labels) + 1,
                                                                                              column=0, columnspan=2)
        except Exception as e:
            print(f"Could not load QR code: {e}")

        # Action Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="Update", command=self.update_record).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Delete", fg_color="red", hover_color="darkred",
                      command=self.delete_record).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Renew", fg_color="blue", hover_color="darkblue",
                      command=self.renew_membership).pack(side="left", padx=5)

    def change_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            with open(file_path, 'rb') as file:
                photo_data = file.read()
            self.cursor.execute("UPDATE registration SET photo_data = ? WHERE id = ?",
                                (sqlite3.Binary(photo_data), self.id_value))
            self.conn.commit()

            # Update displayed image
            photo_image = Image.open(io.BytesIO(photo_data)).resize((150, 150), Image.LANCZOS)
            self.photo_ctk_image = ImageTk.PhotoImage(photo_image)
            self.photo_label.configure(image=self.photo_ctk_image)
            messagebox.showinfo("Success", "Photo updated successfully.")

    def download_qr_code(self):
        qr_code_path = os.path.join("templates/member_qrcodes", f"dgrit_{self.member_data[3]}.png")
        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 initialfile=f"dgrit_{self.member_data[3]}.png",
                                                 filetypes=[("PNG files", "*.png")])
        if save_path:
            shutil.copy(qr_code_path, save_path)
            messagebox.showinfo("Download Successful", f"QR Code saved to {save_path}")

    def update_record(self):
        updated_data = [entry.get() for entry in self.entry_fields.values()]

        try:
            self.cursor.execute('''
                                UPDATE registration
                                SET first_name=?,
                                    middle_name=?,
                                    last_name=?,
                                    age=?,
                                    sex=?,
                                    birth_date=?,
                                    address=?,
                                    nationality=?,
                                    contact_no=?,
                                    email=?,
                                    emergency_contact_no=?,
                                    subscription_id=?,
                                    subscription_plan=?,
                                    start_date=?,
                                    end_date=?,
                                    user_reference=?,
                                    status=?
                                WHERE id = ?
                                ''', (*updated_data, self.id_value))
            self.conn.commit()
            messagebox.showinfo("Success", "Record updated successfully.")
            self.master.refresh_table()
            self.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating record: {e}")

    def delete_record(self):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            try:
                self.cursor.execute("DELETE FROM registration WHERE id=?", (self.id_value,))
                self.conn.commit()
                messagebox.showinfo("Success", "Record deleted successfully.")
                self.master.refresh_table()
                self.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error deleting record: {e}")

    def renew_membership(self):
        self.withdraw()  # Hide the current window
        RenewSubscriptionFrame(self, self.id_value, self.table)

    def __del__(self):
        # Ensure the connection is closed when the window is destroyed
        if self.conn:
            self.conn.close()


class RenewSubscriptionFrame(ctk.CTkToplevel):
    def __init__(self, master, id_value, table_reference):
        super().__init__(master)
        self.table = table_reference
        self.id_value = id_value
        self.parent_edit_form = master

        self.title("Renew Membership")
        self.geometry("400x350")
        self.resizable(False, False)
        self.after(10, lambda: self.geometry(
            f"+{int(self.winfo_screenwidth() / 2 - self.winfo_width() / 2)}+{int(self.winfo_screenheight() / 2 - self.winfo_height() / 2)}"))

        # Fetch data
        conn = sqlite3.connect('SQLite db/registration_form.db')
        cursor = conn.cursor()
        cursor.execute("SELECT first_name, contact_no, subscription_plan, end_date FROM registration WHERE id=?",
                       (self.id_value,))
        member_data = cursor.fetchone()
        conn.close()

        if not member_data:
            messagebox.showerror("Error", "Member not found.")
            self.destroy()
            return

        self.first_name, self.contact_no, old_plan, old_end_date = member_data

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text=f"Renewing for: {self.first_name}", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkLabel(main_frame, text=f"Current Expiry: {old_end_date}").pack()

        ctk.CTkLabel(main_frame, text="Select New Plan:").pack(pady=(20, 5))
        self.plan_var = ctk.StringVar(value=old_plan)
        self.plan_menu = ctk.CTkOptionMenu(main_frame, variable=self.plan_var, values=["Weekly", "Monthly", "Yearly"])
        self.plan_menu.pack()

        ctk.CTkButton(main_frame, text="Renew Subscription", command=self.process_renewal).pack(pady=20)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def process_renewal(self):
        new_plan = self.plan_var.get()
        duration_map = {"Weekly": timedelta(days=7), "Monthly": relativedelta(months=1),
                        "Yearly": relativedelta(years=1)}

        # Start renewal from today
        start_date = datetime.now()
        end_date = start_date + duration_map[new_plan]

        try:
            conn = sqlite3.connect('SQLite db/registration_form.db')
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE registration SET subscription_plan=?, start_date=?, end_date=?, status='Ongoing' WHERE id=?",
                (new_plan, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), self.id_value))
            conn.commit()
            conn.close()

            sms_message = f"Hello {self.first_name}!, Your subscription has been renewed. Your new expiry date is {end_date.strftime('%Y-%m-%d')}."
            send_sms_notification(self.contact_no, sms_message)
            messagebox.showinfo("Success", "Subscription renewed successfully.")

            # Refresh the table in the main view and close windows
            self.table.master.master.refresh_table()
            self.on_close()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to renew subscription: {e}")

    def on_close(self):
        self.parent_edit_form.deiconify()  # Show the parent EditForm again
        self.destroy()