import customtkinter as ctk
import tkinter as tk
import sqlite3
import calendar
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        dashboard_frame = ctk.CTkScrollableFrame(self)
        dashboard_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.create_header(dashboard_frame)
        self.create_panels(dashboard_frame)
        self.create_graphs(dashboard_frame)

    def create_header(self, parent):
        label_frame = ctk.CTkFrame(parent)
        label_frame.pack(pady=5, padx=10, fill="x")

        dashboard_label = ctk.CTkLabel(label_frame, text="Dashboard | Overview", font=("Arial bold", 30))
        dashboard_label.pack(pady=5, padx=10, side=tk.LEFT)

        self.current_time_label = ctk.CTkLabel(label_frame, text="", font=("Agency FB bold", 46))
        self.current_time_label.pack(pady=5, padx=10, side=tk.RIGHT)
        self.update_clock()

    def update_clock(self):
        current_time = datetime.now().strftime("%I:%M:%S %p")
        self.current_time_label.configure(text=current_time)
        self.after(1000, self.update_clock)

    def create_panels(self, parent):
        panel_frame = ctk.CTkFrame(parent)
        panel_frame.pack(pady=5, padx=10, fill="both", expand=True)
        for i in range(5):
            panel_frame.grid_columnconfigure(i, weight=1)

        self.members_counter_label = self.create_info_panel(panel_frame, "Members", 0)
        self.visitor_counter_label = self.create_info_panel(panel_frame, "Gymers", 1)
        self.employee_counter_label = self.create_info_panel(panel_frame, "Employees", 2)
        self.trainer_counter_label = self.create_info_panel(panel_frame, "Trainers", 3)
        self.gym_equipment_counter_label = self.create_info_panel(panel_frame, "Gym Equipment", 4)

        self.update_counts()

    def create_info_panel(self, parent, text, column):
        frame = ctk.CTkFrame(parent, fg_color="#434343")
        frame.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        label = ctk.CTkLabel(frame, text=text, font=("Arial bold", 14))
        label.pack(pady=5, padx=10, anchor="w")
        counter_label = ctk.CTkLabel(frame, text="", font=("Arial bold", 50))
        counter_label.pack(pady=10, padx=10, anchor="center")
        return counter_label

    def update_counts(self):
        self.update_count(self.members_counter_label, 'SQLite db/registration_form.db',
                          "SELECT COUNT(*) FROM registration")
        self.update_count(self.visitor_counter_label, 'SQLite db/visitors_log.db', "SELECT COUNT(*) FROM visitors")
        self.update_count(self.employee_counter_label, 'SQLite db/register_employee.db',
                          "SELECT COUNT(*) FROM employees")
        self.update_count(self.trainer_counter_label, 'SQLite db/register_trainer.db', "SELECT COUNT(*) FROM trainer")
        self.update_count(self.gym_equipment_counter_label, 'SQLite db/register_equipment.db',
                          "SELECT COUNT(*) FROM equipment")
        self.after(1000, self.update_counts)

    def update_count(self, label, db_path, query):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            count = cursor.fetchone()[0]
            label.configure(text=str(count))
            conn.close()
        except Exception as e:
            print(f"Error updating count from {db_path}: {e}")
            label.configure(text="N/A")

    def create_graphs(self, parent):
        graph_frame = ctk.CTkFrame(parent)
        graph_frame.pack(pady=5, padx=10, fill="both", expand=True)
        graph_frame.grid_columnconfigure(0, weight=1)
        graph_frame.grid_columnconfigure(1, weight=1)

        self.create_income_graph(graph_frame, "Membership Monthly Income (PHP)", 0,
                                 self.update_membership_income_report)
        self.create_income_graph(graph_frame, "Gymers Monthly Income (PHP)", 1, self.update_visitors_income_report)

    def create_income_graph(self, parent, title, column, update_func):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")

        label = ctk.CTkLabel(frame, text=title, font=("Arial bold", 16))
        label.pack(pady=5, padx=10, anchor="w")

        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)

        update_func(ax, canvas)

    def update_membership_income_report(self, ax, canvas):
        try:
            conn = sqlite3.connect('SQLite db/registration_form.db')
            cursor = conn.cursor()
            cursor.execute("SELECT strftime('%Y-%m', start_date) as month, COUNT(*) FROM registration GROUP BY month")
            data = cursor.fetchall()
            conn.close()

            processed_data = {month: count * 700 for month, count in data}
            months, incomes = zip(*processed_data.items()) if processed_data else ([], [])
            self.plot_graph(ax, canvas, months, incomes, 'Members', 'green', 'Membership')
        except Exception as e:
            print(f"Error updating membership income: {e}")

        self.after(5000, lambda: self.update_membership_income_report(ax, canvas))

    def update_visitors_income_report(self, ax, canvas):
        try:
            conn = sqlite3.connect('SQLite db/visitors_log.db')
            cursor = conn.cursor()
            cursor.execute("SELECT strftime('%Y-%m', time_start) as month, COUNT(*) FROM visitors GROUP BY month")
            data = cursor.fetchall()
            conn.close()

            processed_data = {month: count * 50 for month, count in data}
            months, incomes = zip(*processed_data.items()) if processed_data else ([], [])
            self.plot_graph(ax, canvas, months, incomes, 'Gymers', 'orange', 'Gymers')
        except Exception as e:
            print(f"Error updating visitors income: {e}")

        self.after(5000, lambda: self.update_visitors_income_report(ax, canvas))

    def plot_graph(self, ax, canvas, months, incomes, label, color, report_type):
        ax.clear()
        if not months:  # Handle case with no data
            ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes)
            canvas.draw()
            return

        current_month_str = datetime.now().strftime('%B %Y')
        bar = ax.bar(np.array(months, dtype=str), incomes, color=color, alpha=0.7, label=label)
        ax.set_ylabel('Income (PHP)')
        ax.set_title(f'Monthly Income Report ({current_month_str})')
        ax.legend()
        ax.grid(True)

        for b, income in zip(bar, incomes):
            ax.text(b.get_x() + b.get_width() / 2, income, f'{income} PHP', ha='center', va='bottom', color='black',
                    fontweight='bold')

        canvas.draw()