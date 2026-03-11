import mysql.connector
from mysql.connector import Error
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import csv

# --- DESIGN SYSTEM ---
COLORS = {
    "bg_dark": "#1a1a1a",
    "bg_sidebar": "#222222",
    "accent": "#3b82f6",  # Royal Blue
    "accent_hover": "#2563eb",
    "text_main": "#ffffff",
    "text_secondary": "#a1a1aa",
    "card_bg": "#2d2d2d",
    "success": "#22c55e",
    "error": "#ef4444",
    "warning": "#f59e0b"
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- DATABASE CONFIG ---
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "littlelamb08"
DB_NAME = "hostel_db"

def get_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except Error as e:
        messagebox.showerror("Database Connection Error", f"Could not connect to database.\nError: {e}")
        return None

def initialize_database():
    try:
        conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_number INT PRIMARY KEY,
                capacity INT NOT NULL,
                occupancy INT DEFAULT 0,
                status VARCHAR(20) DEFAULT 'Available'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                contact VARCHAR(50)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS allocations (
                allocation_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                room_number INT,
                monthly_rent DECIMAL(10,2) DEFAULT 0.00,
                fee_paid BOOLEAN DEFAULT FALSE,
                allocation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (room_number) REFERENCES rooms(room_number) ON DELETE CASCADE
            )
        """)
        
        # Migrations for existing tables
        cursor.execute("SHOW COLUMNS FROM rooms LIKE 'status'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE rooms ADD COLUMN status VARCHAR(20) DEFAULT 'Available'")
            
        cursor.execute("SHOW COLUMNS FROM allocations LIKE 'monthly_rent'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE allocations ADD COLUMN monthly_rent DECIMAL(10,2) DEFAULT 0.00")
            cursor.execute("ALTER TABLE allocations ADD COLUMN fee_paid BOOLEAN DEFAULT FALSE")
            
        conn.commit()
    except Error as e:
        print(f"Error initializing DB: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

class StatCard(ctk.CTkFrame):
    def __init__(self, master, title, value, color, icon="📊"):
        super().__init__(master, fg_color=COLORS["card_bg"], corner_radius=15, border_width=1, border_color="#3d3d3d")
        
        self.grid_columnconfigure(0, weight=1)
        
        self.lbl_icon = ctk.CTkLabel(self, text=icon, font=ctk.CTkFont(size=30))
        self.lbl_icon.pack(pady=(15, 0))
        
        self.lbl_title = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=14, weight="normal"), text_color=COLORS["text_secondary"])
        self.lbl_title.pack(pady=(5, 0))
        
        self.lbl_value = ctk.CTkLabel(self, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=color)
        self.lbl_value.pack(pady=(0, 15))

    def update_value(self, new_value):
        self.lbl_value.configure(text=new_value)

class HostelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Premium Hostel Management System")
        self.geometry("1100x750")
        self.configure(fg_color=COLORS["bg_dark"])
        
        initialize_database()

        # Layout Setup
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLORS["bg_sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="HOSTEL PRO", font=ctk.CTkFont(size=22, weight="bold"), text_color=COLORS["accent"])
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 40))

        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "🏠", "dashboard"),
            ("Add Room", "🏢", "rooms"),
            ("Register Student", "🎓", "students"),
            ("Allocate", "🔑", "allocations"),
            ("View Allocs", "📋", "view"),
            ("Billing", "💰", "billing"),
            ("Rooms List", "🛏️", "view_rooms")
        ]

        for i, (text, icon, name) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar, 
                text=f"  {icon}  {text}", 
                anchor="w",
                font=ctk.CTkFont(size=14, weight="normal"),
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color="#333333",
                height=45,
                command=lambda n=name: self.select_tab(n)
            )
            btn.grid(row=i+1, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[name] = btn

        # Appearance Menu
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar, values=["Dark", "Light", "System"],
            command=self.change_appearance_mode_event,
            fg_color="#333333", button_color="#444444"
        )
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # --- Main Content Area ---
        self.main_container = ctk.CTkFrame(self, corner_radius=20, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Tab Frames
        self.tabs = {
            "dashboard": self.build_dashboard(),
            "rooms": self.build_rooms_form(),
            "students": self.build_students_form(),
            "allocations": self.build_allocations_form(),
            "view": self.build_allocations_view(),
            "billing": self.build_billing_view(),
            "view_rooms": self.build_rooms_view()
        }

        self.select_tab("dashboard")

    def select_tab(self, name):
        for k, frame in self.tabs.items():
            frame.grid_forget()
            self.nav_buttons[k].configure(fg_color="transparent", text_color=COLORS["text_secondary"])
            
        self.tabs[name].grid(row=0, column=0, sticky="nsew")
        self.nav_buttons[name].configure(fg_color=COLORS["accent"], text_color=COLORS["text_main"])
        
        # Refresh logic
        if name == "dashboard": self.refresh_dashboard()
        elif name == "view": self.refresh_allocations_list()
        elif name == "view_rooms": self.refresh_rooms_list()
        elif name == "billing": self.refresh_billing_list()
        elif name == "allocations": self.refresh_dropdowns()

    def change_appearance_mode_event(self, new_mode):
        ctk.set_appearance_mode(new_mode)

    # --- UI BUILDERS ---
    def build_dashboard(self):
        f = ctk.CTkFrame(self.main_container, fg_color="transparent")
        f.grid_columnconfigure((0,1,2), weight=1)
        
        header = ctk.CTkLabel(f, text="Welcome back, Manager", font=ctk.CTkFont(size=28, weight="bold"))
        header.grid(row=0, column=0, columnspan=3, pady=(0, 30), sticky="w")
        
        self.stat_total_rooms = StatCard(f, "Total Rooms", "0", COLORS["accent"], "🏢")
        self.stat_total_rooms.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.stat_occupancy = StatCard(f, "Occupancy", "0/0", COLORS["success"], "📈")
        self.stat_occupancy.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        self.stat_students = StatCard(f, "Students", "0", COLORS["warning"], "🎓")
        self.stat_students.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.stat_fees = StatCard(f, "Pending Fees", "0", COLORS["error"], "💰")
        self.stat_fees.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Quick Actions or Recent Activity could go here
        action_frame = ctk.CTkFrame(f, fg_color=COLORS["card_bg"], corner_radius=15)
        action_frame.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="nsew")
        action_lbl = ctk.CTkLabel(action_frame, text="Quick Overview", font=ctk.CTkFont(size=18, weight="bold"))
        action_lbl.pack(pady=20, padx=20, anchor="w")
        
        self.dash_info_lbl = ctk.CTkLabel(action_frame, text="Loading statistics...", font=ctk.CTkFont(size=14), text_color=COLORS["text_secondary"])
        self.dash_info_lbl.pack(pady=(0, 20), padx=20, anchor="w")
        
        return f

    def build_rooms_form(self):
        f = ctk.CTkFrame(self.main_container, fg_color=COLORS["card_bg"], corner_radius=20)
        
        ctk.CTkLabel(f, text="🏢 Add New Hostel Room", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=40)
        
        self.ent_room_no = ctk.CTkEntry(f, placeholder_text="Room Number (e.g. 101)", width=350, height=50, corner_radius=10)
        self.ent_room_no.pack(pady=15)
        
        self.ent_room_cap = ctk.CTkEntry(f, placeholder_text="Maximum Capacity", width=350, height=50, corner_radius=10)
        self.ent_room_cap.pack(pady=15)

        self.room_status_var = ctk.StringVar(value="Available")
        self.opt_room_status = ctk.CTkOptionMenu(f, variable=self.room_status_var, values=["Available", "Maintenance", "Inactive"], 
                                               width=350, height=50, fg_color="#3d3d3d", button_color="#4d4d4d")
        self.opt_room_status.pack(pady=15)
        
        btn = ctk.CTkButton(f, text="Save Room", width=350, height=50, corner_radius=10, font=ctk.CTkFont(weight="bold"), 
                           fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], command=self.add_room_action)
        btn.pack(pady=40)
        
        return f

    def build_students_form(self):
        f = ctk.CTkFrame(self.main_container, fg_color=COLORS["card_bg"], corner_radius=20)
        
        ctk.CTkLabel(f, text="🎓 Register New Student", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=40)
        
        self.ent_stud_name = ctk.CTkEntry(f, placeholder_text="Full Student Name", width=350, height=50, corner_radius=10)
        self.ent_stud_name.pack(pady=15)
        
        self.ent_stud_contact = ctk.CTkEntry(f, placeholder_text="Contact Number / Email", width=350, height=50, corner_radius=10)
        self.ent_stud_contact.pack(pady=15)
        
        btn = ctk.CTkButton(f, text="Register Student", width=350, height=50, corner_radius=10, font=ctk.CTkFont(weight="bold"),
                           fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], command=self.add_student_action)
        btn.pack(pady=40)
        
        return f

    def build_allocations_form(self):
        f = ctk.CTkFrame(self.main_container, fg_color=COLORS["card_bg"], corner_radius=20)
        
        ctk.CTkLabel(f, text="🔑 Allocate Room to Student", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=40)
        
        self.student_var = ctk.StringVar(value="Select Student")
        self.opt_student = ctk.CTkOptionMenu(f, variable=self.student_var, values=["Select Student"], width=350, height=50, 
                                            fg_color="#3d3d3d", button_color="#4d4d4d")
        self.opt_student.pack(pady=15)
        
        self.room_var = ctk.StringVar(value="Select Room")
        self.opt_room = ctk.CTkOptionMenu(f, variable=self.room_var, values=["Select Room"], width=350, height=50,
                                        fg_color="#3d3d3d", button_color="#4d4d4d")
        self.room_var.set("Select Room")
        self.opt_room.pack(pady=15)

        self.ent_rent = ctk.CTkEntry(f, placeholder_text="Monthly Rent (e.g. 5000)", width=350, height=50, corner_radius=10)
        self.ent_rent.pack(pady=15)
        
        btn = ctk.CTkButton(f, text="Confirm Allocation", width=350, height=50, corner_radius=10, font=ctk.CTkFont(weight="bold"),
                           fg_color=COLORS["success"], hover_color="#16a34a", command=self.allocate_action)
        btn.pack(pady=40)
        
        return f

    def build_allocations_view(self):
        f = ctk.CTkFrame(self.main_container, fg_color="transparent")
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(2, weight=1)
        
        header = ctk.CTkLabel(f, text="All Allocations", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Search Frame
        search_f = ctk.CTkFrame(f, fg_color="transparent")
        search_f.grid(row=1, column=0, pady=10, sticky="ew")
        self.search_alloc = ctk.CTkEntry(search_f, placeholder_text="Search by student name or room...", width=300)
        self.search_alloc.pack(side="left", padx=(0,10))
        ctk.CTkButton(search_f, text="Search", width=80, command=self.refresh_allocations_list).pack(side="left")
        ctk.CTkButton(search_f, text="Clear", width=80, fg_color="#444", command=lambda: (self.search_alloc.delete(0, tk.END), self.refresh_allocations_list())).pack(side="left", padx=5)
        
        # Table Styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2d2d2d", foreground="white", fieldbackground="#2d2d2d", borderwidth=0, rowheight=35)
        style.configure("Treeview.Heading", background=COLORS["accent"], foreground="white", relief="flat", font=("Arial", 11, "bold"))
        style.map("Treeview", background=[("selected", COLORS["accent"])])

        tree_f = ctk.CTkFrame(f, corner_radius=15, fg_color=COLORS["card_bg"])
        tree_f.grid(row=2, column=0, sticky="nsew", pady=10)
        
        cols = ("id", "student", "room", "date")
        self.tree_allocs = ttk.Treeview(tree_f, columns=cols, show="headings")
        self.tree_allocs.heading("id", text="ID")
        self.tree_allocs.heading("student", text="Student Name")
        self.tree_allocs.heading("room", text="Room No")
        self.tree_allocs.heading("date", text="Date Allocated")
        
        self.tree_allocs.column("id", width=60, anchor="center")
        self.tree_allocs.column("student", width=250)
        self.tree_allocs.column("room", width=100, anchor="center")
        self.tree_allocs.column("date", width=150)
        
        self.tree_allocs.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        sb = ttk.Scrollbar(tree_f, orient="vertical", command=self.tree_allocs.yview)
        self.tree_allocs.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", pady=10)

        sb.pack(side="right", fill="y", pady=10)

        btn_f = ctk.CTkFrame(f, fg_color="transparent")
        btn_f.grid(row=3, column=0, pady=10, sticky="ew")
        
        ctk.CTkButton(btn_f, text="📥 Export CSV", fg_color="#444", width=120, command=self.export_allocations_action).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_f, text="🗑️ Remove Selected", fg_color=COLORS["error"], command=self.delete_allocation_action).pack(side="right")
        
        return f

    def build_billing_view(self):
        f = ctk.CTkFrame(self.main_container, fg_color="transparent")
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(1, weight=1)
        
        header = ctk.CTkLabel(f, text="💰 Fee Management", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        tree_f = ctk.CTkFrame(f, corner_radius=15, fg_color=COLORS["card_bg"])
        tree_f.grid(row=1, column=0, sticky="nsew", pady=10)
        
        cols = ("id", "student", "room", "rent", "status")
        self.tree_billing = ttk.Treeview(tree_f, columns=cols, show="headings")
        self.tree_billing.heading("id", text="ID")
        self.tree_billing.heading("student", text="Student Name")
        self.tree_billing.heading("room", text="Room")
        self.tree_billing.heading("rent", text="Rent")
        self.tree_billing.heading("status", text="Payment Status")
        
        for c in cols: self.tree_billing.column(c, anchor="center")
        
        self.tree_billing.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        sb = ttk.Scrollbar(tree_f, orient="vertical", command=self.tree_billing.yview)
        self.tree_billing.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", pady=10)
        
        btn_f = ctk.CTkFrame(f, fg_color="transparent")
        btn_f.grid(row=2, column=0, pady=10, sticky="ew")
        ctk.CTkButton(btn_f, text="✅ Toggle Payment Status", width=200, command=self.toggle_fee_status).pack(side="right")
        
        return f

    def build_rooms_view(self):
        f = ctk.CTkFrame(self.main_container, fg_color="transparent")
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(1, weight=1)
        
        header = ctk.CTkLabel(f, text="Rooms Inventory", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        tree_f = ctk.CTkFrame(f, corner_radius=15, fg_color=COLORS["card_bg"])
        tree_f.grid(row=1, column=0, sticky="nsew", pady=10)
        
        cols = ("no", "cap", "occ", "status")
        self.tree_rooms = ttk.Treeview(tree_f, columns=cols, show="headings")
        self.tree_rooms.heading("no", text="Room No")
        self.tree_rooms.heading("cap", text="Capacity")
        self.tree_rooms.heading("occ", text="Occupancy")
        self.tree_rooms.heading("status", text="Status")
        
        for c in cols: self.tree_rooms.column(c, anchor="center")
        
        self.tree_rooms.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        sb = ttk.Scrollbar(tree_f, orient="vertical", command=self.tree_rooms.yview)
        self.tree_rooms.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", pady=10)
        
        ctk.CTkButton(f, text="Delete Room", fg_color=COLORS["error"], command=self.delete_room_action).grid(row=2, column=0, pady=10, sticky="e")
        
        return f

    # --- ACTIONS ---
    def refresh_dashboard(self):
        try:
            conn = get_connection()
            if not conn: return
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM rooms")
            total_rooms = cur.fetchone()[0]
            
            cur.execute("SELECT SUM(capacity), SUM(occupancy) FROM rooms")
            row = cur.fetchone()
            total_cap = row[0] or 0
            total_occ = row[1] or 0
            
            cur.execute("SELECT COUNT(*) FROM students")
            total_studs = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM allocations WHERE fee_paid = FALSE")
            pending_fees = cur.fetchone()[0]
            
            self.stat_total_rooms.update_value(str(total_rooms))
            self.stat_occupancy.update_value(f"{total_occ} / {total_cap}")
            self.stat_students.update_value(str(total_studs))
            self.stat_fees.update_value(str(pending_fees))
            
            available = total_cap - total_occ
            self.dash_info_lbl.configure(text=f"Total Capacity: {total_cap} | Occupied: {total_occ} | Available Slots: {available}")
            
        except Error as e: print(e)
        finally:
            if conn: conn.close()

    def add_room_action(self):
        no, cap, status = self.ent_room_no.get(), self.ent_room_cap.get(), self.room_status_var.get()
        if not no or not cap: return messagebox.showwarning("Incomplete", "Fill all fields")
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO rooms (room_number, capacity, status) VALUES (%s, %s, %s)", (int(no), int(cap), status))
            conn.commit()
            messagebox.showinfo("Success", f"Room {no} saved.")
            self.ent_room_no.delete(0, tk.END); self.ent_room_cap.delete(0, tk.END)
        except Error as e: messagebox.showerror("Error", str(e))
        finally: 
            if conn: conn.close()

    def add_student_action(self):
        name, contact = self.ent_stud_name.get(), self.ent_stud_contact.get()
        if not name: return messagebox.showwarning("Incomplete", "Name is required")
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO students (name, contact) VALUES (%s, %s)", (name, contact))
            conn.commit()
            messagebox.showinfo("Success", f"Student {name} registered.")
            self.ent_stud_name.delete(0, tk.END); self.ent_stud_contact.delete(0, tk.END)
        except Error as e: messagebox.showerror("Error", str(e))
        finally: 
            if conn: conn.close()

    def allocate_action(self):
        stud_str, room_str, rent = self.student_var.get(), self.room_var.get(), self.ent_rent.get()
        if "Select" in stud_str or "Select" in room_str or not rent: return
        try:
            sid = stud_str.split(" - ")[0]
            rno = room_str.split("Room ")[1].split(" ")[0]
            conn = get_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO allocations (student_id, room_number, monthly_rent) VALUES (%s, %s, %s)", (sid, rno, float(rent)))
            cur.execute("UPDATE rooms SET occupancy = occupancy + 1 WHERE room_number = %s", (rno,))
            conn.commit()
            messagebox.showinfo("Success", "Allocation completed.")
            self.ent_rent.delete(0, tk.END)
            self.refresh_dropdowns()
        except Error as e: messagebox.showerror("Error", str(e))
        finally: 
            if conn: conn.close()

    def refresh_allocations_list(self):
        for i in self.tree_allocs.get_children(): self.tree_allocs.delete(i)
        search = f"%{self.search_alloc.get()}%"
        try:
            conn = get_connection(); cur = conn.cursor()
            query = """
                SELECT a.allocation_id, s.name, a.room_number, a.allocation_date 
                FROM allocations a JOIN students s ON a.student_id = s.student_id
                WHERE s.name LIKE %s OR CAST(a.room_number AS CHAR) LIKE %s
                ORDER BY a.allocation_id DESC
            """
            cur.execute(query, (search, search))
            for row in cur.fetchall(): self.tree_allocs.insert("", "end", values=row)
        except Error as e: print(e)
        finally: 
            if conn: conn.close()

    def refresh_rooms_list(self):
        for i in self.tree_rooms.get_children(): self.tree_rooms.delete(i)
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT room_number, capacity, occupancy, status FROM rooms")
            for r in cur.fetchall():
                occ_stat = f"{r[2]}/{r[1]}"
                self.tree_rooms.insert("", "end", values=(r[0], r[1], occ_stat, r[3]))
        except Error as e: print(e)
        finally: 
            if conn: conn.close()

    def refresh_billing_list(self):
        for i in self.tree_billing.get_children(): self.tree_billing.delete(i)
        try:
            conn = get_connection(); cur = conn.cursor()
            query = """
                SELECT a.allocation_id, s.name, a.room_number, a.monthly_rent, a.fee_paid 
                FROM allocations a JOIN students s ON a.student_id = s.student_id
                ORDER BY a.fee_paid ASC, s.name ASC
            """
            cur.execute(query)
            for (aid, name, rno, rent, paid) in cur.fetchall():
                stat = "Paid" if paid else "Pending"
                self.tree_billing.insert("", "end", values=(aid, name, f"Room {rno}", f"${rent}", stat))
        except Error as e: print(e)
        finally: 
            if conn: conn.close()

    def toggle_fee_status(self):
        sel = self.tree_billing.selection()
        if not sel: return
        aid = self.tree_billing.item(sel[0])['values'][0]
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("UPDATE allocations SET fee_paid = NOT fee_paid WHERE allocation_id = %s", (aid,))
            conn.commit()
            self.refresh_billing_list()
        except Error as e: messagebox.showerror("Error", str(e))
        finally: 
            if conn: conn.close()

    def refresh_dropdowns(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT student_id, name FROM students WHERE student_id NOT IN (SELECT student_id FROM allocations)")
            studs = cur.fetchall()
            s_list = [f"{s[0]} - {s[1]}" for s in studs] or ["No students available"]
            self.opt_student.configure(values=s_list)
            self.student_var.set(s_list[0])
            
            cur.execute("SELECT room_number, capacity, occupancy FROM rooms WHERE occupancy < capacity AND status = 'Available'")
            rms = cur.fetchall()
            r_list = [f"Room {r[0]} ({r[1]-r[2]} open)" for r in rms] or ["No rooms available"]
            self.opt_room.configure(values=r_list)
            self.room_var.set(r_list[0])
        except Error as e: print(e)
        finally: 
            if conn: conn.close()

    def delete_allocation_action(self):
        sel = self.tree_allocs.selection()
        if not sel: return
        item = self.tree_allocs.item(sel[0])
        aid, rno = item['values'][0], item['values'][2]
        if messagebox.askyesno("Confirm", "Delete this allocation?"):
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute("DELETE FROM allocations WHERE allocation_id = %s", (aid,))
                cur.execute("UPDATE rooms SET occupancy = occupancy - 1 WHERE room_number = %s", (rno,))
                conn.commit()
                self.refresh_allocations_list()
            except Error as e: messagebox.showerror("Error", str(e))
            finally: 
                if conn: conn.close()

    def export_allocations_action(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT a.allocation_id, s.name, s.contact, a.room_number, a.allocation_date 
                FROM allocations a JOIN students s ON a.student_id = s.student_id
            """)
            rows = cur.fetchall()
            if not rows: return messagebox.showwarning("Empty", "No data to export.")
            
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                with open(file_path, mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Student Name", "Contact", "Room No", "Date"])
                    writer.writerows(rows)
                messagebox.showinfo("Success", "Allocations exported successfully!")
        except Exception as e: messagebox.showerror("Error", str(e))
        finally:
            if conn: conn.close()

    def delete_room_action(self):
        sel = self.tree_rooms.selection()
        if not sel: return
        rno = self.tree_rooms.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Delete Room {rno}? This will also delete allocations."):
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute("DELETE FROM rooms WHERE room_number = %s", (rno,))
                conn.commit()
                self.refresh_rooms_list()
            except Error as e: messagebox.showerror("Error", str(e))
            finally: 
                if conn: conn.close()

if __name__ == "__main__":
    app = HostelApp()
    app.mainloop()
