# 📚 SmartLibX – Smart Library & Study Room Manager  
A modern **Python + Tkinter + CustomTkinter** based desktop application for managing **Library Books**, **Book Loans**, **Study Room Booking**, **Queue System**, and **QR-Code Based Verification**.

---

## 🚀 Features

### 🔹 **Student Panel**
- Borrow books with automatic **QR code generation**  
- Search books by **title, author, or category**  
- Issue books for custom number of days  
- Automatic **due-date calculation**  
- Book study rooms  
- If rooms are full → automatically added to **queue**

---

### 🔹 **Admin Panel**
- Add rooms with capacity  
- Manage bookings (End / Cancel)  
- View queue list  
- Add books to catalog  
- Track loans (Issued / Returned / Overdue)  
- Automatic overdue detection  
- Fine calculation suggestion  
- View analytics:
  - Room occupancy bar graph  
  - Book-wise loan chart  

---

## 🗂 Project Structure
```
SmartLibX/
│── main.py               # App launcher + admin login
│── student.py            # Student panel + room booking + QR
│── admin.py              # Admin panel + room/booking/queue management
│── book_student.py       # Book borrowing interface for students
│── book_admin.py         # Book catalog & loan management
│── database.py           # SQLite DB setup + tables
│── library.db            # Generated database
│── /qr_codes/            # Auto-generated QR codes saved here
```

---

## 🛠 Technologies Used
- **Python 3**
- **Tkinter**
- **CustomTkinter**
- **SQLite Database**
- **qrcode**  
- **Pillow (PIL)**  
- **Matplotlib**

---

## 📥 Installation & Setup

### 1️⃣ Install Required Libraries
```bash
pip install customtkinter pillow qrcode matplotlib
```

### 2️⃣ Run the App
```bash
python main.py
```

### 3️⃣ Default Admin Password
```
admin123
```

---

## 🔑 How QR Codes Work
- **Room Booking QR** → generated after room booking  
- **Loan QR** → generated after book issue  
- Stored automatically inside `/qr_codes/` folder  
- Used for verification during return/check-in  

---

## 📌 Database Tables
- **rooms** – Room info & occupancy  
- **bookings** – Study room bookings  
- **queue** – Students waiting for rooms  
- **books** – Library catalog  
- **loans** – Issued book records
  
---

## 👨‍💻 Author
**Subham Rout**  
Smart Library Management Project (Python)
