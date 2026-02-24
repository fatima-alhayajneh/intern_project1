from app.database import save_employee_to_db

class Employee:
    def __init__(self, name, employee_id=None, salary=0.0):
        self.name = name
        self.employee_id = employee_id
        self.salary = salary

    def display_info(self):
        return f"ID: {self.employee_id}, Name: {self.name}, Salary: {self.salary}"

    def save_to_db(self):
        save_employee_to_db(self.employee_id, self.name, self.salary)

class Manager(Employee):
    def __init__(self, name, employee_id, salary, department):
        super().__init__(name, employee_id, salary)
        self.department = department

    def display_info(self):
        return f"{super().display_info()}, Department: {self.department}"
