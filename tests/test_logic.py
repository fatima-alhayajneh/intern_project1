import unittest
from app.models import Employee

class TestEmployee(unittest.TestCase):
    def test_employee_creation(self):
        emp = Employee("Test User", "Developer", 5000)
        self.assertEqual(emp.name, "Test User")
        self.assertEqual(emp.salary, 5000)

if __name__ == '__main__':
    unittest.main()
