import customtkinter as ctk

class AppearanceManager:
    """Handle theme and appearance settings for the application."""

    def __init__(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

    def change_mode(self, new_appearance_mode: str) -> None:
        """Update the global appearance mode."""
        ctk.set_appearance_mode(new_appearance_mode)
