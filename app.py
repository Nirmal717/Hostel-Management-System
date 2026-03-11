from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import os

app = FastAPI(title="Hostel Management API")

# Add CORS so React frontend can easily connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        print(f"Database Connection Error: {e}")
        return None

# Models
class Room(BaseModel):
    room_number: int
    capacity: int
    status: str = "Available"

class Student(BaseModel):
    name: str
    contact: str

class Allocation(BaseModel):
    student_id: int
    room_number: int
    monthly_rent: float

@app.get("/")
def read_root():
    return {"message": "Hostel Management API Setup Complete"}

@app.get("/api/dashboard")
def get_dashboard_stats():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cur = conn.cursor(dictionary=True)
        
        cur.execute("SELECT COUNT(*) as count FROM rooms")
        total_rooms = cur.fetchone()['count']
        
        cur.execute("SELECT SUM(capacity) as cap, SUM(occupancy) as occ FROM rooms")
        row = cur.fetchone()
        total_cap = row['cap'] if row['cap'] is not None else 0
        total_occ = row['occ'] if row['occ'] is not None else 0
        
        cur.execute("SELECT COUNT(*) as count FROM students")
        total_studs = cur.fetchone()['count']

        cur.execute("SELECT COUNT(*) as count FROM allocations WHERE fee_paid = FALSE")
        pending_fees = cur.fetchone()['count']
        
        return {
            "total_rooms": total_rooms,
            "total_capacity": total_cap,
            "total_occupied": total_occ,
            "total_students": total_studs,
            "pending_fees": pending_fees,
            "available_slots": total_cap - total_occ
        }
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

@app.get("/api/rooms")
def get_rooms():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM rooms ORDER BY room_number")
        return cur.fetchall()
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

@app.post("/api/rooms")
def add_room(room: Room):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO rooms (room_number, capacity, status) VALUES (%s, %s, %s)", 
                    (room.room_number, room.capacity, room.status))
        conn.commit()
        return {"message": "Room added successfully"}
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

@app.delete("/api/rooms/{room_number}")
def delete_room(room_number: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM rooms WHERE room_number = %s", (room_number,))
        conn.commit()
        return {"message": "Room deleted successfully"}
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

@app.get("/api/students")
def get_students():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM students")
        return cur.fetchall()
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

@app.post("/api/students")
def add_student(student: Student):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO students (name, contact) VALUES (%s, %s)", (student.name, student.contact))
        conn.commit()
        return {"message": "Student registered successfully"}
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

@app.get("/api/allocations")
def get_allocations():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.allocation_id, s.name as student_name, s.contact, a.room_number, 
                   a.monthly_rent, a.fee_paid, a.allocation_date 
            FROM allocations a 
            JOIN students s ON a.student_id = s.student_id
            ORDER BY a.allocation_id DESC
        """)
        return cur.fetchall()
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

@app.post("/api/allocations")
def add_allocation(alloc: Allocation):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cur = conn.cursor()
        # Ensure room has capacity
        cur.execute("SELECT capacity, occupancy FROM rooms WHERE room_number = %s", (alloc.room_number,))
        room_info = cur.fetchone()
        if not room_info:
            raise HTTPException(status_code=400, detail="Room not found")
        if room_info[1] >= room_info[0]:
            raise HTTPException(status_code=400, detail="Room is full")

        # Insert allocation
        cur.execute("INSERT INTO allocations (student_id, room_number, monthly_rent) VALUES (%s, %s, %s)", 
                    (alloc.student_id, alloc.room_number, alloc.monthly_rent))
        
        # Increment occupancy
        cur.execute("UPDATE rooms SET occupancy = occupancy + 1 WHERE room_number = %s", (alloc.room_number,))
        conn.commit()
        return {"message": "Allocation successful"}
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

@app.delete("/api/allocations/{allocation_id}")
def delete_allocation(allocation_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cur = conn.cursor()
        # Find room number first to decrement occupancy
        cur.execute("SELECT room_number FROM allocations WHERE allocation_id = %s", (allocation_id,))
        res = cur.fetchone()
        if not res:
            raise HTTPException(status_code=404, detail="Allocation not found")
        
        room_number = res[0]
        cur.execute("DELETE FROM allocations WHERE allocation_id = %s", (allocation_id,))
        cur.execute("UPDATE rooms SET occupancy = occupancy - 1 WHERE room_number = %s", (room_number,))
        conn.commit()
        return {"message": "Allocation deleted"}
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

@app.put("/api/allocations/{allocation_id}/toggle-fee")
def toggle_fee(allocation_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cur = conn.cursor()
        cur.execute("UPDATE allocations SET fee_paid = NOT fee_paid WHERE allocation_id = %s", (allocation_id,))
        conn.commit()
        return {"message": "Fee status updated"}
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

@app.get("/api/dropdowns")
def get_dropdowns():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cur = conn.cursor(dictionary=True)
        # Students not allocated
        cur.execute("SELECT student_id, name FROM students WHERE student_id NOT IN (SELECT student_id FROM allocations)")
        free_students = cur.fetchall()
        
        # Available rooms
        cur.execute("SELECT room_number, capacity, occupancy FROM rooms WHERE occupancy < capacity AND status = 'Available'")
        available_rooms = cur.fetchall()
        
        return {
            "students": free_students,
            "rooms": available_rooms
        }
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()
