import customtkinter as ctk
import os
from PIL import Image
from utils import change_appearance_mode_event
from pages.home_page import HomePage
from pages.membership_page import MembershipPage
from pages.attendance_page import AttendancePage
from pages.equipment_page import EquipmentPage
from pages.trainers_page import TrainersPage
from pages.gymers_page import GymersPage
from pages.employees_page import EmployeesPage
from pages.user_account_page import UserAccountPage


class MainApp(ctk.CTk):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout = on_logout

        # Fixed size of the window, and cannot be resized
        self.resizable(False, False)
        self.title("D'Grit Gym")
        self.geometry("1240x600")

        # Calculate the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the position to center the window
        x = (screen_width - 1240) // 2
        y = (screen_height - 600) // 2.5

        # Set the window's position
        self.geometry(f"1240x600+{int(x)}+{int(y)}")

        # Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Load images
        self.load_images()

        # Create navigation frame
        self.create_navigation_frame()

        # Create frames dictionary to hold all pages
        self.frames = {}

        container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        container.grid(row=0, column=1, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Instantiate all pages
        for F in (HomePage, MembershipPage, AttendancePage, EquipmentPage, TrainersPage, GymersPage, EmployeesPage,
                  UserAccountPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Select default frame
        self.select_frame_by_name("HomePage")

    def load_images(self):
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates/test_images")
        self.logo_image = ctk.CTkImage(
            dark_image=Image.open(os.path.join(image_path, "gym_dark.png")),
            size=(150, 60))
        self.home_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "home_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.add_user_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))
        self.attendance_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "scan_black.png")),
            dark_image=Image.open(os.path.join(image_path, "scan_white.png")), size=(20, 20))
        self.add_equipment_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "dumbell_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "dumbell_light.png")), size=(20, 20))
        self.trainer_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "trainer_black.png")),
            dark_image=Image.open(os.path.join(image_path, "trainer_white.png")), size=(20, 20))
        self.visitor_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "visitor_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "visitor_light.png")), size=(20, 20))
        self.employee_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "employee_black.png")),
            dark_image=Image.open(os.path.join(image_path, "employee_white.png")), size=(20, 20))

    def create_navigation_frame(self):
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(12, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(
            self.navigation_frame, text="", image=self.logo_image,
            compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=50, border_spacing=10,
            text="Home", fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"), image=self.home_image, anchor="w",
            command=lambda: self.select_frame_by_name("HomePage"))
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=50, border_spacing=10,
            text="Membership", fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"), image=self.add_user_image, anchor="w",
            command=lambda: self.select_frame_by_name("MembershipPage"))
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=50, border_spacing=10,
            text="Take Attendance", fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"), image=self.attendance_image, anchor="w",
            command=lambda: self.select_frame_by_name("AttendancePage"))
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.frame_4_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=50, border_spacing=10,
            text="Gym Equipment", fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"), image=self.add_equipment_image, anchor="w",
            command=lambda: self.select_frame_by_name("EquipmentPage"))
        self.frame_4_button.grid(row=4, column=0, sticky="ew")

        self.frame_5_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=50, border_spacing=10,
            text="Trainers", fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"), image=self.trainer_image, anchor="w",
            command=lambda: self.select_frame_by_name("TrainersPage"))
        self.frame_5_button.grid(row=5, column=0, sticky="ew")

        self.frame_6_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=50, border_spacing=10,
            text="Gymers", fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"), image=self.visitor_image, anchor="w",
            command=lambda: self.select_frame_by_name("GymersPage"))
        self.frame_6_button.grid(row=6, column=0, sticky="ew")

        self.frame_7_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=50, border_spacing=10,
            text="Employees", fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"), image=self.employee_image, anchor="w",
            command=lambda: self.select_frame_by_name("EmployeesPage"))
        self.frame_7_button.grid(row=7, column=0, sticky="ew")

        self.frame_8_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=50, border_spacing=10,
            text="Create User Account", fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"), image=self.add_user_image, anchor="w",
            command=lambda: self.select_frame_by_name("UserAccountPage"))
        self.frame_8_button.grid(row=8, column=0, sticky="ew")

        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self.navigation_frame, values=["Dark", "Light"],
            command=change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=10, column=0, padx=20, pady=10, sticky="s")

        self.logout_button = ctk.CTkButton(
            self.navigation_frame, text="Logout", fg_color="Red", text_color=("gray10", "gray90"),
            hover_color=("red3", "red4"), command=self.logout)
        self.logout_button.grid(row=11, column=0, padx=20, pady=5, sticky="ew")

    def select_frame_by_name(self, page_name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if page_name == "HomePage" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if page_name == "MembershipPage" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if page_name == "AttendancePage" else "transparent")
        self.frame_4_button.configure(fg_color=("gray75", "gray25") if page_name == "EquipmentPage" else "transparent")
        self.frame_5_button.configure(fg_color=("gray75", "gray25") if page_name == "TrainersPage" else "transparent")
        self.frame_6_button.configure(fg_color=("gray75", "gray25") if page_name == "GymersPage" else "transparent")
        self.frame_7_button.configure(fg_color=("gray75", "gray25") if page_name == "EmployeesPage" else "transparent")
        self.frame_8_button.configure(
            fg_color=("gray75", "gray25") if page_name == "UserAccountPage" else "transparent")

        # show selected frame
        frame = self.frames[page_name]
        frame.tkraise()

    def logout(self):
        self.on_logout()