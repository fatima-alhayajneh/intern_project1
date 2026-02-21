class Employee:
    def __init__(self, name, employee_id, salary):
        self.name = name
        self.employee_id = employee_id
        self.salary = salary

    def display_info(self):
        return f"ID: {self.employee_id}, Name: {self.name}, Salary: {self.salary}"

class Manager(Employee):
    def __init__(self, name, employee_id, salary, department):
        super().__init__(name, employee_id, salary)
        self.department = department

    def display_info(self):
        base_info = super().display_info()
        return f"{base_info}, Department: {self.department}"
