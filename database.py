import sqlite3
import os

DB_NAME = "library.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def setup():
    os.makedirs("qr_codes", exist_ok=True)

    conn = get_db()
    c = conn.cursor()

    # ---- existing tables for rooms & queues ----
    c.execute("""
        CREATE TABLE IF NOT EXISTS rooms(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT,
            capacity INTEGER,
            occupied INTEGER DEFAULT 0
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER,
            student_name TEXT,
            status TEXT,
            qr_code TEXT
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS queue(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER,
            student_name TEXT
        );
    """)

    # ---- NEW: books & loans ----
    c.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            category TEXT,
            total_copies INTEGER,
            available_copies INTEGER,
            qr_path TEXT
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS loans(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            student_name TEXT,
            days INTEGER,
            issue_date TEXT,
            due_date TEXT,
            return_date TEXT,
            status TEXT,
            qr_path TEXT
        );
    """)

    conn.commit()
    conn.close()

setup()

