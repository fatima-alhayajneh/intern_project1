class Employee:
    def __init__(self, name, role, salary):
        self.name = name
        self.role = role
        self.salary = salary

    def display_info(self):
        print(f"Employee: {self.name} | Role: {self.role} | Salary: {self.salary}")
