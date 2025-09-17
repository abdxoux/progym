import customtkinter as ctk
from pages.login_page import LoginPage
from app import MainApp

# Global appearance settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class AppController:
    def __init__(self):
        self.login_window = None
        self.main_app_window = None
        self.show_login()

    def show_login(self):
        """Displays the login window."""
        if self.main_app_window:
            self.main_app_window.destroy()
            self.main_app_window = None
        self.login_window = LoginPage(on_login_success=self.show_main_app)
        self.login_window.mainloop()

    def show_main_app(self):
        """Displays the main application window after successful login."""
        if self.login_window:
            self.login_window.destroy()
            self.login_window = None
        self.main_app_window = MainApp(on_logout=self.show_login)
        self.main_app_window.mainloop()

if __name__ == "__main__":
    AppController()