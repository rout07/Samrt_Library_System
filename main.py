import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog, messagebox

from student import open_student_window
from admin import open_admin_window

# Theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

ADMIN_PASSWORD = "admin123"     # you can change this anytime


def admin_login():
    """Popup to authenticate admin."""
    pwd = simpledialog.askstring("Admin Login", "Enter admin password:", show="*")

    if pwd is None:
        return  # cancelled

    if pwd == ADMIN_PASSWORD:
        open_admin_window()
    else:
        messagebox.showerror("Error", "Wrong password!")


def main():
    app = ctk.CTk()
    app.title("SmartLibX – Smart Library System")
    app.geometry("480x450")

    # Title
    title = ctk.CTkLabel(
        app,
        text="📚 SmartLibX\nSmart Library & Study Room Manager",
        font=ctk.CTkFont(size=22, weight="bold"),
        justify="center"
    )
    title.pack(pady=40)

    # Student Button
    btn_student = ctk.CTkButton(
        app,
        text="Student Panel",
        width=240,
        height=45,
        fg_color="#1A73E8",
        hover_color="#0F59C8",
        font=ctk.CTkFont(size=15, weight="bold"),
        command=open_student_window
    )
    btn_student.pack(pady=15)

    # Admin Button
    btn_admin = ctk.CTkButton(
        app,
        text="Admin Panel",
        width=240,
        height=45,
        fg_color="#FF6B6B",
        hover_color="#FF4B4B",
        font=ctk.CTkFont(size=15, weight="bold"),
        command=admin_login
    )
    btn_admin.pack(pady=10)

    # Footer
    footer = ctk.CTkLabel(
        app,
        text="Demo Admin Password: admin123",
        font=ctk.CTkFont(size=11),
        text_color="#666"
    )
    footer.pack(side="bottom", pady=15)

    app.mainloop()


if __name__ == "__main__":
    main()
