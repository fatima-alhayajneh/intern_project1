import sqlite3

def get_db_connection():
    return sqlite3.connect('company.db')

def save_employee_to_db(emp_id, name, salary):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            role TEXT,
            salary REAL
        )
    ''')
    cursor.execute("INSERT OR REPLACE INTO employees (id, name, role, salary) VALUES (?, ?, ?, ?)", 
                   (emp_id, name, "Employee", salary))
    conn.commit()
    conn.close()
    print(f"Employee {name} saved successfully!")
