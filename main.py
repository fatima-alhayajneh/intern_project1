from models import Employee, Manager

def main():
    try:
        name = input("Enter name: ")
        emp_id = input("Enter ID: ")
        salary = float(input("Enter salary: "))
        dept = input("Enter department: ")

        mgr = Manager(name, emp_id, salary, dept)
        print(mgr.display_info())
        
    except ValueError:
        print("Error: Please enter a valid number for the salary.")

if __name__== "__main__":
    main()
