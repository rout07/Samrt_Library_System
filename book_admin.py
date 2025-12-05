import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database import get_db
from datetime import datetime
import matplotlib.pyplot as plt

DATE_FMT = "%Y-%m-%d"

# ----- books -----

def add_book(title, author, category, total_str):
    if not title.strip() or not author.strip() or not total_str.strip():
        messagebox.showerror("Error", "Fill Title, Author and Total copies.")
        return

    try:
        total = int(total_str)
        if total <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Total copies must be a positive integer.")
        return

    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO books(title, author, category,
                          total_copies, available_copies, qr_path)
        VALUES (?,?,?,?,?,?)
    """, (title, author, category, total, total, ""))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Book added to catalog.")

def refresh_book_list(listbox: tk.Listbox):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT id, title, author, category,
               available_copies, total_copies
        FROM books
    """)
    rows = c.fetchall()
    conn.close()

    listbox.delete(0, tk.END)
    for r in rows:
        listbox.insert(
            tk.END,
            f"{r[0]} - {r[1]} | {r[2]} | {r[3]} "
            f"| {r[4]}/{r[5]} available"
        )

# ----- loans -----

def refresh_loan_list(listbox: tk.Listbox):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT l.id, b.title, l.student_name,
               l.issue_date, l.due_date, l.return_date, l.status
        FROM loans l
        JOIN books b ON l.book_id = b.id
        ORDER BY l.id DESC
    """)
    rows = c.fetchall()
    conn.close()

    listbox.delete(0, tk.END)
    today = datetime.now().strftime(DATE_FMT)

    for r in rows:
        status = r[6]
        # mark overdue
        if status == "ISSUED" and r[4] < today:
            status = "OVERDUE"
        text = (f"{r[0]} - {r[1]} | {r[2]} | "
                f"Issue:{r[3]} | Due:{r[4]} | "
                f"Return:{r[5] or '-'} | {status}")
        listbox.insert(tk.END, text)

def mark_return(loan_id: int):
    today = datetime.now().strftime(DATE_FMT)
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT book_id, status, due_date FROM loans WHERE id=?",
              (loan_id,))
    row = c.fetchone()
    if row is None:
        messagebox.showerror("Error", "Invalid Loan ID.")
        conn.close()
        return

    book_id, status, due_date = row
    if status != "ISSUED":
        messagebox.showinfo("Info", "Loan already returned or closed.")
        conn.close()
        return

    c.execute("""
        UPDATE loans
        SET status='RETURNED', return_date=?
        WHERE id=?
    """, (today, loan_id))

    c.execute("""
        UPDATE books
        SET available_copies = available_copies + 1
        WHERE id=?
    """, (book_id,))

    conn.commit()
    conn.close()

    days_late = (datetime.strptime(today, DATE_FMT) -
                 datetime.strptime(due_date, DATE_FMT)).days
    if days_late > 0:
        fine = days_late * 10      # ₹10 per day example
        messagebox.showinfo(
            "Returned",
            f"Book returned.\nLate by {days_late} days.\nSuggested fine: ₹{fine}"
        )
    else:
        messagebox.showinfo("Returned", "Book returned on time.")

# ----- analytics -----

def show_book_analytics():
    conn = get_db()
    c = conn.cursor()

    # count issued / returned / overdue
    c.execute("SELECT COUNT(*) FROM loans WHERE status='ISSUED'")
    issued = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM loans WHERE status='RETURNED'")
    returned = c.fetchone()[0]

    # overdue
    today = datetime.now().strftime(DATE_FMT)
    c.execute("""
        SELECT COUNT(*)
        FROM loans
        WHERE status='ISSUED' AND due_date < ?
    """, (today,))
    overdue = c.fetchone()[0]

    # count per book
    c.execute("""
        SELECT b.title, COUNT(l.id)
        FROM books b
        LEFT JOIN loans l ON l.book_id = b.id
        GROUP BY b.id
    """)
    per_book = c.fetchall()
    conn.close()

    summary = (f"Currently Issued: {issued}\n"
               f"Returned: {returned}\n"
               f"Overdue: {overdue}")
    messagebox.showinfo("Book Analytics", summary)

    if per_book:
        titles = [x[0] for x in per_book]
        counts = [x[1] for x in per_book]
        plt.figure()
        plt.bar(titles, counts)
        plt.title("Loans per Book")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

# ----- main window -----

def open_book_admin_window():
    win = ctk.CTkToplevel()
    win.title("Book Management")
    win.geometry("950x550")

    ctk.CTkLabel(win, text="Book Catalog & Loans",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    main = ctk.CTkFrame(win)
    main.pack(fill="both", expand=True, padx=10, pady=10)

    # left: add books + list
    left = ctk.CTkFrame(main)
    left.pack(side="left", fill="y", padx=10, pady=10)

    ctk.CTkLabel(left, text="Add Book",
                 font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

    title_entry = ctk.CTkEntry(left, placeholder_text="Title")
    title_entry.pack(pady=4)

    author_entry = ctk.CTkEntry(left, placeholder_text="Author")
    author_entry.pack(pady=4)

    cat_entry = ctk.CTkEntry(left, placeholder_text="Category (e.g. CS, Novel)")
    cat_entry.pack(pady=4)

    total_entry = ctk.CTkEntry(left, placeholder_text="Total copies")
    total_entry.pack(pady=4)

    ctk.CTkButton(left, text="Add to Catalog",
                  command=lambda: add_book(
                      title_entry.get(),
                      author_entry.get(),
                      cat_entry.get(),
                      total_entry.get())
                  ).pack(pady=6)

    ctk.CTkLabel(left, text="All Books",
                 font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(15, 4))

    book_list = tk.Listbox(left, width=40, height=18)
    book_list.pack(pady=5)
    refresh_book_list(book_list)

    ctk.CTkButton(left, text="Refresh Books",
                  command=lambda: refresh_book_list(book_list)
                  ).pack(pady=5)

    # center: loans
    center = ctk.CTkFrame(main)
    center.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(center, text="Loans (Issued / Returned)",
                 font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

    loan_list = tk.Listbox(center, width=70, height=20)
    loan_list.pack(pady=5, fill="both", expand=True)
    refresh_loan_list(loan_list)

    btn_center = ctk.CTkFrame(center)
    btn_center.pack(pady=6)

    def get_selected_loan_id():
        try:
            sel = loan_list.get(loan_list.curselection())
            return int(sel.split(" - ")[0])
        except Exception:
            messagebox.showerror("Error", "Select a loan first.")
            return None

    ctk.CTkButton(btn_center, text="Refresh",
                  width=100,
                  command=lambda: refresh_loan_list(loan_list)
                  ).pack(side="left", padx=6)

    ctk.CTkButton(btn_center, text="Mark Returned",
                  width=140,
                  command=lambda: (lid := get_selected_loan_id()) and mark_return(lid)
                  ).pack(side="left", padx=6)

    # right: analytics
    right = ctk.CTkFrame(main)
    right.pack(side="left", fill="y", padx=10, pady=10)

    ctk.CTkLabel(right, text="Analytics",
                 font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

    ctk.CTkButton(right, text="Show Book Analytics",
                  width=180, height=40,
                  fg_color="#4ECDC4",
                  hover_color="#38B2AC",
                  command=show_book_analytics).pack(pady=10)