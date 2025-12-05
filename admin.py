import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database import get_db
from book_admin import open_book_admin_window     # NEW MODULE
import matplotlib.pyplot as plt
import datetime

# -------------------- Room Management --------------------

def refresh_room_list(listbox: tk.Listbox):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, room_name, capacity, occupied FROM rooms")
    rows = c.fetchall()
    conn.close()

    listbox.delete(0, tk.END)
    for r in rows:
        listbox.insert(tk.END,
                       f"{r[0]} - {r[1]} | {r[3]}/{r[2]} occupied")


def add_room(name, cap):
    if not name or not cap:
        messagebox.showerror("Error", "Enter room name and capacity.")
        return
    try:
        cap = int(cap)
    except:
        messagebox.showerror("Error", "Capacity must be a number.")
        return

    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO rooms(room_name, capacity, occupied) VALUES (?,?,0)",
        (name, cap)
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Room added!")


# -------------------- Bookings & Queue --------------------

def refresh_booking_list(listbox: tk.Listbox):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT b.id, r.room_name, b.student_name, b.status
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        ORDER BY b.id DESC
    """)
    rows = c.fetchall()
    conn.close()

    listbox.delete(0, tk.END)
    for r in rows:
        listbox.insert(
            tk.END,
            f"{r[0]} - Room: {r[1]} | {r[2]} | {r[3]}"
        )


def refresh_queue_list(listbox: tk.Listbox):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT q.id, r.room_name, q.student_name
        FROM queue q
        JOIN rooms r ON q.room_id = r.id
        ORDER BY q.id
    """)
    rows = c.fetchall()
    conn.close()

    listbox.delete(0, tk.END)
    for r in rows:
        listbox.insert(
            tk.END,
            f"{r[0]} - Room: {r[1]} | {r[2]}"
        )


def end_booking(booking_id: int):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT room_id, status FROM bookings WHERE id=?",
              (booking_id,))
    row = c.fetchone()

    if not row:
        messagebox.showerror("Error", "Invalid booking selected.")
        return

    room_id, status = row

    if status != "BOOKED":
        messagebox.showinfo("Message", "Already completed/cancelled.")
        return

    # mark completed
    c.execute("UPDATE bookings SET status='COMPLETED' WHERE id=?", (booking_id,))
    c.execute("UPDATE rooms SET occupied = occupied - 1 WHERE id=?",
              (room_id,))

    # check queue
    c.execute("""
        SELECT id, student_name
        FROM queue
        WHERE room_id=?
        ORDER BY id LIMIT 1
    """, (room_id,))
    q = c.fetchone()

    msg = "Booking ended."

    if q:
        queue_id, student = q
        c.execute("""
            INSERT INTO bookings(room_id, student_name, status, qr_code)
            VALUES (?,?,?,?)
        """, (room_id, student, "BOOKED", ""))

        new_id = c.lastrowid
        c.execute("DELETE FROM queue WHERE id=?", (queue_id,))
        c.execute("UPDATE rooms SET occupied = occupied + 1 WHERE id=?",
                  (room_id,))

        msg += f"\nNext in queue: {student} (Booking ID: {new_id})"

    conn.commit()
    conn.close()
    messagebox.showinfo("Success", msg)


def cancel_booking(booking_id: int):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT room_id, status FROM bookings WHERE id=?",
              (booking_id,))
    row = c.fetchone()

    if not row:
        messagebox.showerror("Error", "Invalid booking ID.")
        return

    room_id, status = row

    if status != "BOOKED":
        messagebox.showinfo("Message", "Booking not active.")
        return

    c.execute("UPDATE bookings SET status='CANCELLED' WHERE id=?", (booking_id,))
    c.execute("UPDATE rooms SET occupied = occupied - 1 WHERE id=?", (room_id,))

    conn.commit()
    conn.close()

    messagebox.showinfo("Done", "Booking cancelled.")


# -------------------- Analytics --------------------

def open_analytics():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM bookings WHERE status='BOOKED'")
    active = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM queue")
    queue = c.fetchone()[0]

    c.execute("SELECT room_name, occupied FROM rooms")
    room_data = c.fetchall()

    conn.close()

    messagebox.showinfo(
        "Summary",
        f"Active Bookings: {active}\nIn Queue: {queue}"
    )

    if room_data:
        rooms = [x[0] for x in room_data]
        occ = [x[1] for x in room_data]

        plt.figure()
        plt.bar(rooms, occ)
        plt.xlabel("Room")
        plt.ylabel("Occupied")
        plt.title("Room Occupancy Chart")
        plt.tight_layout()
        plt.show()


# -------------------- Admin Panel UI --------------------

def open_admin_window():
    win = ctk.CTkToplevel()
    win.title("Admin Panel")
    win.geometry("980x600")

    ctk.CTkLabel(
        win,
        text="Admin Panel",
        font=ctk.CTkFont(size=22, weight="bold")
    ).pack(pady=10)

    # --- Button to open Book Management ---
    ctk.CTkButton(
        win,
        text="📘 Open Book Management",
        width=220,
        fg_color="#4ECDC4",
        hover_color="#38B2AC",
        height=40,
        command=open_book_admin_window
    ).pack(pady=10)

    main_frame = ctk.CTkFrame(win)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- LEFT: Rooms ----------------
    left = ctk.CTkFrame(main_frame)
    left.pack(side="left", fill="y", padx=5, pady=5)

    ctk.CTkLabel(left, text="Add Room", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

    name_entry = ctk.CTkEntry(left, placeholder_text="Room Name")
    name_entry.pack(pady=5)

    cap_entry = ctk.CTkEntry(left, placeholder_text="Capacity")
    cap_entry.pack(pady=5)

    ctk.CTkButton(
        left,
        text="Add Room",
        command=lambda: add_room(name_entry.get(), cap_entry.get())
    ).pack(pady=5)

    ctk.CTkLabel(left, text="Rooms", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)

    room_list = tk.Listbox(left, width=35, height=14)
    room_list.pack(pady=5)
    refresh_room_list(room_list)

    ctk.CTkButton(
        left,
        text="Refresh Rooms",
        command=lambda: refresh_room_list(room_list)
    ).pack(pady=5)

    # CENTER: Bookings
    center = ctk.CTkFrame(main_frame)
    center.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    ctk.CTkLabel(center, text="Bookings", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

    booking_list = tk.Listbox(center, width=60, height=18)
    booking_list.pack(fill="both", expand=True, padx=5, pady=5)
    refresh_booking_list(booking_list)

    btn_frame = ctk.CTkFrame(center)
    btn_frame.pack(pady=10)

    def get_selected_booking():
        try:
            return int(booking_list.get(booking_list.curselection()).split(" - ")[0])
        except:
            messagebox.showerror("Error", "Select a booking.")
            return None

    ctk.CTkButton(btn_frame, text="Refresh",
                  command=lambda: refresh_booking_list(booking_list)).pack(side="left", padx=5)

    ctk.CTkButton(btn_frame, text="End Session",
                  command=lambda: (bid := get_selected_booking()) and end_booking(bid)
                  ).pack(side="left", padx=5)

    ctk.CTkButton(btn_frame, text="Cancel Booking",
                  command=lambda: (bid := get_selected_booking()) and cancel_booking(bid)
                  ).pack(side="left", padx=5)

    # RIGHT: Queue & Analytics
    right = ctk.CTkFrame(main_frame)
    right.pack(side="left", fill="y", padx=5, pady=5)

    ctk.CTkLabel(right, text="Queue", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

    queue_list = tk.Listbox(right, width=35, height=14)
    queue_list.pack(pady=5)
    refresh_queue_list(queue_list)

    ctk.CTkButton(
        right,
        text="Refresh Queue",
        command=lambda: refresh_queue_list(queue_list)
    ).pack(pady=5)

    ctk.CTkLabel(right, text="Analytics", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)

    ctk.CTkButton(
        right,
        text="Open Analytics",
        fg_color="#3498DB",
        hover_color="#2C81BA",
        command=open_analytics
    ).pack(pady=10)
