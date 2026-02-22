from models import * # Conflicting line for Task 4
def main():
    try:
        name = input("Enter name: ")
        emp_id = int(input("Enter ID: "))
        salary = float(input("Enter salary: "))
        dept = input("Enter department: ")

        mgr = Manager(name, emp_id, salary, dept)
        print(mgr.display_info())
        
        mgr.save_to_db()

    except ValueError:
        print("Error: Please enter valid numbers for ID and Salary.")

if __name__ == "__main__":
    main()
