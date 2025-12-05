import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database import get_db
from book_student import open_book_student_window   # NEW BOOK MODULE
import qrcode
from PIL import Image, ImageTk
import os

# ------------------ Room Booking Section ------------------

def refresh_rooms(listbox: tk.Listbox):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, room_name, occupied, capacity FROM rooms")
    rooms = c.fetchall()
    conn.close()

    listbox.delete(0, tk.END)
    for r in rooms:
        status = f"{r[0]} - {r[1]} | {r[2]}/{r[3]} occupied"
        listbox.insert(tk.END, status)


def generate_room_qr(booking_id: int) -> str:
    data = f"ROOMBOOKING:{booking_id}"
    img = qrcode.make(data)
    path = os.path.join("qr_codes", f"room_booking_{booking_id}.png")
    img.save(path)
    return path


def show_room_qr(parent, qr_path, booking_id):
    win = ctk.CTkToplevel(parent)
    win.title("Room Booking QR")
    win.geometry("310x360")

    ctk.CTkLabel(win,
                 text=f"Booking ID: {booking_id}",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    img = Image.open(qr_path).resize((220, 220))
    photo = ImageTk.PhotoImage(img)
    lbl = tk.Label(win, image=photo)
    lbl.image = photo
    lbl.pack(pady=10)

    ctk.CTkLabel(win, text="Show this QR at entry.",
                 font=ctk.CTkFont(size=12)).pack(pady=10)


def book_room(room_id: int, student_name: str, parent_window):
    if student_name.strip() == "":
        messagebox.showerror("Error", "Enter your name!")
        return

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT capacity, occupied FROM rooms WHERE id=?", (room_id,))
    row = c.fetchone()

    if not row:
        messagebox.showerror("Error", "Invalid room selected.")
        conn.close()
        return

    capacity, occupied = row

    # If available
    if occupied < capacity:
        c.execute("""
            INSERT INTO bookings(room_id, student_name, status, qr_code)
            VALUES (?,?,?,?)
        """, (room_id, student_name, "BOOKED", ""))

        booking_id = c.lastrowid

        qr_path = generate_room_qr(booking_id)
        c.execute("UPDATE bookings SET qr_code=? WHERE id=?",
                  (qr_path, booking_id))

        c.execute("UPDATE rooms SET occupied = occupied + 1 WHERE id=?",
                  (room_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Room booked successfully!")
        show_room_qr(parent_window, qr_path, booking_id)

    else:
        # Add to queue
        c.execute("INSERT INTO queue(room_id, student_name) VALUES (?,?)",
                  (room_id, student_name))
        conn.commit()
        conn.close()
        messagebox.showwarning("Full", "Room is full. Added to queue.")


# ------------------ Main Student Panel ------------------

def open_student_window():
    win = ctk.CTkToplevel()
    win.title("Student Panel")
    win.geometry("520x580")

    ctk.CTkLabel(
        win,
        text="Student Panel",
        font=ctk.CTkFont(size=22, weight="bold")
    ).pack(pady=10)

    # Name entry
    name_frame = ctk.CTkFrame(win)
    name_frame.pack(pady=10, padx=20, fill="x")

    ctk.CTkLabel(name_frame, text="Your Name:", width=90).pack(side="left", padx=5)
    name_entry = ctk.CTkEntry(name_frame, width=260)
    name_entry.pack(side="left", padx=5)

    # Borrow Books button (NEW)
    ctk.CTkButton(
        win,
        text="📘 Borrow Books (Advanced)",
        fg_color="#4ECDC4",
        hover_color="#38B2AC",
        width=260,
        height=40,
        command=open_book_student_window
    ).pack(pady=10)

    # Room booking section
    ctk.CTkLabel(
        win,
        text="Book Study Room",
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=5)

    list_frame = ctk.CTkFrame(win)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    room_list = tk.Listbox(list_frame, width=55, height=12)
    room_list.pack(side="left", fill="both", expand=True, padx=(5, 0))

    scroll = tk.Scrollbar(list_frame, orient="vertical",
                          command=room_list.yview)
    scroll.pack(side="right", fill="y")
    room_list.config(yscrollcommand=scroll.set)

    refresh_rooms(room_list)

    btn_frame = ctk.CTkFrame(win)
    btn_frame.pack(pady=15)

    ctk.CTkButton(btn_frame, text="Refresh Rooms",
                  width=160,
                  command=lambda: refresh_rooms(room_list)
                  ).pack(side="left", padx=10)

    def on_book():
        try:
            selected = room_list.get(room_list.curselection())
            room_id = int(selected.split(" - ")[0])
        except:
            messagebox.showerror("Error", "Select a room.")
            return

        book_room(room_id, name_entry.get(), win)

    ctk.CTkButton(btn_frame, text="Book Selected Room",
                  fg_color="#1A73E8",
                  hover_color="#0F59C8",
                  width=180,
                  command=on_book).pack(side="left", padx=10)
