import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database import get_db
import qrcode
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import os

DATE_FMT = "%Y-%m-%d"

def generate_loan_qr(loan_id: int) -> str:
    data = f"LOAN:{loan_id}"
    img = qrcode.make(data)
    path = os.path.join("qr_codes", f"loan_{loan_id}.png")
    img.save(path)
    return path

def show_qr_window(parent, qr_path, loan_id):
    top = ctk.CTkToplevel(parent)
    top.title("Loan QR Code")
    top.geometry("320x360")

    ctk.CTkLabel(top, text=f"Loan ID: {loan_id}",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    img = Image.open(qr_path)
    img = img.resize((220, 220))
    photo = ImageTk.PhotoImage(img)
    lbl = tk.Label(top, image=photo)
    lbl.image = photo
    lbl.pack(pady=10)

    ctk.CTkLabel(top,
                 text="Show this QR when returning the book.",
                 font=ctk.CTkFont(size=12)).pack(pady=5)

def refresh_book_list(listbox: tk.Listbox, search_text: str = ""):
    conn = get_db()
    c = conn.cursor()

    if search_text.strip():
        like = f"%{search_text.lower()}%"
        c.execute("""
            SELECT id, title, author, category,
                   available_copies, total_copies
            FROM books
            WHERE lower(title) LIKE ?
               OR lower(author) LIKE ?
               OR lower(category) LIKE ?
        """, (like, like, like))
    else:
        c.execute("""
            SELECT id, title, author, category,
                   available_copies, total_copies
            FROM books
        """)

    rows = c.fetchall()
    conn.close()

    listbox.delete(0, tk.END)
    for r in rows:
        text = (f"{r[0]} - {r[1]} | {r[2]} | {r[3]} "
                f"| {r[4]}/{r[5]} available")
        listbox.insert(tk.END, text)

def issue_book(book_id: int, student_name: str, days_str: str, parent):
    if not student_name.strip():
        messagebox.showerror("Error", "Please enter your name.")
        return

    try:
        days = int(days_str)
        if days <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Days must be a positive integer.")
        return

    conn = get_db()
    c = conn.cursor()

    # check availability
    c.execute("SELECT available_copies FROM books WHERE id=?", (book_id,))
    row = c.fetchone()
    if row is None:
        messagebox.showerror("Error", "Invalid book selected.")
        conn.close()
        return

    available = row[0]
    if available <= 0:
        messagebox.showwarning("Not Available",
                               "No copies available for this book.")
        conn.close()
        return

    issue_date = datetime.now().strftime(DATE_FMT)
    due_date = (datetime.now() + timedelta(days=days)).strftime(DATE_FMT)

    # insert loan
    c.execute("""
        INSERT INTO loans(book_id, student_name, days,
                          issue_date, due_date, return_date,
                          status, qr_path)
        VALUES (?,?,?,?,?,?,?,?)
    """, (book_id, student_name, days,
          issue_date, due_date, "", "ISSUED", ""))

    loan_id = c.lastrowid

    # generate QR and update
    qr_path = generate_loan_qr(loan_id)
    c.execute("UPDATE loans SET qr_path=? WHERE id=?", (qr_path, loan_id))

    # decrease availability
    c.execute("UPDATE books SET available_copies = available_copies - 1 "
              "WHERE id=?", (book_id,))

    conn.commit()
    conn.close()

    messagebox.showinfo(
        "Book Issued",
        f"Loan ID: {loan_id}\nIssue Date: {issue_date}\nDue Date: {due_date}"
    )
    show_qr_window(parent, qr_path, loan_id)

def open_book_student_window():
    win = ctk.CTkToplevel()
    win.title("Borrow Books")
    win.geometry("750x520")

    ctk.CTkLabel(win, text="Borrow Books",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    # name + days
    top_frame = ctk.CTkFrame(win)
    top_frame.pack(pady=5, fill="x", padx=20)

    ctk.CTkLabel(top_frame, text="Your Name:", width=90,
                 anchor="w").grid(row=0, column=0, padx=5, pady=5)
    name_entry = ctk.CTkEntry(top_frame, width=220)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(top_frame, text="Days:", width=60,
                 anchor="w").grid(row=0, column=2, padx=5, pady=5)
    days_entry = ctk.CTkEntry(top_frame, width=80)
    days_entry.insert(0, "7")
    days_entry.grid(row=0, column=3, padx=5, pady=5)

    # search box
    search_frame = ctk.CTkFrame(win)
    search_frame.pack(pady=5, fill="x", padx=20)

    ctk.CTkLabel(search_frame, text="Search:",
                 width=70, anchor="w").pack(side="left", padx=5, pady=5)
    search_entry = ctk.CTkEntry(search_frame, width=260)
    search_entry.pack(side="left", padx=5, pady=5)

    def do_search():
        refresh_book_list(book_list, search_entry.get())

    ctk.CTkButton(search_frame, text="Search",
                  width=80, command=do_search).pack(side="left", padx=5)

    # book list
    list_frame = ctk.CTkFrame(win)
    list_frame.pack(pady=5, padx=20, fill="both", expand=True)

    book_list = tk.Listbox(list_frame, width=90, height=14)
    book_list.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=10)

    scroll = tk.Scrollbar(list_frame, orient="vertical",
                          command=book_list.yview)
    scroll.pack(side="right", fill="y", pady=10)
    book_list.config(yscrollcommand=scroll.set)

    refresh_book_list(book_list)

    # buttons
    btn_frame = ctk.CTkFrame(win)
    btn_frame.pack(pady=10)

    ctk.CTkButton(btn_frame, text="Refresh",
                  width=120,
                  command=lambda: refresh_book_list(book_list,
                                                    search_entry.get())
                  ).pack(side="left", padx=10)

    def on_issue():
        try:
            selected = book_list.get(book_list.curselection())
            book_id = int(selected.split(" - ")[0])
        except Exception:
            messagebox.showerror("Error", "Select a book first.")
            return

        issue_book(book_id, name_entry.get(), days_entry.get(), win)

    ctk.CTkButton(btn_frame, text="Issue Selected Book",
                  width=200, command=on_issue).pack(side="left", padx=10)
