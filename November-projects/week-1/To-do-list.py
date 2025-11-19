tasks = []
print("welcome to my ")
while True:
    print("\n===== TO-DO LIST =====")
    print("1. Add task")
    print("2. View tasks")
    print("3. Remove task")
    print("4. Clear all tasks")
    print("5. Exit")

    choice = input("Choose option: ")

    if choice == "1":
        task = input("Enter a task: ")
        tasks.append(task)
        print("Task added!")

    elif choice == "2":
        if tasks:
            print("\nYour Tasks:")
            for i, t in enumerate(tasks, start=1):
                print(f"{i}. {t}")
        else:
            print("Your list is empty.")

    elif choice == "3":
        if tasks:
            num = int(input("Task number to remove: "))
            if 1 <= num <= len(tasks):
                removed = tasks.pop(num - 1)
                print(f"Removed: {removed}")
            else:
                print("Invalid number!")
        else:
            print("No tasks to remove.")

    elif choice == "4":
        tasks.clear()
        print("All tasks cleared!")

    elif choice == "5":
        print("Goodbye!")
        break

    else:
        print("Invalid option. Try again.")