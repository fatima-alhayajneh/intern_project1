from fastapi import FastAPI
import sqlite3

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect("company.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def read_root():
    return {"status": "Active", "service": "Employee API"}

@app.get("/employee/{emp_id}")
def read_employee(emp_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
    employee = cursor.fetchone()
    conn.close()

    if employee is None:
        return {"error": "Employee not found"}
    
    return dict(employee)
