import mysql.connector
from mysql.connector import Error
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk

# Configure appearance
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

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
        messagebox.showerror("Database Connection Error", 
                             f"Could not connect to database.\nError: {e}")
        return None

def initialize_database():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_number INT PRIMARY KEY,
                capacity INT NOT NULL,
                occupancy INT DEFAULT 0
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
                allocation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (room_number) REFERENCES rooms(room_number)
            )
        """)
        
        conn.commit()
    except Error as e:
        print(f"Error initializing DB: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

class HostelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Modern Hostel Allocation System")
        self.geometry("800x600")
        
        initialize_database()

        # Grid Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Hostel\nSystem", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_rooms = ctk.CTkButton(self.sidebar_frame, text="Add Room", command=lambda: self.select_frame("rooms"))
        self.btn_rooms.grid(row=1, column=0, padx=20, pady=10)

        self.btn_students = ctk.CTkButton(self.sidebar_frame, text="Register Student", command=lambda: self.select_frame("students"))
        self.btn_students.grid(row=2, column=0, padx=20, pady=10)

        self.btn_allocations = ctk.CTkButton(self.sidebar_frame, text="Allocate Room", command=lambda: self.select_frame("allocations"))
        self.btn_allocations.grid(row=3, column=0, padx=20, pady=10)

        self.btn_view = ctk.CTkButton(self.sidebar_frame, text="View All", command=lambda: self.select_frame("view"))
        self.btn_view.grid(row=4, column=0, padx=20, pady=10)

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))

        # Main Frame Switcher Layer
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Build subframes
        self.f_rooms = self.build_rooms_frame()
        self.f_students = self.build_students_frame()
        self.f_allocations = self.build_allocations_frame()
        self.f_view = self.build_view_frame()

        self.frames = {
            "rooms": self.f_rooms,
            "students": self.f_students,
            "allocations": self.f_allocations,
            "view": self.f_view
        }

        # Select default
        self.select_frame("rooms")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def select_frame(self, name):
        for key, frame in self.frames.items():
            frame.grid_forget()
            
        self.frames[name].grid(row=0, column=0, sticky="nsew")
        if name == "view":
            self.refresh_view()
        elif name == "allocations":
            self.refresh_allocations_dropdowns()

    def build_rooms_frame(self):
        f = ctk.CTkFrame(self.main_frame, corner_radius=10)
        
        lbl = ctk.CTkLabel(f, text="Add New Room", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(pady=30)

        self.ent_room_no = ctk.CTkEntry(f, placeholder_text="Room Number", width=250, height=40)
        self.ent_room_no.pack(pady=15)

        self.ent_room_cap = ctk.CTkEntry(f, placeholder_text="Capacity", width=250, height=40)
        self.ent_room_cap.pack(pady=15)

        btn = ctk.CTkButton(f, text="Add Room", width=250, height=40, font=ctk.CTkFont(weight="bold"), command=self.add_room)
        btn.pack(pady=20)
        
        return f

    def build_students_frame(self):
        f = ctk.CTkFrame(self.main_frame, corner_radius=10)
        
        lbl = ctk.CTkLabel(f, text="Register Student", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(pady=30)

        self.ent_stud_name = ctk.CTkEntry(f, placeholder_text="Student Name", width=250, height=40)
        self.ent_stud_name.pack(pady=15)

        self.ent_stud_contact = ctk.CTkEntry(f, placeholder_text="Contact Info", width=250, height=40)
        self.ent_stud_contact.pack(pady=15)

        btn = ctk.CTkButton(f, text="Register Student", width=250, height=40, font=ctk.CTkFont(weight="bold"), command=self.add_student)
        btn.pack(pady=20)
        
        return f

    def build_allocations_frame(self):
        f = ctk.CTkFrame(self.main_frame, corner_radius=10)
        
        lbl = ctk.CTkLabel(f, text="Allocate Room", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(pady=30)

        self.student_var = ctk.StringVar(value="Select Student")
        self.opt_student = ctk.CTkOptionMenu(f, variable=self.student_var, values=["Select Student"], width=250, height=40)
        self.opt_student.pack(pady=15)

        self.room_var = ctk.StringVar(value="Select Room")
        self.opt_room = ctk.CTkOptionMenu(f, variable=self.room_var, values=["Select Room"], width=250, height=40)
        self.opt_room.pack(pady=15)

        btn = ctk.CTkButton(f, text="Allocate Room", width=250, height=40, font=ctk.CTkFont(weight="bold"), command=self.allocate_room)
        btn.pack(pady=20)
        
        return f

    def refresh_allocations_dropdowns(self):
        try:
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()
            
            cursor.execute("SELECT student_id, name FROM students WHERE student_id NOT IN (SELECT student_id FROM allocations)")
            students = cursor.fetchall()
            student_list = [f"{s[0]} - {s[1]}" for s in students] if students else ["No unallocated students"]
            self.opt_student.configure(values=student_list)
            self.student_var.set(student_list[0])
            
            cursor.execute("SELECT room_number, capacity, occupancy FROM rooms WHERE occupancy < capacity")
            rooms = cursor.fetchall()
            room_list = [f"Room {r[0]} ({r[1]-r[2]} spots left)" for r in rooms] if rooms else ["No available rooms"]
            self.opt_room.configure(values=room_list)
            self.room_var.set(room_list[0])
            
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if 'conn' in locals() and conn and conn.is_connected():
                conn.close()

    def build_view_frame(self):
        f = ctk.CTkFrame(self.main_frame, corner_radius=10)
        
        lbl = ctk.CTkLabel(f, text="All Allocations", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(pady=10)
        
        # Style treeview for dark mode integration
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=30,
                        fieldbackground="#2b2b2b",
                        borderwidth=0)
        style.map("Treeview", background=[("selected", "#1f538d")])
        style.configure("Treeview.Heading",
                        background="#1f538d",
                        foreground="white",
                        relief="flat",
                        font=("Arial", 10, "bold"))

        tree_frame = ctk.CTkFrame(f)
        tree_frame.pack(expand=True, fill="both", padx=20, pady=20)

        columns = ("alloc_id", "student_name", "room_no", "date")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.tree.heading("alloc_id", text="Alloc ID")
        self.tree.heading("student_name", text="Student Name")
        self.tree.heading("room_no", text="Room No")
        self.tree.heading("date", text="Allocation Date")
        
        self.tree.column("alloc_id", width=80, anchor=tk.CENTER)
        self.tree.column("student_name", width=200, anchor=tk.W)
        self.tree.column("room_no", width=80, anchor=tk.CENTER)
        self.tree.column("date", width=150, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ctk.CTkButton(f, text="Refresh Data", command=self.refresh_view).pack(pady=10)

        return f

    # --- ACTIONS ---
    def add_room(self):
        room_no = self.ent_room_no.get()
        cap = self.ent_room_cap.get()
        
        if not room_no or not cap:
            messagebox.showwarning("Validation Error", "Please fill all fields.")
            return
            
        try:
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute("INSERT INTO rooms (room_number, capacity) VALUES (%s, %s)", (int(room_no), int(cap)))
            conn.commit()
            messagebox.showinfo("Success", f"Room {room_no} added successfully!")
            self.ent_room_no.delete(0, tk.END)
            self.ent_room_cap.delete(0, tk.END)
        except Error as e:
            if "Duplicate entry" in str(e):
                messagebox.showwarning("Error", f"Room {room_no} already exists.")
            else:
                messagebox.showerror("Database Error", str(e))
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter valid numbers.")
        finally:
            if 'conn' in locals() and conn and conn.is_connected():
                conn.close()

    def add_student(self):
        name = self.ent_stud_name.get()
        contact = self.ent_stud_contact.get()
        
        if not name:
            messagebox.showwarning("Validation Error", "Student name is required.")
            return

        try:
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (name, contact) VALUES (%s, %s)", (name, contact))
            conn.commit()
            stud_id = cursor.lastrowid
            messagebox.showinfo("Success", f"Student '{name}' added successfully!\nAssigned ID: {stud_id}")
            self.ent_stud_name.delete(0, tk.END)
            self.ent_stud_contact.delete(0, tk.END)
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if 'conn' in locals() and conn and conn.is_connected():
                conn.close()

    def allocate_room(self):
        selected_student = self.student_var.get()
        selected_room = self.room_var.get()

        if "No unallocated" in selected_student or "Select Student" in selected_student:
            messagebox.showwarning("Validation Error", "Please select a valid student.")
            return
            
        if "No available" in selected_room or "Select Room" in selected_room:
            messagebox.showwarning("Validation Error", "Please select a valid room.")
            return
            
        try:
            stud_id = int(selected_student.split(" - ")[0])
            room_no = int(selected_room.split(" ")[1])
            
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()
            
            cursor.execute("SELECT capacity, occupancy FROM rooms WHERE room_number = %s", (room_no,))
            room = cursor.fetchone()
            if not room:
                messagebox.showwarning("Error", f"Room {room_no} does not exist.")
                return
                
            if room[1] >= room[0]:
                messagebox.showwarning("Error", f"Room {room_no} is fully occupied.")
                return
                
            cursor.execute("SELECT * FROM students WHERE student_id = %s", (stud_id,))
            if not cursor.fetchone():
                messagebox.showwarning("Error", f"Student ID {stud_id} does not exist.")
                return

            cursor.execute("SELECT * FROM allocations WHERE student_id = %s", (stud_id,))
            if cursor.fetchone():
                messagebox.showwarning("Error", f"Student ID {stud_id} is already allocated a room.")
                return

            cursor.execute("INSERT INTO allocations (student_id, room_number) VALUES (%s, %s)", (stud_id, room_no))
            cursor.execute("UPDATE rooms SET occupancy = occupancy + 1 WHERE room_number = %s", (room_no,))
            conn.commit()
            
            messagebox.showinfo("Success", f"Student {stud_id} successfully allocated to Room {room_no}!")
            self.refresh_allocations_dropdowns()

        except Error as e:
            messagebox.showerror("Database Error", str(e))
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter valid IDs/Room numbers.")
        finally:
            if 'conn' in locals() and conn and conn.is_connected():
                conn.close()

    def refresh_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()
            query = """
                SELECT a.allocation_id, s.name, a.room_number, 
                       DATE_FORMAT(a.allocation_date, '%Y-%m-%d %H:%i')
                FROM allocations a
                JOIN students s ON a.student_id = s.student_id
                ORDER BY a.allocation_id DESC
            """
            cursor.execute(query)
            
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
                
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if 'conn' in locals() and conn and conn.is_connected():
                conn.close()

if __name__ == "__main__":
    app = HostelApp()
    app.mainloop()
