import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import sqlite3


class EquipmentPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_sub_frame = None
        self.create_main_buttons()

    def create_main_buttons(self):
        if self.current_sub_frame:
            self.current_sub_frame.destroy()
            self.current_sub_frame = None

        icons_path = os.path.join(os.path.dirname(__file__), "../templates/frame_4_icons")
        register_image = self.load_image(os.path.join(icons_path, 'dumbell_dark.png'))
        view_image = self.load_image(os.path.join(icons_path, 'list_black.png'))

        self.register_button = self.create_button("Register Equipment", register_image, self.show_register_frame, 150)
        self.view_button = self.create_button("View Equipment Records", view_image, self.show_records_frame, 600)

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
        button.image = image
        button.place(x=x_pos, y=150)
        return button

    def clear_main_buttons(self):
        self.register_button.destroy()
        self.view_button.destroy()

    def show_register_frame(self):
        self.clear_main_buttons()
        self.current_sub_frame = RegistrationEquipment(self, on_back=self.create_main_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)

    def show_records_frame(self):
        self.clear_main_buttons()
        self.current_sub_frame = EquipmentRecords(self, on_back=self.create_main_buttons)
        self.current_sub_frame.pack(fill="both", expand=True)


class RegistrationEquipment(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.create_database_table()

        outer_frame = ctk.CTkFrame(self)
        outer_frame.pack(padx=20, pady=20, expand=True)

        label_font = ctk.CTkFont(family="Arial bold", size=16)

        # Left Frame for entries
        left_frame = ctk.CTkFrame(outer_frame)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        ctk.CTkLabel(left_frame, text="Equipment Details", font=("Arial bold", 18)).pack(anchor="w", padx=10,
                                                                                         pady=(10, 20))
        self.equipment_name_entry = self.create_entry(left_frame, "Equipment Name:", "Description", label_font)
        self.equipment_brand_entry = self.create_entry(left_frame, "Brand:", "Brand/Manufacturer", label_font)
        self.equipment_model_entry = self.create_entry(left_frame, "Model:", "Model/Year", label_font)
        self.equipment_serial_number_entry = self.create_entry(left_frame, "Serial No:", "Serial Number", label_font)
        self.equipment_quantity_entry = self.create_entry(left_frame, "Quantity:", "Quantity", label_font)

        # Right Frame for comboboxes
        right_frame = ctk.CTkFrame(outer_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")
        self.equipment_condition_entry = self.create_combobox(right_frame, "Condition:", ["New", "Used", "Damaged"],
                                                              label_font)
        self.equipment_type_entry = self.create_combobox(right_frame, "Type:",
                                                         ["Cardio", "Strength", "Endurance", "Flexibility", "Others"],
                                                         label_font)
        self.equipment_status_entry = self.create_combobox(right_frame, "Status:",
                                                           ["Available", "Unavailable", "Under Maintenance"],
                                                           label_font)
        self.equipment_location_entry = self.create_combobox(right_frame, "Location:",
                                                             ["First Floor", "Second Floor", "Third Floor"], label_font)
        self.equipment_training_required_entry = self.create_combobox(right_frame, "Training Required:", ["Yes", "No"],
                                                                      label_font)

        # Action Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Register", fg_color="Green", hover_color="darkgreen",
                      command=self.register_equipment_info).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Back", fg_color="Red", hover_color="darkred",
                      command=self.back_button_event).pack(side="left", padx=10)

    def create_entry(self, parent, label_text, placeholder, font):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)
        label = ctk.CTkLabel(frame, text=label_text, font=font, width=150, anchor="w")
        label.pack(side="left")
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, width=200)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def create_combobox(self, parent, label_text, values, font):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)
        label = ctk.CTkLabel(frame, text=label_text, font=font, width=150, anchor="w")
        label.pack(side="left")
        combo = ctk.CTkComboBox(frame, values=values, width=200)
        combo.pack(side="left", fill="x", expand=True)
        return combo

    def create_database_table(self):
        with sqlite3.connect('SQLite db/register_equipment.db') as conn:
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS equipment
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             equipment_name
                             TEXT
                             NOT
                             NULL,
                             equipment_brand
                             TEXT,
                             equipment_model
                             TEXT,
                             equipment_serial_number
                             TEXT
                             UNIQUE,
                             equipment_quantity
                             INTEGER,
                             equipment_condition
                             TEXT,
                             equipment_type
                             TEXT,
                             equipment_status
                             TEXT,
                             equipment_location
                             TEXT,
                             equipment_training_required
                             TEXT
                         )
                         ''')

    def register_equipment_info(self):
        data = (
            self.equipment_name_entry.get(), self.equipment_brand_entry.get(),
            self.equipment_model_entry.get(), self.equipment_serial_number_entry.get(),
            self.equipment_quantity_entry.get(), self.equipment_condition_entry.get(),
            self.equipment_type_entry.get(), self.equipment_status_entry.get(),
            self.equipment_location_entry.get(), self.equipment_training_required_entry.get()
        )
        if not all(data[:1] + data[4:]):  # Check required fields
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            with sqlite3.connect('SQLite db/register_equipment.db') as conn:
                conn.execute('''
                             INSERT INTO equipment (equipment_name, equipment_brand, equipment_model,
                                                    equipment_serial_number,
                                                    equipment_quantity, equipment_condition, equipment_type,
                                                    equipment_status,
                                                    equipment_location, equipment_training_required)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                             ''', data)
            messagebox.showinfo("Success", "Equipment registered successfully!")
            self.clear_form()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Serial number already exists.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def clear_form(self):
        for entry in [self.equipment_name_entry, self.equipment_brand_entry, self.equipment_model_entry,
                      self.equipment_serial_number_entry, self.equipment_quantity_entry]:
            entry.delete(0, tk.END)
        for combo in [self.equipment_condition_entry, self.equipment_type_entry, self.equipment_status_entry,
                      self.equipment_location_entry, self.equipment_training_required_entry]:
            combo.set("")

    def back_button_event(self):
        self.destroy()
        self.on_back()


class EquipmentRecords(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.on_back = on_back
        self.edit_window = None

        label = ctk.CTkLabel(self, text="Gym Equipment Inventory", font=("Arial bold", 28))
        label.pack(pady=20, padx=10)

        search_frame = ctk.CTkFrame(self)
        search_frame.pack(pady=10, padx=10, fill="x")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by equipment name...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(search_frame, text="Search", command=self.search_record).pack(side="left")
        ctk.CTkButton(search_frame, text="Clear", fg_color="red", hover_color="darkred",
                      command=self.clear_search).pack(side="left", padx=5)

        self.create_table()
        self.refresh_table()

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="View / Edit", command=self.edit_record).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Back", fg_color="red", hover_color="darkred",
                      command=self.back_button_event).pack(side="left", padx=10)

    def create_table(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=30, fieldbackground="#343638")
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")

        self.table = ttk.Treeview(table_frame,
                                  columns=("ID", "Name", "Brand", "Quantity", "Type", "Status", "Location"),
                                  show="headings")
        columns = {"ID": 50, "Name": 200, "Brand": 150, "Quantity": 80, "Type": 120, "Status": 120, "Location": 120}
        for col, width in columns.items():
            self.table.heading(col, text=col)
            self.table.column(col, width=width, anchor="center")

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)

    def refresh_table(self, search_term=None):
        for item in self.table.get_children():
            self.table.delete(item)

        with sqlite3.connect('SQLite db/register_equipment.db') as conn:
            cursor = conn.cursor()
            query = "SELECT id, equipment_name, equipment_brand, equipment_quantity, equipment_type, equipment_status, equipment_location FROM equipment"
            params = []
            if search_term:
                query += " WHERE equipment_name LIKE ?"
                params.append(f'%{search_term}%')
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
            messagebox.showwarning("Selection Error", "Please select an item to edit.")
            return

        if self.edit_window is None or not self.edit_window.winfo_exists():
            item_values = self.table.item(selected_item)['values']
            record_id = item_values[0]
            self.edit_window = EditRecord(self, record_id, on_close=self.refresh_table)
        else:
            self.edit_window.lift()

    def back_button_event(self):
        self.destroy()
        self.on_back()


class EditRecord(ctk.CTkToplevel):
    def __init__(self, master, record_id, on_close):
        super().__init__(master)
        self.record_id = record_id
        self.on_close_callback = on_close

        self.title("Edit Equipment")
        self.geometry("450x550")
        self.resizable(False, False)

        with sqlite3.connect('SQLite db/register_equipment.db') as conn:
            self.data = conn.execute("SELECT * FROM equipment WHERE id=?", (self.record_id,)).fetchone()

        if not self.data:
            messagebox.showerror("Error", "Record not found.")
            self.destroy()
            return

        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        label_font = ctk.CTkFont(family="Arial bold", size=14)

        self.entries = {}
        fields = ["Equipment Name", "Brand", "Model", "Serial No", "Quantity", "Condition", "Type", "Status",
                  "Location", "Training Required"]
        for i, field in enumerate(fields):
            self.entries[field] = self.create_entry(main_frame, f"{field}:", self.data[i + 1], label_font, i)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="Update", command=self.update_record).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Delete", fg_color="red", hover_color="darkred",
                      command=self.delete_record).pack(side="left", padx=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_entry(self, parent, label_text, value, font, row):
        label = ctk.CTkLabel(parent, text=label_text, font=font)
        label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        entry = ctk.CTkEntry(parent, width=250)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        entry.insert(0, value if value is not None else "")
        return entry

    def update_record(self):
        updated_values = [self.entries[field].get() for field in self.entries]
        try:
            with sqlite3.connect('SQLite db/register_equipment.db') as conn:
                conn.execute('''
                             UPDATE equipment
                             SET equipment_name=?,
                                 equipment_brand=?,
                                 equipment_model=?,
                                 equipment_serial_number=?,
                                 equipment_quantity=?,
                                 equipment_condition=?,
                                 equipment_type=?,
                                 equipment_status=?,
                                 equipment_location=?,
                                 equipment_training_required=?
                             WHERE id = ?
                             ''', (*updated_values, self.record_id))
            messagebox.showinfo("Success", "Record updated successfully.")
            self.on_close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update: {e}")

    def delete_record(self):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this equipment record?"):
            try:
                with sqlite3.connect('SQLite db/register_equipment.db') as conn:
                    conn.execute("DELETE FROM equipment WHERE id=?", (self.record_id,))
                messagebox.showinfo("Success", "Record deleted.")
                self.on_close()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete: {e}")

    def on_close(self):
        self.on_close_callback()
        self.destroy()