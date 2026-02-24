import requests
from app.models import Employee, Manager

def main():
    url = "https://jsonplaceholder.typicode.com/users"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        users_data = response.json()
        
        print("--- Fetching External Data (API) ---")
        for user in users_data:
            emp = Employee(name=user['name'], employee_id=user['id'], salary=1200.0)
            print(emp.display_info())
            emp.save_to_db()

    except requests.exceptions.RequestException:
        print("Error: Could not connect to the service.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("\n" + "="*30 + "\n")

    add_more = input("Do you want to add a manual employee? (y/n): ").lower()
    
    if add_more == 'y':
        try:
            name = input("Enter name: ")
            emp_id = int(input("Enter ID: "))
            salary = float(input("Enter salary: "))
            
            is_manager = input("Is this a manager? (y/n): ").lower()
            if is_manager == 'y':
                dept = input("Enter department: ")
                new_person = Manager(name, emp_id, salary, dept)
            else:
                new_person = Employee(name, emp_id, salary)
                
            print(new_person.display_info())
            new_person.save_to_db()

        except ValueError:
            print("Error: Please enter valid numbers for ID and Salary.")
    else:
        print("Closing program. Have a great day!")

if __name__ == "__main__":
    main()
