#Python module used to send HTTP requests
import requests

def show_menu():
    print("ToDo App")
    print("1. View Todos")
    print("2. Add Todo")
    print("3. Clear all Todos")
    print("4. Exit")
# comment
while True:
    show_menu()
    choice = input("Enter your choice(1-4): ")
    if choice == '1':
        response = requests.get("http://localhost:8000/todos")
        data = response.json()

        if data.get("status") == "ok":
            todos = data.get("todo",[])
            print("\n ......ToDos......")
            if todos:
                for i, todo in enumerate(todos, 1):
                    print(f"{i}.{todo}")
            else:
                print("No todos found")
        else:
            print(f"Error:{data.get('message')}")


    elif choice == '2':
        todo = input("Enter a new todo: ").strip()
        if not todo:
            print("ToDo cannot be empty.")
            continue

        response = requests.post("http://localhost:8000/add", data=todo)
        data = response.json()
        if data.get("status") == "ok":
            print("Added:",data["todo"][0])
        else:
            print(f"Error:{data.get('message')}")


    elif choice == '3':
        delete = input("are you sure to delete all Todos?yes/no: ")
        if delete.lower() == "yes":
            response = requests.delete("http://localhost:8000/clear")
            data = response.json()
            if data.get("status") == "ok":
                print("all todos deleted")
            else:
                print(f"Error: {data.get('message')}")
        else:
            print("Cancelled deletion")

    elif choice == '4':
        print("Exiting...")
        break

    else:
        print("invalid choice. try again.")